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
    # 49/2010 PN provisional en TM de Carmonita; estación de la línea 510.
    # OJO: entrada previa (38.7005,-6.1530) NO era Carmonita — estaba ~55 km al sur
    # (cerca de Zafra). La estación no está mapeada en OSM y la línea 510 no tiene
    # geometría en ADIF (solo 1 tramo a pk 140-142, otra zona). Usar la POBLACIÓN.
    "060910-290711": dict(estacion="Carmonita (Badajoz)", lat=39.1542463, lng=-6.3385430,
        metodo_geo="poblacion", fuente_geo="Carmonita, Badajoz (centro urbano, Nominatim/OSM CC BY 4.0); accidente a pk 24,250-24,420 de la línea 510 Aljucén-Cáceres"),
    # 10/2012 topera en estación de Mataró
    "090212-271112": dict(estacion="Estación de Mataró", lat=41.5358357, lng=2.4442839,
        metodo_geo="estacion_adif", fuente_geo="OSM node/4683201319 'estación de Mataró' (OpenData ADIF, CC BY 4.0)"),
    # 26/2008 arrollamiento PK 26,100 entre Vilassar de Mar y Mataro: estación de Vilassar de Mar
    "IF-240608-281108": dict(lat=41.500487, lng=2.389831,
        metodo_geo="estacion_adif", fuente_geo="OSM node/7206954494 'Vilassar de Mar' (estación, OpenData ADIF CC BY 4.0); informe 26/2008 PK 26,100 l276 entre Vilassar de Mar y Mataró"),
    # 4/2016 conato en Elx Parc: la coord previa era Sabadell Parc del Nord (Barcelona)
    # — falso match por substring 'Parc'. Nodo correcto: Elx-Parc (IGN 38.27215,-0.69506).
    "170331-160125": dict(pk="435,900", lat=38.2721481, lng=-0.6950608, metodo_geo="estacion_ign",
        estacion="Elx-Parc", fuente_geo="Estación de Elx-Parc (IGN 38.27215,-0.69506); PK 435,900 línea 336 'El Reguerón a Alacant Terminal' (no 657,718 del desvío a la 700)"),
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
