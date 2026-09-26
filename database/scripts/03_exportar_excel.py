#!/usr/bin/env python3
"""
03_exportar_excel.py — Fase 3: la BASE DE DATOS GLOBAL en un único Excel.

Contrato:
  • 1 fila = 1 informe, en la hoja `Informes`.
  • CADA dato de la guía CIAF en SU propia columna (85 refs: 0.1 … 4.6.3),
    más las columnas de identificación y las analíticas derivadas.
  • `url_oficial` NUNCA vacío (obligatorio de proyecto).
  • Hojas 1-a-N desnormalizadas, enlazadas por `clave` (expediente) y con
    su `url_oficial` en cada fila: Recomendaciones, Entidades, Cronología,
    Trenes, Personal, Causas.
  • Hojas de control: Diccionario (los 85 campos) y Cobertura (% por campo).

Fuente única: database/data/crudo/*.json (Fase 2). El Excel es una EXPORT
regenerable — nada se calcula aquí que no esté ya en el crudo.

Uso: py 03_exportar_excel.py [--solo STEM]
"""

import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[2]
CRUDO = RAIZ / "database" / "data" / "crudo"
DATA = RAIZ / "database" / "data"
SALIDA = DATA / "ciaf_base_global.xlsx"

MAX_CELDA = 32000  # límite real de Excel por celda
CAB_FONDO = PatternFill("solid", fgColor="DBEAFE")   # azul suave, monocromo
CAB_LETRA = Font(bold=True, color="1E3A8A", size=10)
TITULO = Font(bold=True, size=11, color="111827")

# columnas analíticas de cabecera (siempre presentes, ordenadas primero)
IDENT = ["clave", "expediente", "anio", "titulo", "url_oficial", "pdf", "md",
         "paginas", "estado_cobertura", "campos_con_valor", "campos_con_cita",
         "cobertura_pct"]

DERIV = ["fecha_suceso", "anio_suceso", "hora_suceso", "tipo_suceso",
         "lugar", "estacion", "pk", "linea", "provincia", "municipio",
         "fallecidos", "heridos_graves", "heridos_leves", "victimas_total",
         "entidades", "causa_directa", "n_recomendaciones", "n_cronologia",
         "n_trenes"]

# claves preferentes para volcar listas de dicts de forma legible
CLAVES_TEXTO = ("texto", "evento", "nombre", "rol", "implicacion",
                "descripcion", "destinatario")


# ------------------------------------------------------------------ utilidades
def a_texto(v):
    """Cualquier valor del crudo → texto de celda legible y no vacío."""
    if v is None or v == "" or v == [] or v == {}:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, list):
        if all(isinstance(x, str) for x in v):
            return " · ".join(x for x in v if x)
        # lista de dicts: volcar la clave de contenido, si todos la comparten
        if all(isinstance(x, dict) for x in v):
            for k in CLAVES_TEXTO:
                if all(k in x and x[k] not in (None, "") for x in v):
                    return " · ".join(str(x[k]) for x in v)
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    if isinstance(v, dict):
        partes = []
        for k, val in v.items():
            if val in (None, "", [], {}):
                continue
            if isinstance(val, (dict, list)):
                partes.append(f"{k}: {json.dumps(val, ensure_ascii=False)}")
            else:
                partes.append(f"{k}: {val}")
        return " · ".join(partes) or ""
    return str(v)


def corte(txt):
    if isinstance(txt, str) and len(txt) > MAX_CELDA:
        return txt[:MAX_CELDA - 24] + " …[TRUNCADO POR EXCEL]"
    return txt


def primero(*vals):
    for v in vals:
        if v not in (None, "", [], {}):
            return v
    return ""


def get(campo, *rutas):
    """Lee partes del dict de un campo: get(campo, 'provincia')."""
    v = campo.get("valor_fuente") if isinstance(campo, dict) else None
    for r in rutas:
        if isinstance(v, dict):
            v = v.get(r)
        else:
            return None
    return v


def cargar():
    # guia_campos.json se guarda como LISTA (orden de la guía); aquí necesitamos
    # acceso por ref → dict indexado. Los valores conservan su orden original
    # porque Python 3.7+ respeta el de inserción.
    guia_lista = json.loads((DATA / "guia_campos.json").read_text(encoding="utf-8"))
    # La tabla de la guía mezcla TÍTULOS de bloque ("0. DATOS DE CONTROL DEL
    # INFORME", campo vacío) con los campos reales (ref numérica). Los títulos
    # se usan para rellenar el `bloque` de lo que viene detrás; NO deben ser
    # columna del Excel.
    guia = {}
    bloque = ""
    for c in guia_lista:
        ref = str(c.get("ref", "")).strip()
        # TÍTULO de bloque = ref no numérica (raro) O ref con `campo` vacío
        # ("0. DATOS DE CONTROL DEL INFORME", "1. RESUMEN", "4.6 RECOMENDACIONES").
        # Sin este filtro entran como columna del Excel con el nombre del bloque.
        if not ref or not ref[0].isdigit() or not (c.get("campo") or "").strip():
            if ref:
                bloque = ref
            continue
        item = dict(c)
        item["campo"] = item.get("campo", "") or item.get("nombre", "")
        item["nombre"] = item["campo"]     # alias: así lo leen las reglas
        item["bloque"] = bloque
        guia[ref] = item
    bases_lista = json.loads((DATA / "guia_bases.json").read_text(encoding="utf-8"))
    # lista de listas: fila 0 = cabecera (Código | Documento / base | Uso)
    bases = {f[0]: (f[1] if len(f) > 1 else "", f[2] if len(f) > 2 else "")
             for f in bases_lista[1:] if f and isinstance(f[0], str)}
    man = json.loads((DATA / "manifest_maestro.json").read_text(encoding="utf-8"))
    por_clave = {r["clave"]: r for r in man["informes"]}
    docs = []
    for f in sorted(CRUDO.glob("*.json")):
        docs.append(json.loads(f.read_text(encoding="utf-8")))
    return guia, bases, por_clave, docs


# --------------------------------------------------------------------- hojas
def filas_informes(guia, por_clave, docs):
    """Una fila por informe: identificación + 85 columnas de guía + derivadas."""
    refs = list(guia)
    filas = []
    for d in docs:
        campos = d.get("campos", {})
        reg = por_clave.get(d.get("clave", ""), {}) or \
              por_clave.get(d.get("id", ""), {}) or {}
        clave = d.get("clave") or reg.get("clave") or d.get("id", "")

        fila = {
            "clave": clave,
            "expediente": d.get("expediente") or reg.get("expediente") or "",
            "anio": reg.get("anio") or "",
            "titulo": d.get("titulo") or reg.get("titulo") or "",
            "url_oficial": d.get("url_oficial") or reg.get("url_oficial") or "",
            "pdf": d.get("pdf", ""),
            "md": d.get("md", ""),
            "paginas": d.get("paginas_md", ""),
            "estado_cobertura": reg.get("estado", ""),
        }
        con_valor = con_cita = 0
        for ref in refs:
            c = campos.get(ref, {})
            val = c.get("valor_fuente")
            if val not in (None, "", [], {}):
                con_valor += 1
                if c.get("pagina"):
                    con_cita += 1
            fila[ref] = corte(a_texto(val))
        fila["campos_con_valor"] = con_valor
        fila["campos_con_cita"] = con_cita
        fila["cobertura_pct"] = round(100 * con_cita / max(1, con_valor), 1) \
            if con_valor else 0

        # ---- derivadas analíticas (del propio crudo, nunca inventadas)
        lugar = campos.get("2.1.3.C", {})
        vic = campos.get("2.3.1.A", {})
        vic_v = vic.get("valor_fuente") if isinstance(vic.get("valor_fuente"), dict) else {}
        geo = campos.get("2.4.2", {})
        geo_v = geo.get("valor_fuente") if isinstance(geo.get("valor_fuente"), dict) else {}
        fecha = campos.get("2.1.3.A", {}).get("valor_fuente")
        fila["fecha_suceso"] = a_texto(fecha) if not isinstance(fecha, dict) \
            else a_texto(fecha.get("fecha") or fecha)
        anio = fila["fecha_suceso"]
        fila["anio_suceso"] = str(anio)[:4] if str(anio)[:4].isdigit() else \
            (reg.get("anio") or "")
        fila["hora_suceso"] = a_texto(
            primero(campos.get("2.1.3.B", {}).get("valor_fuente"),
                    get(campos.get("2.1.3.A", {}), "hora")))
        fila["tipo_suceso"] = a_texto(campos.get("2.1.1", {}).get("valor_fuente"))
        fila["lugar"] = a_texto(primero(get(lugar, "descripcion_lugar"),
                                        get(lugar, "tipo"), lugar.get("valor_fuente")))
        fila["estacion"] = a_texto(primero(get(lugar, "estacion"),
                                           get(lugar, "estacion_nombre"),
                                           geo_v.get("estacion")))
        fila["pk"] = a_texto(primero(get(lugar, "pk"), get(lugar, "punto_kilometrico")))
        fila["linea"] = a_texto(primero(get(lugar, "linea"),
                                        campos.get("2.1.4", {}).get("valor_fuente")))
        fila["provincia"] = a_texto(primero(get(lugar, "provincia"), geo_v.get("provincia")))
        fila["municipio"] = a_texto(primero(get(lugar, "municipio"),
                                            geo_v.get("municipio")))
        fila["fallecidos"] = vic_v.get("fallecidos", "")
        fila["heridos_graves"] = vic_v.get("heridos_graves", "")
        fila["heridos_leves"] = vic_v.get("heridos_leves", "")
        try:
            fila["victimas_total"] = sum(int(x or 0) for x in
                                         (fila["fallecidos"], fila["heridos_graves"],
                                          fila["heridos_leves"])
                                         if str(x).strip() != "")
        except (TypeError, ValueError):
            fila["victimas_total"] = ""
        fila["entidades"] = a_texto(campos.get("2.1.2", {}).get("valor_fuente"))
        causas = campos.get("1.4", {}).get("valor_fuente")
        fila["causa_directa"] = a_texto(causas if isinstance(causas, str)
                                        else get(campos.get("1.4", {}), "directa"))
        for k, ref in (("n_recomendaciones", "4.6.1"),
                       ("n_cronologia", "2.1.6"),
                       ("n_trenes", "2.2.2")):
            v = campos.get(ref, {}).get("valor_fuente")
            fila[k] = len(v) if isinstance(v, list) else ""
        filas.append(fila)
    return refs, filas


def hoja_recomendaciones(docs):
    """1 fila por recomendación, con nº/destinatario/implementador/texto."""
    filas = []
    for d in docs:
        campos = d.get("campos", {})
        base = {"clave": d.get("clave", ""), "url_oficial": d.get("url_oficial", ""),
                "expediente": d.get("expediente", ""), "titulo": d.get("titulo", "")}
        # 1ª fuente: la TABLA convertida en la Fase 1 (determinista, con página)
        for t in d.get("tablas") or []:
            cab = [str(c).strip().lower() for c in (t.get("cabecera") or [])]
            if not any("recomendaci" in c or "recommendation" in c for c in cab):
                continue
            for i, fr in enumerate(t.get("filas") or [], 1):
                if not isinstance(fr, dict) or not any(str(x).strip() for x in fr.values()):
                    continue
                filas.append({**base,
                              "numero": a_texto(fr.get("Número") or fr.get("Number")
                                               or fr.get("Número de recomendación") or ""),
                              "destinatario": a_texto(fr.get("Destinatario")
                                                      or fr.get("Destinatario final")
                                                      or fr.get("Destinatarios")
                                                      or fr.get("Addressee") or ""),
                              "implementador": a_texto(fr.get("Implementador final")
                                                       or fr.get("Implementador")
                                                       or fr.get("Final Implementer") or ""),
                              "texto": a_texto(fr.get("Recomendación")
                                               or fr.get("Recomendaciones")
                                               or fr.get("Recommendation") or ""),
                              "pagina": t.get("pagina", ""),
                              "origen": "tabla_determinista"})
        # 2ª fuente: análisis v3 (solo si la tabla no aportó nada para este informe)
        if not any(f["clave"] == base["clave"] and f["origen"] == "tabla_determinista"
                   for f in filas[-200:]):
            v3 = campos.get("4.6.1", {}).get("valor_fuente")
            if isinstance(v3, list):
                for r in v3:
                    if isinstance(r, dict):
                        filas.append({**base,
                                      "numero": a_texto(r.get("numero") or r.get("n")),
                                      "destinatario": a_texto(r.get("destinatario")
                                                              or r.get("destinatarios")),
                                      "implementador": a_texto(r.get("implementador")),
                                      "texto": a_texto(r.get("texto")
                                                       or r.get("descripcion")
                                                       or r.get("recomendacion")),
                                      "pagina": campos.get("4.6.1", {}).get("pagina", ""),
                                      "origen": "analisis_v3"})
                    else:
                        filas.append({**base, "numero": "", "destinatario": "",
                                      "implementador": "", "texto": a_texto(r),
                                      "pagina": campos.get("4.6.1", {}).get("pagina", ""),
                                      "origen": "analisis_v3"})
    return filas


def hoja_lista_simple(docs, ref, campo, valor="entidad"):
    """Entidades / otros listados simples → 1 fila por elemento."""
    filas = []
    for d in docs:
        campos = d.get("campos", {})
        v = campos.get(ref, {}).get("valor_fuente")
        if not isinstance(v, list):
            continue
        for x in v:
            if x in (None, "", {}, []):
                continue
            filas.append({"clave": d.get("clave", ""),
                          "url_oficial": d.get("url_oficial", ""),
                          "expediente": d.get("expediente", ""),
                          campo: a_texto(x)})
    return filas


def hoja_cronologia(docs):
    filas = []
    for d in docs:
        campos = d.get("campos", {})
        v = campos.get("_cronologia", {}).get("valor_fuente")
        if not isinstance(v, list):
            continue
        for x in v:
            if isinstance(x, dict) and any(x.values()):
                filas.append({"clave": d.get("clave", ""),
                              "url_oficial": d.get("url_oficial", ""),
                              "expediente": d.get("expediente", ""),
                              "hora": a_texto(x.get("hora") or x.get("momento")),
                              "evento": a_texto(x.get("evento") or x.get("texto")
                                                or x.get("descripcion"))})
    return filas


def hoja_trenes(docs):
    filas = []
    for d in docs:
        campos = d.get("campos", {})
        v = campos.get("2.2.2", {}).get("valor_fuente")
        if not isinstance(v, list):
            continue
        for x in v:
            if isinstance(x, dict) and any(x.values()):
                filas.append({"clave": d.get("clave", ""),
                              "url_oficial": d.get("url_oficial", ""),
                              "expediente": d.get("expediente", ""),
                              "numero": a_texto(x.get("numero") or x.get("numero_tren")),
                              "tipo": a_texto(x.get("tipo")),
                              "operador": a_texto(x.get("operador") or x.get("empresa")),
                              "danos": a_texto(x.get("danos"))})
    return filas


def hoja_personal(docs):
    filas = []
    for d in docs:
        campos = d.get("campos", {})
        v = campos.get("2.2.1.A", {}).get("valor_fuente")
        if not isinstance(v, list):
            continue
        for x in v:
            if isinstance(x, dict) and any(x.values()):
                filas.append({"clave": d.get("clave", ""),
                              "url_oficial": d.get("url_oficial", ""),
                              "expediente": d.get("expediente", ""),
                              "rol": a_texto(x.get("rol")),
                              "implicacion": a_texto(x.get("implicacion")
                                                     or x.get("accion"))})
    return filas


def hoja_diccionario(guia, bases):
    filas = []
    for ref, spec in guia.items():
        b = spec.get("base") or ""
        doc, uso = bases.get(b, ("", ""))
        filas.append({"ref": ref, "campo": spec.get("nombre", ""),
                      "bloque": spec.get("bloque", ""),
                      "cumplimentable": spec.get("cumplimentar", ""),
                      "normalizar": spec.get("normalizar", ""),
                      "base": b,
                      "base_documento": doc,
                      "base_uso": uso})
    return filas


def hoja_cobertura(guia, docs):
    filas = []
    n = max(1, len(docs))
    for ref, spec in guia.items():
        con_valor = con_cita = verif = 0
        for d in docs:
            c = d.get("campos", {}).get(ref, {})
            if c.get("valor_fuente") not in (None, "", [], {}):
                con_valor += 1
                if c.get("pagina"):
                    con_cita += 1
                if c.get("verificado"):
                    verif += 1
        filas.append({"ref": ref, "campo": spec.get("campo", ""),
                      "bloque": spec.get("bloque", ""),
                      "cumplimentable": spec.get("cumplimentar", ""),
                      "informes": len(docs), "con_valor": con_valor,
                      "con_cita": con_cita, "verificados": verif,
                      "pct_valor": round(100 * con_valor / n, 1),
                      "pct_cita": round(100 * con_cita / n, 1)})
    return filas


# ------------------------------------------------------------------ escritura
def escribir_hoja(wb, nombre, columnas, filas, primero=False):
    ws = wb.active if primero else wb.create_sheet()
    ws.title = nombre
    ws.append(columnas)
    for c in range(1, len(columnas) + 1):
        cel = ws.cell(row=1, column=c)
        cel.fill = CAB_FONDO
        cel.font = CAB_LETRA
        cel.alignment = Alignment(vertical="center", wrap_text=True)
    for f in filas:
        ws.append([corte(f.get(c, "")) for c in columnas])
    ws.freeze_panes = "A2"
    if filas:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(columnas))}{len(filas) + 1}"
    # anchos: cortos para id, anchos para texto
    for i, c in enumerate(columnas, 1):
        ws.column_dimensions[get_column_letter(i)].width = \
            34 if c in ("url_oficial", "pdf", "md") else \
            26 if c in ("titulo", "expediente") else \
            18 if c in IDENT or c in DERIV else 22
    return ws


def main() -> int:
    guia, bases, por_clave, docs = cargar()
    if not docs:
        print("No hay database/data/crudo/ — corre primero 02_extraer_crudo.py")
        return 1

    refs, filas_inf = filas_informes(guia, por_clave, docs)
    rec = hoja_recomendaciones(docs)
    ent = hoja_lista_simple(docs, "2.1.2", "entidad")
    cro = hoja_cronologia(docs)
    tre = hoja_trenes(docs)
    per = hoja_personal(docs)
    dic = hoja_diccionario(guia, bases)
    cob = hoja_cobertura(guia, docs)

    wb = Workbook()
    escribir_hoja(wb, "Informes", IDENT + DERIV + refs, filas_inf, primero=True)
    escribir_hoja(wb, "Recomendaciones",
                  ["clave", "expediente", "url_oficial", "numero", "destinatario",
                   "implementador", "texto", "pagina", "origen"], rec)
    escribir_hoja(wb, "Entidades",
                  ["clave", "expediente", "url_oficial", "entidad"], ent)
    escribir_hoja(wb, "Cronologia",
                  ["clave", "expediente", "url_oficial", "hora", "evento"], cro)
    escribir_hoja(wb, "Trenes",
                  ["clave", "expediente", "url_oficial", "numero", "tipo",
                   "operador", "danos"], tre)
    escribir_hoja(wb, "Personal",
                  ["clave", "expediente", "url_oficial", "rol", "implicacion"], per)
    escribir_hoja(wb, "Diccionario",
                  ["ref", "campo", "bloque", "cumplimentable", "normalizar",
                   "base", "base_documento", "base_uso"], dic)
    escribir_hoja(wb, "Cobertura",
                  ["ref", "campo", "bloque", "cumplimentable", "informes",
                   "con_valor", "con_cita", "verificados", "pct_valor",
                   "pct_cita"], cob)

    # ---- GATE H4: url_oficial 100% en TODAS las hojas
    fallos = []
    for hoja, filas in (("Informes", filas_inf), ("Recomendaciones", rec),
                        ("Entidades", ent), ("Cronologia", cro),
                        ("Trenes", tre), ("Personal", per)):
        sin = [f.get("clave", "?") for f in filas if not f.get("url_oficial")]
        if sin:
            fallos.append(f"{hoja}: {len(sin)} filas sin url_oficial (ej {sin[0]})")

    wb.save(SALIDA)
    print(f"== Fase 3: base de datos global ==")
    print(f"  → {SALIDA.relative_to(RAIZ)}")
    print(f"  hoja Informes : {len(filas_inf)} filas × {len(IDENT)+len(DERIV)+len(refs)} columnas")
    print(f"    · columnas de guía: {len(refs)} · derivadas: {len(DERIV)}")
    print(f"  Recomendaciones: {len(rec)} · Entidades: {len(ent)} · "
          f"Cronología: {len(cro)} · Trenes: {len(tre)} · Personal: {len(per)}")
    print(f"  Diccionario: {len(dic)} · Cobertura: {len(cob)}")
    if fallos:
        for f in fallos:
            print(f"  ✗ {f}")
        print("  GATE H4: FALLO — url_oficial no es 100%")
        return 1
    print("  GATE H4: OK — url_oficial 100% en todas las hojas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
