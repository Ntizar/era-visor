# -*- coding: utf-8 -*-
"""ocr_escaneados.py — OCR auditado de los informes sin capa de texto.

Los PDF escaneados no tienen texto que extraer: PyMuPDF devuelve páginas vacías y el md
queda declarado `escaneado: true`. Este script los recupera con **Tesseract**, y deja
constancia de CÓMO se ha hecho cada uno (eso es la auditoría):

  · qué motor y qué versión (tesseract 5.4.0 + tessdata_best),
  · qué idiomas se usaron y con qué confianza media/mínima por página,
  · cuántas páginas se OCRearon y cuántas quedaron vacías,
  · md5 del PDF de origen y fecha.

Escribe (o reescribe) el md con el texto OCR y en el frontmatter:
    texto: ocr
    ocr_motor: tesseract 5.4.0.20240606 (tessdata_best)
    ocr_idiomas: pol+eng
    ocr_confianza_media: 86.4
    ocr_confianza_min: 41.0
    ocr_paginas: 34
    ocr_paginas_vacias: 1
    ocr_fecha: 2026-11-19
y el registro por fichero en data/ocr/<CC>.json + la tabla en data/ocr/AUDITORIA.md.

Regla: **nunca se pisa un md con texto**. Sólo se OCR-ean los que están vacíos
(`escaneado: true` o sin páginas con texto). Lo que Tesseract no lea queda vacío y se
declara: no se inventa nada.

Uso:
    python scripts/ocr_escaneados.py --listar            # qué hay pendiente
    python scripts/ocr_escaneados.py PL SI --limite 3    # prueba
    python scripts/ocr_escaneados.py --todos --workers 2 # tanda completa
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pymupdf

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(RAIZ, "md")
PDFS = os.path.join(RAIZ, "pdfs")
REG = os.path.join(RAIZ, "data", "ocr")
TESSDATA = os.path.expandvars(r"%LOCALAPPDATA%\tessdata")
TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
DPI = 300

# país → idiomas de Tesseract (orden: idioma local primero, inglés como red de seguridad)
IDIOMAS = {
    "AT": "deu", "BE": "fra+nld", "BG": "bul", "CH": "deu+fra+ita", "CZ": "ces",
    "DE": "deu", "DK": "dan", "EE": "est", "EL": "ell", "ES": "spa", "FI": "fin",
    "FR": "fra", "HR": "hrv", "HU": "hun", "IE": "eng", "IT": "ita", "LT": "lit",
    "LU": "fra", "LV": "lav", "NL": "nld", "NO": "nor", "PL": "pol", "PT": "por",
    "RO": "ron", "RS": "srp", "SE": "swe", "SI": "slv", "SK": "slk", "UK": "eng",
}


def version_tesseract():
    try:
        r = subprocess.run([TESSERACT, "--version"], capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr).splitlines()[0].strip()
    except Exception as e:
        return f"no disponible ({e})"


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


def tiene_texto(cuerpo):
    for m in re.finditer(r"(?m)^## Página \d+\s*$", cuerpo):
        pass
    limpio = re.sub(r"(?m)^## Página \d+\s*$", "", cuerpo).strip()
    return len(limpio) > 400


def pendientes(refuerza=False):
    out = []
    for code in sorted(os.listdir(MD)):
        base = os.path.join(MD, code)
        if not os.path.isdir(base):
            continue
        for dp, _, fs in os.walk(base):
            for f in sorted(fs):
                if not f.endswith(".md") or f.lower().startswith(("indice", "índice", "leeme", "readme")):
                    continue
                p = os.path.join(dp, f)
                cab, cuerpo = fm(open(p, encoding="utf-8", errors="replace").read())
                if cab.get("pdf") and (refuerza and cab.get("texto") == "ocr" or not tiene_texto(cuerpo)):
                    out.append((code, p, cab))
    return out


def ocr_pdf(ruta_pdf, idiomas):
    """Devuelve (páginas:list[str], confianzas:list[float], n_vacias)."""
    doc = pymupdf.open(ruta_pdf)
    paginas, confs, vacias = [], [], 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, pag in enumerate(doc):
            png = os.path.join(tmp, f"p{i}.png")
            pag.get_pixmap(dpi=DPI).save(png)
            base = os.path.join(tmp, f"p{i}")
            subprocess.run([TESSERACT, png, base, "-l", idiomas, "--psm", "3"],
                           capture_output=True, text=True, timeout=600)
            txt = ""
            if os.path.exists(base + ".txt"):
                txt = open(base + ".txt", encoding="utf-8", errors="replace").read()
            conf = None
            if txt.strip():
                # Confianza por palabra: se pide el TSV con -c tessedit_create_tsv=1
                # (el config "tsv" a secas escribe en .txt en este build y dejaba la
                # confianza siempre a cero).
                subprocess.run([TESSERACT, png, base, "-l", idiomas, "--psm", "3",
                                "-c", "tessedit_create_tsv=1"],
                               capture_output=True, text=True, timeout=600)
                vals = []
                tsv = base + ".tsv"
                if os.path.exists(tsv):
                    for ln in open(tsv, encoding="utf-8", errors="replace").read().splitlines()[1:]:
                        c = ln.split("\t")
                        if len(c) >= 12 and c[11].strip():
                            try:
                                v = float(c[10])
                                if v > 0:
                                    vals.append(v)
                            except ValueError:
                                pass
                conf = round(sum(vals) / len(vals), 1) if vals else None
                paginas.append(txt.strip())
                confs.append(conf)
            else:
                vacias += 1
                paginas.append("")
                confs.append(0.0)
    doc.close()
    return paginas, confs, vacias


def procesar(item, motor):
    code, ruta_md, cab = item
    nom_pdf = cab.get("pdf", "")
    ruta_pdf = os.path.join(PDFS, code, nom_pdf)
    if not os.path.exists(ruta_pdf):
        return code, os.path.basename(ruta_md), "sin_pdf", {}
    idiomas = IDIOMAS.get(code, "eng")
    try:
        paginas, confs, vacias = ocr_pdf(ruta_pdf, idiomas)
    except Exception as e:
        return code, os.path.basename(ruta_md), f"error: {type(e).__name__} {e}"[:160], {}
    if not any(t.strip() for t in paginas):
        return code, os.path.basename(ruta_md), "ocr_vacio", {}
    conf_ok = [c for c in confs if isinstance(c, (int, float))]
    media = round(sum(conf_ok) / len(conf_ok), 1) if conf_ok else -1.0
    minimo = round(min(conf_ok), 1) if conf_ok else -1.0

    texto = "\n\n".join(f"## Página {i+1}\n\n{t}" for i, t in enumerate(paginas))
    md5 = hashlib.md5(open(ruta_pdf, "rb").read()).hexdigest()
    hoy = datetime.date.today().isoformat()
    nuevo_fm = [
        "---",
        f"pais: {code}",
        f"anio: {cab.get('anio', '')}",
        f"idioma: {cab.get('idioma', '??')}",
        f"pdf: {nom_pdf}",
        f"url_oficial: {cab.get('url_oficial', '')}",
        f"md5_pdf: {md5}",
        f"paginas: {len(paginas)}",
        f"chars: {len(texto)}",
        "tablas: 0",
        "cuerpo: \"ocr tesseract\"",
        "verbatim_fallos: no_aplica (texto obtenido por OCR, no hay capa de texto contra la que verificar)",
        "escaneado: true",
        "texto: ocr",
        f"ocr_motor: {motor}",
        f"ocr_idiomas: {idiomas}",
        f"ocr_confianza_media: {media}",
        f"ocr_confianza_min: {minimo}",
        f"ocr_paginas: {len(paginas)}",
        f"ocr_paginas_vacias: {vacias}",
        f"ocr_fecha: {hoy}",
        "generador: ocr_escaneados.py (Tesseract + PyMuPDF, 300 dpi)",
        "---",
        "",
    ]
    with open(ruta_md, "w", encoding="utf-8") as f:
        f.write("\n".join(nuevo_fm) + texto.rstrip() + "\n")
    registro = {"md": os.path.relpath(ruta_md, RAIZ).replace("\\", "/"),
                "pdf": os.path.relpath(ruta_pdf, RAIZ).replace("\\", "/"),
                "motor": motor, "idiomas": idiomas, "paginas": len(paginas),
                "paginas_vacias": vacias, "confianza_media": media,
                "confianza_min": min(minimo, 100), "chars": len(texto),
                "md5_pdf": md5, "fecha": hoy}
    return code, os.path.basename(ruta_md), "ok", registro


def auditoria():
    os.makedirs(REG, exist_ok=True)
    filas, total = [], 0
    for f in sorted(os.listdir(REG)):
        if not f.endswith(".json"):
            continue
        code = f[:-5]
        d = json.load(open(os.path.join(REG, f), encoding="utf-8"))
        if not d:
            continue
        confs = [v["confianza_media"] for v in d.values()]
        vac = sum(v["paginas_vacias"] for v in d.values())
        pags = sum(v["paginas"] for v in d.values())
        motor = next(iter(d.values()))["motor"]
        filas.append(f"| {code} | {len(d)} | {pags} | {vac} | "
                     f"{round(sum(confs)/len(confs),1)} | {motor} |")
        total += len(d)
    cab = ["# Auditoría del OCR",
           "",
           f"Generado por `scripts/ocr_escaneados.py` el {datetime.date.today()}. "
           "Un registro por informe en `data/ocr/<CC>.json`.",
           "",
           "Motor: **Tesseract** con `tessdata_best` a 300 dpi. La confianza es la media "
           "por palabra que declara el propio Tesseract (0-100); por debajo de 70 el texto "
           "se considera dudoso y se revisa a mano antes de traducir.",
           "",
           "| País | Informes OCR | Páginas | Páginas vacías | Confianza media | Motor |",
           "|---|---|---|---|---|---|"]
    with open(os.path.join(REG, "AUDITORIA.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(cab + filas) + f"\n\n**Total OCR-eados: {total}**\n")
    print(f"auditoría escrita: {total} informes en data/ocr/AUDITORIA.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="*")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--limite", type=int, default=0, help="máx. por país")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--confianza-minima", type=float, default=70.0)
    ap.add_argument("--refuerza", action="store_true",
                    help="re-OCRea también los ya hechos (p. ej. para recalcular confianza)")
    a = ap.parse_args()

    pend = pendientes(a.refuerza)
    if a.paises:
        pend = [p for p in pend if p[0] in [c.upper() for c in a.paises]]
    if a.limite:
        porpais, filtrado = {}, []
        for p in pend:
            if porpais.get(p[0], 0) >= a.limite:
                continue
            porpais[p[0]] = porpais.get(p[0], 0) + 1
            filtrado.append(p)
        pend = filtrado
    if a.listar:
        from collections import Counter
        print("pendientes de OCR:", dict(sorted(Counter(p[0] for p in pend).items(), key=lambda x: -x[1])))
        print("total:", len(pend))
        return
    if not pend:
        print("nada pendiente de OCR")
        return

    os.environ["TESSDATA_PREFIX"] = TESSDATA
    motor = f"{version_tesseract()} (tessdata_best, {DPI} dpi)"
    print(f"motor: {motor}")
    print(f"OCR de {len(pend)} informes · {a.workers} en paralelo")
    ok = fallos = 0
    registros = {}
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(procesar, p, motor): p for p in pend}
        for k, fut in enumerate(as_completed(futs), 1):
            code, nombre, estado, reg = fut.result()
            if estado == "ok":
                ok += 1
                registros.setdefault(code, {})[reg["md"]] = reg
                aviso = " ⚠ confianza baja" if reg["confianza_media"] < a.confianza_minima else ""
                print(f"  [{k}/{len(pend)}] ok {code} {nombre[:55]} · "
                      f"{reg['paginas']} pág · conf {reg['confianza_media']}{aviso}", flush=True)
            else:
                fallos += 1
                print(f"  [{k}/{len(pend)}] {estado} {code} {nombre[:55]}", flush=True)
    os.makedirs(REG, exist_ok=True)
    for code, nuevos in registros.items():
        ruta = os.path.join(REG, f"{code}.json")
        previo = json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else {}
        previo.update(nuevos)
        json.dump(previo, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    auditoria()
    print(f"OCR: {ok} recuperados · {fallos} sin recuperar")


if __name__ == "__main__":
    main()
