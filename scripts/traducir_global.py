# -*- coding: utf-8 -*-
"""traducir_global.py — cola GLOBAL de ficheros: los 5 huecos de API nunca se enfrían.

El driver por países (`obreros.py`) pierde capacidad: mientras un obrero revisa, repara o
cambia de país, su hueco de traducción está parado. Aquí se acaba eso:

  · Se construye UNA lista con todos los .md sin traducción (de todos los países).
  · N hilos (5, el tope del modelo) van cogiendo el siguiente fichero y traduciéndolo.
  · No hay fases intermedias: en cuanto un hilo termina, coge otro.

La revisión IA y la reparación quedan para después (usan otro modelo: deepseek), así que
no compiten por los huecos de traducción.

Uso:
    python scripts/traducir_global.py                 # 5 hilos, todo lo pendiente
    python scripts/traducir_global.py --hilos 5 --modelo mimo-v2.6-flash
    python scripts/traducir_global.py --paises CZ HU  # sólo esos países
    python scripts/traducir_global.py --limite 20     # prueba
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import traducir_md_es as t  # noqa: E402

RAIZ = t.RAIZ
MD, MD_ES = t.MD, t.MD_ES
IGN = ("indice", "índice", "leeme", "readme")


def pendientes(paises=None):
    """[(pais, ruta_md)] de todos los ficheros sin traducción válida."""
    out = []
    for code in sorted(os.listdir(MD)):
        base = os.path.join(MD, code)
        if not os.path.isdir(base) or (paises and code not in paises):
            continue
        for dp, _, fs in os.walk(base):
            for f in sorted(fs):
                if not f.endswith(".md") or f.lower().startswith(IGN):
                    continue
                ruta = os.path.join(dp, f)
                try:
                    # hay frontmatter de más de 400 caracteres: se lee de sobra
                    cab = open(ruta, encoding="utf-8").read(4000)
                    chars_md = int(t.partir_frontmatter(cab)[0].get("chars", 0))
                except Exception:
                    chars_md = os.path.getsize(ruta) // 2
                if chars_md < 400:
                    continue                      # sin texto (escaneado sin OCR)
                rel = os.path.relpath(ruta, RAIZ).replace("\\", "/")
                partes = rel.split("/")
                destino = os.path.join(MD_ES, codigo_pais(code), partes[-2], partes[-1])
                if os.path.exists(destino):
                    txt = open(destino, encoding="utf-8", errors="replace").read()
                    if len(txt) >= 0.3 * chars_md:
                        continue                  # ya traducido y con cuerpo suficiente
                out.append((code, ruta))
    return out


def codigo_pais(c):
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hilos", type=int, default=5)
    ap.add_argument("--modelo", default=t.MODELO_DEF)
    ap.add_argument("--paises", nargs="*")
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()

    paises = [p.upper() for p in a.paises] if a.paises else None
    cola = pendientes(paises)
    if a.limite:
        cola = cola[:a.limite]
    if not cola:
        print("nada pendiente")
        return
    base, key = t.cargar_api()
    print(f"COLA GLOBAL: {len(cola)} ficheros · {a.hilos} hilos · modelo {a.modelo}", flush=True)

    indice = {"i": 0}
    cerrojo = __import__("threading").Lock()
    hechos = {"ok": 0, "revisar": 0, "error": 0, "ya": 0}
    t0 = time.time()

    def siguiente():
        with cerrojo:
            if indice["i"] >= len(cola):
                return None
            item = cola[indice["i"]]
            indice["i"] += 1
            return item

    def hilo():
        while True:
            item = siguiente()
            if item is None:
                return
            code, ruta = item
            try:
                r = t.procesar(ruta, code, a.modelo, base, key, False)
                est = r.get("estado", "ok")
            except Exception as e:
                est = "error"
                print(f"  ✗ {os.path.basename(ruta)}: {str(e)[:120]}", flush=True)
            with cerrojo:
                hechos[est] = hechos.get(est, 0) + 1
                n = sum(hechos.values())
                if n % 20 == 0:
                    mins = (time.time() - t0) / 60
                    print(f"  [{n}/{len(cola)}] ok={hechos['ok']} revisar={hechos['revisar']} "
                          f"error={hechos['error']} · {n/mins*60:.0f}/hora", flush=True)

    import threading
    hs = [threading.Thread(target=hilo, daemon=True) for _ in range(a.hilos)]
    for h in hs:
        h.start()
    for h in hs:
        h.join()
    mins = (time.time() - t0) / 60
    print(f"FIN: {sum(hechos.values())} ficheros en {mins:.0f} min "
          f"({sum(hechos.values())/max(mins,1)*60:.0f}/hora) · {json.dumps(hechos)}")


if __name__ == "__main__":
    main()
