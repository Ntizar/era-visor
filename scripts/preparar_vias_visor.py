# -*- coding: utf-8 -*-
"""
Prepara la capa de vías del visor: data/adif-tramos.geojson (trazado oficial
de Adif, 604.913 vértices) -> data/vias-adif.geojson (simplificado con
Douglas-Peucker para poder servirlo al navegador).

Por qué existe: el WMS de Adif (ideadif.adif.es) responde 403 y la malla de
PKs (adif-pkteoricos.geojson) solo tiene un punto cada ~944 m, así que las
vías se veían rectas y con mucho menos detalle que el WMS que había antes.

Uso:
    python scripts/preparar_vias_visor.py [--tolerancia-metros 10]

Salida (se publica en Pages):
    data/vias-adif.geojson   ≈ 1,2 MB a 10 m (40.157 vértices, 2,5× los PKs)
"""
import argparse
import io
import json
import math
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, "data", "adif-tramos.geojson")
SALIDA = os.path.join(RAIZ, "data", "vias-adif.geojson")
PROPS = ("cod_linea", "tipo_red", "provincia", "estado")


def douglas_peucker(puntos, eps):
    """Simplifica una línea [[lng,lat],...] conservando la forma hasta eps (grados)."""
    if len(puntos) < 3:
        return puntos[:]
    mantener = [False] * len(puntos)
    mantener[0] = mantener[-1] = True
    pila = [(0, len(puntos) - 1)]
    while pila:
        a, b = pila.pop()
        if b <= a + 1:
            continue
        ax, ay = puntos[a]
        bx, by = puntos[b]
        dx, dy = bx - ax, by - ay
        largo = math.hypot(dx, dy)
        mejor, i_mejor = -1.0, -1
        for i in range(a + 1, b):
            px, py = puntos[i]
            if largo == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / largo
            if d > mejor:
                mejor, i_mejor = d, i
        if mejor > eps and i_mejor > 0:
            mantener[i_mejor] = True
            pila.append((a, i_mejor))
            pila.append((i_mejor, b))
    return [p for p, k in zip(puntos, mantener) if k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tolerancia-metros", type=float, default=10.0)
    args = ap.parse_args()
    eps = args.tolerancia_metros / 111000.0  # grados ~ metros

    datos = json.load(open(ENTRADA, encoding="utf-8"))
    salida, v_orig, v_nuevo = [], 0, 0
    for f in datos["features"]:
        geom = f["geometry"]
        brutas = (geom["coordinates"] if geom["type"] == "MultiLineString"
                  else [geom["coordinates"]])
        lineas = []
        for linea in brutas:
            v_orig += len(linea)
            simple = douglas_peucker([[p[0], p[1]] for p in linea], eps)
            if len(simple) >= 2:
                v_nuevo += len(simple)
                lineas.append(simple)
        if not lineas:
            continue
        salida.append({
            "type": "Feature",
            "properties": {k: f["properties"][k] for k in PROPS
                           if f["properties"].get(k) not in (None, "")},
            "geometry": {"type": "MultiLineString" if len(lineas) > 1 else "LineString",
                         "coordinates": lineas if len(lineas) > 1 else lineas[0]},
        })

    coleccion = {"type": "FeatureCollection", "features": salida}
    texto = json.dumps(coleccion, ensure_ascii=False, separators=(",", ":"))
    with open(SALIDA, "w", encoding="utf-8") as fh:
        fh.write(texto)
    print("[VIAS] %.1f MB, %d/%d vértices (%.0f%%), %d líneas, tolerancia %.0f m"
          % (len(texto) / 1e6, v_nuevo, v_orig, 100.0 * v_nuevo / v_orig,
             len(salida), args.tolerancia_metros))


if __name__ == "__main__":
    main()
