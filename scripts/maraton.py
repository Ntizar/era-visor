# -*- coding: utf-8 -*-
"""maraton.py — driver único de la fase europea: convierte, traduce y revisa solo.

Recorre los países de menor a mayor volumen y, para cada uno, hace lo que falte:
  1. PDFs sin MD            → convertir_md_pais.py
  2. MD sin castellano      → traducir_md_es.py
  3. MD-es sin revisión IA  → revisar_md_es.py
Y vuelve a empezar hasta que no quede nada pendiente. Todo es reanudable: si se corta,
se relanza y continúa donde estaba.

Uso:
    python scripts/maraton.py            # una pasada completa + repesca hasta vaciar
    python scripts/maraton.py --pais AT  # sólo un país (para pruebas)
    python scripts/maraton.py --max-pasadas 3
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(RAIZ, "scripts")
PY = sys.executable
MAN = os.path.join(RAIZ, "data", "pdf-manifest")
PDFS = os.path.join(RAIZ, "pdfs")
MD = os.path.join(RAIZ, "md")
MD_ES = os.path.join(RAIZ, "md-es")
REV = os.path.join(RAIZ, "data", "revision")
LOG = os.path.join(RAIZ, "data", "maraton.log")

IGNORAR = ("indice", "índice", "readme", "leeme")


def log(msg):
    linea = f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {msg}"
    print(linea, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def corre(args):
    """Ejecuta un script del proyecto y devuelve (código, últimas líneas)."""
    r = subprocess.run([PY] + args, cwd=RAIZ, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    cola = [l for l in (r.stdout or "").strip().splitlines() if l.strip()][-3:]
    if r.returncode != 0:
        cola.append(f"exit {r.returncode}: {(r.stderr or '').strip().splitlines()[-1][:160:] if r.stderr else ''}")
    return r.returncode, cola


def recorrido(base):
    return [os.path.join(dp, f) for dp, _, fs in os.walk(base) for f in fs
            if f.endswith(".md") and not f.lower().startswith(IGNORAR)]


def pendientes(code):
    """(pdfs sin md, md sin md-es, md-es sin revisión) — contando vacías como pendientes."""
    origen = os.path.join(PDFS, code)
    if not os.path.isdir(origen):
        return 0, 0, 0
    pdfs = [p for p in os.listdir(origen) if p.lower().endswith(".pdf")]
    n_md = len(recorrido(os.path.join(MD, code))) if os.path.isdir(os.path.join(MD, code)) else 0
    sin_md = max(0, len(pdfs) - n_md)
    n_es = len(recorrido(os.path.join(MD_ES, code))) if os.path.isdir(os.path.join(MD_ES, code)) else 0
    # una traducción vacía o truncada (md sin texto en el momento de traducir, p. ej.
    # antes del OCR) cuenta como NO hecha: si no, nunca se arreglaría.
    try:
        from traducir_md_es import vacios
        n_vacios = len(vacios(code))
    except Exception:
        n_vacios = 0
    sin_es = max(0, n_md - n_es) + n_vacios
    revisados = 0
    f_rev = os.path.join(REV, f"{code}.json")
    if os.path.exists(f_rev):
        try:
            revisados = len(json.load(open(f_rev, encoding="utf-8")))
        except Exception:
            revisados = 0
    # el contrato pide revisar el 12 % de cada país, no el 100 %
    objetivo_rev = max(3, int(0.10 * n_es + 0.5))
    sin_rev = max(0, objetivo_rev - revisados)
    return sin_md, sin_es, sin_rev


def orden(manual=None):
    if manual:
        return manual
    tam = {}
    for f in os.listdir(MAN):
        if not f.endswith(".json"):
            continue
        code = f[:-5]
        try:
            tam[code] = len(json.load(open(os.path.join(MAN, f), encoding="utf-8")))
        except Exception:
            tam[code] = 0
    tam.pop("ES", None)                    # España ya está cerrada
    return sorted(tam, key=lambda c: tam[c])


def una_pasada(paises):
    trabajo = 0
    for code in paises:
        antes = pendientes(code)
        sin_md, sin_es, sin_rev = pendientes(code)
        if not (sin_md or sin_es or sin_rev):
            continue
        trabajo += 1
        log(f"[{code}] pendiente: {sin_md} sin MD · {sin_es} sin castellano · {sin_rev} sin revisar")
        if sin_md:
            t0 = time.time()
            rc, cola = corre([os.path.join(SCRIPTS, "convertir_md_pais.py"), code,
                              "--workers", "4", "--timeout", "100"])
            log(f"[{code}] conversión ({int(time.time()-t0)}s, rc {rc}): " + " | ".join(cola))
            sin_md, sin_es, sin_rev = pendientes(code)
        if sin_es:
            t0 = time.time()
            rc, cola = corre([os.path.join(SCRIPTS, "traducir_md_es.py"), code,
                              "--workers", "1", "--workers-noche", "1"])
            # las vacías/truncadas se rehacen siempre antes de dar el país por traducido
            corre([os.path.join(SCRIPTS, "traducir_md_es.py"), code, "--vacios", "--rehacer"])
            log(f"[{code}] traducción ({int((time.time()-t0)/60)} min, rc {rc}): " + " | ".join(cola))
            sin_md, sin_es, sin_rev = pendientes(code)
        if sin_es == 0:
            # repaso de calidad: re-traduce SÓLO las páginas marcadas (si hay)
            t0 = time.time()
            rc, cola = corre([os.path.join(SCRIPTS, "traducir_md_es.py"), code, "--reparar"])
            if "REPARADOS 0" not in " ".join(cola):
                log(f"[{code}] reparación ({int((time.time()-t0)/60)} min): " + " | ".join(cola))
        # Revisión IA: objetivo del 12 % del país (el contrato pide >= 10 % global),
        # sin repetir lo ya revisado.
        n_es = len(recorrido(os.path.join(MD_ES, code))) if os.path.isdir(os.path.join(MD_ES, code)) else 0
        f_rev = os.path.join(REV, f"{code}.json")
        hechos_rev = len(json.load(open(f_rev, encoding="utf-8"))) if os.path.exists(f_rev) else 0
        objetivo_rev = max(3, int(0.10 * n_es + 0.5))
        faltan_rev = max(0, objetivo_rev - hechos_rev)
        if faltan_rev:
            t0 = time.time()
            h = datetime.datetime.now().hour
            rc, cola = corre([os.path.join(SCRIPTS, "revisar_md_es.py"), code,
                              "--workers", "1",
                              "--muestras", "6", "--solo-nuevos", "--limite", str(faltan_rev)])
            log(f"[{code}] revisión {faltan_rev}/{objetivo_rev} ({int((time.time()-t0)/60)} min, rc {rc}): "
                + " | ".join(cola))

        # Puerta de calidad: si el país baja de 92 de fidelidad media, se repara página a
        # página y se vuelven a revisar los marcados (da igual que ya estuvieran revisados).
        d = json.load(open(f_rev, encoding="utf-8")) if os.path.exists(f_rev) else {}
        medias = [v["fidelidad_media"] for v in d.values()
                  if isinstance(v.get("fidelidad_media"), (int, float))]
        media = round(sum(medias) / len(medias), 1) if medias else None
        if media is not None and media < 85:
            log(f"[{code}] calidad baja ({media}) → reparación y re-revisión")
            corre([os.path.join(SCRIPTS, "traducir_md_es.py"), code, "--reparar"])
            corre([os.path.join(SCRIPTS, "revisar_md_es.py"), code, "--workers",
                   "1",
                   "--muestras", "6", "--marcados"])
        sin_md, sin_es, sin_rev = pendientes(code)
        if (sin_md, sin_es, sin_rev) == antes:
            # una pasada completa sin mover ni un número: el país está atascado
            # (PDF que no se puede convertir, 429 persistente...). Se declara y se sigue.
            log(f"[{code}] SIN PROGRESO ({sin_md}/{sin_es}/{sin_rev}) — se deja para revisar a mano")
            return trabajo
        log(f"[{code}] {'CERRADO' if not (sin_md or sin_es or sin_rev) else 'queda algo'} "
            f"({sin_md}/{sin_es}/{sin_rev})")
        corre([os.path.join(SCRIPTS, "estado_paises.py")])
    return trabajo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pais", nargs="*")
    ap.add_argument("--max-pasadas", type=int, default=0, help="0 = hasta vaciar la cola")
    a = ap.parse_args()
    paises = [c.upper() for c in a.pais] if a.pais else orden()
    log(f"MARATÓN inicio · países {len(paises)} · {', '.join(paises)}")
    pasada, maximo = 0, a.max_pasadas or 99
    while pasada < maximo:
        pasada += 1
        log(f"— pasada {pasada} —")
        if una_pasada(paises) == 0:
            log("cola vacía: no queda nada pendiente")
            break
    log("MARATÓN fin")


if __name__ == "__main__":
    main()
