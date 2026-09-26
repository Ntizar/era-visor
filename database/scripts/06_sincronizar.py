#!/usr/bin/env python3
"""
06_sincronizar.py — FASE 4A: fusión de las TRES fuentes existentes en una
base canónica por informe. **Determinista, 0 tokens, 0 re-extracción.**

Fuentes que ya existen y que aquí sólo se CRUZAN (nada se re-extrae):

  1. database/data/crudo/    evidencia página+cita, 70 campos de la guía
                             (fuente primaria del dato oficial)
  2. data/db/reports/ES.json consolidado GEOLocalizado: lat/lng con
                             geo_veredicto, víctimas, taxonomía, v3
  3. json/ES/*.json          enriquecido v2/v3: causas sistémicas,
                             precursores, mitigaciones, factores humanos,
                             meteorología, recomendaciones

REGLAS (SPEC):
  · Cada bloque lleva su `origen`: nunca se mezclan fuentes sin decir
    de dónde sale cada dato.
  · La víctimas la manda `data/db` (regla de dominio) y se CONTRASTA con
    el crudo: si difieren se marca `cuadra_crudo=false` y se reporta.
  · La geolocalización NO se modifica: se importa tal cual, con su
    veredicto del auditor. Coords sin verificar jamás entran como
    «exactas».
  · Un informe sin match en alguna fuente queda con ese bloque vacío y
    `fuentes.<n>: null` — nunca se rellena a ojo.

Salida: database/data/sincronizado/<clave>.json (1 por informe,
reanudable) + sincronizado/_resumen.json con las métricas.

Uso:  py database/scripts/06_sincronizar.py [--pais ES] [--fuerza]
Exit: 0 siempre (es una fase de datos); las métricas manda el arnés 99.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DB = RAIZ / "database"
CRUDO = DB / "data" / "crudo"
SINC = DB / "data" / "sincronizado"
DBPAIS = RAIZ / "data" / "db" / "reports"
JSONPAIS = RAIZ / "json"

PAIS = "ES"
if "--pais" in sys.argv:
    PAIS = sys.argv[sys.argv.index("--pais") + 1].upper()
FUERZA = "--fuerza" in sys.argv


def clave_norm(v):
    """0038/2017 · 38/17 · 0013/2007 · 2/2007 -> 0038/2017.
    El cruce con 1-4 dígitos de año de 2-4 es OBLIGATORIO: con un patrón
    de 3-4 dígitos, 8 claves reales no casaban y el cruce parecía roto."""
    v = str(v or "").strip()
    m = re.search(r"(\d{1,4})\s*/\s*(\d{2,4})", v)
    if not m:
        return v
    anio = int(m.group(2))
    if anio < 100:
        anio += 2000
    return "%04d/%d" % (int(m.group(1)), anio)


def txt(v):
    if v in (None, "", [], {}):
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def fallecidos_crudo(doc):
    """Extrae los fallecidos del campo 1.3 del crudo para contrastarlos."""
    c = (doc.get("campos") or {}).get("1.3") or {}
    m = re.search(r"fallecidos:\s*(\d+)", txt(c.get("valor_fuente")))
    return int(m.group(1)) if m else None


def cargar_db():
    """data/db/reports/<PAIS>.json — consolidado geolocalizado."""
    ruta = DBPAIS / ("%s.json" % PAIS)
    if not ruta.is_file():
        return {}
    reg = json.loads(ruta.read_text(encoding="utf-8"))
    out = {}
    for r in reg if isinstance(reg, list) else []:
        out[clave_norm(r.get("expediente") or r.get("id"))] = r
    return out


def cargar_v3():
    """json/<PAIS>/*.json — enriquecido v2/v3 por informe."""
    out = {}
    for f in sorted((JSONPAIS / PAIS).glob("*.json")) if (JSONPAIS / PAIS).is_dir() else []:
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        out[clave_norm(r.get("expediente") or r.get("id"))] = r
    return out


def bloque_geo(db):
    """Sólo los campos con procedencia de auditoría. lat/lng sin veredicto
    NO se consideran exactas y quedan marcadas."""
    if not db:
        return None
    ver = txt(db.get("geo_veredicto"))
    lat, lng = db.get("lat"), db.get("lng")
    tiene = lat not in (None, "", 0, "0") and lng not in (None, "", 0, "0")
    return {
        "lat": float(lat) if tiene else None,
        "lng": float(lng) if tiene else None,
        "metodo_geo": txt(db.get("metodo_geo")),
        "veredicto": ver,
        "motivo": txt(db.get("geo_motivo")),
        "dist_m": db.get("geo_dist_m"),
        "pk": txt(db.get("pk")),
        "linea": txt(db.get("linea")),
        "estacion": txt(db.get("estacion")),
        "provincia": txt(db.get("provincia")),
        "ubicacion_nombre": txt(db.get("ubicacion_nombre")),
        "exacta": bool(tiene and ver == "bien"),
        "origen": "data/db/reports/%s.json" % PAIS,
    }


def bloque_victimas(db, crudo):
    if not db:
        return None
    fdb = db.get("fallecidos")
    fcr = fallecidos_crudo(crudo)
    res = {
        "fallecidos": fdb,
        "heridos_graves": db.get("heridos_graves"),
        "heridos_leves": db.get("heridos_leves"),
        "danos_materiales": txt(db.get("danos_materiales")),
        "gravedad": txt(db.get("gravedad")),
        "origen": "data/db/reports/%s.json" % PAIS,
        "fuente_db_vs_crudo": ("sin_contraste" if fcr is None
                               else "cuadra" if fcr == fdb
                               else "DISCREPANCIA"),
    }
    if fcr is not None and fcr != fdb:
        res["fallecidos_crudo"] = fcr
    return res


def bloque_analisis(db, v3):
    """Todo lo analítico, con su procedencia: lo que trae la consolidación
    y lo que sólo aporta el enriquecido."""
    out = {"origen": []}
    if db:
        for k in ("causa_directa", "tipo", "tipo_categoria", "subsistema",
                  "sistema_proteccion", "tipo_red", "explotacion",
                  "circulation_type", "fase_ciclo_vida", "precursores",
                  "mitigaciones", "factores_humanos", "meteorologia", "tags"):
            if db.get(k) not in (None, "", [], {}):
                out[k] = db[k]
        out["origen"].append("data/db/reports/%s.json" % PAIS)
    if v3:
        for k in ("causas_sistemicas", "tipo_suceso", "tipo_informe",
                  "hora", "entidades", "recomendaciones"):
            if v3.get(k) not in (None, "", [], {}) and k not in out:
                out[k] = v3[k]
        out["origen"].append("json/%s/<id>.json" % PAIS)
    if not out["origen"]:
        return None
    return out


def bloque_textos(db, v3):
    """Resúmenes y narrativas largas (llevan su propia hoja en el Excel)."""
    out = {}
    for fuente, tag in ((db, "db"), (v3, "v3")):
        if not fuente:
            continue
        for k in ("resumen", "descripcion", "hechos", "conclusiones", "v3"):
            v = fuente.get(k)
            if v not in (None, "", [], {}):
                out.setdefault(k, v)
                out.setdefault("_origenes", {})[k] = tag
    return out or None


def main():
    SINC.mkdir(parents=True, exist_ok=True)
    crudos = {}
    for f in sorted(CRUDO.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        crudos[clave_norm(d.get("clave") or d.get("expediente"))] = (f, d)

    db = cargar_db()
    v3 = cargar_v3()

    hechos, solo_crudo, sin_db, sin_v3 = 0, [], [], []
    discrep = []

    for k, (fcr, crudo) in sorted(crudos.items()):
        salida = SINC / (fcr.stem + ".json")
        if salida.is_file() and not FUERZA:
            hechos += 1
            continue
        ddb = db.get(k)
        dv3 = v3.get(k)
        if not ddb:
            sin_db.append(k)
        if not dv3:
            sin_v3.append(k)

        vict = bloque_victimas(ddb, crudo)
        if vict and vict["fuente_db_vs_crudo"] == "DISCREPANCIA":
            discrep.append(k)

        reg = {
            "clave": k,
            "id": crudo.get("id") or (ddb or {}).get("id") or "",
            "pais": PAIS,
            "titulo": (ddb or {}).get("titulo") or crudo.get("titulo") or "",
            "url_oficial": crudo.get("url_oficial") or (ddb or {}).get("url_pdf") or "",
            "anio": crudo.get("anio") or (ddb or {}).get("fecha", "")[:4],
            "fuentes": {
                "crudo": "database/data/crudo/%s" % fcr.name,
                "db": ("data/db/reports/%s.json" % PAIS) if ddb else None,
                "v3": ("json/%s/<id>.json" % PAIS) if dv3 else None,
            },
            "geolocalizacion": bloque_geo(ddb),
            "victimas": vict,
            "analisis": bloque_analisis(ddb, dv3),
            "textos": bloque_textos(ddb, dv3),
        }
        salida.write_text(json.dumps(reg, ensure_ascii=False, indent=1),
                          encoding="utf-8")
        hechos += 1

    # métricas globales para el resumen
    con_geo = exactas = 0
    for k in crudos:
        d = db.get(k)
        if d and d.get("geo_veredicto"):
            con_geo += 1
            if d.get("geo_veredicto") == "bien":
                exactas += 1

    resumen = {
        "pais": PAIS,
        "informes_crudo": len(crudos),
        "sincronizados": hechos,
        "match_db": len(crudos) - len(sin_db),
        "match_v3": len(crudos) - len(sin_v3),
        "sin_db": sin_db,
        "sin_v3": sin_v3,
        "con_veredicto_geo": con_geo,
        "coords_exactas": exactas,
        "victimas_discrepancia": discrep,
    }
    (SINC / "_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")

    print("== 06_sincronizar (%s) ==" % PAIS)
    print("  informes crudo      : %d" % len(crudos))
    print("  sincronizados       : %d" % hechos)
    print("  match con data/db   : %d" % resumen["match_db"])
    print("  match con json/%s   : %d" % (PAIS, resumen["match_v3"]))
    print("  coords con veredicto: %d · exactas (bien): %d"
          % (con_geo, exactas))
    print("  víctimas que DISCREPAN: %d %s" % (len(discrep), discrep[:5]))
    if sin_db:
        print("  ! crudo sin data/db : %s" % sin_db)
    if sin_v3:
        print("  ! crudo sin v3      : %s" % sin_v3[:8])
    return 0


if __name__ == "__main__":
    sys.exit(main())
