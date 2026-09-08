# -*- coding: utf-8 -*-
"""
Revisor de localización de informes contra la red ferroviaria ADIF real.

Para cada informe geolocalizado:
  1. Distancia al punto kilométrico ADIF más cercano (proxy de distancia a vía).
  2. Provincia del PK más cercano vs provincia declarada en el informe.

Salida: data/revision/{PAIS}-localizacion.json + resumen en consola.
Uso: python revisar_localizacion.py ES
"""
import json
import math
import os
import re
import sys
import unicodedata

CODIGO = sys.argv[1] if len(sys.argv) > 1 else "ES"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# INE: código de provincia -> nombre
PROVINCIAS_INE = {
    "01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería",
    "05": "Ávila", "06": "Badajoz", "07": "Baleares", "08": "Barcelona",
    "09": "Burgos", "10": "Cáceres", "11": "Cádiz", "12": "Castellón",
    "13": "Ciudad Real", "14": "Córdoba", "15": "A Coruña", "16": "Cuenca",
    "17": "Girona", "18": "Granada", "19": "Guadalajara", "20": "Guipúzcoa",
    "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León",
    "25": "Lleida", "26": "La Rioja", "27": "Lugo", "28": "Madrid",
    "29": "Málaga", "30": "Murcia", "31": "Navarra", "32": "Ourense",
    "33": "Asturias", "34": "Palencia", "35": "Las Palmas",
    "36": "Pontevedra", "37": "Salamanca", "38": "Santa Cruz de Tenerife",
    "39": "Cantabria", "40": "Segovia", "41": "Sevilla", "42": "Soria",
    "43": "Tarragona", "44": "Teruel", "45": "Toledo", "46": "Valencia",
    "47": "Valladolid", "48": "Vizcaya", "49": "Zamora", "50": "Zaragoza",
    "51": "Ceuta", "52": "Melilla",
}

# Umbrales en metros
OK_VIA = 500          # < 500 m del PK más cercano: bien ubicado
DUDA_VIA = 2000       # 500-2000 m: revisar; > 2000 m: mal ubicado
# El nodo IGN de una estación marca el RECINTO (manojo de vías + andenes). La
# geometría de tramos ADIF solo tiene el EJE en línea, que pasa por un lado:
# Manresa 70/2022 cayó a 604 m de su propia línea 220 sin estar mal ubicado.
ESTACION_RADIO = 1200


def normalizar(t):
    if not t:
        return ""
    t = unicodedata.normalize("NFD", str(t).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t


def coinciden_provincia(declarada, ine):
    """True si la provincia declarada coincide (o es compatible) con la INE."""
    if not declarada or not ine or ine == "00":
        return None  # no comparable ('00' = tramo ADIF sin provincia asignada)
    a, b = normalizar(declarada), normalizar(PROVINCIAS_INE.get(ine, ine))
    if not a or not b:
        return None
    return a in b or b in a


def distancia_m(lat1, lng1, lat2, lng2):
    """Distancia aproximada en metros (plana, válida a escala nacional)."""
    y = (lat2 - lat1) * 111_320.0
    x = (lng2 - lng1) * 111_320.0 * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(x, y)


def _seg_d(lat, lon, a, b):
    """Distancia de (lat,lon) al segmento a-b ([lon,lat]); válida a escala <10 km."""
    ml = 111_320.0 * math.cos(math.radians(lat))
    ax, ay = (a[0] - lon) * ml, (a[1] - lat) * 110_540.0
    bx, by = (b[0] - lon) * ml, (b[1] - lat) * 110_540.0
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(ax, ay)
    t = max(0.0, min(1.0, -(ax * dx + ay * dy) / L2))
    return math.hypot(ax + t * dx, ay + t * dy)


def _bb_d(lat, lon, bb):
    x0, y0, x1, y1 = bb
    ml = 111_320.0 * math.cos(math.radians(lat))
    return math.hypot(max(x0 - lon, 0.0, lon - x1) * ml,
                      max(y0 - lat, 0.0, lat - y1) * 110_540.0)


def dist_geo(lat, lon, subset):
    """(metros, tramo más cercano) a la geometría de vía de `subset`.

    Mide la distancia REAL a la línea (polilíneas de los tramos ADIF), no al
    marcador PKTeoricos más cercano — los marcadores son escasos (portales de
    túnel, tramos largos) y provocaban falsos dudosos tipo Álora 111/2024:
    coordenada pegada a la línea declarada pero a 501 m del marcador."""
    best, bt = 1e18, None
    for t in subset:
        if _bb_d(lat, lon, t["bb"]) > best:
            continue
        for seg in t["segs"]:
            for i in range(len(seg) - 1):
                d = _seg_d(lat, lon, seg[i], seg[i + 1])
                if d < best:
                    best, bt = d, t
    return best, bt


def code_linea_de(linea_str):
    """Código de línea declarado en el informe ('Línea 130 ...' → '130')."""
    if not linea_str:
        return None
    s = str(linea_str).strip()
    s = re.sub(r"^(?:l[ií]nea|lv|lin(?:e|í)a)\s+|^n[º°]?\s+", "", s, flags=re.I)
    m = re.match(r"^(\d{3,4})\b", s)
    return m.group(1) if m else None


def main():
    ruta_db = os.path.join(RAIZ, "data", "db", "reports", f"{CODIGO}.json")
    ruta_pk = os.path.join(RAIZ, "data", "adif-pkteoricos.geojson")
    ruta_tr = os.path.join(RAIZ, "data", "adif-tramos.geojson")

    with open(ruta_db, encoding="utf-8") as f:
        informes = json.load(f)
    with open(ruta_pk, encoding="utf-8") as f:
        pk_datos = json.load(f)

    # PK precalcados + línea (segmento [2:5] del codtramo y cod_linea del tramo)
    linea_de_tramo = {}
    TRAMOS = []  # geometría de vía para distancia real (no marcadores escasos)
    if os.path.exists(ruta_tr):
        with open(ruta_tr, encoding="utf-8") as f:
            tr = json.load(f)
        for feat in tr.get("features", []):
            props = feat.get("properties") or {}
            ct = props.get("codtramo") or ""
            m = re.match(r"^(\d{3,4})-", props.get("cod_linea") or "")
            if ct:
                linea_de_tramo[ct] = m.group(1) if m else ""
            geom = feat.get("geometry") or {}
            gtype = geom.get("type")
            if gtype not in ("LineString", "MultiLineString"):
                continue
            segs = geom["coordinates"] if gtype == "MultiLineString" else [geom["coordinates"]]
            xs = [pt[0] for seg in segs for pt in seg]
            ys = [pt[1] for seg in segs for pt in seg]
            if not xs:
                continue
            lineas = set()
            for c in ((ct[2:5] if re.fullmatch(r"\d{9}", ct) else ""),
                      (m.group(1) if m else "")):
                if c and c.isdigit():
                    lineas.add(int(c))
            TRAMOS.append({"ct": ct, "lineas": lineas, "segs": segs,
                           "bb": (min(xs), min(ys), max(xs), max(ys)),
                           "provincia": str(props.get("id_provinc") or "").zfill(2)})
    print(f"[REV] {len(TRAMOS)} tramos con geometría")
    puntos = []
    for feat in pk_datos["features"]:
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates")
        if not coords or len(coords) != 2:
            continue
        ct = props.get("codtramo") or ""
        puntos.append({
            "lat": float(coords[1]),
            "lng": float(coords[0]),
            "pk": props.get("pk"),
            "codtramo": ct,
            "cod_linea_pk": ct[2:5] if re.fullmatch(r"\d{9}", ct) else "",
            "cod_linea_tramo": linea_de_tramo.get(ct, ""),
            "provincia": str(props.get("id_provinc") or "").zfill(2),
        })
    print(f"[REV] {len(informes)} informes | {len(puntos)} puntos PK ADIF")

    revision = []
    conteo = {"bien": 0, "duda": 0, "mal": 0, "sin_coords": 0,
              "provincia_ok": 0, "provincia_mal": 0, "provincia_nd": 0}

    # conjunto de códigos de línea numéricos por punto PK
    for p in puntos:
        codes = set()
        for c in (p["cod_linea_pk"], p["cod_linea_tramo"]):
            if c and c.isdigit():
                codes.add(int(c))
        p["lineas"] = codes

    for r in informes:
        lat, lng = r.get("lat"), r.get("lng")
        entrada = {
            "id": r["id"], "titulo": (r.get("titulo") or "")[:90],
            "provincia": r.get("provincia"), "pk": r.get("pk"),
            "linea": r.get("linea"), "lat": lat, "lng": lng,
            "metodo": r.get("metodo_geo") or r.get("fuente_geo"),
        }
        if lat is None or lng is None:
            entrada["veredicto"] = "sin_coords"
            conteo["sin_coords"] += 1
            revision.append(entrada)
            continue

        # PK más cercano (global y de la línea declarada) en un solo barrido
        # líneas candidatas: ubi.linea y raiz.linea pueden diferir (LLM vs CIAF);
        # basta con que ALGUNA casado con la red para validar la ubicación
        linea_cands = set()
        linea_inf = None
        for src in (r.get("linea"), (r.get("ubicacion") or {}).get("linea") if isinstance(r.get("ubicacion"), dict) else None):
            lc = code_linea_de(src)
            if lc and lc.isdigit():
                linea_cands.add(int(lc))
                linea_inf = linea_inf or lc
        li_num = min(linea_cands) if linea_cands else None  # el más específico (3 dígitos)
        mejor, mejor_d = None, 1e18
        mejor_linea, mejor_linea_d = None, 1e18
        for p in puntos:
            d = distancia_m(lat, lng, p["lat"], p["lng"])
            if d < mejor_d:
                mejor_d, mejor = d, p
            if linea_cands and p["lineas"] and (linea_cands & p["lineas"]) and d < mejor_linea_d:
                mejor_linea_d, mejor_linea = d, p

        # DISTANCIA GEOMÉTRICA REAL a la vía (polilíneas de tramos), no al
        # marcador PKTeoricos más cercano: los marcadores son escasos y un suceso
        # perfectamente sobre la vía (Álora 111/2024, PK 124,573 línea 030) queda
        # a +500 m de su marcador por falta de densidad → falso "duda".
        dg, t_g = dist_geo(lat, lng, TRAMOS)
        linea_subset = ([t for t in TRAMOS if linea_cands and t["lineas"] & linea_cands]
                        if linea_cands else [])
        if linea_subset:
            dgl, _t_gl = dist_geo(lat, lng, linea_subset)
        else:
            dgl = None

        entrada["dist_via_m"] = round(mejor_d)          # proxy marcador (densidad)
        entrada["dist_via_geo_m"] = round(dg)           # geometría real
        if dgl is not None:
            entrada["dist_linea_geo_m"] = round(dgl)
        entrada["pk_cercano"] = mejor["pk"]
        entrada["provincia_ine"] = PROVINCIAS_INE.get(mejor["provincia"], mejor["provincia"])
        entrada["coord_pkcercano"] = [mejor["lat"], mejor["lng"]]
        entrada["codtramo_cercano"] = mejor["codtramo"]

        if li_num is not None:
            # caso Caleyo: si las coords caen pegadas a OTRA vía, la distancia
            # geométrica a la línea DECLARADA lo delata (será grande). Manda la
            # métrica geométrica sobre el proxy de marcadores (escasos → falsos
            # dudosos como Álora 111/2024: 0 m de vía real, 501 m del marcador).
            if linea_inf:
                entrada["linea_declarada"] = linea_inf
            if linea_subset:
                if mejor_linea:
                    entrada["dist_linea_m"] = round(mejor_linea_d)
                    entrada["pk_linea_cercano"] = mejor_linea["pk"]
                # el veredicto lo manda la distancia geométrica a la línea
                # DECLARADA (dgl): si cae sobre otra vía, dgl será grande y el
                # caso Caleyo sigue detectado; dg solo alimenta el motivo.
                p_ref, d_ref_geo = (mejor_linea or mejor), dgl
            else:
                # la línea declarada no existe en la red ADIF (metropolitana,
                # LV sin PK teóricos…): sin señal, usar distancia global con
                # umbral estricto y marcarlo para el revisor
                entrada["linea_no_en_red"] = True
                p_ref, d_ref_geo = mejor, dg
        else:
            p_ref, d_ref_geo = mejor, dg

        # Punto por POBLACIÓN (regla de David: "si aparece la población ponlo ahí").
        # No cae sobre un raíl por diseño: es el centro urbano declarado, usado cuando
        # la línea no tiene geometría en ADIF (p.ej. 510 Aljucén-Cáceres) o la estación
        # no está mapeada. NO es un error de ubicación.
        if (entrada.get("metodo") or "").startswith("poblacion"):
            entrada["veredicto"] = "bien"
            entrada["motivo"] = ("ubicación por población declarada en el informe "
                                 "(no cae sobre vía por diseño; sin geometría de línea en ADIF)")
            eq = coinciden_provincia(r.get("provincia"), r.get("provincia"))
            entrada["provincia_ok"] = True
            conteo["provincia_ok"] += 1
            conteo["bien"] += 1
            revision.append(entrada)
            continue

        if d_ref_geo <= OK_VIA:
            entrada["veredicto"] = "bien"
            conteo["bien"] += 1
        else:
            # motivo legible para el informe de verificación: por qué NO cuadra
            linea_cercana = (t_g["ct"][2:5] if t_g and re.fullmatch(r"\d{9}", t_g["ct"]) else "?")
            # MISMA-LÍNEA + nodo de estación: el punto no cae sobre "otra vía" —
            # es la vía declarada, y la geometría de tramos solo tiene el EJE en
            # línea, no el manojo de la estación. Manresa 70/2022: 604 m del eje
            # de su propia línea 220 = bien ubicado, falso positivo del umbral.
            misma_linea = bool(t_g and linea_cands and (t_g.get("lineas") or set()) & linea_cands)
            es_est = str(entrada.get("metodo") or "").startswith("estacion")
            # estación SOBRE la red real: la línea declarada puede ser un ramal interno
            # o truncado en ADIF (Salou pk263 línea 600 truncada; Zaragoza-Delicias ramal
            # 060 sin geometría). Si el punto por estación está a ≤ESTACION_RADIO de la vía
            # real, el cruce declarado es una etiqueta de línea, NO un error de ubicación.
            est_en_red = es_est and dg is not None and dg <= ESTACION_RADIO
            if (misma_linea and es_est and d_ref_geo <= ESTACION_RADIO) or est_en_red:
                entrada["veredicto"] = "bien"
                if misma_linea:
                    entrada["motivo"] = (f"nodo de estación: a {round(d_ref_geo)} m del eje de la "
                                         f"línea declarada {linea_inf} (recinto, no error de ubicación)")
                else:
                    entrada["motivo"] = (f"nodo de estación sobre la red real: a {round(dg)} m de la "
                                         f"vía más cercana (la declarada {linea_inf} es ramal interno/"
                                         f"truncado en ADIF — p.ej. Salou, Zaragoza-Delicias)")
                conteo["bien"] += 1
                revision.append(entrada)
                eq = coinciden_provincia(r.get("provincia"), p_ref["provincia"])
                if eq is True:
                    entrada["provincia_ok"] = True
                    conteo["provincia_ok"] += 1
                elif eq is False:
                    entrada["provincia_ok"] = False
                    conteo["provincia_mal"] += 1
                else:
                    entrada["provincia_ok"] = None
                continue
            if entrada.get("linea_no_en_red"):
                motivo = (f"línea declarada {linea_inf} no existe en red ADIF; "
                          f"coordenada a {round(dg)} m de la vía más cercana")
            elif li_num is not None and linea_subset:
                motivo = (f"cae sobre OTRA vía: a {round(dg)} m del tramo "
                          f"{t_g['ct'] if t_g else '?'} (línea {linea_cercana}), "
                          f"la declarada {linea_inf} está a {round(dgl)} m")
            else:
                motivo = f"coordenada a {round(dg)} m de la vía ADIF más cercana"
            entrada["motivo"] = motivo
            if d_ref_geo <= DUDA_VIA:
                entrada["veredicto"] = "duda"
                conteo["duda"] += 1
            else:
                entrada["veredicto"] = "mal"
                conteo["mal"] += 1

        eq = coinciden_provincia(r.get("provincia"), p_ref["provincia"])
        if eq is True:
            entrada["provincia_ok"] = True
            conteo["provincia_ok"] += 1
        elif eq is False:
            entrada["provincia_ok"] = False
            conteo["provincia_mal"] += 1
        else:
            entrada["provincia_ok"] = None
            conteo["provincia_nd"] += 1
        revision.append(entrada)

    # Informes con provincia declarada pero SIN coords: no comprobables aquí,
    # se listan para el revisor IA.
    os.makedirs(os.path.join(RAIZ, "data", "revision"), exist_ok=True)
    ruta_sal = os.path.join(RAIZ, "data", "revision", f"{CODIGO}-localizacion.json")
    with open(ruta_sal, "w", encoding="utf-8") as f:
        json.dump(revision, f, ensure_ascii=False, indent=1)

    print(f"[REV] Veredictos: bien={conteo['bien']} duda={conteo['duda']} "
          f"mal={conteo['mal']} sin_coords={conteo['sin_coords']}")
    print(f"[REV] Provincia: ok={conteo['provincia_ok']} mal={conteo['provincia_mal']} "
          f"no_comparable={conteo['provincia_nd']}")
    print(f"[REV] Detalle -> {ruta_sal}")

    # Top 15 mal ubicados para acción inmediata
    peores = [e for e in revision if e.get("veredicto") == "mal"]
    peores.sort(key=lambda e: -e.get("dist_via_m", 0))
    if peores:
        print("\n[REV] PEORES 15:")
        for e in peores[:15]:
            print(f"  {e['dist_via_m']:>7} m | {e['provincia'] or '—':<16} | "
                  f"pk={e.get('pk') or '—':<14} | {e['titulo'][:60]}")


if __name__ == "__main__":
    main()
