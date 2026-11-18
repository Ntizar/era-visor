# -*- coding: utf-8 -*-
"""convertir_md_pais.py — PDF -> MD v3 (determinista, tipográfico) por país y año.

Porta al repo del visor el convertidor v3 que se validó con los 351 informes del
CIAF (verbatim verificado 0 fallos) y lo generaliza a cualquier país de ERA:

    pdfs/<CC>/*.pdf  ->  md/<CC>/<AAAA>/<slug>.md

Reglas (heredadas de v3 y del SPEC del proyecto):
  · Lee el PDF en modo "dict": cada línea conoce fuente, tamaño y negrita.
  · Encabezados por TAMAÑO de fuente (tiers del propio documento), no por regex.
  · Membrete/cabecera/pie repetido se elimina por repetición enmascarada; la
    portada nunca se toca.
  · Tablas reales -> filas pipe; los marcos de plantilla se descartan.
  · Verificación integrada: cada línea emitida debe ser substring del texto del
    PDF (espacios normalizados). Los fallos van al frontmatter.
  · Cero invención: si una página no tiene capa de texto se marca `escaneado` y
    su página queda vacía (nunca se rellena a mano).

Uso:
    python scripts/convertir_md_pais.py LU            # país completo
    python scripts/convertir_md_pais.py PT --limite 5 # prueba
    python scripts/convertir_md_pais.py ES --refuerza # rehace lo ya convertido
"""
import argparse
import datetime
import hashlib
import json
import multiprocessing
import os
import re
import sys
from collections import Counter

import pymupdf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDFS = os.path.join(RAIZ, "pdfs")
MD = os.path.join(RAIZ, "md")
MANIFEST = os.path.join(RAIZ, "data", "pdf-manifest")
VIEJO_ES = os.path.join(MD, "ES")          # OCR previo disponible solo para España

FRANJA_SUP, FRANJA_INF = 0.14, 0.12
REPETICION_MIN, REPETICION_ABS = 0.6, 4
NIVEL_MIN = 0.8
NIVEL_BOLD = -0.3
MAX_HEAD = 80
MIN_CHARS_PAGINA = 120          # por debajo de esto la página se considera sin capa de texto

# ── detector de idioma por palabras función (gratis, sin LLM) ──────────────
STOP = {
    "ES": "de la que el en y los del se las por un una con para al es su sus lo como más pero o este esta entre cuando muy sin sobre también desde hasta hay fue han",
    "EN": "the of and to in a is that for on with as by at from this be are was were which it its or an not have has had they their there been shall",
    "DE": "der die das und in den von zu mit sich des auf für ist im dem nicht ein eine als auch es an werden wird sind bei aus nach wie oder",
    "FR": "de la le les des et en du un une que qui dans pour est au sur par avec ce cette il elle sont été plus pas aux ne se",
    "IT": "di che e la il un una per con non sono del della nel alla dei degli le si da come anche più tra fra gli",
    "PT": "de que e o a os as do da dos das em um uma para com não por se na no ao aos é foi são mais como",
    "NL": "de van het een en in is op dat te met voor zijn niet aan er ook als bij maar om dan nog",
    "PL": "nie się jest na to że w z do i od dla jak po oraz przez który która które były został",
    "CS": "se na je že v a to z do pro by byl která který jako také není při bylo ze",
    "HU": "a az és hogy nem is egy meg van volt azt kell csak mint pedig már amely",
    "RO": "de la a în și din cu pe un o care se nu fost pentru mai sunt cel",
    "SV": "och att det som på är av för med till den har inte om ett men var",
    "DA": "og at det som på er af for med til den har ikke om et men var",
    "NO": "og at det som på er av for med til den har ikke om et men var",
    "EL": "και το του της των στο στη να δεν με για από που είναι τα οι",
    "BG": "и на в се от за по с не е че като са при или това",
    "HR": "je i u na se da su za od koji koja koje nije bio biti",
    "SK": "sa na je že v a to z do pre by bol ktorá ktorý ako tiež nie",
    "SL": "je in na se da so za od ki kot tudi ni bil pri",
    "FI": "ja on ei se että oli ovat joka mutta myös kun niin vain",
    "LT": "ir yra kad į su iš apie bet kaip ne buvo taip pat",
    "LV": "un ir ka uz no ar par bet kā ne bija arī tad",
}
_STOP = {k: set(v.split()) for k, v in STOP.items()}


def detectar_idioma(texto: str) -> str:
    muestra = re.sub(r"[^A-Za-zÀ-ɏΆ-ώЀ-ӿ ]", " ", texto[:60000]).lower().split()
    if len(muestra) < 40:
        return "??"
    cnt = Counter(muestra)
    mejor, puntos = "??", 0.0
    for code, pal in _STOP.items():
        s = sum(cnt[w] for w in pal)
        if s > puntos:
            mejor, puntos = code, s
    return mejor if puntos >= 15 else "??"


def mascara(s):
    return re.sub(r"\s+", " ", re.sub(r"\d+", "#", s)).strip().casefold()


def lineas_dict(p):
    out = []
    for b in p.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b.get("lines", []):
            spans = [s for s in l.get("spans", []) if s["text"].strip()]
            if not spans:
                continue
            out.append({
                "y": l["bbox"][1], "x": l["bbox"][0],
                "texto": "".join(s["text"] for s in l["spans"]),
                "size": round(max(s["size"] for s in spans), 1),
                "bold": bool(any(s["flags"] & 16 for s in spans)),
            })
    return out


def cuerpo_y_tiers(pags_lineas):
    pesos = Counter()
    for ls in pags_lineas:
        for l in ls:
            if l["size"] >= 5:
                pesos[l["size"]] += len(l["texto"])
    if not pesos:
        return 10.0, []
    cuerpo = pesos.most_common(1)[0][0]
    tiers = sorted({s for s in pesos if s >= cuerpo + NIVEL_MIN}, reverse=True)[:3]
    return cuerpo, tiers


def tablas_de(p):
    W, H = p.rect.width, p.rect.height
    res = []
    try:
        for t in p.find_tables():
            bw, bh = t.bbox[2] - t.bbox[0], t.bbox[3] - t.bbox[1]
            if bw > 0.55 * W and bh > 0.45 * H:
                continue
            if t.row_count < 2 or t.col_count < 2 or t.col_count > 8:
                continue
            res.append(t)
    except Exception:
        pass
    return res


def filas_tabla(t):
    filas = []
    for fila in t.extract():
        celdas = [re.sub(r"\s*\n\s*", " ", (c or "")).strip() for c in fila]
        if any(celdas):
            filas.append("| " + " | ".join(celdas) + " |")
    return filas


def texto_pagina_norm(p):
    return re.sub(r"\s+", " ", p.get_text()).strip()


def procesar_pdf(ruta, con_tablas=True):
    doc = pymupdf.open(ruta)
    n_pag = doc.page_count
    pags_lineas = [lineas_dict(p) for p in doc]
    cuerpo, tiers = cuerpo_y_tiers(pags_lineas)

    repeticiones = {}
    for i, ls in enumerate(pags_lineas):
        if i == 0:
            continue
        H = doc[i].rect.height
        for l in ls:
            if l["y"] < FRANJA_SUP * H or l["y"] > (1 - FRANJA_INF) * H:
                repeticiones.setdefault(mascara(l["texto"]), set()).add(i)
    umbral = max(REPETICION_ABS, REPETICION_MIN * max(n_pag - 1, 1))
    ruido = {k for k, pgs in repeticiones.items() if k and len(pgs) >= umbral}

    md_paginas, verbatim_fallos, n_tablas, excluidos = [], 0, 0, Counter()
    for i, ls in enumerate(pags_lineas):
        H, p = doc[i].rect.height, doc[i]
        tablas = tablas_de(p) if con_tablas else []
        n_tablas += len(tablas)
        cajas = [t.bbox for t in tablas]
        elementos = []
        for l in ls:
            ycentro = l["y"] + 2
            if any(bb[1] <= ycentro <= bb[3] and bb[0] <= l["x"] <= bb[2] for bb in cajas):
                continue
            if i > 0 and mascara(l["texto"]) in ruido and (
                    l["y"] < FRANJA_SUP * H or l["y"] > (1 - FRANJA_INF) * H):
                excluidos[mascara(l["texto"])] += 1
                continue
            nivel = 0
            t = l["texto"].strip()
            if i == 0:
                nivel = 0
            elif len(t) <= MAX_HEAD and not t.islower() and not t.endswith((",", ";")):
                if l["size"] in tiers:
                    nivel = tiers.index(l["size"]) + 1
                elif l["bold"] and l["size"] >= cuerpo + NIVEL_BOLD:
                    nivel = 2 if t.upper() == t else 3
            pref = ("#" * nivel + " ") if nivel else ""
            elementos.append((l["y"], l["x"], "linea", pref + l["texto"]))
        for t in tablas:
            elementos.append((t.bbox[1], t.bbox[0], "tabla", "\n".join(filas_tabla(t))))
        elementos.sort(key=lambda e: (round(e[0], 1), e[1]))
        md_paginas.append("\n".join(e[3] for e in elementos))

    texto = "\n\n".join(f"## Página {i+1}\n\n{t}" for i, t in enumerate(md_paginas))

    for i, ls in enumerate(pags_lineas):
        norm = texto_pagina_norm(doc[i])
        for l in ls:
            if re.sub(r"\s+", " ", l["texto"]).strip() not in norm:
                verbatim_fallos += 1

    vacias = sum(1 for t in md_paginas if len(t.strip()) < MIN_CHARS_PAGINA)
    escaneado = bool(n_pag and vacias / n_pag > 0.5)
    doc.close()
    return {
        "paginas": n_pag, "chars": len(texto), "tablas": n_tablas,
        "excluidos": sum(excluidos.values()), "rotulos": ", ".join(sorted(excluidos)[:6]),
        "cuerpo": cuerpo, "tiers": tiers, "verbatim_fallos": verbatim_fallos,
        "escaneado": escaneado, "paginas_sin_texto": vacias, "texto": texto,
    }


def slug(nombre):
    s = os.path.splitext(nombre)[0]
    s = re.sub(r'[<>:"/\\|?*]', "-", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    return s or "sin-titulo"


def cargar_manifest(code):
    """{nombre_pdf: (año, url_oficial)} desde data/pdf-manifest/<CC>.json"""
    ruta = os.path.join(MANIFEST, f"{code}.json")
    idx = {}
    if not os.path.exists(ruta):
        return idx
    from urllib.parse import unquote
    for it in json.load(open(ruta, encoding="utf-8")):
        nombre = unquote(it["pdf"].split("/")[-1])
        idx[nombre] = (it.get("year"), "https://www.era.europa.eu" + it["pdf"])
    return idx


def convertir_uno(ruta, code, anio, url, dest_dir, refuerza, con_tablas=True):
    nom = os.path.basename(ruta)
    nombre_md = slug(nom) + ".md"
    destino = os.path.join(dest_dir, nombre_md)
    if os.path.exists(destino) and not refuerza:
        return None
    d = procesar_pdf(ruta, con_tablas)
    md5 = hashlib.md5(open(ruta, "rb").read()).hexdigest()
    idioma = detectar_idioma(d["texto"])
    fm = [
        "---",
        f"pais: {code}",
        f"anio: {anio if anio else ''}",
        f"idioma: {idioma}",
        f"pdf: {nom}",
        f"url_oficial: {url}",
        f"md5_pdf: {md5}",
        f"paginas: {d['paginas']}",
        f"chars: {d['chars']}",
        f"tablas: {d['tablas']}{'' if con_tablas else ' (extracción desactivada: la PDF colgaba find_tables)'}",
        f"cuerpo: \"{d['cuerpo']}pt; encabezados {len(d['tiers'])} niveles\"",
        f"rotulos_excluidos: \"{d['excluidos']} ({d['rotulos']})\"",
        f"verbatim_fallos: {d['verbatim_fallos']}",
        f"escaneado: {'true' if d['escaneado'] else 'false'}",
        f"paginas_sin_texto: {d['paginas_sin_texto']}",
        f"fecha_proceso: {datetime.date.today().isoformat()}",
        "generador: convertir_md_pais.py (PyMuPDF %s, dict tipográfico)" % pymupdf.__version__,
        "---",
        "",
    ]
    os.makedirs(dest_dir, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(fm) + d["texto"].rstrip() + "\n")
    return destino, d, idioma


def _una(tarea):
    """Convierte un PDF. Función de nivel de módulo para poder picklear en procesos."""
    code, ruta, anio, url, refuerza, con_tablas = tarea
    nom = os.path.basename(ruta)
    dest_dir = os.path.join(MD, code, str(anio) if anio else "sin-ano")
    try:
        r = convertir_uno(ruta, code, anio, url, dest_dir, refuerza, con_tablas)
        if r is None:
            return code, nom, "ya", False
        return code, nom, "ok", r[1]["escaneado"]
    except Exception as e:
        return code, nom, f"fallo: {type(e).__name__} {e}"[:160], False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="+")
    ap.add_argument("--limite", type=int, default=0, help="máx. PDFs por país (pruebas)")
    ap.add_argument("--refuerza", action="store_true")
    ap.add_argument("--timeout", type=int, default=150,
                    help="segundos máximos por PDF antes de descartarlo")
    ap.add_argument("--workers", type=int, default=4,
                    help="PDFs en paralelo (cada uno es un proceso PyMuPDF)")
    a = ap.parse_args()

    tareas = []
    for code in [c.upper() for c in a.paises]:
        origen = os.path.join(PDFS, code)
        if not os.path.isdir(origen):
            print(f"[{code}] no hay pdfs en {origen}")
            continue
        man = cargar_manifest(code)
        pdfs = sorted(p for p in os.listdir(origen) if p.lower().endswith(".pdf"))
        if a.limite:
            pdfs = pdfs[:a.limite]
        print(f"[{code}] {len(pdfs)} PDFs, manifiesto {len(man)}")
        for nom in pdfs:
            anio, url = man.get(nom, (None, ""))
            tareas.append((code, os.path.join(origen, nom), anio, url, a.refuerza, True))

    if not tareas:
        return
    por_pais, ok, fallos, escaneados = {}, 0, 0, 0
    pendientes = list(tareas)

    def anotar(res):
        nonlocal ok, fallos, escaneados
        code, nom, estado, esc = res
        if estado == "ok":
            ok += 1
            por_pais[code] = por_pais.get(code, 0) + 1
            if esc:
                escaneados += 1
                print(f"  ⚠ ESCANEADO [{code}] {nom}")
        elif estado.startswith("fallo"):
            fallos += 1
            print(f"  ✗ [{code}] {nom}: {estado}")
        return estado

    # multiprocessing.Pool (no ProcessPoolExecutor) porque permite matar y rehacer el
    # pool cuando un PDF se cuelga o revienta: hay documentos que dejan find_tables
    # girando minutos. Con timeout por fichero se aísla el venenoso y se sigue.
    while pendientes:
        mp = multiprocessing.Pool(processes=a.workers, maxtasksperchild=4)
        cortado = False
        try:
            asyncs = [(t, mp.apply_async(_una, (t,))) for t in pendientes]
            for t, ar in asyncs:
                try:
                    res = ar.get(timeout=a.timeout)
                except multiprocessing.TimeoutError:
                    print(f"  ⏱ TIMEOUT [{t[0]}] {os.path.basename(t[1])} "
                          f"({a.timeout}s) — se descarta y se sigue", flush=True)
                    pendientes.remove(t)
                    if t[5]:          # reintento sin tablas antes de descartarla
                        print(f"     ↻ reintento sin tablas: {os.path.basename(t[1])}", flush=True)
                        pendientes.append((t[0], t[1], t[2], t[3], t[4], False))
                    else:
                        fallos += 1
                    cortado = True
                    break
                except Exception as e:
                    res = (t[0], os.path.basename(t[1]),
                           f"fallo: {type(e).__name__} {e}"[:160], False)
                anotar(res)
                pendientes.remove(t)
                hechas = len(tareas) - len(pendientes)
                if hechas % 25 == 0:
                    print(f"  [{hechas}/{len(tareas)}] ok={ok} fallos={fallos} "
                          f"escaneados={escaneados}", flush=True)
        finally:
            mp.terminate()
            mp.join()
        if cortado:
            continue

    print("CONVERTIDOS por país: " + ", ".join(f"{c}:{n}" for c, n in sorted(por_pais.items())))
    print(f"TOTAL {ok}/{len(tareas)} · fallos {fallos} · escaneados {escaneados}")


if __name__ == "__main__":
    main()
