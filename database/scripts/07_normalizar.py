#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_normalizar.py — Base CIAF normalizada (Fase 5).

Sobre `ciaf_base_v2.xlsx` aplica la normalización que pedía David:

  · `expediente` → **NNNN/AAAA** (4 dígitos + 4 cifras de año) en TODAS las
    hojas. El literal del informe se conserva en `expediente_crudo` (solo en
    la hoja Informes) para poder trazar sin duplicar columnas en 13 hojas.
  · `tipo_suceso` canónico (8 valores, misma taxonomía que el visor) y
    `categoria_suceso` (accidente_grave · accidente · incidente · conato),
    conservando el valor literal del informe en `tipo_suceso_crudo`.
  · `titulo_normalizado` con UN solo patrón (los canceléricos "INFORME
    FINAL DE LA CIAF..." quedan como frase natural descriptiva).
  · Recomendaciones: 1 recomendación por fila con `tipo_suceso` y
    `categoria_suceso` (→ filtrables por tipo de incidente) + `rec_1..rec_3`
    en celdas separadas dentro de la hoja Informes.
  · `anio` a 4 cifras en todas partes.

Salida:
  · `entregables/03-excel-normalizado/ciaf_normalizado.xlsx`
  · `entregables/base_ciaf.json`   ← la base de datos única de todo

NUNCA inventa: si un valor no se puede clasificar con reglas deterministas se
conserva tal cual en la columna `_crudo` y la canónica queda `indeterminado`.

Uso:  python database/scripts/07_normalizar.py [--sin-entregables]
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

RAIZ = Path(__file__).resolve().parent.parent.parent
DATA = RAIZ / "database" / "data"
V2 = DATA / "ciaf_base_v2.xlsx"
SALIDA = RAIZ / "entregables" / "03-excel-normalizado" / "ciaf_normalizado.xlsx"
BASE_JSON = RAIZ / "entregables" / "base_ciaf.json"

# ---------------------------------------------------------------- taxonomía
TIPOS_CANONICOS = ("descarrilamiento", "arrollamiento", "colision",
                   "paso_a_nivel", "incendio", "fallos_senal", "otro",
                   "indeterminado")
CATEGORIAS = ("accidente_grave", "accidente", "incidente", "conato",
              "sin_categoria")


def _plano(t: str) -> str:
    """minúsculas, sin acentos, sin espacios sobrantes: la base de TODO."""
    t = unicodedata.normalize("NFKD", str(t or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", t).strip()


def normalizar_expediente(v) -> str:
    """'0038/17' · '17/2007' · '0002/010' · '0062/07' → 'NNNN/AAAA'.

    Un solo formato en todo el sistema. Si no se puede interpretar se
    devuelve tal cual (nunca se inventa un año).
    """
    s = str(v or "").strip()
    if not s:
        return ""
    m = re.fullmatch(r"\s*(\d{1,4})\s*/\s*(\d{2,4})\s*", s)
    if not m:
        # casos raros: '0002/010' → segundo grupo de 3 cifras es el año corto
        m = re.fullmatch(r"\s*(\d{1,4})\s*/\s*(\d{3})\s*", s)
        if not m:
            return s
    num = int(m.group(1))
    anio = m.group(2)
    if len(anio) == 2:
        anio = ("20" + anio) if int(anio) < 30 else ("19" + anio)
    elif len(anio) == 3:                       # '010' → año con siglo deducido
        anio = ("2" + anio) if int(anio) >= 50 else ("19" + anio[1:])
    if not anio.isdigit() or len(anio) != 4:
        return s
    return f"{num:04d}/{anio}"


def normalizar_anio(v):
    """Año siempre de 4 cifras enteras; vacío si no es interpretable."""
    if v is None or v == "":
        return ""
    s = str(v).strip()
    if s.isdigit():
        n = int(s)
        if 100 <= n <= 999:
            n = 1900 + n if n >= 50 else 2000 + n
        return n if 1900 <= n <= 2100 else ""
    m = re.search(r"\d{2,4}", s)
    if m:
        return normalizar_anio(m.group(0))
    return ""


def clasificar_tipo(texto: str) -> str:
    """Valor literal del informe → uno de los 8 tipos canónicos.

    Orden de prioridad fijo (de lo más específico a lo más genérico) para que
    el resultado sea SIEMPRE el mismo con el mismo texto.
    """
    t = _plano(texto)
    if not t or t in ("none", "nan", "sin dato", "-"):
        return "indeterminado"
    if "colision" in t or "alcance" in t:
        return "colision"
    if "descarril" in t:
        return "descarrilamiento"
    if "arrollam" in t or "atropell" in t:
        return "arrollamiento"
    if "paso a nivel" in t or "cruce de via" in t or "cruce via" in t:
        return "paso_a_nivel"
    if "incendio" in t or "humo" in t:
        return "incendio"
    if any(p in t for p in ("senal", "enclavam", "baliza", "asfa",
                            "rebase", "bloqueo")):
        return "fallos_senal"
    if "accidente" in t or "incidente" in t:
        # trae la categoría pero no el tipo de suceso: el tipo NO se inventa
        return "indeterminado"
    return "otro"


def clasificar_categoria(texto: str) -> str:
    """Categoría normativa: qué dice el informe que es (accidente/incidente)."""
    t = _plano(texto)
    if not t:
        return "sin_categoria"
    if "conato" in t:
        return "conato"
    if "accidente" in t:
        return "accidente_grave" if "grave" in t else "accidente"
    if "incidente" in t:
        return "incidente"
    return "sin_categoria"


def titulo_natural(titulo: str, contexto: dict = None) -> str:
    """Quita el preámbulo cancelérico y deja UN patrón de frase natural.

    'INFORME FINAL DE LA CIAF SOBRE EL INCIDENTE ... Nº 0046/2006 OCURRIDO EL
    12.08.2017' → 'Incidente ...' (sin nº ni fecha: ya tienen columna).
    """
    t = re.sub(r"\s{2,}", " ", str(titulo or "")).strip()
    if not t:
        # informe sin título en el Excel: se compone desde sus columnas
        c0 = contexto or {}
        partes0 = [str(c0["tipo"]).strip()] if c0.get("tipo") else []
        lugar0 = c0.get("lugar") or c0.get("estacion") or c0.get("provincia")
        if lugar0:
            partes0.append(f"en {str(lugar0).strip()}" if partes0
                           else f"En {str(lugar0).strip()}")
        if partes0 and c0.get("fecha"):
            partes0.append(f"— {c0['fecha']}")
        elif partes0 and not lugar0 and c0.get("clave"):
            partes0.append(f"({c0['clave']})")
        comp0 = " ".join(partes0).strip()
        return comp0 if len(comp0) >= 12 else ""
    if not t.upper().startswith("INFORME"):
        return t                      # ya es frase natural: no se toca
    limpio = re.sub(r"^\s*INFORME\b.*?(\d{1,4})\s*/\s*(\d{2,4})\s*,?\s*",
                    "", t, flags=re.I | re.S)
    limpio = re.sub(r"^\s*OCURRIDO\s+(?:EL\s+(?:D[ÍI]A\s+)?)?[\d./\-]{4,25}\s*,?\s*",
                    "", limpio, flags=re.I)
    # Títulos heredados que ya no llevan el nº de expediente (Fase 2): el
    # patrón de arriba no matchea, así que se quita el preámbulo de cabecera
    # con un patrón corto y explícito. NO toca el resto de la frase.
    if re.match(r"^\s*informe\b", limpio, re.I):
        limpio = re.sub(
            r"^\s*informe\s+(?:final|definitivo)(?:\s+de\s+la\s+ciaf)?(?:\s*\(i[fc]\))?"
            r"(?:\s+de\s+la\s+ciaf)?(?:\s*(?:sobre|del)\s+(?:el\s+|la\s+)?)?",
            "", limpio, flags=re.I, count=1)
        limpio = re.sub(r"^\s*(?:de\s+la\s+ciaf)?\s*", "", limpio, flags=re.I)
        limpio = re.sub(r"^\s*(?:sobre\s+)?", "", limpio, flags=re.I)
    limpio = limpio.strip(" ,;-.—")
    if len(limpio) < 12:
        # La cabecera pura (sin frase descriptiva): se compone con datos que
        # YA están en sus propias columnas (tipo, lugar, fecha) — no se
        # inventa nada nuevo. Si no hay contexto, manda el original.
        c = contexto or {}
        partes = [str(c["tipo"]).strip()] if c.get("tipo") else []
        lugar = c.get("lugar") or c.get("estacion") or c.get("provincia")
        if lugar:
            partes.append(f"en {str(lugar).strip()}" if partes
                          else f"En {str(lugar).strip()}")
        if partes and c.get("fecha"):
            partes.append(f"— {c['fecha']}")
        elif partes and not lugar and c.get("clave"):
            partes.append(f"({c['clave']})")
        compuesto = " ".join(partes).strip()
        if compuesto[:1].islower():
            compuesto = compuesto[0].upper() + compuesto[1:]
        return compuesto if len(compuesto) >= 12 else t
    limpio = re.sub(r"\s{2,}", " ", limpio)
    if limpio.isupper() or (limpio and limpio[0].islower()):
        limpio = limpio[0].upper() + limpio[1:]
    return limpio


# --------------------------------------------------------------------- main
def main() -> int:
    if not V2.exists():
        print(f"[07] falta {V2}", file=sys.stderr)
        return 1

    # La DB publicada (data/db/reports/ES.json) ES la referencia de tipo:
    # es lo que se muestra en el visor y lo que ya está auditado. El Excel se
    # alinea con ella para que las dos fuentes dejen de discrepar.
    db_path = RAIZ / "data" / "db" / "reports" / "ES.json"
    tipo_por_clave = {}
    clave_por_stem = {}
    db_por_clave = {}
    if db_path.exists():
        for reg in json.loads(db_path.read_text(encoding="utf-8")):
            k = reg.get("clave") or ""
            if k and str(reg.get("tipo") or "").strip().lower() in TIPOS_CANONICOS:
                tipo_por_clave[k] = str(reg["tipo"]).strip().lower()
            # el id de la DB es ES-<stem del pdf/md>: por ahí se recupera la
            # clave de una fila de Excel que quedó sin expediente
            clave_por_stem[reg.get("id", "").split("-", 1)[-1]] = k
            if k:
                db_por_clave[k] = {
                    "fecha": reg.get("fecha"),
                    "ubicacion": reg.get("ubicacion_nombre"),
                    "estacion": reg.get("estacion"),
                    "provincia": reg.get("provincia"),
                    "titulo": reg.get("titulo"),
                }
        print(f"[07] DB publicada: {len(tipo_por_clave)} informes de referencia")

    print("[07] abriendo ciaf_base_v2.xlsx …")
    wb = load_workbook(V2)

    # ---- 1) expediente/anio normalizados en TODAS las hojas -------------
    # En la hoja Informes se guarda además el literal previo, que luego
    # ocupa la columna `expediente_crudo` (trazabilidad sin duplicar
    # columnas en las otras 12 hojas).
    crudos_informes = {}
    clave_mala_ok = {}
    n_exp = n_anio = n_rescatadas = n_claves = 0
    for ws in wb.worksheets:
        hdr = [c.value for c in ws[1]]
        if not hdr:
            continue
        col_exp = hdr.index("expediente") + 1 if "expediente" in hdr else None
        col_anio = hdr.index("anio") + 1 if "anio" in hdr else None
        for fila in ws.iter_rows(min_row=2):
            if col_exp:
                c = fila[col_exp - 1]
                if ws.title == "Informes" and c.value:
                    crudos_informes[fila[0].row] = str(c.value)
                nuevo = normalizar_expediente(c.value)
                # fila sin expediente (informe que llegó por OCR): se rescata
                # su clave desde la DB publicada por el stem del pdf
                if ws.title == "Informes" and not nuevo and "pdf" in hdr:
                    stem = Path(str(fila[hdr.index("pdf")].value or "")).stem
                    if stem in clave_por_stem and clave_por_stem[stem]:
                        nuevo = clave_por_stem[stem]
                        n_rescatadas += 1
                if nuevo != c.value:
                    n_exp += 1
                c.value = nuevo
            # la clave sigue el mismo canon (NNNN/AAAA); si no, se deriva del
            # expediente recién normalizado, de la equivalencia aprendida en
            # la hoja Informes o del stem del pdf — nunca queda un valor de
            # colación como 'ID_230507_140907'
            if "clave" in hdr:
                kc = fila[hdr.index("clave")]
                if not re.fullmatch(r"\d{4}/\d{4}", str(kc.value or "")):
                    vieja = str(kc.value)
                    nvo = (c.value if col_exp and c.value else None)
                    if not nvo and vieja in clave_mala_ok:
                        nvo = clave_mala_ok[vieja]
                    if not nvo and "pdf" in hdr:
                        nvo = clave_por_stem.get(
                            Path(str(fila[hdr.index("pdf")].value or "")).stem)
                    if nvo:
                        kc.value = normalizar_expediente(nvo) or nvo
                        n_claves += 1
                        clave_mala_ok.setdefault(vieja, kc.value)
            if col_anio:
                c = fila[col_anio - 1]
                nuevo = normalizar_anio(c.value)
                if not nuevo:
                    # año vacío: se deriva de fecha_suceso y, si no existe,
                    # de la parte del año de la clave — nunca se inventa
                    if "fecha_suceso" in hdr:
                        m = re.search(r"(19|20)\d{2}", str(
                            fila[hdr.index("fecha_suceso")].value or ""))
                        if m:
                            nuevo = int(m.group(0))
                    if not nuevo and "clave" in hdr:
                        kc2 = str(fila[hdr.index("clave")].value or "")
                        if re.fullmatch(r"\d{4}/\d{4}", kc2):
                            nuevo = int(kc2.split("/")[1])
                if nuevo != c.value:
                    n_anio += 1
                c.value = nuevo
    print(f"[07] expediente normalizado en {n_exp} celdas · anio en {n_anio}"
          f" · claves corregidas: {n_claves} · rescatadas: {n_rescatadas}")

    # ---- 2) hoja Informes: tipo canónico + título + expediente_crudo ----
    ws = wb["Informes"]
    hdr = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(hdr) if h}
    i_clave, i_exp = idx["clave"], idx["expediente"]
    i_211, i_tsn = idx["2.1.1"], idx["titulo_normalizado"]
    i_tit, i_tsv3 = idx["titulo"], idx.get("tipo_suceso_v3", None)
    i_tsu = idx["tipo_suceso"]
    idx_lugar = idx.get("lugar", -1)
    idx_est = idx.get("estacion", -1)
    idx_prov = idx.get("provincia", -1)
    idx_fecha = idx.get("fecha_suceso", -1)
    # columnas nuevas, al final de la cabecera
    extra = ["expediente_crudo", "categoria_suceso", "tipo_suceso_crudo"]
    for h in extra:
        if h not in idx:
            idx[h] = len(hdr)
            hdr.append(h)
    for col, val in zip((idx["expediente_crudo"], idx["categoria_suceso"],
                         idx["tipo_suceso_crudo"]), extra):
        ws.cell(row=1, column=col + 1).value = val
        ws.cell(row=1, column=col + 1).font = Font(bold=True)

    stats_tipo, stats_cat, t_titulo = Counter(), Counter(), 0
    n_completadas = 0
    datos_por_clave = {}          # clave → fila (para cruzar recomendaciones)
    for fila in ws.iter_rows(min_row=2, max_col=len(hdr)):
        c = fila[i_exp]
        crudo = crudos_informes.get(fila[0].row, c.value)
        ws.cell(row=fila[0].row, column=idx["expediente_crudo"] + 1).value = crudo
        clave = fila[i_clave].value
        # clave canónica: si la del Excel no encaja con NNNN/AAAA (p. ej. es
        # el nombre del pdf de un informe rescatado) se deriva del expediente
        if not re.fullmatch(r"\d{4}/\d{4}", str(clave or "")):
            clave = fila[i_exp].value or clave
            fila[i_clave].value = clave

        # tipo: manda el ya canónico (v3/CIAF); si está vacío se deriva
        actual = fila[i_tsu].value
        canonico = str(actual or "").strip().lower()
        if canonico not in TIPOS_CANONICOS:
            canonico = clasificar_tipo(fila[i_211].value) if fila[i_211].value else "indeterminado"
        # manda la DB publicada (mismo valor que el visor); si ese expediente
        # no tiene entrada se conserva el derivado del propio Excel
        canonico = tipo_por_clave.get(clave, canonico)
        if canonico not in TIPOS_CANONICOS:
            canonico = "indeterminado"
        fila[i_tsu].value = canonico
        stats_tipo[canonico] += 1
        ws.cell(row=fila[0].row, column=idx["tipo_suceso_crudo"] + 1).value = (
            fila[i_211].value or actual or "")

        # categoría: 2.1.1 primero, si no el título crudo
        cat = clasificar_categoria(fila[i_211].value) \
            if fila[i_211].value else "sin_categoria"
        if cat == "sin_categoria":
            cat = clasificar_categoria(fila[i_tit].value)
        ws.cell(row=fila[0].row, column=idx["categoria_suceso"] + 1).value = cat
        stats_cat[cat] += 1

        # completar desde la DB publicada lo que el Excel dejó vacío (los
        # dos informes que llegaron tarde: El Carrión y el del OCR)
        d = db_por_clave.get(clave)
        if d:
            # lugar: estación y provincia (topónimos), nunca el resumen en
            # inglés que usa la geolocalización
            ci = idx.get("lugar", -1)
            if ci >= 0 and not fila[ci].value:
                top = d.get("estacion") or d.get("provincia")
                if top and d.get("provincia") and d.get("estacion"):
                    top = f"{d['estacion']} ({d['provincia']})"
                if top:
                    fila[ci].value = top
                    n_completadas += 1
            for col, campo in (("fecha_suceso", "fecha"),
                               ("estacion", "estacion"),
                               ("provincia", "provincia")):
                ci = idx.get(col, -1)
                if ci >= 0 and not fila[ci].value and d.get(campo):
                    fila[ci].value = d[campo]
                    n_completadas += 1
            # título: si el Excel no lo tiene, se usa el de la DB (frase
            # natural en castellano) antes que componer uno
            if not fila[i_tsn].value and d.get("titulo"):
                fila[i_tsn].value = d["titulo"]
                n_completadas += 1

        # título con UN solo patrón: si el normalizado heredado todavía es
        # el cancelérico de cabecera, se deja frase natural descriptiva
        actual_tit = fila[i_tsn].value
        # si el Excel ya tiene título (o la DB acabó de ponerlo) manda ese;
        # solo se parte del crudo cuando la celda está vacía
        base_tit = actual_tit if str(actual_tit or "").strip() \
            else fila[i_tit].value
        nuevo_tit = titulo_natural(base_tit, {
            "tipo": fila[i_tsu].value,
            "lugar": fila[idx_lugar].value if idx_lugar >= 0 else None,
            "estacion": fila[idx_est].value if idx_est >= 0 else None,
            "provincia": fila[idx_prov].value if idx_prov >= 0 else None,
            "fecha": fila[idx_fecha].value if idx_fecha >= 0 else None,
            "clave": clave,
        })
        if nuevo_tit and nuevo_tit != actual_tit:
            fila[i_tsn].value = nuevo_tit
            t_titulo += 1

        if clave:
            datos_por_clave[clave] = {
                "expediente": fila[i_exp].value,
                "tipo_suceso": canonico,
                "categoria_suceso": cat,
                "titulo_normalizado": fila[i_tsn].value,
            }
    print(f"[07] tipo_suceso → {dict(stats_tipo)}")
    print(f"[07] categoria_suceso → {dict(stats_cat)} · títulos reescritos: {t_titulo}"
          f" · campos completados desde la DB: {n_completadas}")

    # ---- 3) Recomendaciones: tipo de suceso + cruce por clave ----------
    wr = wb["Recomendaciones"]
    hr = [c.value for c in wr[1]]
    iex2 = hr.index("expediente")
    col_tipo = len(hr)
    for h, off in (("tipo_suceso", 0), ("categoria_suceso", 1)):
        if h not in hr:
            hr.append(h)
            wr.cell(row=1, column=col_tipo + 1 + off).value = h
            wr.cell(row=1, column=col_tipo + 1 + off).font = Font(bold=True)
    it_tipo = hr.index("tipo_suceso")
    it_cat = hr.index("categoria_suceso")
    it_clave = hr.index("clave")
    recs_por_clave = defaultdict(list)
    n_rec_cruzadas = 0
    for fila in wr.iter_rows(min_row=2, max_col=len(hr)):
        fila[iex2].value = normalizar_expediente(fila[iex2].value)
        clave = fila[it_clave].value
        d = datos_por_clave.get(clave) or {}
        wsx = wr
        wsx.cell(row=fila[0].row, column=it_tipo + 1).value = d.get("tipo_suceso", "")
        wsx.cell(row=fila[0].row, column=it_cat + 1).value = d.get("categoria_suceso", "")
        if d:
            n_rec_cruzadas += 1
        recs_por_clave[clave].append({
            "numero": fila[hr.index("numero")].value,
            "destinatario": fila[hr.index("destinatario")].value,
            "implementador": fila[hr.index("implementador")].value,
            "texto": fila[hr.index("texto")].value,
            "pagina": fila[hr.index("pagina")].value,
            "tipo_suceso": d.get("tipo_suceso", ""),
            "categoria_suceso": d.get("categoria_suceso", ""),
        })
    print(f"[07] recomendaciones: {sum(len(v) for v in recs_por_clave.values())} "
          f"cruzadas por tipo en {n_rec_cruzadas} filas")

    # ---- 4) Informes: rec_1..rec_3 en celdas separadas -----------------
    n_rec_cols = 3
    for k in range(1, n_rec_cols + 1):
        h = f"rec_{k}"
        if h not in idx:
            idx[h] = len(hdr)
            hdr.append(h)
            ws.cell(row=1, column=idx[h] + 1).value = h
            ws.cell(row=1, column=idx[h] + 1).font = Font(bold=True)
    i_nrec = idx["n_recomendaciones"]
    for fila in ws.iter_rows(min_row=2, max_col=len(hdr)):
        clave = fila[i_clave].value
        recs = recs_por_clave.get(clave) or []
        fila[i_nrec].value = len(recs) if recs else (fila[i_nrec].value or 0)
        for k in range(n_rec_cols):
            ws.cell(row=fila[0].row, column=idx[f"rec_{k + 1}"] + 1).value = (
                recs[k]["texto"] if k < len(recs) else "")
    # cabecera final (por si se añadieron columnas nuevas)
    for i, h in enumerate(hdr, start=1):
        if ws.cell(row=1, column=i).value != h:
            ws.cell(row=1, column=i).value = h

    # ---- 5) escritura ---------------------------------------------------
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    print(f"[07] escribiendo {SALIDA.relative_to(RAIZ)} …")
    wb.save(SALIDA)

    # ---- 6) base de datos única (JSON canónico) -------------------------
    if "--sin-entregables" not in sys.argv:
        base = {
            "descripcion": "Base CIAF única — todos los informes, con claves, "
                           "años y tipos de suceso normalizados.",
            "normalizacion": {
                "clave": "NNNN/AAAA (4 dígitos + 4 cifras de año)",
                "tipo_suceso": list(TIPOS_CANONICOS),
                "categoria_suceso": list(CATEGORIAS),
                "n_informes": len(datos_por_clave),
                "n_recomendaciones": sum(len(v) for v in recs_por_clave.values()),
            },
            "informes": [
                dict(d, clave=clave,
                     recomendaciones=recs_por_clave.get(clave, []))
                for clave, d in sorted(datos_por_clave.items())
            ],
        }
        BASE_JSON.parent.mkdir(parents=True, exist_ok=True)
        BASE_JSON.write_text(json.dumps(base, ensure_ascii=False,
                                        separators=(",", ":")),
                             encoding="utf-8")
        print(f"[07] {BASE_JSON.relative_to(RAIZ)} — "
              f"{len(base['informes'])} informes, "
              f"{base['normalizacion']['n_recomendaciones']} recomendaciones")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
