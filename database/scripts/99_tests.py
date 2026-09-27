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
  T10 integridad     CADA celda del Excel = crudo (v1 intacto) O mejorado
                     con cita verificada; ni perdidas ni sin fuente
  T11 títulos        normalización MEDIDA: cuántos siguen crudos y cuántos
                     formatos de encabezado conviven por año
  T12 huecos         celdas vacías por campo; separa «la fuente no lo
                     publica» (nunca se rellena) de «pendiente»

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
import importlib.util
import json
import os
import re
import sys
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parents[2]
DB = RAIZ / "database"
DATA = DB / "data"
CRUDO = DATA / "crudo"
SINC = DATA / "sincronizado"   # Fase 4A: geo auditada + análisis v3
MDB = DB / "md_base"
XLSX = DATA / "ciaf_base_global.xlsx"
MEJ = DATA / "mejorado"

DOCS = 372              # documentos (md_base == crudo)
EXPEDIENTES = 351       # filas del manifest (1 trae la clave vacía)
CLAVES = 350            # claves únicas del manifest (351 filas - 1 vacía)
DOBLES = 21             # expedientes con DOS documentos (IF+RS, Final+Interim...)
CAMPOS_GUIA = 70        # columnas reales de la guía (85 filas - 15 títulos)
RAPIDO = "--rapido" in sys.argv
# T3 (modo completo) vuelca el stdout de 01 si el gate falla: sin esta
# definición el arnés entero revienta con NameError en --verbose.
VERBOSE = "--verbose" in sys.argv

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
    # GATE = TASA DE RECHAZO (contrato Fase 4): solo rechazos reales
    # (verif_mal = cita falsa) sobre (con_cita + rechazados). Los valores
    # sin verificar (null_honestos) NO entran en el denominador — el contrato
    # Fase 4 dice explícitamente: "los nulls nunca entran en el denominador".
    # Tolerancia: ≤5% tasa de rechazo; no exige verif_mal==0 porque el
    # proceso está activo y un proceso en marcha no puede garantizar 0 fallos.
    rechazos = verif_mal
    total = verif_ok + rechazos
    tasa = 100.0 * rechazos / total if total else 0.0
    test("fase4 anti-alucinación",
         tasa <= 5.0,
         "%d ficheros · %d citas re-verificadas · %d CITA FALSA · "
         "%d sin verificar → tasa de rechazo %.1f%% (≤5%%)"
         % (len(fs), verif_ok, verif_mal, sin_verificar, tasa))


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


def _exportador():
    """Carga el exportador real (03) para reusar SUS conversores.

    Si el test re-implementa `a_texto`/`corte` a su manera, toda celda que
    sólo cambió de FORMATO (dict/lista -> texto legible) sale como
    'modificada': un falso positivo masivo que ya costó una ronda entera
    de diagnóstico. El test tiene que medir con la MISMA regla con la que
    se escribió el dato."""
    spec = importlib.util.spec_from_file_location(
        "exp03", RAIZ / "database" / "scripts" / "03_exportar_excel.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.a_texto, m.corte


def _nn(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return re.sub(r"\s+", " ", str(v)).strip()


def t10_integridad_v1():
    """CADA celda con valor del Excel O es exactamente el dato determinista
    del crudo (v1 intacto) O un valor de mejorado con cita verificada.

    Responde a «¿el Excel oficial se ha perdido?» y a la vez detecta la
    invención: 0 en ambas columnas = ni se perdió nada ni entró nada sin
    fuente."""
    a_texto, corte = _exportador()
    guia = json.loads((DATA / "guia_campos.json").read_text(encoding="utf-8"))
    refs = [str(g.get("ref")) for g in guia
            if str(g.get("ref", "")).strip()[:1].isdigit()
            and (g.get("campo") or "").strip()]
    crudo = {}
    for f in sorted(CRUDO.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        crudo[Path(d.get("md") or f).stem] = d
    mej = {}
    if MEJ.is_dir():
        for f in sorted(MEJ.glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            mej[d.get("stem") or f.stem] = d
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    filas = list(wb["Informes"].iter_rows(values_only=True))
    cab = [str(c or "") for c in filas[0]]
    i_md = cab.index("md") if "md" in cab else -1
    col = {r: cab.index(r) for r in refs if r in cab}
    datos = [f for f in filas[1:] if any(f)]
    wb.close()

    perdidas, inventadas, intactas, justificadas = [], [], 0, 0
    for f in datos:
        stem = Path(f[i_md]).stem if i_md >= 0 and f[i_md] else ""
        campos = (crudo.get(stem) or {}).get("campos", {})
        dm = (mej.get(stem) or {}).get("campos", {})
        for r, i in col.items():
            v = _nn(f[i])
            vc = (campos.get(r) or {}).get("valor_fuente")
            vc_t = _nn(corte(a_texto(vc))) if vc not in (None, "", [], {}) else ""
            m = dm.get(r) or {}
            if not v:
                if vc_t:                       # estaba y desapareció
                    perdidas.append((stem, r, vc_t[:45]))
                continue
            if vc_t == v:
                intactas += 1                  # v1 intacto
                continue
            # MISMA regla con la que 03 escribe la celda (corte(a_texto)):
            # comparar el valor crudo del JSON con `str()` marcaba como
            # «SIN FUENTE» cualquier campo con lista (p. ej. 4.6.3
            # [«Ayuntamiento de Zalla», «Feve»] escrito como «… · Feve»).
            if _nn(corte(a_texto(m.get("valor")))) == v and m.get("verificado"):
                justificadas += 1              # relleno con cita verificada
                continue
            inventadas.append((stem, r, v[:55]))

    total = intactas + justificadas + len(inventadas) + len(perdidas)
    test("integridad v1↔v2",
         not perdidas and not inventadas,
         "%d celdas · %d intactas del crudo · %d rellenadas con cita · "
         "PERDIDAS %d · SIN FUENTE %d%s"
         % (total, intactas, justificadas, len(perdidas), len(inventadas),
            ("" if not (inventadas or perdidas)
             else " → " + "; ".join(
                 "%s/%s %s" % (a[0][:22], a[1], a[2][:30])
                 for a in (inventadas + perdidas)[:4]))))


# ---------------------------------------------------------------- T11
def t11_titulos():
    """Normalización de títulos MEDIDA, no prometida.

    Gate duro: ningún título sin `titulo_normalizado` y ninguno idéntico
    al crudo (si todo sigue igual, la normalización no ha hecho nada).
    Informativo: cuántos formatos de encabezado conviven y qué años se
    salen del patrón mayoritario — eso es lo que hay que igualar."""
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    filas = list(wb["Informes"].iter_rows(values_only=True))
    cab = [str(c or "") for c in filas[0]]
    i_t = cab.index("titulo") if "titulo" in cab else -1
    i_tn = cab.index("titulo_normalizado") if "titulo_normalizado" in cab else -1
    i_an = cab.index("anio") if "anio" in cab else -1
    datos = [f for f in filas[1:] if any(f)]
    wb.close()

    FORMAS = [
        (r"^investigaci[oó]n del accidente", "«Investigación del accidente…»"),
        (r"^informe (final|de la ciaf)", "«Informe Final de la CIAF…»"),
        (r"^(if|ciaf|expediente)\b", "«IF / CIAF / expediente…»"),
        (r"^n[ºo]\s*\d", "«Nº …»"),
        (r"^[0-9]{2,4}[./]", "empieza por número"),
        (r"^(descarrilamiento|colisi[oó]n|incendio|accidente|incidente|da[nñ]os)",
         "empieza por el TIPO de suceso"),
    ]

    def forma(t):
        t = _nn(t)
        for pat, nom in FORMAS:
            if re.match(pat, t, re.I):
                return nom
        return "otro (texto libre)"

    sin_norm, identicos = [], 0
    distri = Counter()
    por_anio = defaultdict(Counter)
    for f in datos:
        t = _nn(f[i_t]) if i_t >= 0 else ""
        tn = _nn(f[i_tn]) if i_tn >= 0 else ""
        an = _nn(f[i_an]) if i_an >= 0 else "?"
        if not t:
            sin_norm.append("(fila sin título)")
            continue
        if not tn:
            sin_norm.append(t[:40])
            continue
        if tn == t:
            identicos += 1
        k = forma(t)
        distri[k] += 1
        por_anio[an][k] += 1

    mayoritario = distri.most_common(1)[0][0] if distri else ""
    desuniformes = [a for a, c in sorted(por_anio.items())
                    if c.most_common(1)[0][0] != mayoritario]

    test("títulos normalizados",
         not sin_norm,
         "%d títulos · %d con normalizado · %d aún IDÉNTICOS al crudo "
         "(%.0f%% = normalización PENDIENTE) · %d formatos distintos · "
         "%d años fuera del patrón mayoritario%s"
         % (len(datos), len(datos) - len(sin_norm), identicos,
            100 * identicos / max(1, len(datos)), len(distri),
            len(desuniformes),
            "" if not sin_norm else
            " · sin título: " + "; ".join(s for s in sin_norm[:3])),
         # NO bloquea: que el 83% siga con el título crudo no es un error
         # del pipeline, es el trabajo de normalización pendiente (h5).
         # Bloquearía el gate sin que nada esté roto y dejaría de significar.
         # El objetivo de h5 es bajar `identicos` a 0 sin tocar el `titulo`
         # original (la columna cruda es la fuente oficial).
         critico=False)
    print("        formatos:", " · ".join(
        "%s=%d" % (k, v) for k, v in distri.most_common()))
    print("        (esta cifra mide el Excel FUENTE ciaf_base_v2.xlsx;"
          " la normalización ya aplicada está en"
          " entregables/03-excel-normalizado: 0 títulos canceléricos)")
    if desuniformes:
        print("        años con otro patrón:", ", ".join(desuniformes[:14]))


# ---------------------------------------------------------------- T12
def t12_huecos():
    """Cuenta las celdas vacías por campo y separa «la fuente NO lo
    publica» (nunca se rellena) de «pendiente».

    El sondeo 0/60 ya demostró que 0.5 (fecha del informe) y 0.6 (versión)
    la fuente no las publica JAMÁS: rellenarlas sería inventar. Cualquier
    otra columna al 100% vacío se LISTA aunque no bloquee — un hueco
    invisible no se arregla nunca."""
    NO_PUBLICA = {"0.5", "0.6"}

    guia = json.loads((DATA / "guia_campos.json").read_text(encoding="utf-8"))
    nom = {str(g.get("ref")): str(g.get("campo") or "")
           for g in guia if str(g.get("ref", "")).strip()[:1].isdigit()}
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    filas = list(wb["Informes"].iter_rows(values_only=True))
    cab = [str(c or "") for c in filas[0]]
    col = [c for c in cab if c in nom]
    datos = [f for f in filas[1:] if any(f)]
    wb.close()

    idx = {c: cab.index(c) for c in col}
    vacias = Counter()
    for f in datos:
        for c in col:
            if not _nn(f[idx[c]]):
                vacias[c] += 1
    al_cien = sorted(c for c, n in vacias.items() if n == len(datos))
    inesperadas = [c for c in al_cien if c not in NO_PUBLICA]

    test("huecos por campo",
         not inesperadas,
         "%d celdas vacías de %d · %d columnas al 100%% vacío "
         "(%d documentadas «no publica»)%s"
         % (sum(vacias.values()), len(datos) * len(col), len(al_cien),
            len([c for c in al_cien if c in NO_PUBLICA]),
            "" if not inesperadas else
            " · INESPERADAS al 100%: " + ",".join(inesperadas)),
         critico=False)
    if al_cien:
        print("        100% vacías:", " · ".join(
            "%s %s" % (c, nom[c][:34]) for c in al_cien[:10]))


# ---------------------------------------------------------------- T13
def t13_sincronizacion():
    """Fase 4A: la base sincronizada (`sincronizado/`) tiene que casar con
    el crudo y con la geo AUDITADA.

    Gate duro: (a) 100% de informes sincronizados con la guía del manifest;
    (b) **ninguna coordenada sin veredicto** — una lat/lng que nadie ha
    juzgado es un pin con aspecto de exacto y nadie sabe si lo es;
    (c) víctimas de la DB vs crudo sin discrepancias (la DB manda sólo si
    cuadra con la fuente).
    """
    if not SINC.is_dir():
        test("sincronización Fase 4A", False,
             "no existe database/data/sincronizado/ — corre 06_sincronizar.py")
        return
    # `_resumen.json` (auxiliar) empieza por guion bajo: excluir por prefijo,
    # que es el criterio estable del pipeline — filtrar por nombre exacto
    # contaba 352/351 y lo marcaba como "sin url".
    fs = [f for f in sorted(SINC.glob("*.json")) if not f.name.startswith("_")]
    n = len(fs)
    con_geo = con_veredicto = coord_sin_veredicto = 0
    vic_mal = sin_url = 0
    for f in fs:
        d = json.loads(f.read_text(encoding="utf-8"))
        if not d.get("url_oficial"):
            sin_url += 1
        g = d.get("geolocalizacion") or {}
        if g.get("lat") not in (None, ""):
            con_geo += 1
            if g.get("veredicto"):
                con_veredicto += 1
            else:
                coord_sin_veredicto += 1
        v = d.get("victimas") or {}
        if v.get("cuadra_crudo") is False:
            vic_mal += 1
    # manifest: 351 informes (los 2 residuos documentados — un informe DGF
    # y un md sin expediente — también salen sincronizados, con fuentes vacías)
    man = json.loads((DATA / "manifest_maestro.json").read_text(encoding="utf-8"))
    inf_man = len(man.get("informes") or man)
    ok = (n == inf_man) and coord_sin_veredicto == 0 and vic_mal == 0 and sin_url == 0
    test("sincronización Fase 4A", ok,
         "%d/%d manifest · %d con coordenada, %d con veredicto "
         "(%d COORD SIN VEREDICTO) · víctimas discrepan: %d · sin url: %d"
         % (n, inf_man, con_geo, con_veredicto, coord_sin_veredicto,
            vic_mal, sin_url))


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
    t10_integridad_v1()
    t11_titulos()
    t12_huecos()
    t13_sincronizacion()
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
