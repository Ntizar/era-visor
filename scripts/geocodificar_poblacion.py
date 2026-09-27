# -*- coding: utf-8 -*-
"""
Geocodificacion por POBLACION/ESTACION nombrada: para informes que siguen sin
coords pero que NOMBRAN un lugar claro en el titulo o en el campo `estacion`
(Pedralba, Atocha-Cercanías, Novelda, Las Matas...).

Regla de David (2026-09): «en alguno lugar estaran, aunque sea cerca de algo».
Si el informe nombra la localidad, el pin va en ella — nunca se inventa una
coordenada: el punto sale de Nominatim (OSM) y queda citado en `fuente_geo`
con su osm_type/osm_id (trazable, CC BY 4.0).

  metodo_geo = "poblacion"   (marca propia: se puede deshacer por clase entera)

El auditor `revisar_localizacion.py` ya trata `poblacion*` como ubicacion
declarada (no mide distancia a la linea: un centro urbano no cae sobre un rail).

Uso: python scripts/geocodificar_poblacion.py ES
"""
import glob
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# prefijos que no son localidad
PREFIJOS = [
    "en la estacion de", "en estacion de", "en el apeadero de",
    "en la bifurcacion de", "en bifurcacion de", "en el puesto de bloqueo de",
    "en el tunel de", "en el tunel n", "en la via de", "en el km",
    "estacion de", "apeadero de", "bifurcacion de", "puesto de bloqueo de",
]


def sin_acentos(t):
    return "".join(c for c in unicodedata.normalize("NFD", t)
                   if unicodedata.category(c) != "Mn")


# tipos de resultado aceptables (Nominatim): NUNCA consulados, polígonos
# industriales, gasolineras ni cursos de agua — esos fueron los falsos
# positivos de la 1ª pasada (Embajada de Rusia para «Madrid Chamartín»).
TIPOS_OK = {
    "train_station", "station", "stop", "halt", "tram_stop", "junction",
    "gauge_conversion", "signal_box", "village", "town", "city", "municipality",
    "locality", "hamlet", "suburb", "neighbourhood", "city_district",
    "yes", "railway", "platform",
    # municipio/localidad devuelto como `administrative`: ya se valida después
    # con las dos reglas duras (el display CONTIENE el lugar y la provincia casa)
    "administrative",
}
# `administrative`/localidad SÍ sirve si el display contiene el lugar y la
# provincia cuadra (las dos reglas siguientes); lo que nunca vale es un
# resultado que no contenga lo consultado (consulado, gasolinera, río).
TIPOS_NO = {"diplomatic", "industrial", "service_station", "river", "stream",
            "embassy", "province", "state", "country"}
# frases que en el título NO introducen localidad (evitan «túnel nº 15», «km 26»)


def candidatos_lugar(d):
    """Localidades probables de este informe [(texto, es_estacion)], en orden."""
    out = []
    for campo in ("estacion", "lugar"):
        v = d.get(campo) or ((d.get("ubicacion") or {}).get(campo))
        if v and len(str(v)) >= 4:
            out.append((str(v), True))
    tit = sin_acentos(d.get("titulo") or "").lower()

    # «estación de X», «apeadero de X», «bifurcación de X», «puesto de bloqueo de X»
    for m in re.finditer(
            r"(?:estacion de|apeadero de|bifurcacion de|puesto de bloqueo de)\s+"
            r"([a-z][a-záéíóúñ'´ .-]{3,40}?)(?=[,.;:()\-–—]|\s+el |\s+la |\s+en |\s+por |\s+con |\s+tras |\s*$)",
            tit):
        out.append((m.group(1).strip(), True))
    # «en <Lugar> (Provincia)» / «en <Lugar>, <Provincia>»
    for m in re.finditer(r"\ben\s+([a-z][a-záéíóúñ'´ .-]{3,30}?)\s*\(([a-z áéíóúñ]+)\)", tit):
        out.append((m.group(1).strip(), True))
    # «Lugar (Provincia)» como localidad conocida (Novelda (Alicante))
    for m in re.finditer(r"(?:en|de|sobre)\s+([a-z][a-záéíóúñ'´.-]{3,25})\s*\(([a-z áéíóúñ]+)\)", tit):
        out.append((m.group(1).strip(), False))

    # único, sin duplicados, sin palabras vacías
    vistas, res = set(), []
    for x, es_est in out:
        x = re.sub(r"\s+", " ", x).strip(" ,.;:-–—.")
        k = x.lower()
        if len(x) < 4 or k in vistas:
            continue
        if k in PREFIJOS or len(x.split()) > 5:
            continue
        if re.match(r"^n[ºo°]?\s*\d", k) or re.search(r"\b\d{1,4}\s*$", k) \
                or " tunel" in k or k.startswith("km "):
            continue
        vistas.add(k)
        res.append((x, es_est))
    return res


def nominatim(lugar, provincia, es_estacion=False):
    q = "%s, %s, España" % (lugar, provincia or "")
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 3, "addressdetails": 1})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:                      # red/tasa: no se inventa nada
        print("    ! nominatim %s: %s" % (lugar, e))
        return []


def main():
    codigo = sys.argv[1] if len(sys.argv) > 1 else "ES"
    jsons = sorted(glob.glob(os.path.join(RAIZ, "json", codigo, "*.json")))
    hechos, abstenidos = 0, 0
    for jf in jsons:
        d = json.load(open(jf, encoding="utf-8"))
        loc = d.get("ubicacion") or {}
        if loc.get("lat") or d.get("lat"):
            continue
        provincia = (d.get("provincia") or loc.get("provincia") or "")
        lados = candidatos_lugar(d)  # [(texto, es_estacion)]
        if not lados:
            abstenidos += 1
            continue
        resuelto = False
        for lugar, es_est in lados[:3]:          # a lo sumo 3 intentos por informe
            for hit in nominatim(lugar, provincia, es_est)[:3]:
                tipo = hit.get("type") or ""
                if tipo in TIPOS_NO or tipo not in TIPOS_OK:
                    print("    · %s -> descartado (%s)" % (lugar[:34], tipo))
                    continue
                # el resultado debe CONTENER el lugar consultado: sin esto,
                # «Madrid Chamartín» cae en «Estación de Avenida América» y
                # «Barcelona Marina» en «Estación de Sitges» (50 km)
                dir_ok = sin_acentos(hit.get("display_name", "")).lower()
                palabras = [w for w in sin_acentos(lugar).lower().split() if len(w) >= 4]
                if not all(w in dir_ok for w in palabras):
                    print("    · %s -> descartado: el resultado no lo contiene" % lugar[:34])
                    continue
                # si el informe declara provincia y el resultado no la nombra,
                # es sospechoso: se descarta (mejor sin coord que en otra CCAA)
                if provincia:
                    dir_ = sin_acentos(hit.get("display_name", "")).lower()
                    pv = sin_acentos(provincia).lower()
                    alias = {"a coruna": ["coruna"], "girona": ["gerona"],
                             "lleida": ["lerida"], "ourense": ["orense"],
                             "asturias": ["oviedo"], "cantabria": ["santander"]}
                    ok_pv = pv in dir_ or any(a in dir_ for a in alias.get(pv, []))
                    if not ok_pv and not re.search(r",\s*%s[ ,]" % re.escape(pv), dir_):
                        print("    · %s -> descartado: no está en %s" % (lugar[:34], provincia))
                        continue
                lat, lng = float(hit["lat"]), float(hit["lon"])
                loc.update({
                    "lat": lat, "lng": lng, "metodo_geo": "poblacion",
                    "poblacion_nombre": hit.get("display_name", "")[:120],
                    "fuente_geo": "Nominatim %s/%s (%s)" % (
                        hit.get("osm_type"), hit.get("osm_id"), tipo),
                })
                d["ubicacion"] = loc
                json.dump(d, open(jf, "w", encoding="utf-8"),
                          ensure_ascii=False, indent=1)
                print("  [%s] %-42s -> %s (%s)" % (
                    codigo, lugar[:42], hit.get("display_name", "")[:70], tipo))
                hechos += 1
                resuelto = True
                break
            if resuelto:
                break
            time.sleep(1.1)                     # cortesía con Nominatim
        if not resuelto:
            abstenidos += 1
        time.sleep(1.1)
    print("[POB] geocodificados por poblacion: %d | sin resolver: %d" % (hechos, abstenidos))


if __name__ == "__main__":
    main()
