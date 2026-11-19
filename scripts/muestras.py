# -*- coding: utf-8 -*-
"""muestras.py — muestrario aleatorio del corpus para revisión humana.

Elige N informes al azar (semilla fija para que sea reproducible), reparte entre países
para que no salgan todos del mismo, y escribe `MUESTRAS.md` con:
  · ficha del informe (país, año, idioma, páginas, caracteres, verificación, fidelidad IA),
  · una página real del original y la misma página en castellano, una al lado de la otra,
  · la ruta exacta del fichero para poder abrirlo entero.

Uso:
    python scripts/muestras.py                 # 6 informes, semilla 7
    python scripts/muestras.py --n 12 --semilla 42 --pagina 3
"""
import argparse
import json
import os
import random
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(RAIZ, "md")
MD_ES = os.path.join(RAIZ, "md-es")
REV = os.path.join(RAIZ, "data", "revision")
SALIDA = os.path.join(RAIZ, "MUESTRAS.md")


def fm(texto):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", texto, re.S)
    if not m:
        return {}, texto
    d = {}
    for l in m.group(1).splitlines():
        if ":" in l:
            k, v = l.split(":", 1)
            d[k.strip()] = v.strip().strip('"')
    return d, texto[m.end():]


def paginas(cuerpo):
    out, ms = {}, list(re.finditer(r"(?m)^## Página (\d+)\s*$", cuerpo))
    for i, m in enumerate(ms):
        out[int(m.group(1))] = cuerpo[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(cuerpo)]
    return out


def ficha_fidelidad(code, rel):
    f = os.path.join(REV, f"{code}.json")
    if not os.path.exists(f):
        return None
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        return None
    v = d.get(rel) or d.get(rel.replace("\\", "/"))
    return v.get("fidelidad_media") if v else None


def limpiar(t):
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--pagina", type=int, default=0, help="0 = página con más texto")
    a = ap.parse_args()

    candidatos = []
    for code in sorted(os.listdir(MD_ES)):
        base = os.path.join(MD_ES, code)
        if not os.path.isdir(base):
            continue
        for dp, _, fs in os.walk(base):
            for f in fs:
                if f.endswith(".md") and not f.lower().startswith(("indice", "índice", "leeme", "readme")):
                    candidatos.append((code, os.path.join(dp, f)))
    random.Random(a.semilla).shuffle(candidatos)

    # reparto por país: primero uno de cada país distinto
    elegidos, vistos = [], set()
    for code, p in candidatos:
        if code not in vistos and len(elegidos) < a.n:
            elegidos.append((code, p))
            vistos.add(code)
    for code, p in candidatos:
        if len(elegidos) >= a.n:
            break
        if (code, p) not in elegidos:
            elegidos.append((code, p))

    lineas = ["# Muestrario del corpus — informes al azar",
              "",
              f"Semilla {a.semilla}, {len(elegidos)} informes de {len({c for c, _ in elegidos})} países.",
              "Cada bloque enseña una página del original y la misma en castellano, tal cual está en el repo.",
              ""]
    for code, ruta_es in elegidos:
        texto_es = open(ruta_es, encoding="utf-8").read()
        fmd, cuerpo_es = fm(texto_es)
        rel_es = os.path.relpath(ruta_es, RAIZ).replace("\\", "/")
        ruta_or = os.path.join(RAIZ, fmd.get("md_origen", "").replace("/", os.sep))
        if not os.path.exists(ruta_or):
            continue
        fmo, cuerpo_or = fm(open(ruta_or, encoding="utf-8").read())
        po, pe = paginas(cuerpo_or), paginas(cuerpo_es)
        comunes = sorted(set(po) & set(pe))
        if not comunes:
            continue
        # Página de muestra: la de más texto que NO sea índice (los sumarios van
        # llenos de puntos suspensivos y no enseñan nada del contenido real).
        def es_indice(t):
            return sum(1 for l in t.splitlines() if "...." in l) >= 3

        utiles = [k for k in comunes if not es_indice(pe[k])] or comunes
        if a.pagina:
            pag = a.pagina if a.pagina in comunes else utiles[0]
        else:
            pag = max(utiles, key=lambda k: len(pe[k]))
        fidel = ficha_fidelidad(code, rel_es)
        lineas += [
            f"## {code} · {fmd.get('anio', '?')} · {os.path.basename(ruta_es)}",
            "",
            "| Dato | Valor |",
            "|---|---|",
            f"| País / año | {code} / {fmd.get('anio', '?')} |",
            f"| Idioma original | **{fmd.get('idioma_origen', '?')}** |",
            f"| Páginas · caracteres | {fmd.get('paginas') or fmo.get('paginas', '?')} · {fmd.get('chars', '?')} |",
            f"| Verificación numérica | {fmd.get('verificacion', '—')} |",
            f"| Fidelidad IA (0-100) | {fidel if fidel is not None else 'sin revisar'} |",
            f"| Fichero castellano | `{rel_es}` |",
            f"| Original | `{fmd.get('md_origen', '')}` |",
            f"| PDF oficial | {fmd.get('url_oficial', '')[:110]} |",
            "",
            f"**Página {pag} — original ({fmd.get('idioma_origen', '?')})**",
            "",
            "```text",
            limpiar(po[pag])[:1400],
            "```",
            "",
            f"**Página {pag} — castellano**",
            "",
            "```text",
            limpiar(pe[pag])[:1400],
            "```",
            "",
            "---",
            "",
        ]
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))
    print(f"escrito {SALIDA} con {len(elegidos)} informes")


if __name__ == "__main__":
    main()
