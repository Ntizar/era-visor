#!/usr/bin/env python3
"""
09_dedupe.py — Fase 2B: un expediente = una fila (regla del cierre del proyecto).

David (2026-09-28): «he encontrado en el excel de la ciaf varios duplicados.
Quédate siempre con el que tenga más páginas e información.»

Qué hace:
  1. Agrupa los JSON de database/data/crudo/ por expediente literal.
  2. Los 21 expedientes con DOS documentos (IF+RS de 2 pág, Final vs Interim,
     español vs versión eRAIL en inglés) resuelven su GANADOR por
     (paginas, campos_con_valor): gana el de más páginas; empate → el de
     más campos; empate total → el primero alfabético (quedaría en el log).
  3. El ganador SE QUEDA en crudo/; el perdedor se MUEVE a
     database/data/duplicados_excel/ (nunca se borra: es evidencia).
  4. Escribe database/data/dedupe_map.json: qué documento ganó y cuál fue
     descartado, con sus métricas. 03_exportar_excel.py lo lee para rellenar
     `n_documentos`/`tipo_documento2`/`descartado_pdf` sin fusionar nada.
  5. Escribe data/revision/dedupe-excel.md con las 21 decisiones una a una.

El pipeline queda: 02_extraer_crudo → 09_dedupe → 03_exportar_excel.
(Un `02 --refrescar` COMPLETO re-hace los 372: volver a pasar el 09 después.)

Uso:
    py 09_dedupe.py --listar     # sólo muestra las decisiones, no mueve nada
    py 09_dedupe.py              # aplica (mueve perdedores + escribe mapas)
    py 09_dedupe.py --deshacer   # restaura los perdedores a crudo/ (rollback)
"""

import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATA = RAIZ / "database" / "data"
CRUDO = DATA / "crudo"
DUPLES = DATA / "duplicados_excel"
MAPA = DATA / "dedupe_map.json"
LOG = RAIZ / "data" / "revision" / "dedupe-excel.md"

LISTAR = "--listar" in sys.argv
DESHACER = "--deshacer" in sys.argv

RX_EXP = re.compile(r"^\s*(\d{1,4})\s*/\s*(\d{2,4})\s*$")


def campos_con_valor(d):
    n = 0
    for c in (d.get("campos") or {}).values():
        if c.get("valor_fuente") not in (None, "", [], {}):
            n += 1
    return n


def paginas(d):
    v = d.get("paginas_md")
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def tipo_doc(d):
    """Etiqueta legible del documento (IF / RS / interim / EN...)."""
    pdf = (d.get("pdf") or "").upper()
    if "RS-" in pdf or "RESUMEN" in pdf:
        return "RS"
    if "INTERIM" in pdf or "INTERIM" in (d.get("titulo") or "").upper():
        return "INTERIM"
    return "IF"


def main() -> int:
    if not CRUDO.is_dir():
        print("No hay database/data/crudo/ — corre primero 02_extraer_crudo.py")
        return 1

    if DESHACER:
        if not DUPLES.is_dir():
            print("No hay nada que deshacer:", DUPLES)
            return 0
        n = 0
        for f in sorted(DUPLES.glob("*.json")):
            shutil.move(str(f), str(CRUDO / f.name))
            n += 1
        if MAPA.exists():
            MAPA.unlink()
        print(f"--deshacer: {n} documentos devueltos a crudo/. "
              f"Regenera los excels con 03_exportar_excel.py.")
        return 0

    docs = [json.loads(f.read_text(encoding="utf-8"))
            for f in sorted(CRUDO.glob("*.json"))]

    grupos = {}
    for d in docs:
        exp = (d.get("expediente") or "").strip()
        if RX_EXP.match(exp):
            clave = exp
        else:
            clave = "clave:" + (d.get("clave") or d.get("id") or "?")
        grupos.setdefault(clave, []).append(d)

    dobles = {k: v for k, v in grupos.items() if len(v) > 1}
    print(f"== Fase 2B (dedupe): {len(docs)} documentos, {len(grupos)} expedientes, "
          f"{len(dobles)} con más de un documento ==")
    for k in dobles:
        if not RX_EXP.match(k):
            print(f"  AVISO: {k} agrupado por clave, no por expediente")

    decisiones = []
    for exp in sorted(dobles):
        rs = dobles[exp]
        # más páginas gana; empate → más campos; empate total → alfabético
        rs2 = sorted(rs, key=lambda d: (-paginas(d), -campos_con_valor(d),
                                        d.get("pdf") or ""))
        gana, pierde = rs2[0], rs2[1]
        p_g, p_p = paginas(gana), paginas(pierde)
        c_g, c_p = campos_con_valor(gana), campos_con_valor(pierde)
        empate = (p_g == p_p and c_g == c_p)
        print(f"  {exp}: [{tipo_doc(gana)} {p_g:.0f}p {c_g} campos] vs "
              f"[{tipo_doc(pierde)} {p_p:.0f}p {c_p} campos] → se queda "
              f"{Path(gana.get('pdf') or '').name[:60]}")
        decisiones.append({
            "expediente": exp,
            "ganador": {"stem": Path(gana.get("md") or "").stem,
                        "pdf": gana.get("pdf"), "tipo": tipo_doc(gana),
                        "paginas": p_g, "campos": c_g},
            "descartado": {"stem": Path(pierde.get("md") or "").stem,
                           "pdf": pierde.get("pdf"), "tipo": tipo_doc(pierde),
                           "paginas": p_p, "campos": c_p},
            "motivo": ("empate total (mismo tamaño y mismos campos): se conserva "
                       "el primero alfabético" if empate else
                       "más páginas e información: %gp/%g campos contra %gp/%g"
                       % (p_g, c_g, p_p, c_p)),
        })

    if LISTAR:
        print("\n(--listar: no se ha movido nada)")
        return 0

    if not decisiones:
        print("Nada que deduplicar.")
        if MAPA.exists():
            MAPA.unlink()
        return 0

    # mover perdedores (json crudo + md de md_base: el mismo documento en
    # ambas colecciones; nunca se borran, se archivan como evidencia)
    DUPLES.mkdir(parents=True, exist_ok=True)
    movidos = 0
    for dec in decisiones:
        stem = dec["descartado"]["stem"]
        origen = CRUDO / (stem + ".json")
        if origen.exists():
            shutil.move(str(origen), str(DUPLES / origen.name))
            movidos += 1
        md = RAIZ / "md" / "ES" / (stem + ".md")
        if md.exists():
            shutil.move(str(md), str(DUPLES / md.name))

    # mapa para el exportador
    mapa = {dec["expediente"]: dec for dec in decisiones}
    MAPA.write_text(json.dumps(mapa, ensure_ascii=False, indent=1),
                    encoding="utf-8")

    # log legible
    LOG.parent.mkdir(parents=True, exist_ok=True)
    filas = ["| Expediente | Se queda | Descartado | Motivo |",
             "|---|---|---|---|"]
    for dec in decisiones:
        g, p = dec["ganador"], dec["descartado"]
        filas.append(
            "| %s | %s (%s, %gp, %d campos) | %s (%s, %gp, %d campos) | %s |"
            % (dec["expediente"],
               Path(g["pdf"] or "").name[:48], g["tipo"], g["paginas"], g["campos"],
               Path(p["pdf"] or "").name[:48], p["tipo"], p["paginas"], p["campos"],
               dec["motivo"]))
    LOG.write_text(
        "# Dedupe del Excel — un expediente, una fila\n\n"
        "Regla de David (2026-09-28): «quédate siempre con el que tenga más "
        "páginas e información».\n\n"
        "Los 21 expedientes con DOS documentos (IF + resumen de 2 pág, final vs "
        "interim, español vs inglés) resueltos por (paginas, campos). El "
        "documento descartado NO se borra: está en `database/data/duplicados_excel/` "
        "y su ficha dice qué era.\n\n" + "\n".join(filas) + "\n",
        encoding="utf-8")

    print(f"\n  movidos a duplicados_excel/: {movidos}")
    print(f"  mapa: {MAPA.relative_to(RAIZ)} · log: {LOG.relative_to(RAIZ)}")
    print("  siguiente paso: py 03_exportar_excel.py  (y --v2)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
