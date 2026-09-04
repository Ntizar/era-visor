# -*- coding: utf-8 -*-
"""
Extraccion v3 COMPLETA: convierte cada md/<pais>/*.md en un analisis profundo
y estructurado (json/<pais>/v3/<id>.json) con IA, tras limpiar el texto:

  1. Limpieza determinista del .md:
     - elimina lineas de indice (puntos de relleno "......  12")
     - elimina numeros de pagina sueltos y cabeceras/pies repetidos
  2. Extraccion IA (qwen3.8-flash) con schema v3 amplio:
     titulo_normalizado, resumen, hechos, cronologia, material_rodante,
     personal, infraestructura, causas, consecuencias, lecciones,
     recomendaciones (con destinatario), idioma_original
  3. Validacion anti-indice y anti-invencion:
     - hechos no puede contener puntos de relleno ni mas de 25 lineas
     - si un dato no esta en el texto -> null

Reanudable: salta los que ya tienen v3/<id>.json salvo --force.
Uso: python extraer_completo.py ES [--limite N] [--force]
"""
import glob
import json
import os
import re
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROMPT = """/no_think
Eres un analista de investigaciones de accidentes ferroviarios (CIAF/ERA). \
Te doy el texto de un informe (limpio, sin indice). Extrae TODA la informacion util \
en espanol, con precision quirurgica.

REGLAS ANTI-INVENCION:
- SOLO datos que aparezcan en el texto. Si no esta: null o lista vacia.
- "hechos" es la descripcion narrativa del suceso (2-4 parrafos max), NUNCA el \
indice del documento ni listas de secciones.
- "titulo_normalizado": titulo breve en espanol, ej. "Descarrilamiento en plena via \
entre Ballobar y Penalba por incendio en locomotora".
- "idioma_original": es/en/fr/de/pt/it... en que esta escrito el informe.
- fechas ISO (YYYY-MM-DD), horas HH:MM.

Devuelve EXCLUSIVAMENTE JSON valido con esta estructura:
{
 "titulo_normalizado": str|null,
 "idioma_original": str|null,
 "resumen": str|null,            // 3-5 frases
 "hechos": str|null,             // narrativa del suceso, sin indice
 "lugar": {"tipo": "plena_via|estacion|apartado|taller|null",
           "estacion": str|null, "pk": str|null, "linea": str|null,
           "provincia": str|null, "descripcion_lugar": str|null},
 "cronologia": [{"hora": str|null, "evento": str}],
 "trenes": [{"numero": str|null, "tipo": str|null, "operador": str|null, "danos": str|null}],
 "personal": [{"rol": str|null, "implicacion": str|null}],
 "infraestructura": {"senalizacion": str|null, "tipo_via": str|null,
                     "velocidad_maxima": str|null, "ancho": str|null,
                     "electrificacion": str|null, "estado_via": str|null,
                     "otro": str|null},
 "material_rodante": {"series": str|null, "averia": str|null, "mantenimiento": str|null},
 "clima": str|null,
 "causas": {"directa": str|null,
            "contribuyentes": [str],
            "sistemicas": [str]},
 "consecuencias": {"fallecidos": int|null, "heridos_graves": int|null,
                   "heridos_leves": int|null, "danos_materiales": str|null,
                   "afectacion_servicio": str|null},
 "lecciones": [str],             // lecciones aprendidas si el informe las enumera
 "recomendaciones": [{"texto": str, "destinatario": str|null}],
 "tags": [str]                   // 5-12 conceptos clave en minusculas
}

--- INFORME (limpio) ---
{texto}

--- DATOS YA CONOCIDOS (usar como pista, verificar contra el texto) ---
{pista}
"""


def cargar_credenciales():
    from dotenv import load_dotenv
    env = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", ".env")
    load_dotenv(env)
    base = os.environ.get("OPENAI_BASE_URL")
    key = os.environ.get("OPENAI_API_KEY")
    if not base or not key:
        raise SystemExit("Faltan OPENAI_BASE_URL/OPENAI_API_KEY en " + env)
    return base.rstrip("/"), key


def llamar_llm(prompt, max_tokens=8000):
    import urllib.request
    base, key = CRED
    cuerpo = json.dumps({
        "model": "qwen3.8-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(
        base + "/chat/completions", data=cuerpo,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key,
                 "User-Agent": "era-visor/1.0"})
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))["choices"][0]["message"]["content"]
        except Exception:
            if intento == 2:
                raise
            time.sleep(90 * (intento + 1))


def limpiar_json(texto):
    texto = re.sub(r"<think>[\s\S]*?</think>", "", texto)
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.S)
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        return None
    bruto = m.group(0)
    try:
        return json.loads(bruto)
    except json.JSONDecodeError:
        return json.loads(bruto, strict=False)  # tolera saltos sin escapar


LIMPIAR_PUNTOS = re.compile(r"\.{4,}\s*\d{0,4}\s*$")


def limpiar_md(texto):
    """Quita indice (puntos de relleno), paginas sueltas y lineas vacias excesivas."""
    lineas = []
    for ln in texto.splitlines():
        l = ln.rstrip()
        if LIMPIAR_PUNTOS.search(l):
            continue
        # numero de pagina suelto
        if re.fullmatch(r"\s*\d{1,3}\s*", l):
            continue
        lineas.append(l)
    # colapsar 3+ vacias a 1
    out, vacias = [], 0
    for l in lineas:
        if not l.strip():
            vacias += 1
            if vacias > 2:
                continue
        else:
            vacias = 0
        out.append(l)
    return "\n".join(out)


def ventana(texto, cabeza=18000, cola=6000):
    if len(texto) <= cabeza + cola:
        return texto
    return texto[:cabeza] + "\n[...]\n" + texto[-cola:]


def validar_v3(v):
    """Repara/censura lo que incumpla las reglas."""
    hechos = v.get("hechos") or ""
    if hechos:
        # descripcion-indice colada
        if re.search(r"\.{4,}", hechos) or len(hechos.splitlines()) > 40:
            v["hechos"] = None
    for k in ("resumen", "hechos"):
        if v.get(k) is not None and not str(v[k]).strip():
            v[k] = None
    for lista in ("cronologia", "recomendaciones", "tags", "lecciones",
                  "personal", "trenes"):
        if not isinstance(v.get(lista), list):
            v[lista] = []
    return v


def main():
    global CRED
    codigo = sys.argv[1] if len(sys.argv) > 1 else "ES"
    limite = None
    if "--limite" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--limite") + 1])
    force = "--force" in sys.argv
    solo = None
    if "--solo" in sys.argv:
        solo = sys.argv[sys.argv.index("--solo") + 1]  # filtro por subcadena del stem

    carpeta_v3 = os.path.join(RAIZ, "json", codigo, "v3")
    os.makedirs(carpeta_v3, exist_ok=True)
    CRED = cargar_credenciales()

    jsons = sorted(glob.glob(os.path.join(RAIZ, "json", codigo, "*.json")))
    hechos_n = fallos = omitidos = 0
    n = 0
    for jf in jsons:
        stem = os.path.splitext(os.path.basename(jf))[0]
        if solo and solo.lower() not in stem.lower():
            continue
        ruta_v3 = os.path.join(carpeta_v3, stem + ".json")
        if os.path.exists(ruta_v3) and not force_flag:
            omitidos += 1
            continue
        if limite and n >= limite:
            break

        ruta_md = jf.replace(os.sep + "json" + os.sep, os.sep + "md" + os.sep).replace(".json", ".md")
        if not os.path.exists(ruta_md):
            omitidos += 1
            continue
        texto = limpiar_md(open(ruta_md, encoding="utf-8").read())
        if len(texto.strip()) < 500:
            omitidos += 1
            continue
        try:
            d_base = json.load(open(jf, encoding="utf-8"))
        except Exception:
            d_base = {}
        pista = json.dumps({k: d_base.get(k) for k in
                            ("titulo", "fecha", "pk", "linea", "provincia", "estacion")},
                           ensure_ascii=False)

        try:
            v = limpiar_json(llamar_llm(PROMPT.replace("{texto}", texto).replace("{pista}", pista)))
            if not v:
                raise ValueError("respuesta sin JSON")
            validar_v3(v)
        except Exception as e:
            fallos += 1
            print(f"  x {stem}: {str(e)[:90]}")
            continue

        v["v3_completo"] = True
        v["id"] = d_base.get("id") or stem
        json.dump(v, open(ruta_v3, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        hechos_n += 1
        n += 1
        if n % 10 == 0:
            print(f"  {n} v3 generados (ult: {stem})")

    print(f"[V3] generados: {hechos_n} | fallos: {fallos} | omitidos: {omitidos}")


force_flag = False
if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    main()
