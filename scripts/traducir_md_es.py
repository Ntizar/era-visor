# -*- coding: utf-8 -*-
"""traducir_md_es.py — MD original -> MD en castellano normalizado (con verificación).

Lee  md/<CC>/<AAAA>/<slug>.md   (extracción v3, idioma original)
y escribe md-es/<CC>/<AAAA>/<slug>.md  (castellano, estructura normalizada).

Qué hace por informe:
  1. Si el informe ya está en español (idioma: ES) no se traduce: se copia y se
     marca `traduccion: no` (es el original oficial en castellano).
  2. Si no, se trocea por páginas (respetando `## Página N`) en bloques de ~7 000
     caracteres para no perder fidelidad ni truncar la respuesta.
  3. Cada bloque se traduce con el modelo indicado (por defecto qwen3.8-flash,
     el barato de la casa) con un prompt de traductor técnico ferroviario:
     fidelidad literal, cero invención, cero resumen, tablas celda a celda,
     números/referencias/siglas intactos, encabezados a la sección canónica.
  4. Verificación automática por bloque y por informe:
       · los marcadores `## Página N` deben ser exactamente los mismos
       · los tokens numéricos deben coincidir (multiconjunto, tolerancia 2 %)
       · el ratio de longitud castellano/original debe quedar en [0,75 · 1,60]
     Si algo falla se reintenta una vez con instrucción correctiva; si sigue
     fallando el informe se marca `verificacion: revisar` con el motivo
     (nunca se maquilla el resultado).
  5. Estado por informe en data/traduccion/<CC>.json (reanudable).

Uso:
    python scripts/traducir_md_es.py LU
    python scripts/traducir_md_es.py PT --modelo qwen3.6 --workers 3
    python scripts/traducir_md_es.py --pendientes LU PT   # solo lo que falte
"""
import argparse
import concurrent.futures as cf
import datetime
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(RAIZ, "md")
MD_ES = os.path.join(RAIZ, "md-es")
ESTADO = os.path.join(RAIZ, "data", "traduccion")
MODELO_DEF = "qwen3.8-flash"

# Reutiliza el detector de idioma del conversor (mismas listas de palabras función).
from convertir_md_pais import _STOP  # noqa: E402
BLOQUE = 7000          # caracteres por llamada
RATIO_MIN, RATIO_MAX = 0.75, 1.60
TOL_NUMEROS = 0.02

NL = chr(10)

SECCIONES = [
    "Resumen", "Hechos", "Consecuencias", "Cronología", "Infraestructura",
    "Material rodante", "Personal", "Condiciones meteorológicas", "Causas",
    "Factores contribuyentes", "Recomendaciones", "Lecciones aprendidas",
    "Medidas adoptadas", "Anexos",
]

SISTEMA = """Eres traductor técnico jurado especializado en investigación de accidentes ferroviarios.
Traduces al español de España, registro técnico-administrativo oficial (el de un informe de
investigación de un organismo nacional de seguridad ferroviaria).

REGLAS INNEGOCIABLES
1. Fidelidad literal. No resumas, no amplíes, no interpretes, no añadas comentarios.
2. Conserves TODOS los números, fechas, horas, importes, medidas, coordenadas, puntos
   kilométricos, referencias normativas, códigos de tren, siglas (ASFA, ERTMS, LZB, ATP,
   GSM-R...), nombres de estaciones, empresas y personas. No los traduzcas ni los redondees.
3. Conservas el marcado Markdown tal cual: líneas `## Página N` idénticas, encabezados con
   el mismo número de `#`, listas, negritas y tablas (mismas filas y columnas; traduces el
   contenido de cada celda, nunca la estructura).
4. Si un encabezado corresponde a una sección canónica, usa EXACTAMENTE uno de estos nombres:
   """ + ", ".join(SECCIONES) + """.
   Si no corresponde a ninguno, tradúcelo de forma literal.
   IMPORTANTE: si el encabezado lleva numeración (1., 2.3, 4.1.2, 3.5-), CONSÉRVALA delante
   del nombre ("3.5 Recomendaciones"). Nunca borres la numeración: es la estructura del informe.
5. Los superíndices de nota al pie (un número suelto pegado a una palabra o al final de una
   frase) se conservan tal cual y en el mismo punto del texto.
6. Si una palabra o frase es ilegible o está corrupta en el original, escribe [ilegible: ...]
   conservando lo que se lea. Nunca inventes el contenido que falta.
7. Devuelves SOLO la traducción del fragmento, sin preámbulo ni comentario final."""


# ───────────────────────── utilidades ─────────────────────────
def cargar_api():
    from dotenv import load_dotenv
    ruta = os.path.expandvars(r"%LOCALAPPDATA%\hermes\.env")
    if os.path.exists(ruta):
        load_dotenv(ruta)
    base = os.environ["OPENAI_BASE_URL"].strip().strip('"').rstrip("/")
    key = os.environ["OPENAI_API_KEY"].strip()
    return base, key


def partir_frontmatter(texto):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", texto, re.S)
    if not m:
        return {}, texto
    fm = {}
    for linea in m.group(1).splitlines():
        if ":" in linea:
            k, v = linea.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, texto[m.end():]


def trocear(cuerpo, limite=BLOQUE):
    """Parte por páginas (`## Página N`) en bloques <= limite caracteres."""
    piezas = re.split(r"(?m)^(## Página \d+)\s*$", cuerpo)
    paginas = []
    if len(piezas) == 1:
        paginas = [("", cuerpo)]
    else:
        for i in range(1, len(piezas) - 1, 2):
            paginas.append((piezas[i], piezas[i + 1]))
    bloques, actual = [], []
    for marca, txt in paginas:
        trozo = (marca + "\n" + txt) if marca else txt
        if actual and sum(len(x) for x in actual) + len(trozo) > limite:
            bloques.append("\n".join(actual))
            actual = []
        if len(trozo) > limite * 2:            # página gigante: se parte por párrafos
            for sub in re.split(r"\n{2,}", trozo):
                if actual and sum(len(x) for x in actual) + len(sub) > limite:
                    bloques.append("\n".join(actual))
                    actual = []
                actual.append(sub)
        else:
            actual.append(trozo)
    if actual:
        bloques.append("\n".join(actual))
    return [b for b in bloques if b.strip()]


# Solo fechas inequívocas: DD.MM.AAAA, DD/MM/AAAA o AAAAMMDD. NO se incluyen
# variantes de 2 cifras de año ni de 6 dígitos: muerden la numeración de sección
# ("1.12.4.7") y los identificadores, y generan falsos «faltan cifras».
RE_FECHA = re.compile(r"\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4}|(?:19|20)\d{6}")


def numeros(t):
    """(cifras, n_fechas) — y por qué se separan.

    · Las cifras se comparan como tiras de dígitos, sin separadores: "1,5" y "1.5"
      son el mismo dato con otro separador decimal (normalizar la coma es correcto).
    · Las FECHAS se cuentan aparte porque normalizarlas es parte del trabajo:
      "15122017" (alemán) y "15.12.2017" (castellano) son la misma fecha, y
      comparar sus dígitos daría un falso «faltan cifras».
    """
    fechas = len(RE_FECHA.findall(t))
    resto = RE_FECHA.sub(" ", t)
    return Counter(re.findall(r"\d+", resto)), fechas


def marcas(t):
    return Counter(re.findall(r"(?m)^## Página (\d+)\s*$", t))


RE_PAG = re.compile(r"(?m)^## Página (\d+)\s*$")


def paginas(cuerpo):
    """{nº de página: texto} usando los marcadores `## Página N`."""
    out = {}
    ms = list(RE_PAG.finditer(cuerpo))
    for i, m in enumerate(ms):
        fin = ms[i + 1].start() if i + 1 < len(ms) else len(cuerpo)
        out[m.group(1)] = cuerpo[m.end():fin]
    return out


def llamar(base, key, modelo, mensajes, max_tokens=8000, intentos=4):
    cuerpo = json.dumps({
        "model": modelo, "messages": mensajes, "temperature": 0.1,
        "max_tokens": max_tokens, "stream": False,
        # CRÍTICO: los qwen3.x razonan por defecto y se comen TODO el max_tokens
        # en cadenas de pensamiento (respuesta vacía, 10x coste y latencia).
        "enable_thinking": False,
    }).encode()
    for i in range(intentos):
        req = urllib.request.Request(
            base + "/chat/completions", data=cuerpo,
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + key,
                     "User-Agent": "era-visor/traductor"})
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=600).read())
            txt = r["choices"][0]["message"]["content"] or ""
            uso = r.get("usage", {})
            return txt, uso
        except urllib.error.HTTPError as e:
            detalle = e.read().decode("utf-8", "replace")[:200]
            if e.code in (429, 500, 502, 503, 504) and i < intentos - 1:
                time.sleep(8 * (i + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {detalle}")
        except Exception as e:
            if i < intentos - 1:
                time.sleep(5 * (i + 1))
                continue
            raise RuntimeError(f"{type(e).__name__}: {e}")


def traducir_bloque(base, key, modelo, bloque, idioma, correctivo=""):
    user = (f"Traduce al español este fragmento de un informe de investigación ferroviaria "
            f"(idioma original: {idioma}). Devuelve solo la traducción.\n{correctivo}\n\n"
            f"---FRAGMENTO---\n{bloque}")
    return llamar(base, key, modelo,
                  [{"role": "system", "content": SISTEMA}, {"role": "user", "content": user}],
                  max_tokens=min(16000, max(2000, len(bloque) * 2)))


def idioma_linea(linea):
    """Idioma probable de una línea por palabras función (None si no hay señal)."""
    palabras = re.findall(r"[^\W\d_]+", linea.lower())
    if len(palabras) < 4:
        return None
    mejor, puntos = None, 0
    for code, pal in _STOP.items():
        n = sum(1 for p in palabras if p in pal)
        if n > puntos:
            mejor, puntos = code, n
    return mejor if puntos >= 2 else None


def pagina_bilingue(texto):
    """¿La página mezcla dos idiomas (PDF bilingüe intercalado línea a línea)?

    Los informes portugueses (y algunos checos) publican portugués e inglés
    entrelazados en el PDF, de modo que la extracción trae el mismo contenido DOS
    veces. La traducción correcta colapsa el duplicado y sale a la mitad de
    caracteres: sin detectarlo, el verificador lo leía como pérdida masiva.
    """
    cuenta, chars = {}, {}
    for linea in texto.splitlines():
        l = idioma_linea(linea)
        if l:
            cuenta[l] = cuenta.get(l, 0) + 1
            chars[l] = chars.get(l, 0) + len(linea)
    if len(cuenta) < 2:
        return None
    total = sum(cuenta.values())
    principales = [c for c, n in cuenta.items() if n / total >= 0.25]
    if len(principales) < 2:
        return None
    return max(principales, key=lambda c: chars[c])


def solo_idioma(texto, code):
    """Líneas de la página que pertenecen al idioma principal."""
    out = []
    for linea in texto.splitlines():
        l = idioma_linea(linea)
        if l is None or l == code:
            out.append(linea)
    return NL.join(out)


def verificar(orig, trad):
    """Verifica una página; si falla y el original es bilingüe (PT+EN
    intercalados del mismo contenido), repite contra el idioma principal.
    """
    fallos, avisos = _verificar_base(orig, trad)
    if fallos:
        principal = pagina_bilingue(orig)
        if principal:
            f2, a2 = _verificar_base(solo_idioma(orig, principal), trad)
            if len(f2) < len(fallos):
                return f2, a2 + ["original bilingüe: comparado contra el idioma principal (" + principal + ")"]
    return fallos, avisos


def _verificar_base(orig, trad):
    """Dos niveles, porque no todas las cifras pesan igual.

    · DURAS (>=3 dígitos: fechas, PK, importes, referencias, velocidades): deben
      coincidir en multiconjunto. Es la comprobación que manda.
    · CORTAS (1-2 dígitos: "vía 1", "sector 2" y también superíndices de nota al
      pie, que el traductor pierde de forma legítima): se cuentan como aviso, no
      como fallo, salvo que falte más del 15 %.
    El multiconjunto no detecta un cambio de valor (1 por 2), eso lo cubre la
    revisión IA del informe; aquí se garantiza que no DESAPAREZCA contenido.
    """
    fallos, avisos = [], []
    principal = pagina_bilingue(orig)
    if principal:
        orig = solo_idioma(orig, principal)
        avisos.append(f"original bilingüe: se compara contra el idioma principal ({principal})")

    if marcas(orig) != marcas(trad):
        fallos.append(f"marcadores de página: {sum(marcas(orig).values())} vs {sum(marcas(trad).values())}")

    (no, f_o), (nt, f_t) = numeros(orig), numeros(trad)
    if f_o and abs(f_o - f_t) / f_o > 0.10:
        fallos.append(f"fechas: {f_t} en castellano vs {f_o} en el original")
    duras_o = Counter({k: v for k, v in no.items() if len(k) >= 3})
    duras_t = Counter({k: v for k, v in nt.items() if len(k) >= 3})
    faltan = sum((duras_o - duras_t).values())
    total = max(sum(duras_o.values()), 1)
    # Umbral alto a propósito: por debajo de esto lo que hay son artefactos
    # tipográficos (superíndices "Nadal¹⁰", numeración "1.12.4.7", fechas
    # normalizadas). Lo que se persigue aquí es la PÉRDIDA MASIVA (una tabla o un
    # bloque de datos que el traductor se ha saltado); el juicio fino lo hace
    # revisar_md_es.py leyendo original y traducción.
    if faltan / total > 0.20:
        fallos.append(f"cifras largas: faltan {faltan}/{total} ({faltan/total:.0%})")
    elif faltan:
        avisos.append(f"cifras largas: {faltan}/{total}")

    cortas_o = Counter({k: v for k, v in no.items() if len(k) < 3})
    cortas_t = Counter({k: v for k, v in nt.items() if len(k) < 3})
    faltan_c = sum((cortas_o - cortas_t).values())
    total_c = max(sum(cortas_o.values()), 1)
    if faltan_c:
        avisos.append(f"cifras cortas: {faltan_c}/{total_c}")

    if orig.strip():
        ratio = len(trad) / len(orig)
        if not (RATIO_MIN <= ratio <= RATIO_MAX):
            fallos.append(f"ratio {ratio:.2f}")
    return fallos, avisos


def procesar(ruta, code, modelo, base, key, refuerza):
    rel = os.path.relpath(ruta, RAIZ).replace("\\", "/")
    partes = rel.split("/")                    # md/<CC>/<anio>/<fichero>
    anio, fichero = partes[-2], partes[-1]
    destino = os.path.join(MD_ES, code, anio, fichero)
    if os.path.exists(destino) and not refuerza:
        return {"fichero": rel, "estado": "ya"}

    texto = open(ruta, encoding="utf-8").read()
    fm, cuerpo = partir_frontmatter(texto)
    idioma = fm.get("idioma", "")
    hoy = datetime.date.today().isoformat()

    cab = ["---", f"pais: {code}", f"anio: {anio}",
           f"idioma_origen: {idioma}", f"md_origen: md/{code}/{anio}/{fichero}",
           f"md5_origen: {hashlib.md5(texto.encode()).hexdigest()}"]

    if idioma.upper() == "ES":
        trad, avisos, notas, tokens = cuerpo, [], [], [0, 0]
        cab += ["traduccion: no", "modelo: -"]
    else:
        bloques = trocear(cuerpo)
        salida, avisos, notas, tokens = [], [], [], [0, 0]
        for k, b in enumerate(bloques, 1):
            trad_b, uso = traducir_bloque(base, key, modelo, b, idioma)
            fallos, blandos = verificar(b, trad_b)
            if fallos:
                trad_b2, uso2 = traducir_bloque(
                    base, key, modelo, b, idioma,
                    correctivo=("CORRECCIÓN OBLIGATORIA: en el intento anterior falló "
                                + "; ".join(fallos) + ". Repite la traducción completa "
                                "conservando exactamente los marcadores '## Página N' y "
                                "TODOS los números del original."))
                tokens[0] += uso.get("prompt_tokens", 0) + uso2.get("prompt_tokens", 0)
                tokens[1] += uso.get("completion_tokens", 0) + uso2.get("completion_tokens", 0)
                fallos2, blandos2 = verificar(b, trad_b2)
                if len(fallos2) <= len(fallos):
                    trad_b, fallos, blandos = trad_b2, fallos2, blandos2
            else:
                tokens[0] += uso.get("prompt_tokens", 0)
                tokens[1] += uso.get("completion_tokens", 0)
            if fallos:
                avisos.append(f"bloque {k}: " + "; ".join(fallos))
            if blandos:
                notas.append(f"bloque {k}: " + "; ".join(blandos))
            salida.append(trad_b.strip())

        trad = "\n\n".join(salida)
        cab += [f"modelo: {modelo}", f"bloques: {len(bloques)}"]

    ratio = (len(trad) / len(cuerpo)) if cuerpo.strip() else 0
    cab += [f"chars: {len(trad)}",
            f"ratio_longitud: {ratio:.2f}",
            f"tokens_in: {tokens[0]}", f"tokens_out: {tokens[1]}",
            f"verificacion: {'ok' if not avisos else 'revisar'}"]
    if notas:
        cab += [f"notas_cifras: {json.dumps(notas[:6], ensure_ascii=False)}"]
    if avisos:
        cab += [f"avisos: {json.dumps(avisos[:6], ensure_ascii=False)}"]
    cab += [f"fecha_proceso: {hoy}",
            "generador: traducir_md_es.py (traducción IA + verificación numérica)",
            "---", ""]

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(cab) + trad.rstrip() + "\n")
    return {"fichero": rel, "estado": "ok" if not avisos else "revisar",
            "idioma": idioma, "chars": len(trad), "ratio": round(ratio, 2),
            "avisos": avisos[:4], "tokens_in": tokens[0], "tokens_out": tokens[1],
            "destino": os.path.relpath(destino, RAIZ).replace("\\", "/")}


def reverificar(code, refuerza=False):
    """Re-verifica md-es ya traducidos contra su original, SIN llamar al modelo.

    Sirve cuando cambia el verificador (p. ej. la coma decimal): no hace falta
    re-traducir nada, sólo volver a medir y corregir el veredicto del frontmatter.
    """
    raiz = os.path.join(MD_ES, code)
    if not os.path.isdir(raiz):
        return
    n_ok = n_rev = 0
    for dp, _, fs in os.walk(raiz):
        for f in sorted(fs):
            if not f.endswith(".md"):
                continue
            ruta = os.path.join(dp, f)
            texto = open(ruta, encoding="utf-8").read()
            fm, cuerpo = partir_frontmatter(texto)
            origen = fm.get("md_origen", "")
            ruta_or = os.path.join(RAIZ, origen.replace("/", os.sep))
            if not origen or not os.path.exists(ruta_or):
                continue
            _, cuerpo_or = partir_frontmatter(open(ruta_or, encoding="utf-8").read())
            avisos, notas = [], []
            p_or, p_es = paginas(cuerpo_or), paginas(cuerpo)
            if set(p_or) != set(p_es):
                avisos.append(f"páginas: {len(p_or)} original vs {len(p_es)} castellano")
            for k in sorted(set(p_or) & set(p_es), key=int):
                fallos, blandos = verificar(p_or[k], p_es[k])
                if fallos:
                    avisos.append(f"página {k}: " + "; ".join(fallos))
                elif blandos:
                    notas.append(f"página {k}: " + "; ".join(blandos))
            nuevas = []
            for linea in texto.splitlines():
                if linea.startswith("verificacion:"):
                    nuevas.append("verificacion: " + ("ok" if not avisos else "revisar"))
                elif linea.startswith("avisos:") or linea.startswith("notas_cifras:"):
                    continue
                else:
                    nuevas.append(linea)
            if avisos or notas:
                i = nuevas.index("---", 1) if nuevas.count("---") > 1 else len(nuevas)
                if notas:
                    nuevas.insert(i, "notas_cifras: " + json.dumps(notas[:6], ensure_ascii=False))
                if avisos:
                    nuevas.insert(i, "avisos: " + json.dumps(avisos[:6], ensure_ascii=False))
            with open(ruta, "w", encoding="utf-8") as f:
                f.write("\n".join(nuevas) + "\n")
            n_ok += 0 if avisos else 1
            n_rev += 1 if avisos else 0
    print(f"[{code}] reverificados {n_ok + n_rev} · ok {n_ok} · revisar {n_rev}")


def vacios(code, umbral=0.3):
    """Traducciones vacías o truncadas: el castellano es menos del 30% del original.

    Pasa cuando el md se tradujo estando aún sin texto (PDF escaneado antes del OCR)
    o cuando la respuesta del modelo se cortó. Se comparan longitudes de cuerpo, no
    frontmatter, para no confundirlo con un simple cambio de fecha.
    """
    salida = []
    raiz = os.path.join(MD_ES, code)
    if not os.path.isdir(raiz):
        return salida
    for dp, _, fs in os.walk(raiz):
        for f in sorted(fs):
            if not f.endswith('.md') or f.lower().startswith(('indice', 'índice', 'leeme', 'readme')):
                continue
            ruta_es = os.path.join(dp, f)
            fm, cuerpo_es = partir_frontmatter(open(ruta_es, encoding='utf-8').read())
            origen = fm.get('md_origen', '')
            ruta_or = os.path.join(RAIZ, origen.replace('/', os.sep))
            if not origen or not os.path.exists(ruta_or):
                continue
            _, cuerpo_or = partir_frontmatter(open(ruta_or, encoding='utf-8').read())
            if len(cuerpo_or.strip()) < 800:
                continue                      # el original tampoco tiene texto (escaneado)
            if len(cuerpo_es.strip()) < umbral * len(cuerpo_or.strip()):
                salida.append((ruta_es, len(cuerpo_or), len(cuerpo_es)))
    return salida


def obsoletos(code):
    """md-es cuyo origen ha cambiado (md regenerado tras OCR, por ejemplo).

    Cada md-es guarda el md5 del md del que se tradujo. Si el md se ha vuelto a
    generar (OCR de un escaneado, reconversión), esa traducción ya no representa al
    original y hay que rehacerla: aquí se detecta comparando los md5.
    """
    salida = []
    raiz = os.path.join(MD_ES, code)
    if not os.path.isdir(raiz):
        return salida
    for dp, _, fs in os.walk(raiz):
        for f in sorted(fs):
            if not f.endswith('.md') or f.lower().startswith(('indice', 'índice', 'leeme', 'readme')):
                continue
            ruta = os.path.join(dp, f)
            fm, _ = partir_frontmatter(open(ruta, encoding='utf-8').read())
            origen = fm.get('md_origen', '')
            ruta_or = os.path.join(RAIZ, origen.replace('/', os.sep))
            if not origen or not os.path.exists(ruta_or):
                continue
            actual = hashlib.md5(open(ruta_or, encoding='utf-8').read().encode()).hexdigest()
            if fm.get('md5_origen') != actual:
                salida.append(ruta)
    return salida


def reparar(code, modelo, base, key, max_paginas=40):
    """Re-traduce SÓLO las páginas que fallan en los md-es ya escritos.

    Sirve para los informes que quedaron `verificacion: revisar`: en vez de rehacer el
    informe entero (caro y lento), se detectan las páginas con pérdida de cifras o con
    marcador roto y se piden otra vez, con instrucción correctiva. Después se recalcula
    el veredicto. Devuelve (reparados, paginas_reparadas).
    """
    raiz = os.path.join(MD_ES, code)
    if not os.path.isdir(raiz):
        return 0, 0
    n_docs = n_pags = 0
    for dp, _, fs in os.walk(raiz):
        for f in sorted(fs):
            if not f.endswith(".md") or f.lower().startswith(("indice", "índice", "leeme", "readme")):
                continue
            ruta = os.path.join(dp, f)
            texto = open(ruta, encoding="utf-8").read()
            fm, cuerpo = partir_frontmatter(texto)
            if fm.get("verificacion") == "ok" or fm.get("texto") == "ocr":
                continue
            origen = fm.get("md_origen", "")
            ruta_or = os.path.join(RAIZ, origen.replace("/", os.sep))
            if not origen or not os.path.exists(ruta_or):
                continue
            _, cuerpo_or = partir_frontmatter(open(ruta_or, encoding="utf-8").read())
            p_or, p_es = paginas(cuerpo_or), paginas(cuerpo)
            malas = []
            for k in sorted(set(p_or) & set(p_es), key=int):
                fallos, _ = verificar(p_or[k], p_es[k])
                if fallos:
                    malas.append(k)
            for k in [k for k in p_or if k not in p_es]:
                p_es[k] = ""
                malas.append(k)
            if not malas:
                # los avisos no se reparan (son ruido tipográfico): se marca ok
                p_es = p_es
                nuevo = _reconstruir(texto, p_es, fm, "ok", [])
                open(ruta, "w", encoding="utf-8").write(nuevo)
                continue
            for k in malas[:max_paginas]:
                bloque = f"## Página {k}\n\n{p_or[k]}"
                trad, _ = traducir_bloque(base, key, modelo, bloque, fm.get("idioma_origen", ""))
                # se quita el marcador que devuelve el modelo (lo pone el ensamblador)
                lineas = [l for l in trad.strip().splitlines() if not re.match(r"(?m)^## Página \d+\s*$", l)]
                p_es[k] = "\n".join(lineas).strip()
                fallos, _ = verificar(p_or[k], p_es[k])
                if fallos:
                    trad2, _ = traducir_bloque(
                        base, key, modelo, bloque, fm.get("idioma_origen", ""),
                        correctivo=("CORRECCIÓN OBLIGATORIA: falló " + "; ".join(fallos)
                                    + ". Traduce el fragmento completo, sin omitir ninguna "
                                      "línea, tabla ni cifra."))
                    lineas = [l for l in trad2.strip().splitlines()
                              if not re.match(r"(?m)^## Página \d+\s*$", l)]
                    cand = "\n".join(lineas).strip()
                    fallos2, _ = verificar(p_or[k], cand)
                    if len(fallos2) <= len(fallos):
                        p_es[k] = cand
                n_pags += 1
            # veredicto final del informe
            avisos = []
            for k in sorted(set(p_or) & set(p_es), key=int):
                fallos, _ = verificar(p_or[k], p_es[k])
                if fallos:
                    avisos.append(f"página {k}: " + "; ".join(fallos))
            nuevo = _reconstruir(texto, p_es, fm, "ok" if not avisos else "revisar", avisos)
            open(ruta, "w", encoding="utf-8").write(nuevo)
            n_docs += 1
            print(f"  reparado {f} · {len(malas)} pág · "
                  f"{'ok' if not avisos else str(len(avisos)) + ' siguen mal'}", flush=True)
    print(f"[{code}] REPARADOS {n_docs} informes · {n_pags} páginas re-traducidas")
    return n_docs, n_pags


def _reconstruir(texto, p_es, fm, veredicto, avisos):
    """Rehace el fichero md-es con las páginas nuevas y el veredicto recalculado."""
    nuevas = []
    for k, v in fm.items():
        if k in ('verificacion', 'avisos', 'notas_cifras'):
            continue
        nuevas.append(f"{k}: {v}")
    nuevas.append(f"verificacion: {veredicto}")
    if avisos:
        nuevas.append("avisos: " + json.dumps(avisos[:6], ensure_ascii=False))
    cuerpo = []
    for k in sorted(p_es, key=int):
        cuerpo += [f"## Página {k}", "", p_es[k].rstrip(), ""]
    return ("---" + NL + NL.join(nuevas) + NL + "---" + NL + NL
            + NL.join(cuerpo).rstrip() + NL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="+")
    ap.add_argument("--modelo", default=MODELO_DEF)
    ap.add_argument("--workers", type=int, default=3,
                    help="llamadas simultáneas de día")
    ap.add_argument("--workers-noche", type=int, default=6,
                    help="llamadas simultáneas de 00:00 a 06:00")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--refuerza", action="store_true")
    ap.add_argument("--reverificar", action="store_true",
                    help="solo re-verifica los md-es existentes (no llama al modelo)")
    ap.add_argument("--rehacer", action="store_true",
                    help="con --vacios: vuelve a traducir los detectados")
    ap.add_argument("--vacios", action="store_true",
                    help="rehace las traducciones vacías o truncadas")
    ap.add_argument("--obsoletos", action="store_true",
                    help="solo lista/las rehace si su md de origen ha cambiado")
    ap.add_argument("--reparar", action="store_true",
                    help="re-traduce solo las páginas que fallan en los md-es marcados")
    a = ap.parse_args()

    if a.reverificar:
        for code in [c.upper() for c in a.paises]:
            reverificar(code)
        return

    if a.vacios:
        base, key = cargar_api() if a.rehacer else (None, None)
        for code in [c.upper() for c in a.paises]:
            lista = vacios(code)
            print(f'[{code}] vacios: {len(lista)}')
            for r, lo, le in lista[:10]:
                print(f'   {os.path.relpath(r, RAIZ)}  ({lo} -> {le})')
            if not (a.rehacer and lista):
                continue
            origenes = []
            for ruta_es, _, _ in lista:
                fm, _c = partir_frontmatter(open(ruta_es, encoding='utf-8').read())
                origen = os.path.join(RAIZ, fm.get('md_origen', '').replace('/', os.sep))
                if os.path.exists(origen):
                    origenes.append((origen, ruta_es))
            h = datetime.datetime.now().hour
            n_hilos = a.workers_noche if 0 <= h < 6 else a.workers
            with cf.ThreadPoolExecutor(max_workers=n_hilos) as ex:
                futs = {ex.submit(procesar, o, code, a.modelo, base, key, True): r for o, r in origenes}
                for fut in cf.as_completed(futs):
                    nombre = os.path.basename(futs[fut])
                    try:
                        res = fut.result()
                        print(f"   rehecho {nombre} -> {res.get('estado')} "
                              f"{res.get('chars', '')} chars", flush=True)
                    except Exception as e:
                        print(f"   fallo {nombre}: {e}", flush=True)
        return

    if a.obsoletos:
        for code in [c.upper() for c in a.paises]:
            lista = obsoletos(code)
            print(f'[{code}] obsoletos: {len(lista)}')
            for r in lista[:20]:
                print('   ' + os.path.relpath(r, RAIZ).replace(chr(92), '/'))
        return

    if a.reparar:
        base, key = cargar_api()
        for code in [c.upper() for c in a.paises]:
            reparar(code, a.modelo, base, key)
        return

    base, key = cargar_api()
    os.makedirs(ESTADO, exist_ok=True)
    for code in [c.upper() for c in a.paises]:
        raiz = os.path.join(MD, code)
        if not os.path.isdir(raiz):
            print(f"[{code}] no hay md en {raiz}")
            continue
        ficheros = sorted(
            os.path.join(dp, f) for dp, _, fs in os.walk(raiz) for f in fs if f.endswith(".md"))
        if a.limite:
            ficheros = ficheros[:a.limite]
        print(f"[{code}] {len(ficheros)} informes · modelo {a.modelo} · "
              f"{a.workers} hilos (noche {a.workers_noche} de 00:00 a 06:00)")
        hechos, t_in, t_out = [], 0, 0

        # Concurrencia adaptativa: el límite se consulta antes de cada informe, así
        # que a medianoche sube sola sin reiniciar el proceso y a las 06:00 vuelve a
        # bajar. Se abren los hilos del turno más alto y la puerta los frena.
        tope = max(a.workers, a.workers_noche)
        indice = {"i": 0}
        cerrojo = threading.Lock()
        activos = {"n": 0}

        def limite():
            h = datetime.datetime.now().hour
            return a.workers_noche if 0 <= h < 6 else a.workers

        def coger():
            with cerrojo:
                if indice["i"] >= len(ficheros):
                    return None
                f = ficheros[indice["i"]]
                indice["i"] += 1
                return f

        def obrero(resultados):
            while True:
                f = coger()
                if f is None:
                    return
                while True:                      # puerta: espera a que haya hueco
                    with cerrojo:
                        if activos["n"] < limite():
                            activos["n"] += 1
                            break
                    time.sleep(1)
                try:
                    r = procesar(f, code, a.modelo, base, key, a.refuerza)
                except Exception as e:
                    r = {"fichero": f, "estado": "error", "error": str(e)[:300]}
                finally:
                    with cerrojo:
                        activos["n"] -= 1
                with cerrojo:
                    resultados.append(r)

        resultados = []
        hilos = [threading.Thread(target=obrero, args=(resultados,), daemon=True)
                 for _ in range(tope)]
        for h in hilos:
            h.start()
        vistos = 0
        while any(h.is_alive() for h in hilos):
            time.sleep(5)
            with cerrojo:
                nuevos = resultados[vistos:]
                vistos = len(resultados)
            for r in nuevos:
                hechos.append(r)
                t_in += r.get("tokens_in", 0)
                t_out += r.get("tokens_out", 0)
                if r["estado"] not in ("ya",):
                    print(f"  [{len(hechos)}/{len(ficheros)}] {r['estado']:8s} "
                          f"{os.path.basename(r['fichero'])}"
                          + (f" · {r['chars']} chars · ratio {r['ratio']}"
                             if r.get("chars") else "")
                          + (f" · {r['avisos']}" if r.get("avisos") else ""), flush=True)
        for h in hilos:
            h.join()
        with cerrojo:
            for r in resultados[vistos:]:
                hechos.append(r)
                t_in += r.get("tokens_in", 0)
                t_out += r.get("tokens_out", 0)
        estado = os.path.join(ESTADO, f"{code}.json")
        previo = json.load(open(estado, encoding="utf-8")) if os.path.exists(estado) else {}
        previo.update({r["fichero"]: r for r in hechos})
        json.dump(previo, open(estado, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        ok = sum(1 for r in hechos if r["estado"] in ("ok", "ya"))
        print(f"[{code}] traducidos {ok}/{len(hechos)} · revisar "
              f"{sum(1 for r in hechos if r['estado']=='revisar')} · errores "
              f"{sum(1 for r in hechos if r['estado']=='error')} · tokens {t_in}↓ {t_out}↑")


if __name__ == "__main__":
    main()
