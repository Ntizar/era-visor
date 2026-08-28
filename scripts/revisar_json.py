# -*- coding: utf-8 -*-
"""
Revisor IA: valida cada json/ES/<id>.json contra su .md original con LLM,
detecta errores de localizacion, campos vacios o incoherencias, y corrige.

Fases:
  1) Comprobaciones sin LLM (rapidasy deterministas):
     - campos clave presentes y no vacios
     - fecha tipo YYYY-MM-DD, victimas >= 0
     - localizacion: distancia a la red ADIF (usa data/revision/{PAIS}-localizacion.json)
  2) Revision LLM (qwen3.8-flash) sobre los que fallan:
     - lee el .md (cabeza 8000 + cola 8000 chars) y corrige los campos malos.

Uso: python revisar_json.py ES [--limite N]
Salida: data/revision/ES-revision.json + json corregidos en sitio.
"""
import glob
import json
import os
import sys
import re
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CAMPOS_REVISAR = ["titulo", "fecha", "hora", "provincia", "estacion", "pk", "linea", "tipo"]

PROMPT = """Eres un revisor de datos ferroviarios. Te doy un fragmento de un informe de \
investigacion de accidente ferroviario y un JSON ya extraido de el.

Comprueba CADA campo del JSON contra el texto. Corrige SOLO los campos que esten mal, \
inventados o mal interpretados. NO inventes datos que no esten en el texto: si un dato \
no aparece en el texto, dejalo como None. Manten el formato: fecha YYYY-MM-DD, pk tal \
cual aparece, provincia tal cual se nombra.

Devuelve EXCLUSIVAMENTE un JSON valido con ESTAS claves:
{{"titulo": str|null, "fecha": str|null, "hora": str|null, "provincia": str|null, \
"estacion": str|null, "pk": str|null, "linea": str|null, "tipo": str|null, \
"cambios": [lista breve de los campos que corregiste]}}

--- FRAGMENTO DEL INFORME ---
{texto}

--- JSON A REVISAR ---
{json}
"""

CRED = None


def cargar_credenciales():
    global CRED
    if CRED:
        return CRED
    from dotenv import load_dotenv
    env = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", ".env")
    load_dotenv(env)
    base = os.environ.get("OPENAI_BASE_URL")
    key = os.environ.get("OPENAI_API_KEY")
    if not base or not key:
        raise SystemExit("Faltan OPENAI_BASE_URL/OPENAI_API_KEY en " + env)
    CRED = (base.rstrip("/"), key)
    return CRED


def llamar_llm(prompt, max_tokens=1200):
    import urllib.request
    base, key = cargar_credenciales()
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
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))["choices"][0]["message"]["content"]
        except Exception as e:
            if intento == 2:
                raise
            time.sleep(60 * (intento + 1))


def limpiar_json(texto):
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.S)
    m = re.search(r"\{.*\}", texto, re.S)
    return json.loads(m.group(0)) if m else None


def ventana_texto(md):
    if len(md) <= 16000:
        return md
    return md[:8000] + "\n[...]\n" + md[-8000:]


def main():
    codigo = sys.argv[1] if len(sys.argv) > 1 else "ES"
    limite = None
    if "--limite" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--limite") + 1])

    ruta_rev = os.path.join(RAIZ, "data", "revision", f"{codigo}-localizacion.json")
    revision_geo = {}
    if os.path.exists(ruta_rev):
        with open(ruta_rev, encoding="utf-8") as f:
            revision_geo = {e["id"]: e for e in json.load(f)}

    jsons = sorted(glob.glob(os.path.join(RAIZ, "json", codigo, "*.json")))
    os.makedirs(os.path.join(RAIZ, "data", "revision"), exist_ok=True)

    resultados = []
    revisados = 0
    for jf in jsons:
        if limite and revisados >= limite:
            break
        with open(jf, encoding="utf-8") as f:
            d = json.load(f)
        jid = d.get("id") or os.path.splitext(os.path.basename(jf))[0]
        geo = revision_geo.get(jid) or revision_geo.get(os.path.splitext(os.path.basename(jf))[0])

        problemas = []
        # 1) deterministas
        for campo in CAMPOS_REVISAR:
            v = d.get(campo)
            if campo in ("titulo", "fecha") and not v:
                problemas.append(f"campo_vacio:{campo}")
        if d.get("fecha") and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(d["fecha"])):
            problemas.append("formato_fecha")
        # 2) localizacion
        if geo:
            if geo.get("veredicto") in ("duda", "mal"):
                problemas.append(f"localizacion:{geo.get('veredicto')}:{geo.get('dist_via_m')}m")
            if geo.get("provincia_ok") is False:
                problemas.append("provincia_no_coincide")

        entrada = {"id": jid, "problemas": problemas, "cambios": []}
        if problemas:
            md_path = jf.replace("json" + os.sep + codigo, "md" + os.sep + codigo).replace(".json", ".md")
            if os.path.exists(md_path):
                texto = ventana_texto(open(md_path, encoding="utf-8").read())
                prompt = PROMPT.format(texto=texto, json=json.dumps(
                    {c: d.get(c) for c in CAMPOS_REVISAR}, ensure_ascii=False, indent=1))
                try:
                    corr = limpiar_json(llamar_llm(prompt))
                except Exception as e:
                    entrada["error"] = str(e)[:150]
                    resultados.append(entrada)
                    continue
                cambios = []
                for c in CAMPOS_REVISAR:
                    nuevo = corr.get(c)
                    viejo = d.get(c)
                    if nuevo is not None and nuevo != viejo:
                        d[c] = nuevo
                        cambios.append(f"{c}: {viejo!r} -> {nuevo!r}")
                if cambios:
                    with open(jf, "w", encoding="utf-8") as f:
                        json.dump(d, f, ensure_ascii=False, indent=1)
                entrada["cambios"] = cambios
            else:
                entrada["error"] = "sin_md"
        revisados += 1
        resultados.append(entrada)
        if problemas or revisados % 25 == 0:
            print(f"  {revisados} revisados | {jid}: {len(problemas)} problemas, {len(entrada['cambios'])} cambios")

    ruta_sal = os.path.join(RAIZ, "data", "revision", f"{codigo}-revision.json")
    with open(ruta_sal, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=1)

    n_prob = sum(1 for r in resultados if r["problemas"])
    n_camb = sum(1 for r in resultados if r["cambios"])
    print(f"[REVISOR] {len(resultados)} revisados | con problemas: {n_prob} | corregidos: {n_camb}")
    print(f"[REVISOR] Detalle -> {ruta_sal}")


if __name__ == "__main__":
    main()
