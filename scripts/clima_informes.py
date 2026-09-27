#!/usr/bin/env python3
"""Clima histórico del día (y la hora) del suceso por informe.

Fuente: Open-Meteo Archive API (reanálisis ERA5, sin API key, CORS '*').
  https://open-meteo.com/en/docs/historical-weather-api

Por cada informe con fecha y coordenadas guarda, en `data/db/clima.json`:
  "<id>": { "dia": {tmax, tmin, lluvia_mm, horas_lluvia, viento_kmh,
                    rafagas_kmh, wmo},
             "hora": {t, lluvia_mm, viento_kmh, rafagas_kmh, wmo} | null }
La hora es la del propio suceso (312/351 informes la publican); sin hora
se queda en null y la ficha muestra solo el día. Los 3 informes sin
coordenadas no llevan clima (nunca se inventa).

Uso:  python scripts/clima_informes.py            # solo huecos (reanudable)
      python scripts/clima_informes.py --refrescar  # todo de nuevo
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "data", "db", "index.json")
DST = os.path.join(BASE, "data", "db", "clima.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) era-visor/1.0"
DAILY = ("temperature_2m_max,temperature_2m_min,precipitation_sum,"
         "precipitation_hours,wind_speed_10m_max,wind_gusts_10m_max,weather_code")
HOURLY = ("temperature_2m,precipitation,wind_speed_10m,wind_gusts_10m,weather_code")


def hora_minutos(h):
    """'14:24' -> 864 | '07:00' -> 420 | cualquier formato raro -> None"""
    if not h or ":" not in str(h):
        return None
    try:
        hh, mm = str(h).split(":")[0:2]
        m = int(hh) * 60 + int(mm)
        return m if 0 <= m < 1440 else None
    except ValueError:
        return None


def pedir(lat, lng, fecha, intentos=4):
    q = urllib.parse.urlencode({
        "latitude": round(lat, 4), "longitude": round(lng, 4),
        "start_date": fecha, "end_date": fecha,
        "daily": DAILY, "hourly": HOURLY,
        "timezone": "auto",
    })
    url = "https://archive-api.open-meteo.com/v1/archive?" + q
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 — reintento con espera
            if i == intentos - 1:
                print(f"  ! sin respuesta {fecha}: {e}")
                return None
            time.sleep(1.5 * (i + 1))
    return None


def procesar(reg):
    """Descarta y compacta un informe -> (clave, dict) | (None, None)."""
    if not reg.get("fecha") or reg.get("lng") is None or reg.get("lat") is None:
        return None, None
    d = pedir(reg["lat"], reg["lng"], reg["fecha"])
    if not d or "daily" not in d:
        return reg["id"], {"error": "sin_datos"}
    dia = d["daily"]

    def uno(campo, i=0):
        v = dia.get(f"{campo}") or [None]
        return v[i] if v else None

    def fl(x, nd=1):
        return None if x is None else round(float(x), nd)

    out = {
        "fuente": "ERA5 · Open-Meteo Archive",
        "dia": {
            "tmax": fl(uno("temperature_2m_max")),
            "tmin": fl(uno("temperature_2m_min")),
            "lluvia_mm": fl(uno("precipitation_sum")),
            "horas_lluvia": fl(uno("precipitation_hours"), 0),
            "viento_kmh": fl(uno("wind_speed_10m_max")),
            "rafagas_kmh": fl(uno("wind_gusts_10m_max")),
            "wmo": uno("weather_code"),
        },
        "hora": None,
    }
    m = hora_minutos(reg.get("hora"))
    h = d.get("hourly") or {}
    if m is not None and h.get("temperature_2m"):
        i = m // 60
        if i < len(h["temperature_2m"]):
            out["hora"] = {
                "t": fl(h["temperature_2m"][i]),
                "lluvia_mm": fl(h["precipitation"][i], 2),
                "viento_kmh": fl(h["wind_speed_10m"][i]),
                "rafagas_kmh": fl(h["wind_gusts_10m"][i]),
                "wmo": h.get("weather_code", [None])[i],
            }
    return reg["id"], out


def main():
    refrescar = "--refrescar" in sys.argv
    regs = json.load(open(SRC, encoding="utf-8"))
    if isinstance(regs, dict):
        regs = regs.get("registros") or regs.get("items")
    previo = {}
    if not refrescar and os.path.exists(DST):
        try:
            previo = json.load(open(DST, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            previo = {}
    pendientes = [r for r in regs
                  if r.get("fecha") and r.get("lng") is not None
                  and r["id"] not in previo]
    print(f"informes {len(regs)} · ya con clima {len(previo)} · a consultar {len(pendientes)}")
    if not pendientes:
        print("nada que hacer")
    else:
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=4) as ex:
            for n, (clave, val) in enumerate(ex.map(procesar, pendientes), 1):
                if clave:
                    previo[clave] = val
                if n % 50 == 0 or n == len(pendientes):
                    print(f"  {n}/{len(pendientes)} · {time.time()-t0:.0f}s")
        os.makedirs(os.path.dirname(DST), exist_ok=True)
        tmp = DST + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(previo, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, DST)
    ok = sum(1 for v in previo.values() if "error" not in v)
    con_hora = sum(1 for v in previo.values() if v.get("hora"))
    print(f"clima.json: {len(previo)} informes · {ok} con datos · {con_hora} con hora exacta"
          f" · {os.path.getsize(DST)/1024:.0f} KB")


if __name__ == "__main__":
    main()
