#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cruce eRAIL ↔ PDFs por fecha de suceso.

Uso:
    python cruce_erail.py ES

Estrategias de emparejamiento (en orden):
  1. Fecha de suceso en el título eRAIL ("..., 29/06/2002, ...")
  2. Fecha de suceso en 'Date of occurrence'
     ↔ fecha de ocurrencia codificada en el nombre del PDF:
        ID-DDMMYY-DDMMYY | IF-DDMMYY-... | DDMMYY-... | YYYY-NN-DDMM
Guarda data/cruce/ES-cruce.json con emparejamientos y huérfanos.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MESES = {"01": "enero", "02": "febrero", "03": "marzo", "04": "abril", "05": "mayo",
         "06": "junio", "07": "julio", "08": "agosto", "09": "septiembre",
         "10": "octubre", "11": "noviembre", "12": "diciembre"}
MESES_EN = {"enero": "january", "febrero": "february", "marzo": "march", "abril": "april",
            "mayo": "may", "junio": "june", "julio": "july", "agosto": "august",
            "septiembre": "september", "octubre": "october", "noviembre": "november",
            "diciembre": "december", "ene": "jan", "abr": "apr", "ago": "aug",
            "sept": "september", "dic": "dec"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip().lower()


def fecha_desde_titulo(titulo: str):
    """Extrae fecha DD/MM/YYYY (o '12 de junio de 2006') del título eRAIL."""
    if not titulo:
        return None
    m = re.search(r"(\d{2})/(\d{2})/(\d{4})", titulo)
    if m:
        d, mo, y = m.groups()
        if 1 <= int(mo) <= 12:
            return f"{y}-{mo}-{d}"
    m = re.search(r"\b(\d{1,2})-(\d{1,2})-(\d{2}|\d{4})\b", titulo)
    if m:
        d, mo, y = m.groups()
        if 1 <= int(mo) <= 12 and 1 <= int(d) <= 31:
            y = ("20" + y) if len(y) == 2 else y
            return f"{y}-{int(mo):02d}-{int(d):02d}"
    t = norm(titulo)
    for dd, mes in MESES.items():
        m = re.search(rf"(\d{{1,2}}) de {norm(mes)}(?: de)? (\d{{4}})", t)
        if m:
            return f"{m.group(3)}-{dd}-{int(m.group(1)):02d}"
        men = MESES_EN[mes]
        m = re.search(rf"(\d{{1,2}}) {men} (\d{{4}})", t)
        if m:
            return f"{m.group(2)}-{dd}-{int(m.group(1)):02d}"
        m = re.search(rf"{men} (\d{{1,2}}),? (\d{{4}})", t)
        if m:
            return f"{m.group(2)}-{dd}-{int(m.group(1)):02d}"
    return None


def fechas_desde_nombre(nombre: str):
    """Fechas candidatas (iso,DDMMYY) codificadas en el nombre del PDF."""
    base = nombre.rsplit(".", 1)[0]
    out = []
    # patrón YYYY-NN-MMDD o YYYY-NN-DDMM (informes recientes: 2024-111-1029 = 29 oct)
    for m in re.finditer(r"(20\d\d)-\d{1,3}-(\d{2})(\d{2})", base):
        a, b = m.group(2), m.group(3)
        # interpretación MMDD
        if 1 <= int(a) <= 12 and 1 <= int(b) <= 31:
            out.append((f"{m.group(1)}-{a}-{b}", "MMDD"))
        # interpretación DDMM (si distinta de la anterior)
        if 1 <= int(b) <= 12 and 1 <= int(a) <= 31:
            iso2 = f"{m.group(1)}-{b}-{a}"
            if not any(o[0] == iso2 for o in out):
                out.append((iso2, "DDMM2"))
    # patrón DDMMYY
    for m in re.finditer(r"(?:^|[-_ ])(\d{2})(\d{2})(\d{2})(?:[-_ ]|$)", base):
        dd, mm, yy = m.groups()
        if 1 <= int(dd) <= 31 and 1 <= int(mm) <= 12:
            out.append((f"20{yy}-{mm}-{dd}", "DDMMYY"))
    return out


def main(codigo: str):
    inv = json.loads((RAIZ / "data" / "erail" / f"{codigo}-investigations.json").read_text(encoding="utf-8"))
    manifest = json.loads((RAIZ / "data" / "pdf-manifest" / f"{codigo}.json").read_text(encoding="utf-8"))

    # índice de PDFs por fecha
    pdfs_por_fecha = {}
    for item in manifest:
        nombre = item["pdf"].split("/")[-1]
        for iso, tipo in fechas_desde_nombre(nombre):
            pdfs_por_fecha.setdefault(iso, []).append({**item, "nombre": nombre, "patron": tipo})

    pares, sin_pdf, sin_fecha = [], [], []
    pdfs_usados = set()
    for fila in inv:
        fecha = fila.get("Date of occurrence") or fecha_desde_titulo(fila.get("Title"))
        metodo = "date_field" if fila.get("Date of occurrence") else "title"
        if not fecha:
            fecha = fecha_desde_titulo(fila.get("Title"))
            metodo = "title"
        candidatos = pdfs_por_fecha.get(fecha, [])
        libres = [c for c in candidatos if c["pdf"] not in pdfs_usados]
        if libres:
            pdfs_usados.add(libres[0]["pdf"])
            pares.append({
                "erail": fila,
                "pdf": libres[0]["nombre"],
                "pdf_path": libres[0]["pdf"],
                "fecha": fecha,
                "metodo": metodo,
                "ambiguo": len(libres) > 1,
            })
        elif fecha:
            sin_pdf.append({"erail": fila, "fecha": fecha})
        else:
            sin_fecha.append(fila)

    # PDFs sin pareja
    huerfanos = [it["pdf"].split("/")[-1] for it in manifest if it["pdf"] not in pdfs_usados]

    out = RAIZ / "data" / "cruce"
    out.mkdir(parents=True, exist_ok=True)
    res = {"pares": pares, "sin_pdf": sin_pdf, "sin_fecha": sin_fecha, "pdfs_huerfanos": huerfanos}
    (out / f"{codigo}-cruce.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[{codigo}] eRAIL {len(inv)} ↔ PDFs {len(manifest)}")
    print(f"  emparejados: {len(pares)} | sin PDF: {len(sin_pdf)} | sin fecha: {len(sin_fecha)} | PDFs sin pareja: {len(huerfanos)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1].upper())
