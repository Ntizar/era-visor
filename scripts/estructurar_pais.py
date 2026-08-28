#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estructuración de informes .md → JSON con LLM (qwen3.8-flash vía NaN).

Uso:
    python estructurar_pais.py ES [--limite N] [--force]

Lee md/ES/*.md + data/cruce/ES-cruce.json (datos eRAIL) → json/ES/<id>.json
El eRAIL manda en campos tabulares; el LLM extrae lo que solo está en el texto.
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

SCHEMA_PROMPT = """Eres un extractor de datos de informes de investigación de accidentes ferroviarios.
Del texto del informe, extrae EXACTAMENTE este JSON (sin markdown, solo el JSON):

{
 "expediente": "número de expediente del informe, ej 0041/2008, o null",
 "titulo": "título descriptivo en español (máx 120 chars): qué ocurrió y dónde",
 "fecha_suceso": "YYYY-MM-DD o null",
 "tipo_informe": "final|interino|relacion|otro",
 "tipo_suceso": "descarrilamiento|arrollamiento|colision|paso_a_nivel|incendio|fallos_senal|otro",
 "ubicacion": {"estacion": "nombre o null", "provincia": "null", "pk": "punto kilometrico o null", "linea": "línea/tramo o null"},
 "entidades": ["operadoras y gestores de infraestructura implicados"],
 "resumen": "resumen del suceso en español, 3-5 frases",
 "causa_directa": "causa directa según el informe, 1-3 frases, o null",
 "causas_sistemicas": "factores sistémicos/subyacentes, o null",
 "recomendaciones": ["texto breve de cada recomendación de seguridad"],
 "fallecidos": null,
 "heridos_graves": null,
 "notas": null
}

REGLAS:
- NO inventes datos. Si un campo no está en el texto, pon null. (fallecidos/heridos_graves: déjalos null, se toman de eRAIL)
- Si el texto está en otro idioma, traduce título y resumen al español.
- Devuelve SOLO JSON válido."""


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
                        {"role": "system", "content": SCHEMA_PROMPT},
                        {"role": "user", "content": f"INFORME (puede estar truncado):\n\n{texto}"},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000,
                }).encode(),
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + key,
                         "User-Agent": "era-visor/1.0"},
            )
            r = json.loads(urllib.request.urlopen(req, timeout=180).read())
            contenido = r["choices"][0]["message"]["content"].strip()
            # limpiar posible envoltorio ```json
            contenido = re.sub(r"^```(?:json)?\s*|\s*```$", "", contenido)
            return json.loads(contenido)
        except json.JSONDecodeError as e:
            print(f"    ⚠ JSON inválido ({e}), reintento {i+1}/{reintentos}")
            time.sleep(3)
        except Exception as e:
            print(f"    ⚠ Error LLM: {e}, reintento {i+1}/{reintentos}")
            time.sleep(5 * (i + 1))
    return None


def ventana(texto: str, cabeza=8000, cola=8000) -> str:
    if len(texto) <= cabeza + cola:
        return texto
    return texto[:cabeza] + "\n\n[...SECCION INTERMEDIA OMITIDA...]\n\n" + texto[-cola:]


def main(codigo: str, limite: int = None, force: bool = False):
    base, key = cargar_api()
    cruce = json.loads((RAIZ / "data" / "cruce" / f"{codigo}-cruce.json").read_text(encoding="utf-8"))
    erail_por_pdf = {}
    from urllib.parse import unquote
    for p in cruce["pares"]:
        erail_por_pdf[unquote(p["pdf_path"].split("/")[-1])] = p["erail"]

    src = RAIZ / "md" / codigo
    dst = RAIZ / "json" / codigo
    dst.mkdir(parents=True, exist_ok=True)

    mds = sorted(src.glob("*.md"))
    if limite:
        mds = mds[:limite]
    print(f"[{codigo}] {len(mds)} informes a estructurar")
    ok, fallidos = 0, 0
    for md in mds:
        pdf_rel = "pdfs/" + codigo + "/" + md.stem + ".pdf"
        out = dst / (md.stem + ".json")
        if out.exists() and not force:
            ok += 1
            continue
        texto = md.read_text(encoding="utf-8")
        # saltar placeholders de OCR pendiente
        if "Pendiente de OCR" in texto[:400]:
            print(f"  ⊘ {md.name}: pendiente OCR")
            continue
        erail = erail_por_pdf.get(md.stem + ".pdf", {})
        datos = llamar_llm(base, key, ventana(texto))
        if not datos:
            print(f"  ✗ {md.name}: LLM falló")
            fallidos += 1
            continue
        # fusionar con eRAIL (eRAIL manda en tabulares)
        registro = {
            "id": f"{codigo}-{md.stem}",
            "pais": codigo,
            "archivo_pdf": pdf_rel,
            "url_pdf": "https://www.era.europa.eu" + (cruce["pdfs_huerfanos"] and "" or ""),
            "erail_id": erail.get("ERAIL Occurrence"),
            **datos,
            "erail": {k: v for k, v in erail.items() if v not in (None, "", 0) and k in (
                "Report Type", "Investigation Status", "Occurrence type", "Occurrence description",
                "Location name", "Railway System type", "Line type", "Location type", "Movement type",
                "RU involved", "IM involved", "Total fatalities", "Total serious injuries",
                "Passenger fatalities", "Staff fatalities", "LC User fatalities",
                "Unauthorised person fatalities", "Other fatalities",
                "Passenger serious injuries", "Staff serious injuries", "LC User serious injuries",
                "Unauth. person serious injuries", "Other serious injuries",
                "Estimated total material costs", "Reporting Body",
                "Direct cause description (including causal and contributing factors, excluding those of systemic nature)",
                "Underlying and root causes description (i.e. systemic factors, if any)")},
        }
        # víctimas: del eRAIL siempre
        if erail.get("Total fatalities") is not None:
            registro["fallecidos"] = erail.get("Total fatalities")
        if erail.get("Total serious injuries") is not None:
            registro["heridos_graves"] = erail.get("Total serious injuries")
        # URL real del PDF desde el manifest
        registro["url_pdf"] = None
        out.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
        ok += 1
        time.sleep(1.0)
    print(f"[{codigo}] ESTRUCTURADO: {ok} ok, {fallidos} fallos")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    codigo = sys.argv[1].upper()
    limite = None
    if "--limite" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--limite") + 1])
    main(codigo, limite, force="--force" in sys.argv)
