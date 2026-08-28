#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consolidación: json/ES/*.json + recomendaciones eRAIL → data/db/

Uso:
    python consolidar.py ES

Genera:
    data/db/index.json      metadatos mínimos (mapa + filtros)
    data/db/reports/ES.json registros completos
    data/db/recs/ES.json    recomendaciones de seguridad vinculadas
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main(codigo: str):
    jsons = sorted((RAIZ / "json" / codigo).glob("*.json"))
    # mapa nombre de archivo → URL real desde el manifest
    url_por_archivo = {}
    manifest_f = RAIZ / "data" / "pdf-manifest" / f"{codigo}.json"
    if manifest_f.exists():
        for it in json.loads(manifest_f.read_text(encoding="utf-8")):
            nombre = it["pdf"].split("/")[-1]
            from urllib.parse import unquote
            url_por_archivo[unquote(nombre)] = "https://www.era.europa.eu" + it["pdf"]
    registros, sin_coords = [], 0
    por_expediente = {}   # expediente normalizado → registro (CIAF gana)
    for f in jsons:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        erail = d.get("erail") or {}
        loc = d.get("ubicacion") or {}
        es_ciaf = d.get("fuente") == "CIAF-visor"
        rec = {
            "id": d.get("id"),
            "expediente": d.get("expediente"),
            "titulo": d.get("titulo") or erail.get("Location name", ""),
            "pais": codigo,
            "fecha": d.get("fecha_suceso") or (erail.get("Date of occurrence") or "")[:10] or None,
            "hora": d.get("hora"),
            "tipo": d.get("tipo_suceso") or "otro",
            "tipo_categoria": d.get("tipo"),
            "tipo_informe": d.get("tipo_informe") or "otro",
            "gravedad": d.get("gravedad"),
            "estacion": loc.get("estacion") or d.get("estacion"),
            "provincia": loc.get("provincia") or d.get("provincia"),
            "pk": d.get("pk") or loc.get("pk"),
            "linea": d.get("linea") or loc.get("linea"),
            "ubicacion_nombre": erail.get("Location name"),
            "trenes": d.get("trenes") or [],
            "entidades": d.get("entidades") or [],
            "fallecidos": d.get("fallecidos") or 0,
            "heridos_graves": d.get("heridos_graves") or 0,
            "danos_materiales": d.get("danos_materiales"),
            "url_pdf": url_por_archivo.get((d.get("archivo_pdf") or "").split("/")[-1]) or d.get("url_pdf"),
            "archivo_pdf": d.get("archivo_pdf"),
            "erail_id": d.get("erail_id"),
            "lat": loc.get("lat") or d.get("lat"),
            "lng": loc.get("lng") or d.get("lng"),
            "resumen": d.get("resumen"),
            "descripcion": d.get("descripcion"),
            "causa_directa": d.get("causa_directa"),
            "conclusiones": d.get("conclusiones") or [],
            "recomendaciones": d.get("recomendaciones") or [],
            "tags": d.get("tags") or [],
            "subsistema": d.get("subsistema"),
            "sistema_proteccion": d.get("sistema_proteccion"),
            "tipo_red": d.get("tipo_red"),
            "explotacion": d.get("explotacion"),
            "precursores": d.get("precursores") or [],
            "mitigaciones": d.get("mitigaciones") or [],
            "factores_humanos": d.get("factores_humanos") or [],
            "meteorologia": d.get("meteorologia") or [],
            "circulation_type": d.get("circulation_type"),
            "fase_ciclo_vida": d.get("fase_ciclo_vida"),
            "fuente": d.get("fuente") or "LLM",
        }
        if not rec["lat"]:
            sin_coords += 1
        # dedupe por expediente: CIAF (verificado) pisa al LLM
        import re as _re
        clave = None
        if rec["expediente"]:
            m = _re.search(r"(\d{1,4})\s*/\s*(\d{2,4})", str(rec["expediente"]))
            if m:
                anio = m.group(2)
                if len(anio) == 2:
                    anio = ("20" + anio) if int(anio) < 30 else ("19" + anio)
                clave = f"{int(m.group(1))}/{anio}"
        existente = por_expediente.get(clave) if clave else None
        if existente and existente["fuente"] == "CIAF-visor" and not es_ciaf:
            continue  # CIAF ya está, no pisar con LLM
        if rec["id"] is None:
            rec["id"] = f"{codigo}-{f.stem}"
        registros.append(rec)
        if clave:
            por_expediente[clave] = rec

    # recomendaciones
    recs_file = RAIZ / "data" / "erail" / f"{codigo}-recommendations.json"
    recs = []
    if recs_file.exists():
        recs = json.loads(recs_file.read_text(encoding="utf-8"))

    db = RAIZ / "data" / "db"
    (db / "reports").mkdir(parents=True, exist_ok=True)
    (db / "recs").mkdir(parents=True, exist_ok=True)
    (db / "reports" / f"{codigo}.json").write_text(
        json.dumps(registros, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (db / "recs" / f"{codigo}.json").write_text(
        json.dumps(recs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # índice ligero
    index = [{
        "id": r["id"], "pais": r["pais"], "fecha": r["fecha"], "tipo": r["tipo"],
        "titulo": r["titulo"], "fallecidos": r["fallecidos"], "heridos": r["heridos_graves"],
        "estacion": r["estacion"], "provincia": r["provincia"], "lat": r["lat"], "lng": r["lng"],
        "pk": r["pk"], "linea": r["linea"], "fuente": r["fuente"],
        "tiene_informe": bool(r["url_pdf"]),
    } for r in registros]
    idx_path = db / "index.json"
    merged = index
    if idx_path.exists():
        prev = {x["id"]: x for x in json.loads(idx_path.read_text(encoding="utf-8"))}
        for x in index:
            prev[x["id"]] = x
        merged = list(prev.values())
    idx_path.write_text(json.dumps(merged, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    tam = sum(f.stat().st_size for f in db.rglob("*.json"))
    print(f"[{codigo}] {len(registros)} registros → data/db/ (total DB: {tam/1024:.0f} KB)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1].upper())
