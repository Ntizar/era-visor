# -*- coding: utf-8 -*-
"""Correcciones verificadas contra OpenStreetMap (extracción con data=[out::reverse]) 
de los mal ubicados: nodo/nombre exacto en la red ADIF, no coordenadas inventadas.
Cada una contrastada con el título del informe. Transitorio: se ejecuta una vez."""
import json, glob, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# substring archivo -> (estacion, lat, lng, linea_ok, fuente)
FIX = {
    "151124-141118": ("Estación de Tarragona Clasificación", 41.1326042, 1.2295355,
        "622 Aguja Clasif. PK 272,0 a Tarragona Clasificación", "OSM node/2272953656 'Tarragona Clasificación'"),
    "211207-290408": ("Estación de Salou", 41.1118033, 1.0817892,
        "600 Valencia Nord - Sant Vicent de Calders", "OSM node/3979687106 'estación de Salou' (línea 600)"),
    "201208-210409": ("Estación de Salou", 41.1118033, 1.0817892,
        "600 Valencia Nord - Sant Vicent de Calders", "OSM node/3979687106 'estación de Salou' (línea 600)"),
    "090212-271112": ("Estación de Mataró", 41.5358357, 2.4442839,
        "276 Maçanet-Massanes a Bifurcación Sagrera", "OSM node/4683201319 'estación de Mataró' (línea 276)"),
    "240608-281108": ("Estación de Mataró", 41.5358357, 2.4442839,
        "276 Barcelona Sagrera a Maçanet-Massanes", "OSM node/4683201319 'estación de Mataró' (línea 276; 26/2008 fue atropello en Mataró según título)"),
    "060910-290711": ("Estación de Carmonita", 38.7005144, -6.1530109,
        "510 Aljucén - Cáceres", "OSM node/5436494761 'Estación de Carmonita' (línea 510, término municipal de Carmonita)"),
}

for sub, (est, la, lo, linea, fuente) in FIX.items():
    hits = [f for f in glob.glob(os.path.join(RAIZ, "json", "ES", "*.json")) if sub in os.path.basename(f)]
    assert len(hits) == 1, (sub, hits)
    f = hits[0]
    d = json.load(open(f, encoding="utf-8-sig"))
    loc = d.get("ubicacion") or {}
    loc.update({"estacion": est, "lat": la, "lng": lo, "linea": linea,
                "metodo_geo": "estacion_adif", "fuente_geo": fuente, "pk": loc.get("pk")})
    d["ubicacion"] = loc
    json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", os.path.basename(f), "->", est, la, lo)
