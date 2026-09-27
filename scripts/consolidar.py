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
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- normalización
# Nada de «0062/07», «17/2007» o «0002/010»: una sola forma en TODA la base.
_RE_CLAVE = re.compile(r"(\d{1,4})\s*/\s*(\d{2,4})")
_STOP = {"estacion", "apeadero", "andenes", "andén", "proximidades", "via",
         "del", "de", "la", "el", "los", "las", "por", "con", "entre"}


def normalizar_clave(valor):
    """0062/07 · 17/2007 · 0002/010 → NNNN/AAAA (4+4). None si no hay clave."""
    if not valor:
        return None
    m = _RE_CLAVE.search(str(valor))
    if not m:
        return None
    anio = m.group(2)
    if len(anio) == 2:
        anio = ("20" + anio) if int(anio) < 30 else ("19" + anio)
    elif len(anio) == 3:            # «010» mal truncado → 2010
        anio = "2" + anio
    return f"{int(m.group(1)):04d}/{anio}"


def _nucleo(texto):
    """Tokens significativos de una estación/lugar, para comparar sin substrings."""
    t = (texto or "").lower()
    t = "".join(c for c in t if c.isalnum() or c.isspace())
    return {w for w in t.split() if len(w) >= 4 and w not in _STOP}


def mismo_suceso(a, b):
    """¿Dos registros con el mismo expediente son REALMENTE el mismo suceso?

    Regla conservadora: mismos hechos si coincide la fecha Y el lugar (una de
    las dos estaciones vacía, una contiene a la otra, o comparten palabra
    significativa). Si duda → NO fusionar: mejor dos registros que perder un
    informe (el dedupe es reversible, un informe borrado no).
    """
    fa, fb = a.get("fecha"), b.get("fecha")
    if fa and fb and fa != fb:
        return False
    la = (a.get("estacion") or "").strip()
    lb = (b.get("estacion") or "").strip()
    if not la or not lb:
        return True
    if la.lower() in lb.lower() or lb.lower() in la.lower():
        return True
    return bool(_nucleo(la) & _nucleo(lb))


def main(codigo: str):
    jsons = sorted((RAIZ / "json" / codigo).glob("*.json"))
    # mapa nombre de archivo → URL real.
    # orden: manifest_maestro (372/372 md, ERA + CIAF) > pdf-manifest ERA > url del json.
    # antes SOLO se miraba el manifest de ERA, y por eso el único informe publicado
    # en transportes.gob.es (114/2023) salía SIN enlace a PDF en el visor.
    url_por_archivo = {}
    manifest_f = RAIZ / "data" / "pdf-manifest" / f"{codigo}.json"
    if manifest_f.exists():
        for it in json.loads(manifest_f.read_text(encoding="utf-8")):
            nombre = it["pdf"].split("/")[-1]
            from urllib.parse import unquote
            url_por_archivo[unquote(nombre)] = "https://www.era.europa.eu" + it["pdf"]
    manifest_maestro_f = RAIZ / "database" / "data" / "manifest_maestro.json"
    if manifest_maestro_f.exists():
        mm = json.loads(manifest_maestro_f.read_text(encoding="utf-8"))
        for it in mm.get("informes", []):
            for pl in it.get("pdf_local") or []:
                url_por_archivo[os.path.splitext(os.path.basename(pl))[0] + ".pdf"] = it.get("url_oficial") or ""
    registros, sin_coords = [], 0
    por_expediente = {}   # expediente normalizado → registro (CIAF gana)
    avisos = []           # colisiones de dedupe que NO se han fusionado

    # carga analisis v3 (json/ES/v3/<stem>.json) indexado por stem del json base
    ruta_v3 = os.path.join(RAIZ, "json", codigo, "v3")
    v3_por_stem = {}
    if os.path.isdir(ruta_v3):
        for fv in Path(ruta_v3).glob("*.json"):
            try:
                v3_por_stem[fv.stem] = json.loads(fv.read_text(encoding="utf-8"))
            except Exception:
                continue

    for f in jsons:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        # analisis v3 de este informe (si existe)
        v3 = v3_por_stem.get(f.stem) or {}
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
            "pk": loc.get("pk") or d.get("pk"),
            "linea": loc.get("linea") or d.get("linea"),
            "ubicacion_nombre": erail.get("Location name"),
            "trenes": d.get("trenes") or [],
            "entidades": d.get("entidades") or [],
            "fallecidos": d.get("fallecidos") or 0,
            "heridos_graves": d.get("heridos_graves") or 0,
            "heridos_leves": d.get("heridos_leves") or 0,
            "danos_materiales": d.get("danos_materiales"),
            "url_pdf": url_por_archivo.get((d.get("archivo_pdf") or "").split("/")[-1]) or d.get("url_pdf"),
            "archivo_pdf": d.get("archivo_pdf"),
            "erail_id": d.get("erail_id"),
            "lat": loc.get("lat") or d.get("lat"),
            "lng": loc.get("lng") or d.get("lng"),
            "metodo_geo": loc.get("metodo_geo"),
            "resumen": d.get("resumen") or v3.get("resumen"),
            "hechos": v3.get("hechos"),
            "v3": v3 if v3 else None,
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
        # ---- clave canónica: NNNN/AAAA (4 dígitos + 4 cifras de año) ----
        clave = normalizar_clave(rec.get("expediente"))
        if clave:
            rec["clave"] = clave
        rec["documentos"] = [f.stem]
        existente = por_expediente.get(clave) if clave else None
        if existente and not mismo_suceso(existente, rec):
            # Colisión de expediente ≠ mismo suceso. Antes esto fusionaba a ciegas y
            # se comió el informe 0013/2007 (El Carrión): su JSON traía mal el número
            # y colisionó con el 0014/2007 (Sant Vicenç) → dos víctimas mortales
            # distintas del 27/02/2007 acabaron siendo UN registro.
            avisos.append(f"[{codigo}] COLISIÓN de expediente {clave}: NO se fusionan "
                          f"«{existente.get('titulo', '')[:60]}» y «{rec.get('titulo', '')[:60]}» "
                          f"(fechas/estaciones distintas) → quedan ambos en la DB")
            existente = None
        if existente:
            # dedupe bidireccional: un solo registro por expediente.
            # gana el que tenga analisis v3/hechos; si empata, CIAF.
            # el perdedor aporta los campos que el ganador no tenga.
            campos_v2 = ("subsistema", "sistema_proteccion", "tipo_red", "explotacion",
                         "precursores", "mitigaciones", "factores_humanos", "meteorologia",
                         "circulation_type", "fase_ciclo_vida", "v3", "hechos",
                         "resumen", "causa_directa", "conclusiones", "recomendaciones", "tags",
                         "trenes", "entidades", "lat", "lng", "metodo_geo", "pk", "linea",
                         "estacion", "provincia", "gravedad", "danos_materiales", "hora")
            def tiene_analisis(x):
                return bool(x.get("hechos") or x.get("v3"))
            if tiene_analisis(rec) and not tiene_analisis(existente):
                gana, pierde = rec, existente
            elif tiene_analisis(existente) and not tiene_analisis(rec):
                gana, pierde = existente, rec
            else:
                # empate: CIAF verificado manda
                if es_ciaf and existente["fuente"] != "CIAF-visor":
                    gana, pierde = rec, existente
                else:
                    gana, pierde = existente, rec
            for campo in campos_v2:
                if pierde.get(campo) and not gana.get(campo):
                    gana[campo] = pierde[campo]
            # los dos documentos del mismo suceso quedan trazados (IF + RS, etc.)
            gana["documentos"] = list(dict.fromkeys(
                (gana.get("documentos") or []) + (pierde.get("documentos") or [])))
            # consecuencias del analisis v3 mandan sobre el JSON base (v3 fue
            # extraido del PDF completo: mas fiable que la primera pasada)
            cons = ((gana.get("v3") or {}).get("consecuencias") or {})
            if cons.get("fallecidos") is not None:
                gana["fallecidos"] = cons["fallecidos"]
            if cons.get("heridos_graves") is not None:
                gana["heridos_graves"] = cons["heridos_graves"]
            if cons.get("heridos_leves") is not None:
                gana["heridos_leves"] = cons["heridos_leves"]
            if gana is rec:
                idx = registros.index(existente)
                registros[idx] = rec
                if rec["id"] is None:
                    rec["id"] = f"{codigo}-{f.stem}"
                por_expediente[clave] = rec
            continue
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

    # normalizacion final: consecuencias del v3 mandan (para TODOS los registros)
    for r in registros:
        cons = ((r.get("v3") or {}).get("consecuencias") or {})
        if cons.get("fallecidos") is not None:
            r["fallecidos"] = cons["fallecidos"]
        if cons.get("heridos_graves") is not None:
            r["heridos_graves"] = cons["heridos_graves"]
        if cons.get("heridos_leves") is not None:
            r["heridos_leves"] = cons["heridos_leves"]

    # propagar el veredicto del auditor geográfico: los mal geolocalizados deben
    # ser visibles y filtrables EN EL VISOR, no solo en data/revision/
    rev_path = RAIZ / "data" / "revision" / f"{codigo}-localizacion.json"
    if rev_path.exists():
        rev = {e["id"]: e for e in json.loads(rev_path.read_text(encoding="utf-8"))}
        n_geo = 0
        for r in registros:
            e = rev.get(r["id"])
            if e:
                r["geo_veredicto"] = e.get("veredicto")
                r["geo_dist_m"] = e.get("dist_via_m")
                r["geo_motivo"] = e.get("motivo")
                if e.get("veredicto") in ("mal", "duda"):
                    n_geo += 1
        print(f"[{codigo}] auditoría geográfica propagada: {n_geo} registros con mal/duda")

    (db / "reports" / f"{codigo}.json").write_text(
        json.dumps(registros, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (db / "recs" / f"{codigo}.json").write_text(
        json.dumps(recs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # índice ligero → ampliado: el visor nueva pantalla (dashboard + tabla) se
    # monta SOLO con esto; el detalle (v3, cronología, recomendaciones) baja
    # suelto por informe desde data/db/detalle/. Así la primera carga deja de
    # tirar de reports/ES.json (4,4 MB) para mostrar 349 filas.
    def _n(x):
        return len(x) if isinstance(x, (list, dict)) else 0

    index = []
    for r in registros:
        v3 = r.get("v3") or {}
        cron = v3.get("cronologia") or []
        index.append({
            "id": r["id"], "pais": r["pais"],
            "clave": normalizar_clave(r.get("expediente")),
            "expediente": r.get("expediente"),
            "fecha": r["fecha"],
            "anio": (r["fecha"] or "")[:4] or None,
            "hora": r.get("hora"),
            "titulo": r["titulo"],
            "titulo_normalizado": v3.get("titulo_normalizado"),
            "tipo": r["tipo"], "tipo_categoria": r.get("tipo_categoria"),
            "tipo_informe": r.get("tipo_informe"),
            "gravedad": r.get("gravedad"),
            "fallecidos": r["fallecidos"],
            "heridos_graves": r["heridos_graves"],
            "heridos_leves": r.get("heridos_leves") or 0,
            "estacion": r["estacion"], "provincia": r["provincia"],
            "pk": r["pk"], "linea": r["linea"],
            "lat": r["lat"], "lng": r["lng"],
            "metodo_geo": r.get("metodo_geo"),
            "geo_veredicto": r.get("geo_veredicto"),
            "geo_dist_m": r.get("geo_dist_m"),
            "fuente": r.get("fuente"), "url_pdf": r["url_pdf"],
            "subsistema": r.get("subsistema"),
            "sistema_proteccion": r.get("sistema_proteccion"),
            "tipo_red": r.get("tipo_red"), "explotacion": r.get("explotacion"),
            "entidades": r.get("entidades") or [],
            "n_recomendaciones": _n(r.get("recomendaciones")),
            "n_cronologia": _n(cron),
            "n_trenes": _n(r.get("trenes")),
            "n_documentos": _n(r.get("documentos")) or 1,
            "victimas_total": (r["fallecidos"] + r["heridos_graves"]
                               + (r.get("heridos_leves") or 0)),
        })
    idx_path = db / "index.json"
    merged = index
    if idx_path.exists():
        prev = json.loads(idx_path.read_text(encoding="utf-8"))
        # conservar SOLO los de otros países: fusionar por id dejaba registros
        # fantasmas de expedientes archivados/deduplicados (619 vs 349 en ES)
        otros = [x for x in prev if x.get("pais") != codigo]
        por_id = {x["id"]: x for x in otros}
        for x in index:
            por_id[x["id"]] = x
        merged = list(por_id.values())
    idx_path.write_text(json.dumps(merged, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # detalle por informe: lo que pide la ficha, bajo demanda (una petición de
    # ~12 KB en lugar de los 4,4 MB de reports/ES.json en cada primera carga)
    det = db / "detalle"
    det.mkdir(parents=True, exist_ok=True)
    viejos = {p.stem for p in det.glob("*.json")}
    for r in registros:
        (det / f"{r['id']}.json").write_text(
            json.dumps(r, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for stem in viejos - {r["id"] for r in registros}:
        (det / f"{stem}.json").unlink(missing_ok=True)

    # dashboard: campos que solo necesita la pestaña de gráficos (causas,
    # precursores, factores, velocidades…). Se pide SOLO al abrir esa pestaña,
    # así la primera carga del visor no arrastra ~600 KB de texto de análisis.
    dash = {}
    for r in registros:
        v3 = r.get("v3") or {}
        inf = v3.get("infraestructura") or {}
        dash[r["id"]] = {
            "causa_directa": r.get("causa_directa"),
            "causas": v3.get("causas") or {},
            "precursores": r.get("precursores") or [],
            "factores_humanos": r.get("factores_humanos") or [],
            "mitigaciones": r.get("mitigaciones") or [],
            "meteorologia": r.get("meteorologia") or [],
            "circulation_type": r.get("circulation_type"),
            "fase_ciclo_vida": r.get("fase_ciclo_vida"),
            "velocidad_maxima": inf.get("velocidad_maxima"),
            "clima": v3.get("clima"),
            "tags": v3.get("tags") or [],
        }
    (db / "dashboard.json").write_text(
        json.dumps(dash, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    for a in avisos:
        print(a)
    tam = sum(f.stat().st_size for f in db.rglob("*.json"))
    print(f"[{codigo}] {len(registros)} registros → data/db/ "
          f"(index {os.path.getsize(idx_path)/1024:.0f} KB · "
          f"detalle/{len(registros)} ficheros · total DB {tam/1024:.0f} KB)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1].upper())
