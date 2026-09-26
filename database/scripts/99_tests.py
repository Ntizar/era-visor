#!/usr/bin/env python3
"""
99_tests.py — ARNÉS DE TESTS RECURRENTES de la base de datos CIAF.

Filosofía: los gates viven DENTRO de cada script (01/02/03/05 afirman que
están bien). Este arnés los RELEE por fuera y los contraste contra los
fuentes, para que un cambio en un script no se cuele sin que salte algo.

Cada test es independiente: si uno falla, los demás siguen corriendo y el
resumen lista TODOS los fallos de una vez (nada de "arregla uno y descubre
el siguiente a la semana siguiente").

  T1 estructura      ficheros y recuentos base
  T2 manifest        H1: manifest completo, url_oficial 100%
  T3 md_base         H2: NO-pérdida verificada por el gate de 01 (01 --verificar)
  T4 crudo           H3: cada valor con cita O procedencia; muestra re-verificada
  T5 excel           H4: filas/columnas, url, sin títulos de bloque, refs
  T6 fase4           anti-alucinación: cita re-verificada FUERA de 05
  T7 consistencia    md_base ↔ crudo (stem a stem) y crudo ↔ manifest (clave)
  T8 dobles          expedientes con 2 documentos: marcados, nunca fusionados
  T9 regeneración    02+03 sobre 1 informe sin tocar el resto

NOTA de calibración: el primer arnés daba 5 fallos — 4 eran supuestos MÍOS
erróneos (esperaba 372 informes en el manifest cuando son 351, comparaba
stem contra clave, exigía cita a campos de procedencia v3, y contaba como
"pérdidas" frases del índice que 01 elimina a propósito). Un test que grita
siempre no protege de nada: antes de ampliar un umbral, comprobar cuál es
el valor real del corpus.

Uso:  py database/scripts/99_tests.py [--rapido] [--verbose]
Salida: exit 0 si todo OK, exit 1 con el listado de fallos.
"""

import glob
import json
import os
import re
import sys
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DB = RAIZ / "database"
DATA = DB / "data"
CRUDO = DATA / "crudo"
MDB = DB / "md_base"
XLSX = DATA / "ciaf_base_global.xlsx"
MEJ = DATA / "mejorado"

DOCS = 372              # documentos (md_base == crudo)
EXPEDIENTES = 351       # filas del manifest (1 trae la clave vacía)
CLAVES = 350            # claves únicas del manifest (351 filas - 1 vacía)
DOBLES = 21             # expedientes con DOS documentos (IF+RS, Final+Interim...)
CAMPOS_GUIA = 70        # columnas reales de la guía (85 filas - 15 títulos)
RAPIDO = "--rapido" in sys.argv

fallos, okey, avisos = [], [], []


def test(nombre, ok, detalle="", critico=True):
    """Los avisos NO bloquean: documentan algo raro pero legítimo (p. ej.
    un PDF escaneado sin OCR). Contarlos como fallo inunda el gate y deja
    de significar nada."""
    if ok:
        marca, bucket = "OK   ", okey
    elif critico:
        marca, bucket = "FALLA", fallos
    else:
        marca, bucket = "aviso", avisos
    line = "[%s] %-26s %s" % (marca, nombre, detalle)
    print(line, flush=True)
    bucket.append(line)
    return ok


def norm(t):
    return re.sub(r"\s+", " ", str(t or "")).strip()


def paginas(md_text):
    partes = re.split(r"^##\s*P[áa]gina\s+(\d+)\s*$", md_text,
                      flags=re.M | re.I)
    return {int(partes[i]): partes[i + 1]
            for i in range(1, len(partes) - 1, 2)}


def cita_en_pagina(cita, pagina_txt):
    """True sólo si la cita aparece LITERALMENTE en la página citada."""
    c, p = norm(cita), norm(pagina_txt)
    if len(c) < 12:
        return False
    return c in p or c[:60] in p


# ---------------------------------------------------------------- T1
def t1_estructura():
    faltan = [str(p.relative_to(RAIZ)) for p in
              (DB / "SPEC.md", DATA / "manifest_maestro.json",
               DATA / "guia_campos.json", XLSX) if not p.exists()]
    n_md = len(glob.glob(str(MDB / "*.md")))
    n_cr = len(glob.glob(str(CRUDO / "*.json")))
    ok = not faltan and n_md == DOCS and n_cr == DOCS
    test("estructura", ok,
         "%d md · %d crudo · falta: %s" % (n_md, n_cr, faltan or "-"))


# ---------------------------------------------------------------- T2
def t2_manifest():
    man = json.loads((DATA / "manifest_maestro.json").read_text(encoding="utf-8"))
    inf = man.get("informes", [])
    sin_url = [r.get("clave", "?") for r in inf if not r.get("url_oficial")]
    claves = [r.get("clave") for r in inf if r.get("clave")]
    dups = len(claves) - len(set(claves))
    test("manifest H1",
         len(inf) == EXPEDIENTES and not sin_url and dups == 0,
         "%d/%d informes · %d sin url · %d claves dup"
         % (len(inf), EXPEDIENTES, len(sin_url), dups))


# ---------------------------------------------------------------- T3
def t3_md_base():
    """El gate de no-pérdida es el de 01, corrido FUERA de él."""
    if RAPIDO:
        fs = sorted(glob.glob(str(MDB / "*.md")))
        sin = [f for f in fs
               if not re.search(r"^##\s*P[áa]gina\s+1\s*$",
                                Path(f).read_text(encoding="utf-8",
                                                  errors="replace"),
                                re.M | re.I)]
        test("md_base H2", not sin,
             "(rápido) %d sin página 1 / %d" % (len(sin), len(fs)),
             critico=False)
        return
    r = subprocess.run(
        [sys.executable, str(DB / "scripts" / "01_mejorar_md.py"), "--verificar"],
        cwd=str(RAIZ), capture_output=True, text=True, timeout=900)
    ok = r.returncode == 0 and "GATE H2: OK" in (r.stdout or "")
    ult = [l for l in (r.stdout or "").splitlines() if l.strip()][-1:] or [""]
    test("md_base H2", ok, ult[0][:110])
    if not ok and VERBOSE:
        print((r.stdout or "")[-800:])


# ---------------------------------------------------------------- T4
def t4_crudo():
    fs = sorted(glob.glob(str(CRUDO / "*.json")))
    sin_traza = 0       # sin cita Y sin procedencia = dato sin fuente
    verif_ok = verif_mal = 0
    refs = set()
    try:
        guia = json.loads((DATA / "guia_campos.json").read_text(encoding="utf-8"))
        refs = {str(g.get("ref")) for g in guia
                if str(g.get("ref", "")).strip()[:1].isdigit()
                and (g.get("campo") or "").strip()}
    except Exception:
        pass
    cols = set()
    for f in fs:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        md = d.get("md") or ""
        pags = paginas(Path(md).read_text(encoding="utf-8", errors="replace")) \
            if Path(md).exists() else {}
        for ref, c in (d.get("campos") or {}).items():
            if ref in refs:
                cols.add(ref)
            if c.get("valor_fuente") in (None, "", [], {}):
                continue
            # regla de oro 1: cita literal O procedencia; sin NINGUNA = fallo
            if not (c.get("pagina") or c.get("origen") or c.get("regla")):
                sin_traza += 1
            if (verif_ok + verif_mal) < 40 and c.get("pagina") and c.get("cita"):
                if cita_en_pagina(c.get("cita"),
                                  pags.get(int(c.get("pagina")), "")):
                    verif_ok += 1
                else:
                    verif_mal += 1
    test("crudo H3",
         sin_traza == 0 and verif_mal == 0 and len(cols) == CAMPOS_GUIA,
         "%d sin fuente · muestra %d/%d citas OK · %d/%d campos"
         % (sin_traza, verif_ok, verif_ok + verif_mal, len(cols), CAMPOS_GUIA))


# ---------------------------------------------------------------- T5
def t5_excel():
    try:
        from openpyxl import load_workbook
    except ImportError:
        test("excel H4", False, "openpyxl no instalado", critico=False)
        return
    wb = load_workbook(XLSX, read_only=True)
    ws = wb["Informes"]
    filas = list(ws.iter_rows(values_only=True))
    cab = [str(x or "") for x in filas[0]]
    datos = filas[1:]
    i_url = cab.index("url_oficial") if "url_oficial" in cab else -1
    sin_url = sum(1 for f in datos if i_url < 0 or not f[i_url])
    # títulos de bloque colados como columna (bug real: 85 → 70)
    fantasmas = [c for c in cab if c and c[0].isdigit() and "." in c
                 and len(c) > 12 and not re.match(r"^\d+(\.\d+)*$", c)]
    dup = len(cab) - len(set(cab))
    esperadas = ["Informes", "Recomendaciones", "Entidades", "Cronologia",
                 "Trenes", "Personal", "Diccionario", "Cobertura", "Tablas",
                 "Mejorado"]
    faltan = [h for h in esperadas if h not in wb.sheetnames]
    # columnas de la GUÍA: se comparan contra guia_campos.json (la fuente),
    # nunca con un patrón heurístico — una regex se quedó corta (61/70)
    # porque la guía trae refs mixtas.
    try:
        guia = json.loads((DATA / "guia_campos.json").read_text(encoding="utf-8"))
        refs_guia = {str(x.get("ref")) for x in guia
                     if str(x.get("ref", "")).strip()[:1].isdigit()
                     and (x.get("campo") or "").strip()}
    except Exception:
        refs_guia = set()
    faltan_refs = sorted(refs_guia - set(cab))
    guia_cols = sorted(refs_guia & set(cab))
    wb.close()
    test("excel H4",
         len(datos) == DOCS and sin_url == 0 and not fantasmas
         and dup == 0 and not faltan
         and len(refs_guia) == CAMPOS_GUIA and not faltan_refs,
         "%d×%d · %d sin url · %d fantasma · %d/%d cols guía · faltan %s%s"
         % (len(datos), len(cab), sin_url, len(fantasmas), len(guia_cols),
            CAMPOS_GUIA, faltan or "-",
            (" · refs ausentes " + ",".join(faltan_refs[:3])) if faltan_refs
            else ""))


# ---------------------------------------------------------------- T6
def t6_fase4():
    fs = sorted(glob.glob(str(MEJ / "*.json"))) if MEJ.is_dir() else []
    if not fs:
        test("fase4 anti-alucinación", True, "sin datos mejorados aún",
             critico=False)
        return
    verif_ok = verif_mal = 0
    sin_verificar = 0
    for f in fs:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        base = MDB / (d.get("stem", "") + ".md")
        pags = paginas(base.read_text(encoding="utf-8", errors="replace")) \
            if base.exists() else {}
        for ref, m in (d.get("campos") or {}).items():
            if m.get("valor") in (None, "", [], {}):
                continue
            # un valor NO nulo DEBE estar verificado; si no lo está, es un
            # rechazo colado en el fichero
            if not m.get("verificado"):
                sin_verificar += 1
                continue
            # RE-VERIFICACIÓN independiente con criterio estricto
            if cita_en_pagina(m.get("cita"),
                              pags.get(int(m.get("pagina") or 0), "")):
                verif_ok += 1
            else:
                verif_mal += 1
    test("fase4 anti-alucinación",
         verif_mal == 0 and sin_verificar == 0,
         "%d ficheros · %d/%d citas re-verificadas · %d CITA FALSA · %d sin verificar"
         % (len(fs), verif_ok, verif_ok + verif_mal, verif_mal, sin_verificar))


# ---------------------------------------------------------------- T7
def t7_consistencia():
    man = json.loads((DATA / "manifest_maestro.json").read_text(encoding="utf-8"))
    k_man = {r.get("clave") for r in man.get("informes", []) if r.get("clave")}
    k_md = {Path(f).stem for f in glob.glob(str(MDB / "*.md"))}
    k_cr_md, k_cr_cl = set(), set()
    for f in glob.glob(str(CRUDO / "*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        k_cr_md.add(Path(d.get("md") or f).stem)
        k_cr_cl.add(d.get("clave") or Path(f).stem)
    ok_docs = (k_md == k_cr_md) and len(k_md) == DOCS
    ok_exp = (k_man <= k_cr_cl) and len(k_man) == CLAVES
    test("consistencia",
         ok_docs and ok_exp,
         "md↔crudo (stem): %s · manifest %d/%d claves ⊆ crudo %d: %s"
         % ("IGUAL" if ok_docs else sorted(k_md ^ k_cr_md)[:3],
            len(k_man), CLAVES, len(k_cr_cl), ok_exp))


# ---------------------------------------------------------------- T8
def t8_dobles():
    """21 expedientes con 2 documentos: marcados, jamás fusionados."""
    from collections import defaultdict
    por = defaultdict(list)
    for f in glob.glob(str(CRUDO / "*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        por[d.get("clave") or "?"].append(f)
    dobles = {k: v for k, v in por.items() if len(v) > 1}
    # el Excel debe distinguirlos: columna tipo_documento + principal
    ok_excel = False
    try:
        from openpyxl import load_workbook
        wb = load_workbook(XLSX, read_only=True)
        filas = list(wb["Informes"].iter_rows(values_only=True))
        cab = [str(x or "") for x in filas[0]]
        wb.close()
        if "tipo_documento" in cab and "principal" in cab:
            i_exp = cab.index("clave")     # NO `expediente`: el crudo se
                                           # indexa por clave y a veces difiere
            i_prin = cab.index("principal")
            # cada expediente doble tiene exactamente 1 principal
            from collections import Counter
            prin = Counter((f[i_exp], f[i_prin]) for f in filas[1:]
                           if f[i_exp] in dobles)
            por_exp = Counter(f[i_exp] for f in filas[1:]
                              if f[i_exp] in dobles)
            ok_excel = all(prin.get((e, "sí")) == 1 for e in dobles) \
                and all(por_exp[e] == len(dobles[e]) for e in dobles)
    except Exception as e:
        ok_excel = False
    test("dobles por expediente",
         len(dobles) == DOBLES and ok_excel,
         "%d/%d dobles · Excel con tipo_documento+principal: %s"
         % (len(dobles), DOBLES, "sí" if ok_excel else "NO"))


# ---------------------------------------------------------------- T9
def t9_regeneracion():
    if RAPIDO:
        return
    r = subprocess.run(
        [sys.executable, str(DB / "scripts" / "02_extraer_crudo.py"),
         "--refrescar", "--solo", "Medinaceli"],
        cwd=str(RAIZ), capture_output=True, text=True, timeout=600)
    r2 = subprocess.run(
        [sys.executable, str(DB / "scripts" / "03_exportar_excel.py")],
        cwd=str(RAIZ), capture_output=True, text=True, timeout=600)
    ok = r.returncode == 0 and r2.returncode == 0
    test("regeneración", ok, "02 exit=%d · 03 exit=%d"
         % (r.returncode, r2.returncode))
    if not ok:
        print("    " + ((r.stderr or "") + (r2.stderr or ""))[-700:])


def main():
    print("== Arnés de tests de la base de datos CIAF ==")
    t1_estructura()
    if not (MDB.is_dir() and CRUDO.is_dir()):
        print("GATE TESTS: IMPOSIBLE — faltan md_base/crudo")
        return 1
    t2_manifest()
    t3_md_base()
    t4_crudo()
    t5_excel()
    t6_fase4()
    t7_consistencia()
    t8_dobles()
    t9_regeneracion()
    print()
    total = len(fallos) + len(okey) + len(avisos)
    if fallos:
        print("GATE TESTS: FALLO — %d de %d" % (len(fallos), total))
        for f in fallos:
            print("  ✗ " + f)
        return 1
    if avisos:
        print("  · avisos (%d, no bloquean):" % len(avisos))
        for a in avisos:
            print("    " + a)
    print("GATE TESTS: OK — %d/%d tests en verde (%d avisos)"
          % (len(okey), len(okey) + len(avisos), len(avisos)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
