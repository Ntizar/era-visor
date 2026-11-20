# -*- coding: utf-8 -*-
"""obreros.py — 4 obreros en paralelo, uno por país, saltando al siguiente al acabar.

Reparte los países con trabajo pendiente entre N procesos. Cada obrero "reclama" un país
creando `data/cola/<CC>.claim` (creación atómica con O_EXCL): si otro ya lo tiene, prueba
el siguiente. Al terminar el país, lo marca como hecho y salta al siguiente de la cola.

El trabajo de cada país lo hace `maraton.py --pais <CC>` (convertir → traducir → reparar →
revisar el 10 %). Así el obrero sólo reparte; la lógica de calidad no se duplica.

Uso:
    python scripts/obreros.py                 # 4 obreros, todos los países con pendiente
    python scripts/obreros.py 3               # 3 obreros
    python scripts/obreros.py 4 LU LU2 ...    # sólo esos países (para pruebas)

Reanudable: si se corta, se relanza y los países ya cerrados se saltan.
"""
import datetime
import json
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLA = os.path.join(RAIZ, "data", "cola")
LOG = os.path.join(RAIZ, "data", "obreros.log")
PY = sys.executable
MAN = os.path.join(RAIZ, "data", "pdf-manifest")


def log(msg):
    linea = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(linea, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linea + chr(10))


def reclama(obrero, code):
    """Intenta quedarse con el país. True si lo consigue (creación atómica del claim)."""
    ruta = os.path.join(COLA, f"{code}.claim")
    try:
        fd = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w") as f:
        f.write(f"{obrero} {datetime.datetime.now().isoformat()}")
    return True


def libera(code, motivo="hecho"):
    ruta = os.path.join(COLA, f"{code}.claim")
    try:
        os.remove(ruta)
    except FileNotFoundError:
        pass
    with open(os.path.join(COLA, f"{code}.{motivo}"), "w", encoding="utf-8") as f:
        f.write(datetime.datetime.now().isoformat())


def hay_trabajo(code):
    """¿Queda algo por hacer en este país? (lee el estado real, no la marca del obrero)"""
    sys.path.insert(0, os.path.join(RAIZ, "scripts"))
    try:
        import maraton
        a, b, c = maraton.pendientes(code)
        return (b + c) > 0
    except Exception:
        return False


def orden():
    sys.path.insert(0, os.path.join(RAIZ, "scripts"))
    import maraton
    queda = {}
    for f in os.listdir(MAN):
        if not f.endswith(".json"):
            continue
        code = f[:-5]
        if code == "ES":                    # España ya está cerrada
            continue
        try:
            queda[code] = maraton.pendientes(code)[1]     # traducciones pendientes
        except Exception:
            queda[code] = 0
    # el más gordo primero: así los 4 obreros atacan los países que mandan en el total
    return sorted(queda, key=lambda c: -queda[c])


def obrero(n, paises, nombre):
    # cada país se procesa UNA vez por ronda: si queda un PDF que no se deja convertir,
    # el país no debe volver a la cola en bucle (se hace cargo otro paso posterior).
    restantes = list(paises)
    while restantes:
        elegido = None
        for code in list(restantes):
            if reclama(nombre, code):
                if hay_trabajo(code):
                    elegido = code
                    break
                restantes.remove(code)
                libera(code, "sin_pendientes")
        if not elegido:
            log(f"{nombre}: no queda nada que reclamar. Fin.")
            return
        log(f"{nombre}: se queda con {elegido}")
        t0 = time.time()
        salida = subprocess.run([PY, os.path.join(RAIZ, "scripts", "maraton.py"), "--pais", elegido, "--max-pasadas", "2"],
                                cwd=RAIZ, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        dur = int((time.time() - t0) / 60)
        cola = [l for l in (salida.stdout or "").splitlines() if "CERRADO" in l or "queda algo" in l]
        log(f"{nombre}: {elegido} terminado en {dur} min (rc {salida.returncode}) {' | '.join(cola)}")
        restantes.remove(elegido)
        libera(elegido, "hecho")


def main():
    os.makedirs(COLA, exist_ok=True)
    args = sys.argv[1:]
    n = 4
    if args and args[0].isdigit():
        n = int(args.pop(0))
    paises = [a.upper() for a in args] if args else orden()
    log(f"INICIO {n} obreros · países {len(paises)}: {', '.join(paises)}")
    procesos = []
    for i in range(n):
        # multiprocessing en Windows: se usan procesos hijos vía subprocess del propio script
        p = subprocess.Popen([PY, os.path.abspath(__file__), "obrero", str(i + 1)] + paises,
                             cwd=RAIZ)
        procesos.append(p)
    for p in procesos:
        p.wait()
    log("FIN de todos los obreros")


if __name__ == "__main__":
    # modo interno: un solo obrero
    if len(sys.argv) > 1 and sys.argv[1] == "obrero":
        num = sys.argv[2]
        paises = sys.argv[3:]
        obrero(num, paises, f"obrero{num}")
    else:
        main()
