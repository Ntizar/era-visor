#!/usr/bin/env python3
"""
03_exportar_excel.py — Fase 3: la BASE DE DATOS GLOBAL en un único Excel.

Contrato:
  • 1 fila = 1 informe, en la hoja `Informes`.
  • CADA dato de la guía CIAF en SU propia columna (las 70 refs reales;
    los 15 títulos de bloque de la guía NO son campos y se excluyen),
    más las columnas de identificación (incluye `titulo_normalizado`, un
    único formato para todos los años) y las analíticas derivadas.
  • `url_oficial` NUNCA vacío (obligatorio de proyecto).
  • Hojas 1-a-N desnormalizadas, enlazadas por `clave` (expediente) y con
    su `url_oficial` en cada fila: Recomendaciones, Entidades, Cronología,
    Trenes, Personal, Tablas (fila a fila, con página y cita) y Mejorado
    (Fase 4B: revisión LLM celda a celda con su cita literal).
  • Hojas de control: Diccionario (los 70 campos) y Cobertura (% por campo).

Fuente única: database/data/crudo/*.json (Fase 2) + database/data/mejorado/
(Fase 4B, opcional). Un valor LLM SÓLO rellena huecos deterministas: nunca
pisa un valor con cita (columna `campos_llm` cuenta los rellenados).

Uso: py 03_exportar_excel.py [--solo STEM]
"""

import json
import re
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

RAIZ = Path(__file__).resolve().parents[2]
CRUDO = RAIZ / "database" / "data" / "crudo"
DATA = RAIZ / "database" / "data"
SALIDA = DATA / "ciaf_base_global.xlsx"     # v1: sólo fuentes 00-02 (intacto)
SALIDA_V2 = DATA / "ciaf_base_v2.xlsx"      # v2: + Fase 4A (geo auditada/v3)
SINC = DATA / "sincronizado"                # salida de 06_sincronizar.py
V2 = "--v2" in sys.argv
# columnas que SÓLO existen con --v2 (salen de la Fase 4A)
COLS_SINC = ["lat", "lng", "veredicto_geo", "metodo_geo", "dist_via_m",
             "linea_geo", "pk_geo", "provincia_geo", "causa_directa_v3",
             "tipo_suceso_v3", "gravedad_victimas"]
# Fase 4B: revisión LLM con cita verificada (opcional — si no existe, el
# Excel sale idéntico al determinista).
MEJORADO = DATA / "mejorado"

MAX_CELDA = 32000  # límite real de Excel por celda
CAB_FONDO = PatternFill("solid", fgColor="DBEAFE")   # azul suave, monocromo
CAB_LETRA = Font(bold=True, color="1E3A8A", size=10)
TITULO = Font(bold=True, size=11, color="111827")

# columnas analíticas de cabecera (siempre presentes, ordenadas primero)
IDENT = ["clave", "expediente", "anio", "titulo", "titulo_normalizado",
         "url_oficial", "pdf", "md", "tipo_documento", "n_documentos",
         "principal",
         "paginas", "estado_cobertura", "campos_con_valor", "campos_con_cita",
         "campos_llm", "cobertura_pct"]

DERIV = ["fecha_suceso", "anio_suceso", "hora_suceso", "tipo_suceso",
         "lugar", "estacion", "pk", "linea", "provincia", "municipio",
         "fallecidos", "heridos_graves", "heridos_leves", "victimas_total",
         "entidades", "causa_directa", "n_recomendaciones", "n_cronologia",
         "n_trenes"]

# claves preferentes para volcar listas de dicts de forma legible
CLAVES_TEXTO = ("texto", "evento", "nombre", "rol", "implicacion",
                "descripcion", "destinatario")


# ---------------------------------------------------------------- normalización
# Los títulos de la DB mezclan dos épocas de redacción y por eso "no todos
# tienen el mismo formato": los antiguos son cancelería mayúscula con fórmula
# ("INFORME DEFINITIVO SOBRE LA INVESTIGACIÓN DEL ACCIDENTE FERROVIARIO
# Nº 0046/2006 OCURRIDO EL 12.08.2017 ...") y los recientes, frase natural
# ("Accidente en paso a nivel en Novelda (Alicante), ocurrido el 2 de julio").
# El título canónico deja UN solo formato y sin la parte redundante: el nº de
# expediente y la fecha ya están en sus propias columnas.
# Medido sobre los 349 títulos de la DB: 79 son cancelérica (23%) y el 77%
# ya son frase natural. Este patrón matchea 79/79 (probado antes de usarlo).
# V1 fallaba 0/79 porque exigía "SOBRE ... Nº" sin pasar por "DE LA CIAF (IF)".
RX_PREAMBULO = re.compile(
    r"^\s*INFORME\b.*?\d{3,4}\s*/\s*\d{2,4}\s*,?\s*", re.I | re.S)
# El resto es redundante: expediente y fecha ya tienen su propia columna.
# NO se ancla al final: después del suele venir el sitio ("... en la
# estación de X"), que es justamente lo que sí aporta al título.
RX_OCURRECIDO = re.compile(
    r"^\s*OCURRIDO\s+(?:EL\s+(?:D[ÍI]A\s+)?)?[\d./\-]{4,25}\s*,?\s*",
    re.I)
RX_ESPACIOS = re.compile(r"\s{2,}")


def titulo_canonico(titulo: str) -> str:
    """Un único formato para todos los años. NUNCA inventa: si al limpiar no
    queda texto descriptivo sensato, devuelve el original intacto."""
    t = RX_ESPACIOS.sub(" ", str(titulo or "")).strip()
    if not t:
        return ""
    limpio = RX_PREAMBULO.sub("", t)
    limpio = RX_OCURRECIDO.sub("", limpio).strip(" ,;-")
    # conserva el original si la limpieza no deja nada útil
    if len(limpio) < 12:
        return t
    limpio = RX_ESPACIOS.sub(" ", limpio).strip(" ,-")
    # si quedó TODO en mayúsculas, a frase normal; si no, se respeta
    if limpio.isupper():
        limpio = limpio.lower().capitalize()
    return limpio


def tipo_documento(pdf, md=""):
    """Documenta QUÉ es el fichero dentro de un expediente.

    21 expedientes tienen DOS documentos (medido): IF (informe final, 10-16
    pág) vs RS (resumen de 2 pág), Final vs Interim, español vs versión
    eRAIL en inglés. NUNCA se fusionan — dos fuentes distintas mezcladas en
    una celda romperían la regla de oro 2 —; se marcan para poder filtrar.
    """
    n = (pdf or "").upper()
    if re.search(r"ERA-\d{4}-\d+", n) or n.rstrip(".JSON").endswith("-EN") \
            or "-EN." in n or n.endswith("EN.JSON"):
        return "EN"          # versión eRAIL en inglés
    if re.search(r"(^|[-_ ])RS[-_ ]", n):
        return "RS"          # resumen de 2 páginas
    if "INTERIM" in n or "AVANCE" in n or "STATEMENT" in n:
        return "INTERIM"     # nota de avance de investigación
    if "IF" in n:
        return "IF"          # informe final
    return "OTRO"


def hoja_tablas(docs):
    """1 fila por FILA de tabla: nada de las 538 tablas se pierde, y cada
    fila lleva su página y su cita literal para poder verificarla."""
    filas = []
    for d in docs:
        for i, t in enumerate(d.get("tablas", []), 1):
            cab = [str(c) for c in (t.get("cabecera") or [])]
            for j, f in enumerate(t.get("filas") or [], 1):
                if isinstance(f, dict):
                    vals = [str(f.get(c, "")) for c in cab]
                else:
                    vals = [str(x) for x in f]
                filas.append({
                    "clave": d.get("clave", ""),
                    "expediente": d.get("expediente", ""),
                    "url_oficial": d.get("url_oficial", ""),
                    "pagina": t.get("pagina", ""),
                    "tabla": i, "fila": j,
                    "cabecera": json.dumps(cab, ensure_ascii=False),
                    "valores": json.dumps(vals, ensure_ascii=False),
                    "tipo": "recomendaciones"
                            if ("destinatario" in " ".join(cab).lower()
                                and "recomend" in " ".join(cab).lower())
                            else "otra",
                    "cita": t.get("cita", ""),
                })
    return filas


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
    # Fase 4B (opcional): {stem: {campos: {ref: {valor, pagina, cita, ...}}}}
    mej = {}
    if MEJORADO.is_dir():
        for f in sorted(MEJORADO.glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            mej[d.get("stem") or f.stem] = d
    return guia, bases, por_clave, docs, mej


def cargar_sinc():
    """Fase 4A: base canónica sincronizada (06_sincronizar.py).

    Fusiona por expediente el crudo (evidencia) con la geo AUDITADA y el
    análisis v3, ya verificados — se importa, nunca se re-extrae. Vacío si
    no existe: así el v1 sale exactamente igual que antes.
    """
    sinc = {}
    if SINC.is_dir():
        for f in sorted(SINC.glob("*.json")):
            if f.name.startswith("_"):     # `_resumen.json` auxiliar
                continue
            d = json.loads(f.read_text(encoding="utf-8"))
            clave = d.get("clave") or f.stem
            sinc[clave] = d
    return sinc


# ------------------------------------------------------ Fase 4A — hojas nuevas
def _t(v):
    """A texto SOLO lo escalar: las listas/dict del análisis (precursores,
    mitigaciones, cronología...) no los admite Excel. No se envuelve todo en
    `a_texto` porque perdería los números de las hojas Diccionario/Cobertura.
    """
    return a_texto(v) if isinstance(v, (list, dict)) else v


def hoja_geo(sinc, docs):
    """COORDENADAS EXACTAS: 1 fila por informe con su veredicto de auditoría.

    Regla del dominio: mejor sin coordenada que mal puesta. Un informe sin
    geocodificar sale con la fila vacía y el motivo explícito — jamás con un
    pin inventado. `geo_veredicto` es el que manda (`bien`/`mal`/`sin_geo`).
    """
    filas = []
    for d in docs:
        clave = d.get("clave") or d.get("id", "")
        g = (sinc.get(clave) or {}).get("geolocalizacion") or {}
        filas.append({
            "clave": clave,
            "expediente": d.get("expediente", ""),
            "url_oficial": d.get("url_oficial", ""),
            "lat": g.get("lat", ""),
            "lng": g.get("lng", ""),
            "veredicto": g.get("veredicto", ""),
            "motivo": g.get("motivo", ""),
            "metodo_geo": g.get("metodo_geo", ""),
            "dist_a_via_m": g.get("dist_m", ""),
            "linea": _t(g.get("linea", "")),
            "pk": _t(g.get("pk", "")),
            "estacion": _t(g.get("estacion", "")),
            "provincia": _t(g.get("provincia", "")),
            "sincronizado": "sí" if clave in sinc else "no",
        })
    return filas


def hoja_analisis(sinc, docs):
    """Taxonomía v3 sincronizada: causas, factores, infraestructura."""
    filas = []
    for d in docs:
        clave = d.get("clave") or d.get("id", "")
        s = sinc.get(clave) or {}
        a = s.get("analisis") or {}
        v = s.get("victimas") or {}
        filas.append({
            "clave": clave,
            "expediente": d.get("expediente", ""),
            "url_oficial": d.get("url_oficial", ""),
            "causa_directa": _t(a.get("causa_directa", "")),
            "causas_sistemicas": _t(a.get("causas_sistemicas", "")),
            "precursores": _t(a.get("precursores", "")),
            "mitigaciones": _t(a.get("mitigaciones", "")),
            "factores_humanos": _t(a.get("factores_humanos", "")),
            "meteorologia": _t(a.get("meteorologia", "")),
            "subsistema": _t(a.get("subsistema", "")),
            "sistema_proteccion": _t(a.get("sistema_proteccion", "")),
            "tipo_red": _t(a.get("tipo_red", "")),
            "explotacion": _t(a.get("explotacion", "")),
            "tipo_suceso": _t(a.get("tipo_suceso", "")),
            "gravedad": _t(v.get("gravedad", "")),
            "victimas_cuadran": ("sí" if v.get("cuadra_crudo") else
                                 ("no" if v.get("cuadra_crudo") is False else "")),
        })
    return filas


def hoja_textos(sinc, docs):
    """Textos largos por informe — aparte, para que la hoja `Informes` no se
    llene de párrafos y siga siendo legible. `lecciones` y `cronologia` salen
    del bloque v3 (`descripcion`/`conclusiones` NO existen en la fuente:
    pedirlos daría siempre una columna vacía silenciosa)."""
    filas = []
    for d in docs:
        clave = d.get("clave") or d.get("id", "")
        s = sinc.get(clave) or {}
        t = s.get("textos") or {}
        v3 = t.get("v3") or {}
        filas.append({
            "clave": clave,
            "expediente": d.get("expediente", ""),
            "url_oficial": d.get("url_oficial", ""),
            "resumen": t.get("resumen", ""),
            "hechos": t.get("hechos", ""),
            "lecciones": a_texto(v3.get("lecciones", "")),
            "cronologia": a_texto(v3.get("cronologia", "")),
        })
    return filas


# --------------------------------------------------------------------- hojas
def filas_informes(guia, por_clave, docs, mej=None, sinc=None):
    """Una fila por informe: identificación + 70 columnas de guía + derivadas.

    REGLA DE ORO 1: un valor LLM sólo puede rellenar un hueco determinista,
    nunca pisar uno existente. Así `valor_fuente` (Fase 2) sigue siendo el
    que manda y el aporte de la Fase 4 queda contado en `campos_llm`.
    """
    mej = mej or {}
    refs = list(guia)
    filas = []
    for d in docs:
        campos = d.get("campos", {})
        # el fichero de la Fase 4 se llama por el stem del md_base
        stem = Path(d.get("md") or "").stem or d.get("stem", "")
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
            "tipo_documento": tipo_documento(d.get("pdf", ""),
                                             d.get("md", "")),
        }
        con_valor = con_cita = rellenos_llm = 0
        for ref in refs:
            c = campos.get(ref, {})
            val = c.get("valor_fuente")
            if val not in (None, "", [], {}):
                con_valor += 1
                if c.get("pagina"):
                    con_cita += 1
                fila[ref] = corte(a_texto(val))
                continue
            # hueco determinista: lo rellena SOLO un valor LLM verificado
            m = ((mej.get(stem) or {}).get("campos") or {}).get(ref, {})
            if m.get("verificado") and m.get("valor") not in (None, "", [], {}):
                fila[ref] = corte(a_texto(m.get("valor")))
                rellenos_llm += 1
            else:
                fila[ref] = ""
        fila["campos_con_valor"] = con_valor
        fila["campos_con_cita"] = con_cita
        fila["campos_llm"] = rellenos_llm
        fila["cobertura_pct"] = round(100 * con_cita / max(1, con_valor), 1) \
            if con_valor else 0

        # ---- Fase 4A (sólo con --v2): geo AUDITADA + análisis v3 por
        # expediente. Nunca rellena nada del crudo: son columnas nuevas.
        s = (sinc or {}).get(clave) or {}
        if s:
            g = s.get("geolocalizacion") or {}
            a = s.get("analisis") or {}
            v = s.get("victimas") or {}
            fila["lat"] = g.get("lat", "")
            fila["lng"] = g.get("lng", "")
            fila["veredicto_geo"] = g.get("veredicto", "")
            fila["metodo_geo"] = g.get("metodo_geo", "")
            fila["dist_via_m"] = g.get("dist_m", "")
            fila["linea_geo"] = g.get("linea", "")
            fila["pk_geo"] = g.get("pk", "")
            fila["provincia_geo"] = g.get("provincia", "")
            fila["causa_directa_v3"] = a.get("causa_directa", "")
            fila["tipo_suceso_v3"] = a.get("tipo_suceso", "")
            fila["gravedad_victimas"] = v.get("gravedad", "")

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


def hoja_mejorado(docs, mej):
    """Una fila por (informe, campo) revisado por LLM con su cita y página.

    Es la trazabilidad Celda a Celda de la Fase 4B: sin esta hoja, un valor
    LLM rellenado en `Informes` sería indistinguible de uno determinista.
    """
    # url_oficial/expediente del crudo, indexados por stem del md_base
    idx = {}
    for d in docs:
        stem = Path(d.get("md") or "").stem or d.get("stem", "")
        idx[stem] = (d.get("clave") or "", d.get("expediente") or "",
                     d.get("url_oficial") or "")
    filas = []
    for stem, doc in sorted(mej.items()):
        clave, exp, url = idx.get(stem, ("", "", ""))
        for ref, m in sorted((doc.get("campos") or {}).items()):
            filas.append({
                "clave": clave, "expediente": exp, "url_oficial": url,
                "ref": ref,
                "valor": a_texto(m.get("valor")),
                "pagina": m.get("pagina") or "",
                "cita": corte(m.get("cita") or ""),
                "verificado": "sí" if m.get("verificado") else "NO",
                "verificacion": m.get("verificacion") or "",
                "intentos": m.get("intentos", ""),
            })
    return filas


def main() -> int:
    guia, bases, por_clave, docs, mej = cargar()
    if not docs:
        print("No hay database/data/crudo/ — corre primero 02_extraer_crudo.py")
        return 1

    # Fase 4A sólo con --v2: sin flag, sinc()={} y el v1 sale idéntico
    sinc = cargar_sinc() if V2 else {}
    refs, filas_inf = filas_informes(guia, por_clave, docs, mej, sinc)
    # título canónico: un solo formato para todos los años (columna nueva)
    for f in filas_inf:
        f["titulo_normalizado"] = titulo_canonico(f.get("titulo", ""))
    # expedientes con DOS documentos (21 medidos: IF+RS, Final+Interim,
    # es+eRAIL): se marcan y se elige el principal por número de campos.
    # NO se fusionan nunca — cada fila sigue siendo UN documento.
    por_exp = {}
    for i, f in enumerate(filas_inf):
        por_exp.setdefault(f.get("expediente") or f.get("clave"), []).append(
            (i, f.get("campos_con_valor", 0) or 0))
    for lst in por_exp.values():
        mejor = max(lst, key=lambda t: t[1])[0]
        for i, _ in lst:
            filas_inf[i]["n_documentos"] = len(lst)
            filas_inf[i]["principal"] = "sí" if i == mejor else "no"
    rec = hoja_recomendaciones(docs)
    ent = hoja_lista_simple(docs, "2.1.2", "entidad")
    cro = hoja_cronologia(docs)
    tre = hoja_trenes(docs)
    per = hoja_personal(docs)
    dic = hoja_diccionario(guia, bases)
    cob = hoja_cobertura(guia, docs)
    tab = hoja_tablas(docs)
    mejo = hoja_mejorado(docs, mej)
    # ---- Fase 4A (--v2): hojas de la base sincronizada
    geo_f = hoja_geo(sinc, docs) if sinc else []
    ana_f = hoja_analisis(sinc, docs) if sinc else []
    txt_f = hoja_textos(sinc, docs) if sinc else []
    cols_inf = IDENT + DERIV + refs + (COLS_SINC if sinc else [])

    wb = Workbook()
    escribir_hoja(wb, "Informes", cols_inf, filas_inf, primero=True)
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
    escribir_hoja(wb, "Tablas",
                  ["clave", "expediente", "url_oficial", "pagina", "tabla",
                   "fila", "cabecera", "valores", "tipo", "cita"], tab)
    escribir_hoja(wb, "Mejorado",
                  ["clave", "expediente", "url_oficial", "ref", "valor",
                   "pagina", "cita", "verificado", "verificacion",
                   "intentos"], mejo)
    # ---- hojas Fase 4A (--v2)
    if sinc:
        escribir_hoja(wb, "Geo",
                      ["clave", "expediente", "url_oficial", "lat", "lng",
                       "veredicto", "motivo", "metodo_geo", "dist_a_via_m",
                       "linea", "pk", "estacion", "provincia",
                       "sincronizado"], geo_f)
        escribir_hoja(wb, "Analisis",
                      ["clave", "expediente", "url_oficial", "causa_directa",
                       "causas_sistemicas", "precursores", "mitigaciones",
                       "factores_humanos", "meteorologia", "subsistema",
                       "sistema_proteccion", "tipo_red", "explotacion",
                       "tipo_suceso", "gravedad", "victimas_cuadran"], ana_f)
        escribir_hoja(wb, "Textos",
                      ["clave", "expediente", "url_oficial", "resumen",
                       "hechos", "lecciones", "cronologia"], txt_f)

    # ---- GATE H4: url_oficial 100% en TODAS las hojas (las nuevas
    # incluidas: una hoja que no entra al gate sólo es una promesa)
    hojas = [("Informes", filas_inf), ("Recomendaciones", rec),
             ("Entidades", ent), ("Cronologia", cro),
             ("Trenes", tre), ("Personal", per),
             ("Tablas", tab), ("Mejorado", mejo)]
    if sinc:
        hojas += [("Geo", geo_f), ("Analisis", ana_f), ("Textos", txt_f)]
    fallos = []
    for hoja, filas in hojas:
        sin = [f.get("clave", "?") for f in filas if not f.get("url_oficial")]
        if sin:
            fallos.append(f"{hoja}: {len(sin)} filas sin url_oficial (ej {sin[0]})")

    salida = SALIDA_V2 if V2 else SALIDA
    wb.save(salida)
    print(f"== Fase 3: base de datos global {'(v2 — Fase 4A incluida)' if V2 else '(v1)'} ==")
    print(f"  → {salida.relative_to(RAIZ)}")
    print(f"  hoja Informes : {len(filas_inf)} filas × {len(cols_inf)} columnas")
    print(f"    · columnas de guía: {len(refs)} · derivadas: {len(DERIV)}"
          + (f" · Fase 4A: {len(COLS_SINC)}" if sinc else ""))
    print(f"  Recomendaciones: {len(rec)} · Entidades: {len(ent)} · "
          f"Cronología: {len(cro)} · Trenes: {len(tre)} · Personal: {len(per)}")
    print(f"  Diccionario: {len(dic)} · Cobertura: {len(cob)}")
    print(f"  Mejorado (Fase 4B): {len(mejo)} filas revisadas por LLM "
          f"→ {sum(1 for f in filas_inf if f.get('campos_llm'))} informes "
          f"con huecos rellenados ({sum(f.get('campos_llm', 0) for f in filas_inf)} celdas)")
    if fallos:
        for f in fallos:
            print(f"  ✗ {f}")
        print("  GATE H4: FALLO — url_oficial no es 100%")
        return 1
    print("  GATE H4: OK — url_oficial 100% en todas las hojas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
