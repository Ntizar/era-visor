#!/usr/bin/env python3
"""
_recuperar_faltantes.py — repone en database/data/mejorado/ los campos que un
grupo del API devolvió vacío (content '') y se perdieron al reescribir el
informe completo.

A diferencia de 05_llm_lotes.py, SOLO AÑADE campos ausentes: nunca pisa un
campo ya verificado. Reutiliza el candado de 05_llm_lotes (verifica_cita).

Uso:
  py _recuperar_faltantes.py                     # barre los 372 y repara
  py _recuperar_faltantes.py IF-290808-181208-CIAF
  py _recuperar_faltantes.py --solo-informe      # informa, no escribe
"""
import importlib.util
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RUTA_MOD = RAIZ / "database" / "scripts" / "05_llm_lotes.py"
_spec = importlib.util.spec_from_file_location("lotes", RUTA_MOD)
lotes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lotes)

RONDAS = 6          # tandas de reintentos por campo que siga sin salir
SOLO_INFORME = "--solo-informe" in sys.argv
HILOS = 1
for _a in sys.argv[1:]:
    if _a.startswith("--hilos="):
        HILOS = max(1, int(_a.split("=", 1)[1]))


def refs_llm():
    guia = json.loads((lotes.DATA / "guia_campos.json").read_text(encoding="utf-8"))
    return [str(g["ref"]).strip() for g in guia
            if str(g.get("ref", "")).strip()[:1].isdigit()
            and (g.get("campo") or "").strip()
            and str(g.get("cumplimentar", "")).strip().lower() not in ("sí", "si")]


def procesar(stem, refs, base, key, modelo):
    ruta = lotes.MEJORADO / (stem + ".json")
    if not ruta.exists():
        print("  sin mejorado: %s" % stem)
        return 0, 0
    doc = json.loads(ruta.read_text(encoding="utf-8"))
    campos = doc.setdefault("campos", {})
    antes = len(campos)
    faltan = [r for r in refs if r not in campos]
    if not faltan:
        return 0, 0
    inf = lotes.prep_infome(stem)
    if not inf:
        print("  sin md_base: %s" % stem)
        return 0, 0
    print("%s: faltan %d" % (stem[:56], len(faltan)), flush=True)

    rondas = 0
    while faltan and rondas < RONDAS:
        rondas += 1
        grupos = [faltan[i:i + lotes.GRUPO_CAMPOS]
                  for i in range(0, len(faltan), lotes.GRUPO_CAMPOS)]
        siguen = []
        for grupo in grupos:
            peticion = ("CAMPOS A REVISAR (ref - nombre):\n"
                        + "\n".join("- %s" % r for r in grupo))
            respuesta = None
            for ve in inf["ventanas"]:          # la ventana que los contenga
                respuesta = lotes.llamar(base, key, modelo, lotes.SYSTEMA,
                                         peticion + "\n\nINFORME:\n\n"
                                         + lotes.texto_pagina_head(ve))
                if respuesta:
                    break
            if not respuesta:
                siguen += grupo
                print("    ronda %d: respuesta vacía para %d campos"
                      % (rondas, len(grupo)), flush=True)
                continue
            vistos = set()
            for item in (respuesta.get("resultados") or []):
                ref = str(item.get("ref") or "")
                if ref not in grupo:
                    continue
                vistos.add(ref)
                if item.get("valor") in (None, "", [], {}):
                    campos[ref] = {"valor": None, "cita": None, "pagina": None,
                                   "verificado": True,
                                   "verificacion": "null honesto: no consta en el informe"}
                    continue
                ok, motivo = lotes.verifica_cita(inf["paginas"],
                                                 item.get("cita"),
                                                 item.get("pagina"))
                if ok:
                    campos[ref] = {"valor": item.get("valor"),
                                   "cita": item.get("cita"),
                                   "pagina": item.get("pagina"),
                                   "verificado": True,
                                   "verificacion": "cita literal en página"}
                else:
                    # no se guarda: el candado sólo rechaza, se reintenta
                    print("    ronda %d: %s rechazada (%s)" % (rondas, ref, motivo),
                          flush=True)
            siguen += [r for r in grupo if r not in vistos or r not in campos
                       or campos[r].get("verificado") is not True]
        faltan = [r for r in refs if r not in campos
                  or campos[r].get("verificado") is not True]
        # los rechazados no se conservan como campo: se vuelve a intentar
        for r in siguen:
            if r in campos and campos[r].get("verificado") is not True:
                del campos[r]
        print("    ronda %d → quedan %d" % (rondas, len(faltan)), flush=True)

    cita = sum(1 for v in campos.values() if v.get("verificado") and v.get("cita"))
    nul = sum(1 for v in campos.values() if v.get("verificado") and not v.get("cita"))
    rech = sum(1 for v in campos.values() if v.get("verificado") is not True)
    faltan = [r for r in refs if r not in campos]
    if not SOLO_INFORME:
        doc["campos"] = campos
        ruta.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print("  %s campos=%d (antes %d) cita=%d null=%d rech=%d faltan=%d"
          % ("" if not SOLO_INFORME else "[dry] ", len(campos), antes,
             cita, nul, rech, len(faltan)), flush=True)
    return len(campos), len(faltan)


def main():
    refs = refs_llm()
    stems = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not stems:
        stems = sorted(p.stem for p in lotes.MD_BASE.glob("*.md"))
    base, key, modelo = lotes.api(None)   # mimo-v2.6-flash por defecto
    print("== recuperación de campos (modelo %s, hilos=%d) ==" % (modelo, HILOS))

    def _trabajo(stem):
        """Repara UN informe. Cada stem escribe SU fichero: sin estado
        compartido, así que paralelizar es seguro."""
        ruta = lotes.MEJORADO / (stem + ".json")
        if not ruta.exists():
            return 0, 0
        campos = json.loads(ruta.read_text(encoding="utf-8")).get("campos", {})
        falta = len([r for r in refs if r not in campos
                     or campos[r].get("verificado") is not True])
        if falta:
            procesar(stem, refs, base, key, modelo)
        campos = json.loads(ruta.read_text(encoding="utf-8")).get("campos", {})
        return falta, len([r for r in refs if r not in campos])

    import concurrent.futures as cf
    if HILOS > 1:
        with cf.ThreadPoolExecutor(HILOS) as ex:
            res = list(ex.map(_trabajo, stems))
    else:
        res = [_trabajo(s) for s in stems]
    total_falta_antes = sum(a for a, _ in res)
    total_falta_ahora = sum(b for _, b in res)
    print("\n  faltantes antes: %d | después: %d" % (total_falta_antes,
                                                     total_falta_ahora))
    return 0 if total_falta_ahora == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
