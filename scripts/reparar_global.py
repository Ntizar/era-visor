# -*- coding: utf-8 -*-
"""reparar_global.py — reparación por página en paralelo (5 huecos, una cola de ficheros).

Coge todos los md-es con `verificacion: revisar` de todos los países y los repara con N
hilos, cada uno un fichero: re-traduce SOLO las páginas que fallan y recalcula el veredicto.

Uso:
    python scripts/reparar_global.py                # 5 hilos, todos los marcados
    python scripts/reparar_global.py --paises CZ NO
    python scripts/reparar_global.py --limite 10
    python scripts/reparar_global.py --listar
"""
import argparse
import os
import re
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import traducir_md_es as t  # noqa: E402

IGN = ("indice", "índice", "leeme", "readme")
RE_REVISAR = re.compile(r"(?m)^verificacion:\s*revisar")


def marcados(paises=None):
    out = []
    for dp, _, fs in os.walk(t.MD_ES):
        code = os.path.relpath(dp, t.MD_ES).split(os.sep)[0]
        if paises and code not in paises:
            continue
        for f in sorted(fs):
            if not f.endswith(".md") or f.lower().startswith(IGN):
                continue
            p = os.path.join(dp, f)
            try:
                cab = open(p, encoding="utf-8", errors="replace").read(800)
            except Exception:
                continue
            if RE_REVISAR.search(cab):
                out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hilos", type=int, default=5)
    ap.add_argument("--modelo", default=t.MODELO_DEF)
    ap.add_argument("--paises", nargs="*")
    ap.add_argument("--limite", type=int, default=0)
    ap.add_argument("--listar", action="store_true")
    a = ap.parse_args()

    paises = [p.upper() for p in a.paises] if a.paises else None
    cola = marcados(paises)
    if a.limite:
        cola = cola[:a.limite]
    if a.listar:
        print(f"marcados: {len(cola)}")
        for p in cola[:30]:
            print("  " + os.path.relpath(p, t.RAIZ))
        return
    if not cola:
        print("nada marcado: todo ok")
        return

    base, key = t.cargar_api()
    print(f"REPARACIÓN: {len(cola)} ficheros · {a.hilos} hilos · {a.modelo}", flush=True)
    indice = {"i": 0}
    cerrojo = threading.Lock()
    cuenta = {"ok": 0, "revisar": 0, "sin_origen": 0, "error": 0}
    paginas = {"n": 0}
    t0 = time.time()

    def trabajo():
        while True:
            with cerrojo:
                if indice["i"] >= len(cola):
                    return
                ruta = cola[indice["i"]]
                indice["i"] += 1
            try:
                _, n_pag, estado = t.reparar_uno(ruta, a.modelo, base, key)
            except Exception as e:
                estado, n_pag = "error", 0
                print(f"  ✗ {os.path.basename(ruta)}: {str(e)[:110]}", flush=True)
            with cerrojo:
                cuenta[estado] = cuenta.get(estado, 0) + 1
                paginas["n"] += n_pag
                n = sum(cuenta.values())
                if n % 20 == 0:
                    mins = (time.time() - t0) / 60
                    print(f"  [{n}/{len(cola)}] ok={cuenta['ok']} siguen={cuenta['revisar']} "
                          f"err={cuenta['error']} · {n/max(mins,1)*60:.0f}/hora", flush=True)

    hs = [threading.Thread(target=trabajo, daemon=True) for _ in range(a.hilos)]
    for h in hs:
        h.start()
    for h in hs:
        h.join()
    mins = (time.time() - t0) / 60
    print(f"FIN reparación: {sum(cuenta.values())} ficheros · {paginas['n']} páginas "
          f"re-traducidas · {mins:.0f} min · {cuenta}")


if __name__ == "__main__":
    main()
