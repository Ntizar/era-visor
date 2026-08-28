#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enriquecimiento IA schema v2 — añade campos filtrables KAIZEN a los JSON.

Uso:
    python enriquecer_ia.py ES [--limite N] [--force]

Campos: subsistema, sistema_proteccion, tipo_red, explotacion,
        precursores, mitigaciones, factores_humanos, meteorologia,
        circulation_type, fase_ciclo_vida
"""
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MODELO = "qwen3.8-flash"

PROMPT = """Eres un analista de seguridad ferroviaria. Del informe de investigacion, extrae EXACTAMENTE este JSON (sin markdown):

{
 "subsistema": "Infraestructura|Energia|CMS en via|CMS a bordo|Material Rodante Adif|Material Rodante Operador|Explotacion y gestion del trafico|Mantenimiento|Aplicaciones telematicas|null",
 "sistema_proteccion": "ASFA|ERTMS|LZB|EBCL|Otro|Ninguno|null",
 "tipo_red": "Alta Velocidad|Convencional|Cercanias|Media Distancia|Ancho Metrico|null",
 "explotacion": "Nominal|Degradada|null",
 "precursores": ["acciones u omisiones que precedieron al suceso, max 4, 3-8 palabras, en espanol"],
 "mitigaciones": ["medidas que redujeron o habrian reducido la gravedad, max 4, 3-8 palabras, en espanol"],
 "factores_humanos": ["factores humanos u organizativos, max 4, 3-8 palabras, en espanol"],
 "meteorologia": ["viento|precipitacion|hielo|nieve|niebla|temperatura extrema|sismo|luz natural|luz artificial, solo los presentes"],
 "circulation_type": "via_unica|via_multiple|null",
 "fase_ciclo_vida": "Concepto/Diseno|Construccion|Puesta en servicio|Operacion normal|Operacion degradada|Mantenimiento|Retirada del servicio|null"
}

REGLAS:
- NO inventes. Si no consta, null (o [] si es lista).
- Si el texto esta en otro idioma, traduce al espanol.
- Devuelve SOLO JSON valido."""

VALIDOS = {
    "subsistema": ["Infraestructura", "Energía", "CMS en vía", "CMS a bordo",
                   "Material Rodante Adif", "Material Rodante Operador",
                   "Explotación y gestión del tráfico", "Mantenimiento", "Aplicaciones telemáticas"],
    "sistema_proteccion": ["ASFA", "ERTMS", "LZB", "EBCL", "Otro", "Ninguno"],
    "tipo_red": ["Alta Velocidad", "Convencional", "Cercanías", "Media Distancia", "Ancho Métrico"],
    "explotacion": ["Nominal", "Degradada"],
    "circulation_type": ["via_unica", "via_multiple"],
    "fase_ciclo_vida": ["Concepto/Diseño", "Construcción", "Puesta en servicio", "Operación normal",
                        "Operación degradada", "Mantenimiento", "Retirada del servicio"],
}
CAMPOS_LISTA = ["precursores", "mitigaciones", "factores_humanos", "meteorologia"]
METEO = {"viento", "precipitacion", "hielo", "nieve", "niebla",
         "temperatura extrema", "sismo", "luz natural", "luz artificial"}


def cargar_api():
    from dotenv import load_dotenv
    load_dotenv(os.path.expandvars(r"%LOCALAPPDATA%\hermes\.env"))
    base = os.environ["OPENAI_BASE_URL"].rstrip("/")
    key = os.environ["OPENAI_API_KEY"]
    return base, key


def llamar_llm(base, key, texto, reintentos=3):
    for i in range(reintentos):
        try:
            req = urllib.request.Request(
                base + "/chat/completions",
                data=json.dumps({
                    "model": MODELO,
                    "messages": [
                        {"role": "system", "content": PROMPT},
                        {"role": "user", "content": "INFORME:\n\n" + texto},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1500,
                }).encode(),
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + key,
                         "User-Agent": "era-visor/1.0"},
            )
            r = json.loads(urllib.request.urlopen(req, timeout=180).read())
            contenido = r["choices"][0]["message"]["content"].strip()
            contenido = re.sub(r"^```(?:json)?\s*|\s*```$", "", contenido)
            return json.loads(contenido)
        except json.JSONDecodeError as e:
            print("    aviso JSON invalido (%s), reintento %d/%d" % (e, i + 1, reintentos))
            time.sleep(3)
        except Exception as e:
            print("    aviso Error LLM: %s, reintento %d/%d" % (e, i + 1, reintentos))
            time.sleep(5 * (i + 1))
    return None


def ventana(texto, cabeza=9000, cola=6000):
    if len(texto) <= cabeza + cola:
        return texto
    return texto[:cabeza] + "\n[...OMITIDO...]\n" + texto[-cola:]


def sin_acentos(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def sanea(d):
    out = {}
    for k, opciones in VALIDOS.items():
        v = d.get(k)
        v_norm = sin_acentos(v) if isinstance(v, str) else ""
        canon = None
        for o in opciones:
            if v_norm == sin_acentos(o):
                canon = o
                break
        if canon is None and v_norm:
            for o in opciones:
                if v_norm in sin_acentos(o) or sin_acentos(o) in v_norm:
                    canon = o
                    break
        out[k] = canon
    for k in CAMPOS_LISTA:
        v = d.get(k)
        if isinstance(v, str):
            v = [v]
        if not isinstance(v, list):
            v = []
        items = []
        for x in v:
            if not isinstance(x, str):
                continue
            x = re.sub(r"\s+", " ", x.strip())
            n_palabras = len(x.split())
            if 2 <= n_palabras <= 10:
                items.append(x)
        if k == "meteorologia":
            items = [m for m in items if sin_acentos(m) in METEO]
        out[k] = items[:4]
    return out


def main(codigo, limite=None, force=False):
    base, key = cargar_api()
    src = RAIZ / "md" / codigo
    dst = RAIZ / "json" / codigo
    mds = sorted(src.glob("*.md"))
    if limite:
        mds = mds[:limite]
    print("[%s] %d informes a enriquecer" % (codigo, len(mds)))
    ok = fail = skip = 0
    for md in mds:
        out = dst / (md.stem + ".json")
        if not out.exists():
            skip += 1
            continue
        registro = json.loads(out.read_text(encoding="utf-8"))
        if registro.get("enriquecido_v2") and not force:
            ok += 1
            continue
        texto = md.read_text(encoding="utf-8")
        if "Pendiente de OCR" in texto[:400]:
            skip += 1
            continue
        datos = llamar_llm(base, key, ventana(texto))
        if not datos:
            print("  x %s" % md.name)
            fail += 1
            continue
        registro.update(sanea(datos))
        registro["enriquecido_v2"] = True
        out.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
        ok += 1
        time.sleep(1.0)
    print("[%s] ENRIQUECIDO: %d ok, %d fallos, %d omitidos" % (codigo, ok, fail, skip))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    limite = None
    if "--limite" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--limite") + 1])
    main(sys.argv[1].upper(), limite, "--force" in sys.argv)
