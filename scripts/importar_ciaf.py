#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Importa los informes verificados de CIAF-visor al proyecto era-visor.

Uso:
    python importar_ciaf.py [ruta-ciaf-visor]

Los informes CIAF (269, 100% geolocalizados, con conclusiones/recomendaciones/tags)
son la fuente PREMIUM para España: sobreescriben a los extraídos por LLM cuando
coincide el expediente (ver consolidar.py).
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DEFECTO_CIAF = RAIZ.parent / "ciaf-visor-ref"


def norm_expediente(exp: str):
    """'0054/2006' → ('0054', '2006') → clave '54/2006'."""
    if not exp:
        return None
    m = re.search(r"(\d{1,4})\s*/\s*(\d{2,4})", str(exp))
    if not m:
        return None
    num = str(int(m.group(1)))
    anio = m.group(2)
    if len(anio) == 2:
        anio = "20" + anio if int(anio) < 30 else "19" + anio
    return f"{num}/{anio}"


def clasificar(tipo: str):
    t = (tipo or "").lower()
    if "descarril" in t: return "descarrilamiento"
    if "arroll" in t: return "arrollamiento"
    if "colision" in t or "conato" in t or "alcance" in t: return "colision"
    if "rebase" in t or "señal" in t or "senal" in t: return "fallos_senal"
    if "incendio" in t: return "incendio"
    if "paso" in t and "nivel" in t: return "paso_a_nivel"
    return "otro"


def normalizar_recs(recs):
    """recomendaciones CIAF: str o dict → (lista de str, lista de dict)."""
    textos, detalles = [], []
    for rec in recs or []:
        if isinstance(rec, dict):
            txt = rec.get("texto") or rec.get("contenido") or rec.get("descripcion") or json.dumps(rec, ensure_ascii=False)
            textos.append(str(txt))
            detalles.append(rec)
        else:
            textos.append(str(rec))
            detalles.append({"texto": str(rec)})
    return textos, detalles


def importar(ruta_ciaf: Path):
    out_dir = RAIZ / "json" / "ES"
    out_dir.mkdir(parents=True, exist_ok=True)
    importados = 0
    for f in sorted((ruta_ciaf / "data" / "reports").glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            clave = norm_expediente(r.get("expediente"))
            if not clave:
                continue
            num, anio = clave.split("/")
            loc = r.get("ubicacion") or {}
            cons = r.get("consecuencias") or {}
            an = r.get("analisis") or {}
            recs_txt, recs_det = normalizar_recs(r.get("recomendaciones"))
            fallecidos = (cons.get("victimas_fallecidos") if cons.get("victimas_fallecidos") is not None
                          else cons.get("victimas_mortales")) or 0
            heridos = (cons.get("victimas_graves") if cons.get("victimas_graves") is not None
                       else cons.get("heridos")) or 0
            enlaces = r.get("enlaces") or {}
            registro = {
                "id": f"ES-CIAF-{num}-{anio}",
                "pais": "ES",
                "expediente": r.get("expediente"),
                "titulo": r.get("titulo"),
                "fecha_suceso": r.get("fecha_suceso"),
                "hora": r.get("hora"),
                "tipo_informe": "final",
                "tipo_suceso": r.get("tipo_suceso") or r.get("tipo"),
                "tipo": clasificar(r.get("tipo_suceso") or r.get("tipo")),
                "gravedad": r.get("gravedad"),
                "ubicacion": {
                    "estacion": loc.get("estacion"),
                    "provincia": loc.get("provincia"),
                    "lat": loc.get("lat"),
                    "lng": loc.get("lng"),
                },
                "pk": r.get("pk"),
                "linea": r.get("tramo"),
                "trenes": r.get("trenes") or [],
                "entidades": r.get("entidades") or [],
                "fallecidos": fallecidos,
                "heridos_graves": heridos,
                "danos_materiales": cons.get("danos_materiales"),
                "resumen": r.get("resumen_verificado") or an.get("resumen"),
                "descripcion": an.get("descripcion"),
                "causa_directa": an.get("causa_directa"),
                "conclusiones": r.get("conclusiones") or [],
                "recomendaciones": recs_txt,
                "recomendaciones_detalle": recs_det,
                "tags": r.get("tags") or [],
                "url_pdf": enlaces.get("ciaf_web"),
                "fuente": "CIAF-visor",
                "calidad": "verificado",
            }
            out = out_dir / f"{registro['id']}.json"
            out.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
            importados += 1
    print(f"[CIAF] {importados} informes importados a json/ES/")


if __name__ == "__main__":
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFECTO_CIAF
    if not ruta.exists():
        print(f"No existe {ruta} — clona CIAF-visor o pasa la ruta")
        sys.exit(1)
    importar(ruta)
