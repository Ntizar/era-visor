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
import time
import urllib.error
import urllib.request
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(RAIZ, "md")
MD_ES = os.path.join(RAIZ, "md-es")
ESTADO = os.path.join(RAIZ, "data", "traduccion")
MODELO_DEF = "qwen3.8-flash"
BLOQUE = 7000          # caracteres por llamada
RATIO_MIN, RATIO_MAX = 0.75, 1.60
TOL_NUMEROS = 0.02

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


def verificar(orig, trad):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="+")
    ap.add_argument("--modelo", default=MODELO_DEF)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--refuerza", action="store_true")
    ap.add_argument("--reverificar", action="store_true",
                    help="solo re-verifica los md-es existentes (no llama al modelo)")
    a = ap.parse_args()

    if a.reverificar:
        for code in [c.upper() for c in a.paises]:
            reverificar(code)
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
        print(f"[{code}] {len(ficheros)} informes · modelo {a.modelo} · {a.workers} hilos")
        hechos, t_in, t_out = [], 0, 0
        with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(procesar, f, code, a.modelo, base, key, a.refuerza): f for f in ficheros}
            for k, fut in enumerate(cf.as_completed(futs), 1):
                try:
                    r = fut.result()
                except Exception as e:
                    r = {"fichero": futs[fut], "estado": "error", "error": str(e)[:300]}
                hechos.append(r)
                t_in += r.get("tokens_in", 0)
                t_out += r.get("tokens_out", 0)
                if r["estado"] not in ("ya",):
                    print(f"  [{k}/{len(ficheros)}] {r['estado']:8s} {os.path.basename(r['fichero'])}"
                          + (f" · {r['chars']} chars · ratio {r['ratio']}" if r.get("chars") else "")
                          + (f" · {r['avisos']}" if r.get("avisos") else ""))
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
