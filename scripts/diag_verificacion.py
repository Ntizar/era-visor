# -*- coding: utf-8 -*-
"""diag_verificacion.py — enseña QUÉ falla en un md-es, página a página.

Uso:
    python scripts/diag_verificacion.py md-es/LU/2006/xxx.md [--texto]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import traducir_md_es as t  # noqa: E402

RE_PAG = re.compile(r"(?m)^## Página (\d+)\s*$")


def paginas(cuerpo):
    out = {}
    marcas = list(RE_PAG.finditer(cuerpo))
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(cuerpo)
        out[m.group(1)] = cuerpo[m.end():fin]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md_es")
    ap.add_argument("--texto", action="store_true", help="enseña el inicio de la página original")
    a = ap.parse_args()
    texto = open(a.md_es, encoding="utf-8").read()
    fm, ce = t.partir_frontmatter(texto)
    ruta_or = os.path.join(t.RAIZ, fm.get("md_origen", "").replace("/", os.sep))
    _, co = t.partir_frontmatter(open(ruta_or, encoding="utf-8").read())
    po, pe = paginas(co), paginas(ce)
    print(f"{os.path.basename(a.md_es)} · {len(po)} páginas original · {len(pe)} castellano")
    malas = 0
    for k in sorted(set(po) & set(pe), key=int):
        fallos, blandos = t.verificar(po[k], pe[k])
        if not fallos and not blandos:
            continue
        malas += 1 if fallos else 0
        no, _ = t.numeros(po[k])
        nt, _ = t.numeros(pe[k])
        faltan = sorted((no - nt).elements())
        etiqueta = "FALLO" if fallos else "nota "
        print(f"  {etiqueta} pág {k:>3} · {'; '.join(fallos + blandos)} · faltan {faltan[:12]} · "
              f"{len(po[k])}→{len(pe[k])} chars")
        if a.texto:
            print("      ORIG:", re.sub(r"\s+", " ", po[k])[:300])
            print("      CAST:", re.sub(r"\s+", " ", pe[k])[:300])
    print(f"páginas con fallo: {malas}/{len(set(po) & set(pe))}")


if __name__ == "__main__":
    main()
