# -*- coding: utf-8 -*-
"""Correcciones verificadas de los 'mal ubicados'. Cada coordenada es un nodo
EXACTO de la red ferroviaria (OSM sobre OpenData ADIF, CC BY 4.0) confirmado por
nombre, o el centro urbano de la localidad que el informe declara.
Transitorio: se ejecuta una vez sobre los JSON fuente.
"""
import json, glob, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# substring archivo -> dict a volcar en ubicacion
FIX = {
    # 18/2014 via EV "Tarragona Clasificación": nodo exacto en red ADIF
    "151124-141118": dict(estacion="Estación de Tarragona Clasificación", lat=41.1326042, lng=1.2295355,
        metodo_geo="estacion_adif", fuente_geo="OSM node/2272953656 'Tarragona Clasificación' (OpenData ADIF, CC BY 4.0)"),
    # 27/2007 y 08/2009 arrollamientos en estación de Salou (Tarragona)
    "211207-290408": dict(estacion="Estación de Salou", lat=41.1118033, lng=1.0817892,
        metodo_geo="estacion_adif", fuente_geo="OSM node/3979687106 'estación de Salou' (OpenData ADIF, CC BY 4.0)"),
    "201208-210409": dict(estacion="Estación de Salou", lat=41.1118033, lng=1.0817892,
        metodo_geo="estacion_adif", fuente_geo="OSM node/3979687106 'estación de Salou' (OpenData ADIF, CC BY 4.0)"),
    # 49/2010 PN provisional en TM de Carmonita; estación de la línea 510
    "060910-290711": dict(estacion="Estación de Carmonita", lat=38.7005144, lng=-6.1530109,
        metodo_geo="estacion_adif", fuente_geo="OSM node/5436494761 'Estación de Carmonita' (OpenData ADIF, CC BY 4.0)"),
    # 10/2012 topera en estación de Mataró
    "090212-271112": dict(estacion="Estación de Mataró", lat=41.5358357, lng=2.4442839,
        metodo_geo="estacion_adif", fuente_geo="OSM node/4683201319 'estación de Mataró' (OpenData ADIF, CC BY 4.0)"),
    # 26/2008 arrollamiento PK 26,100 entre Vilassar de Mar y Mataro: estación de Vilassar de Mar
    "IF-240608-281108": dict(lat=41.500487, lng=2.389831,
        metodo_geo="estacion_adif", fuente_geo="OSM node/7206954494 'Vilassar de Mar' (estación, OpenData ADIF CC BY 4.0); informe 26/2008 PK 26,100 l276 entre Vilassar de Mar y Mataró"),
    # 4/2016 conato en Elx Parc: nodo IGN ya correcto; PK 435,900 linea 336 (ADIF,
    # el tramo 657,718 que decia la IA era del desvio a la linea 700)
    "170331-160125": dict(pk="435,900", fuente_geo="PK confirmado 435,900 linea 336 (no 657,718 que corresponde al km 0 del desvio a la 700)"),
    # 44/2013 y su gemelo: recodo del cambiador enlazado a linea 200 (ramales 060 fuera de geometria)
    "IF_060613_281014": dict(fuente_geo="Cambiador de ancho Zaragoza-Delicias (41.658683,-0.910775): recodo enlazado a linea 200; ramal 060 no tiene geometria en ADIF"),
    "271211-250912": dict(fuente_geo="Cambiador de ancho Zaragoza-Delicias (41.658683,-0.910775): recodo enlazado a linea 200; ramal 060 no tiene geometria en ADIF"),
}

for sub, upd in FIX.items():
    hits = [f for f in glob.glob(os.path.join(RAIZ, "json", "ES", "*.json")) if sub in os.path.basename(f)]
    if len(hits) != 1:
        print("SALTADO", sub, "->", [os.path.basename(h) for h in hits]); continue
    d = json.load(open(hits[0], encoding="utf-8-sig"))
    loc = d.get("ubicacion") or {}
    loc.update(upd)
    d["ubicacion"] = loc
    json.dump(d, open(hits[0], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", os.path.basename(hits[0]), "->", {k: upd[k] for k in list(upd)[:2]})
