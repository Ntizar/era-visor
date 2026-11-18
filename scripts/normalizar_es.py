# -*- coding: utf-8 -*-
"""normalizar_es.py — mete los 351 informes españoles (md_v3) en la colección nueva.

Lee  md_v3/*.md  (castellano original, extracción v3 ya validada) y escribe
md-es/ES/<AAAA>/<slug>.md con el frontmatter normalizado del proyecto + los campos
estructurados que la base de datos ya tiene verificados (expediente, tipo, víctimas,
ubicación). No traduce nada: el original español se conserva literal.

Uso:
    python scripts/normalizar_es.py
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_V3 = os.path.join(RAIZ, "md_v3")
SALIDA = os.path.join(RAIZ, "md-es", "ES")
DB = os.path.join(RAIZ, "data", "db", "reports", "ES.json")

CAMPOS_DB = ["expediente", "titulo", "tipo", "tipo_categoria", "tipo_informe", "gravedad",
             "fecha", "hora", "estacion", "provincia", "fallecidos", "heridos_graves",
             "heridos_leves", "linea", "pk"]


def fm_y_cuerpo(texto):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", texto, re.S)
    if not m:
        return {}, texto
    fm = {}
    for l in m.group(1).splitlines():
        if ":" in l:
            k, v = l.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, texto[m.end():]


def clave(nombre):
    return os.path.splitext(nombre)[0]


def main():
    db = {r["id"]: r for r in json.load(open(DB, encoding="utf-8"))}
    por_fichero = {}
    for ident, r in db.items():
        # id "ES-190628-120817-IF-SN_CIAF" -> fichero "190628-120817-IF-SN_CIAF.md"
        por_fichero[ident[3:] if ident.startswith("ES-") else ident] = r

    hechos, sin_datos, anios = 0, [], {}
    for nom in sorted(os.listdir(MD_V3)):
        if not nom.endswith(".md") or nom.lower().startswith(("leeme", "readme", "index")):
            continue
        ruta = os.path.join(MD_V3, nom)
        texto = open(ruta, encoding="utf-8").read()
        fm, cuerpo = fm_y_cuerpo(texto)
        r = por_fichero.get(clave(nom))
        anio = (r or {}).get("fecha", "")[:4] if r else ""
        if not re.fullmatch(r"\d{4}", anio or ""):
            anio = "sin-ano"
            sin_datos.append(nom)
        cab = ["---", "pais: ES", f"anio: {anio}", "idioma_origen: ES", "traduccion: no",
               f"md_origen: md_v3/{nom}",
               f"pdf: {fm.get('pdf', '')}", f"url_oficial: {fm.get('url_oficial', '')}",
               f"md5_pdf: {fm.get('md5_pdf', '')}", f"paginas: {fm.get('paginas', '')}",
               f"chars: {fm.get('chars', '')}", f"verbatim_fallos: {fm.get('verbatim_fallos', '')}"]
        if r:
            cab += [f"id_db: {r['id']}"]
            for c in CAMPOS_DB:
                v = r.get(c)
                if v not in (None, "", [], 0):
                    if isinstance(v, str) and any(ch in v for ch in ':#"'):
                        v = '"' + v.replace('"', "'") + '"'
                    cab.append(f"{c}: {v}")
        cab += ["normalizado: si", "---", ""]
        dest_dir = os.path.join(SALIDA, anio)
        os.makedirs(dest_dir, exist_ok=True)
        with open(os.path.join(dest_dir, nom), "w", encoding="utf-8") as f:
            f.write("\n".join(cab) + cuerpo.lstrip("\n"))
        hechos += 1
        anios[anio] = anios.get(anio, 0) + 1

    print(f"ES: {hechos} informes normalizados en md-es/ES/")
    print("  por año:", dict(sorted(anios.items())))
    if sin_datos:
        print(f"  ⚠ {len(sin_datos)} sin año en la BD (quedan en sin-ano): {sin_datos[:5]}")


if __name__ == "__main__":
    main()
