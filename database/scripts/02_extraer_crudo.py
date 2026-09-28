#!/usr/bin/env python3
"""
02_extraer_crudo.py — Fase 2: JSON crudo por informe con página-evidencia.

CERO TOKENS. El agente nunca lee informes; este script sí.

Para cada md de database/md_base/ emite database/data/crudo/<id>.json con los
85 CAMPOS de la guía CIAF Fase I (database/data/guia_campos.json), cada uno con
estado explícito:

    determinista  valor extraído del propio md, con página + cita literal
    importado     valor ya verificado en data/db/reports/ES.json, LOCALIZADO
                  en el md (si no se localiza → verificado=false + nota)
    no consta     el md no contiene ese dato — la guía manda decirlo, no inferir
    pendiente     aún sin regla determinista → cola de la Fase 4B (LLM)

DIFERENCIA CLAVE con un parser por número de ref: las refs de la guía NO casan
con la numeración real de los informes (2.1.1 = "Tipo de suceso" en la guía pero
"Datos" en los informes; 0.1/1.1/4.6.1 no aparecen ni una vez en 60 md
sondeados). Por eso TODO se localiza por ANCLA SEMÁNTICA de título; el número
solo se conserva como diagnóstico.

Uso:
  py 02_extraer_crudo.py                # reanudable (salta los ya hechos)
  py 02_extraer_crudo.py --refrescar    # rehace todos
  py 02_extraer_crudo.py --solo STEM    # un informe
"""

import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
MD_BASE = RAIZ / "md" / "ES"          # única colección md (la mejorada)
CRUDO = RAIZ / "database" / "data" / "crudo"
DATA = RAIZ / "database" / "data"
INFORMES = RAIZ / "database" / "informes"
DB_REPORTS = RAIZ / "data" / "db" / "reports" / "ES.json"

RX_PAGINA = re.compile(r"^## P[áa]gina (\d+)\s*$", re.M)
RX_FM = re.compile(r"^---\n(.*?)\n---\n", re.S)
RX_SEC = re.compile(
    r"^[ \t]*(\d{1,2}(?:\.\d{1,2}){0,4}(?:\.[A-Da-d])?)\.?[ \t]+([^\n]{2,70})$", re.M)

NO_CONSTA = "no consta"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


# ------------------------------------------------------------------ utilidades

def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).lower().strip()


def fecha_variantes(iso) -> list[str]:
    """2017-08-12 → ['12/08/2017', '12/8/2017', '12-08-2017', '12 de agosto...']"""
    if not iso:
        return []
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(iso))
    if not m:
        return [str(iso)]
    a, mes, d = m.group(1), int(m.group(2)), int(m.group(3))
    return [f"{d:02d}/{mes:02d}/{a}", f"{d}/{mes}/{a}", f"{d:02d}-{mes:02d}-{a}",
            f"{d} de {MESES[mes - 1]} de {a}", f"{d} {MESES[mes - 1]} {a}"]


def compacto(s) -> str:
    """Para localizar textos largos aunque el md rompa las líneas por ancho."""
    return re.sub(r"[\s ]+", " ", norm(s)).strip()


def rutas(db: dict, ruta: str):
    """'v3.causas.directa' → valor o None."""
    cur = db
    for k in ruta.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
        if cur is None:
            return None
    return cur


def a_texto(v) -> str:
    """Valor de DB → texto buscable."""
    if v is None:
        return ""
    if isinstance(v, list):
        piezas = []
        for x in v:
            if isinstance(x, dict):
                piezas.append(" ".join(str(y) for y in x.values() if isinstance(y, (str, int, float))))
            else:
                piezas.append(str(x))
        return " ".join(piezas)
    if isinstance(v, dict):
        return " ".join(str(y) for y in v.values() if isinstance(y, (str, int, float)))
    return str(v)


# ------------------------------------------------------------------ informe

class Informe:
    """md_base parseado: frontmatter, mapa offset→página y de secciones."""

    def __init__(self, ruta: Path):
        self.ruta = ruta
        self.stem = ruta.stem
        bruto = ruta.read_text(encoding="utf-8", errors="replace")
        fm = RX_FM.match(bruto)
        self.front: dict = {}
        self.cuerpo = bruto
        if fm:
            for ln in fm.group(1).splitlines():
                if ":" in ln:
                    k, _, v = ln.partition(":")
                    self.front[k.strip()] = v.strip()
            self.cuerpo = bruto[fm.end():]

        self.paginas = [(m.start(), int(m.group(1))) for m in RX_PAGINA.finditer(self.cuerpo)]
        self.secciones = []
        for m in RX_SEC.finditer(self.cuerpo):
            num, tit = m.group(1), m.group(2).strip().rstrip(".")
            if not re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", tit):
                continue                       # "180718161104ifciafdocx" y demás ruido
            self.secciones.append({
                "offset": m.start(), "num": num, "titulo": tit,
                "titulo_norm": norm(tit), "pagina": self.pagina_de(m.start()),
            })

    # ---------------- páginas
    def pagina_de(self, offset) -> int:
        p = 1
        for start, num in self.paginas:
            if start <= offset:
                p = num
            else:
                break
        return p

    def texto_pagina(self, num) -> str:
        idx = [i for i, (s, n) in enumerate(self.paginas) if n == num]
        if not idx:
            return ""
        i = idx[0]
        fin = self.paginas[i + 1][0] if i + 1 < len(self.paginas) else len(self.cuerpo)
        return self.cuerpo[self.paginas[i][0]:fin]

    def cita_de(self, offset, max_chars=220) -> str:
        if offset is None or offset >= len(self.cuerpo):
            return ""
        ini = self.cuerpo.rfind("\n", 0, offset) + 1
        fin = self.cuerpo.find("\n", offset)
        if fin < 0:
            fin = len(self.cuerpo)
        cita = self.cuerpo[ini:fin].strip()
        if len(cita) < 20:
            cita = re.sub(r"\s+", " ", self.cuerpo[ini:ini + max_chars].strip())
        return cita[:max_chars]

    def buscar(self, patron, desde=0, hasta=None):
        hasta = len(self.cuerpo) if hasta is None else hasta
        return patron.search(self.cuerpo, desde, hasta)

    # ---------------- secciones
    def seccion(self, *patrones) -> dict | None:
        for pat in patrones:
            rx = re.compile(pat, re.I)
            for s in self.secciones:
                if rx.search(s["titulo_norm"]):
                    return s
        return None

    def bloque(self, sec) -> tuple[str, int]:
        """Texto desde la sección hasta la siguiente de nivel ≤ suyo."""
        fin, mi_nivel = len(self.cuerpo), sec["num"].count(".") + 1
        for s in self.secciones:
            if s["offset"] <= sec["offset"]:
                continue
            if s["num"].count(".") + 1 <= mi_nivel:
                fin = s["offset"]
                break
        return self.cuerpo[sec["offset"]:fin], sec["offset"]

    def bloque_con(self, *patrones) -> tuple[str, int] | tuple[None, None]:
        sec = self.seccion(*patrones)
        if not sec:
            return None, None
        return self.bloque(sec)


# ------------------------------------------------------------------ localizar

RX_ESTRUCT = re.compile(
    r"^(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"      # fecha
    r"\d{1,2}:\d{2}|"                            # hora
    r"\d{1,4}/\d{2,4}|"                          # expediente / recomendación
    r"\d{1,3}[.,]\d{1,3}/\d{1,3})$")             # P.K. notación CIAF (124/573)


def localizar(inf: Informe, valor, contexto_rx=None):
    """Busca un valor importado en el md → (pagina, cita) o (None, None).

    Tres vías, de más a menos fiable, y NUNCA se devuelve una página sin haber
    visto la coincidencia (una cita falsa es peor que una ausencia declarada):
      1. VALOR ESTRUCTURADO (fecha/hora/expediente/PK) → búsqueda directa con
         límites: su formato es específico, no hace falta contexto y los de
         5 caracteres ya no se quedan sin buscar.
      2. TEXTO LIBRE ≥ 8 chars → literal y tolerante a espacios/saltos.
      3. TEXTO CORTO o cifra → solo con etiqueta de contexto en su ventana.
    """
    if valor is None or valor == "":
        return None, None

    # --- dict/lista: localizar sus partes (el concatenado jamás aparece)
    if isinstance(valor, (dict, list)):
        partes = (list(valor.values()) if isinstance(valor, dict) else valor)
        for p in partes:
            if isinstance(p, (dict, list)):
                r = localizar(inf, p, contexto_rx)
                if r[0]:
                    return r
                continue
            if p in (None, ""):
                continue
            r = localizar(inf, p, contexto_rx)
            if r[0]:
                return r
        return None, None

    txt = str(valor).strip()
    if not txt:
        return None, None

    # --- 1) valor estructurado: búsqueda directa con límites
    if RX_ESTRUCT.match(txt):
        m = re.search(r"(?<![\d./-])" + re.escape(txt) + r"(?![\d./-])", inf.cuerpo)
        if m:
            return inf.pagina_de(m.start()), inf.cita_de(m.start())

    # --- 2) texto libre
    if len(txt) >= 8:
        for trozo in (txt, txt[:160], txt.split(".")[0][:160]):
            trozo = trozo.strip()
            if len(trozo) < 6:
                continue
            m = re.search(re.escape(trozo), inf.cuerpo)
            if m:
                return inf.pagina_de(m.start()), inf.cita_de(m.start())
            m = _buscar_flexible(inf, trozo)
            if m:
                return inf.pagina_de(m.start()), inf.cita_de(m.start())

    # --- 2b) nombre propio corto (Soria, ADIF): suficientemente específico
    #         como para buscarlo sin etiqueta de contexto
    if 4 <= len(txt) <= 7 and (txt[0].isupper() or txt.isupper() or txt.isdigit()) \
            and not RX_ESTRUCT.match(txt):
        m = re.search(r"(?<![A-Za-zÁÉÍÓÚÑáéíóúñ])" + re.escape(txt) + r"(?![A-Za-zÁÉÍÓÚÑáéíóúñ])",
                      inf.cuerpo)
        if m:
            return inf.pagina_de(m.start()), inf.cita_de(m.start())

    # --- fechas en ISO → variantes
    if re.match(r"\d{4}-\d{2}-\d{2}", txt):
        for v in fecha_variantes(txt):
            m = re.search(r"(?<!\d)" + re.escape(v) + r"(?!\d)", inf.cuerpo)
            if m:
                return inf.pagina_de(m.start()), inf.cita_de(m.start())

    # --- 3) etiqueta de contexto + valor en la ventana
    if contexto_rx:
        rx = re.compile(contexto_rx, re.I)
        for m in rx.finditer(inf.cuerpo):
            ventana = inf.cuerpo[m.start(): m.start() + 500]
            if re.search(r"(?<![\d./-])" + re.escape(txt) + r"(?![\d./-])", ventana):
                return inf.pagina_de(m.start()), inf.cita_de(m.start())

    return None, None


def _buscar_flexible(inf: Informe, texto: str):
    """Busca un texto con cualquier separador entre palabras: espacios, saltos
    de línea, guiones y comas. Pitfall real: la DB guarda
    'Línea 200 Madrid-Chamartín a Barcelona-França' y el PDF imprime
    'Línea 200 Madrid - Chamartín a Barcelona - França' (PyMuPDF parte además
    por ancho) → con un solo separador la coincidencia nunca se produce."""
    trozos = [re.escape(t) for t in re.split(r"[\s\-–—,;]+", texto) if t]
    if len(trozos) < 3:
        return None
    rx = re.compile(r"[\s\-–—,;]+" + r"[\s\-–—,;]+".join(trozos[:14]), re.I)
    return rx.search(inf.cuerpo)


# ==================================================================== REGLAS
# Las 43 refs que la guía marca «Sí» + las importaciones de la DB. Las que no
# tienen regla salen como "pendiente" y alimentan la cola de la Fase 4B (LLM):
# no se inventa una extracción determinista que no sabemos hacer bien.

def imp(ruta, ctx=None):
    return {"t": "imp", "ruta": ruta, "ctx": ctx}


def sec(*anclas, rx=None):
    return {"t": "sec", "anclas": anclas, "rx": rx}


def portada(rx):
    return {"t": "portada", "rx": rx}


RX_EXP = r"(?:n[º°]|n[úu]mero de referencia del informe|expediente)[^\d\n]{0,40}(\d{1,4}\s*/\s*\d{2,4})"

CAMPOS: dict[str, dict] = {
    # ---------------- 0 control ----------------
    "0.1": {"nombre": "Número de referencia del informe",
            "fuentes": [imp("expediente", ctx=RX_EXP),
                        portada(RX_EXP),
                        {"t": "seccion_rx", "rx": r"investigaci[óo]n del (?:accidente|incidente)[^\d]{0,30}(\d{1,4}\s*/\s*\d{2,4})"}]},
    "0.2": {"nombre": "Código interno del suceso", "fuentes": []},
    "0.5": {"nombre": "Fecha del informe",
            "fuentes": [portada(r"fecha (?:de )?(?:emisi[óo]n|aprobaci[óo]n|publicaci[óo]n|de aprobaci[óo]n|del informe)[^\d\n]{0,30}"
                                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2} de \w+ de \d{4})")]},
    "0.6": {"nombre": "Versión / revisión del informe", "fuentes": []},

    # ---------------- 1 resumen ----------------
    "1.1": {"nombre": "Descripción breve del suceso",
            "fuentes": [imp("v3.resumen"), imp("resumen"),
                        sec(r"^resumen$")]},
    "1.2": {"nombre": "Fecha, hora y lugar del suceso",
            "fuentes": [{"t": "multi", "partes": [("fecha", ["fecha"]),
                                                  ("hora", ["hora"]),
                                                  ("lugar", ["v3.lugar", "ubicacion_nombre", "estacion"])]}]},
    "1.3": {"nombre": "Consecuencias principales",
            "fuentes": [imp("v3.consecuencias", ctx=r"víctimas mortales|fallecidos|heridos"),
                        imp("v3.resumen"),
                        sec(r"^da[ñn]os materiales$", r"^v[íi]ctimas mortales y heridos$")]},
    "1.4": {"nombre": "Causas directas",
            "fuentes": [imp("v3.causas.directa"), imp("causa_directa"),
                        sec(r"^causas? directas?$", r"^causas?$")]},
    "1.7": {"nombre": "Recomendaciones principales",
            "fuentes": [{"t": "tabla"}, imp("v3.recomendaciones"), imp("recomendaciones"),
                        sec(r"^recomendaciones$", r"^medidas adoptadas$")]},
    "1.8": {"nombre": "Destinatarios de las recomendaciones",
            "fuentes": [{"t": "tabla", "campo": "destinatario"}, imp("v3.recomendaciones")]},

    # ---------------- 2.1 suceso ----------------
    "2.1.1": {"nombre": "Tipo de suceso",
              "fuentes": [imp("tipo_categoria"), imp("tipo"),
                          sec(r"^datos$", r"^aspectos generales$")]},
    "2.1.2": {"nombre": "Administrador de infraestructura y empresas ferroviarias implicadas",
              "fuentes": [imp("entidades"), imp("v3.trenes")]},
    "2.1.3.A": {"nombre": "Fecha del suceso", "fuentes": [imp("fecha", ctx=r"fecha")]},
    "2.1.3.B": {"nombre": "Hora del suceso", "fuentes": [imp("hora", ctx=r"hora")]},
    "2.1.3.C": {"nombre": "Localización exacta del suceso",
                "fuentes": [imp("v3.lugar"), imp("ubicacion_nombre"),
                            imp("estacion", ctx=r"estaci[óo]n"), imp("municipio", ctx=r"municipio")]},
    "2.1.4": {"nombre": "Identificación y características de la infraestructura ferroviaria",
              "fuentes": [imp("linea", ctx=r"l[íi]nea"), imp("pk", ctx=r"p\.?\s?k"),
                          sec(r"^descripci[óo]n de la infraestructura$")]},
    "2.1.5": {"nombre": "Identificación y características de los vehículos ferroviarios",
              "fuentes": [imp("v3.material_rodante"), imp("v3.trenes")]},
    "2.1.6": {"nombre": "Descripción de los hechos",
              "fuentes": [imp("v3.hechos"), imp("hechos"),
                          sec(r"^descripci[óo]n del suceso$", r"^descripci[óo]n de los hechos$",
                              r"^descripci[óo]n de los acontecimientos$")]},
    "2.1.7": {"nombre": "Descripción del lugar del accidente/incidente",
              "fuentes": [imp("v3.lugar"), imp("estacion", ctx=r"estaci[óo]n"),
                          sec(r"^descripci[óo]n del lugar$", r"^circunstancias externas$")]},
    "2.1.9": {"nombre": "Causas presuntas inicialmente identificadas", "fuentes": []},
    "2.1.10": {"nombre": "Consecuencias inicialmente identificadas",
               "fuentes": [imp("v3.consecuencias", ctx=r"víctimas mortales|fallecidos|heridos"),
                           sec(r"^consecuencias$", r"^da[ñn]os materiales$")]},
    "2.1.11": {"nombre": "Medidas inmediatas adoptadas por la entidad",
               "fuentes": [sec(r"^medidas inmediatas", r"^actuaciones inmediatas",
                               r"^plan de emergencia internoexterno$")]},

    # ---------------- 2.2 personal / material ----------------
    "2.2.1.A": {"nombre": "Personal ferroviario implicado",
                "fuentes": [imp("v3.personal"), imp("entidades"),
                            sec(r"^personal ferroviario implicado$")]},
    "2.2.1.B": {"nombre": "Terceros implicados",
                "fuentes": [sec(r"^terceros implicados$", r"^terceros$")]},
    "2.2.2": {"nombre": "Trenes implicados y composición",
              "fuentes": [imp("v3.trenes"),
                          sec(r"^trenes y composici[óo]n$", r"^los trenes y su composici[óo]n$",
                              r"^material rodante$")]},
    "2.2.3": {"nombre": "Matrícula del material rodante implicado",
              "fuentes": [imp("v3.material_rodante")]},
    "2.2.4": {"nombre": "Subsistema afectado", "fuentes": [imp("subsistema")]},
    "2.2.5": {"nombre": "Descripción de la infraestructura: vía, agujas y otros elementos",
              "fuentes": [imp("v3.infraestructura"),
                          sec(r"^descripci[óo]n de la infraestructura$")]},
    "2.2.6": {"nombre": "Sistema de señalización, enclavamiento, señales y protección",
              "fuentes": [imp("v3.infraestructura.senalizacion"),
                          sec(r"^sistemas de se[ñn]alizaci[óo]n", r"^se[ñn]alizaci[óo]n$")]},
    "2.2.7": {"nombre": "Sistemas de comunicación",
              "fuentes": [sec(r"^sistemas de comunicaci[óo]n$")]},
    "2.2.9": {"nombre": "Obras en el lugar o en sus cercanías",
              "fuentes": [sec(r"^obras en el lugar o cercan[íi]as$", r"^obras$")]},

    # ---------------- 2.3 víctimas y daños ----------------
    "2.3.1.A": {"nombre": "Viajeros",
                "fuentes": [imp("v3.consecuencias", ctx=r"viajeros|v[íi]ctimas mortales|heridos")]},
    "2.3.1.B": {"nombre": "Personal ferroviario",
                "fuentes": [imp("v3.consecuencias", ctx=r"personal ferroviario|ferroviarios|heridos")]},
    "2.3.1.C": {"nombre": "Terceras personas",
                "fuentes": [imp("v3.consecuencias", ctx=r"terceras personas|terceros|heridos")]},
    "2.3.2": {"nombre": "Carga", "fuentes": [sec(r"^carga$")]},
    "2.3.3": {"nombre": "Material rodante",
              "fuentes": [imp("v3.material_rodante"),
                          sec(r"^da[ñn]os materiales$", r"^material rodante$")]},
    "2.3.4": {"nombre": "Infraestructura",
              "fuentes": [imp("v3.infraestructura"),
                          sec(r"^da[ñn]os materiales$", r"^infraestructura$")]},
    "2.3.5": {"nombre": "Medio ambiente", "fuentes": [sec(r"^da[ñn]os al medio ambiente$")]},
    "2.3.6": {"nombre": "Impacto económico", "fuentes": []},
    "2.3.3b": {"nombre": "Interceptación de vía / minutos perdidos",
               "fuentes": [sec(r"^interceptaci[óo]n de la? v[íi]a")]},

    # ---------------- 2.4 circunstancias externas ----------------
    "2.4.1": {"nombre": "Condiciones meteorológicas",
              "fuentes": [imp("v3.clima"), imp("meteorologia"),
                          sec(r"^condiciones meteorol[óo]gicas$", r"^circunstancias externas$")]},
    "2.4.2": {"nombre": "Referencias geográficas",
              "fuentes": [{"t": "multi", "partes": [("provincia", ["provincia"]),
                                                    ("municipio", ["municipio"]),
                                                    ("estacion", ["estacion"])]}]},
    "2.4.3": {"nombre": "Condiciones de visibilidad, iluminación u otras condiciones ambientales",
              "fuentes": [imp("v3.clima")]},

    # ---------------- 3 investigaciones ----------------
    "3.4.1": {"nombre": "Sistema de control de mando y señalización",
              "fuentes": [imp("v3.infraestructura.senalizacion")]},
    "3.4.3": {"nombre": "Infraestructura", "fuentes": [imp("v3.infraestructura")]},
    "3.4.5": {"nombre": "Material rodante", "fuentes": [imp("v3.material_rodante")]},
    "3.5.1": {"nombre": "Medidas tomadas por el personal de circulación",
              "fuentes": [sec(r"^medidas tomadas por el personal de circulaci[óo]n$")]},

    # ---------------- 4 análisis y recomendaciones ----------------
    "4.1": {"nombre": "Descripción definitiva de la cadena de acontecimientos",
            "fuentes": [imp("v3.hechos"),
                        sec(r"^descripci[óo]n definitiva",
                            r"^descripci[óo]n definitiva de los acontecimientos$")]},
    "4.2": {"nombre": "Análisis de los hechos y eficacia de los servicios de salvamento",
            "fuentes": [sec(r"^an[áa]lisis", r"^an[áa]lisis y conclusiones$")]},
    "4.3.1": {"nombre": "Causas directas e inmediatas del suceso",
              "fuentes": [imp("v3.causas.directa"), imp("causa_directa"),
                          sec(r"^causas directas", r"^causas?$")]},
    "4.3.2": {"nombre": "Factores coadyuvantes",
              "fuentes": [imp("v3.causas.contribuyentes"), imp("precursores"),
                          sec(r"^factores? coadyuvantes?$", r"^factores contribuyentes$")]},
    "4.5.1": {"nombre": "Medidas adoptadas inmediatamente",
              "fuentes": [sec(r"^medidas adoptadas$", r"^medidas inmediatas")]},
    "4.6.1": {"nombre": "Recomendaciones de seguridad",
              "fuentes": [{"t": "tabla"}, imp("v3.recomendaciones"), imp("recomendaciones"),
                          sec(r"^recomendaciones$", r"^recomendaciones de seguridad$")]},
    "4.6.2.A": {"nombre": "Destinatarios de las recomendaciones",
                "fuentes": [{"t": "tabla", "campo": "destinatario"}]},
    "4.6.3": {"nombre": "Implementadores previstos",
              "fuentes": [{"t": "tabla", "campo": "implementador final"}]},
}

# ---------------------------------------------------------------------------
# PARCHES DE COBERTURA — anclas calibradas con los títulos REALES de los
# 372 md_base (sondeo: 1.140 títulos únicos; norm() elimina acentos, así que
# las anclas van SIN tilde: "observaciones adicionales", "sistemas de
# comunicacion"...). Cubren los campos de la guía que estaban al 0% porque su
# sección lleva otro nombre en los informes que en la norma.
# Los que siguen al 0% tras esto NO EXISTEN en los informes → "no consta"
# es la respuesta correcta (regla 3 de la guía), y quedan para la Fase 4B.
# ---------------------------------------------------------------------------
CAMPOS.update({
    "0.5": {"nombre": "Fecha del informe",
            "fuentes": [portada(r"fecha (?:de|del) (?:emisi[óo]n|aprobaci[óo]n|"
                                r"publicaci[óo]n|informe|elaboraci[óo]n)")]},
    "1.5": {"nombre": "Factores coadyuvantes",
            "fuentes": [imp("v3.causas.contribuyentes"),
                        sec(r"^factores? coadyuvantes?", r"^factores contribuyentes",
                            r"^causas contribuyentes")]},
    "1.6": {"nombre": "Causas subyacentes",
            "fuentes": [imp("v3.causas.sistemicas"), imp("v3.causas.sistemica"),
                        sec(r"^causas sistemicas", r"^causas subyacentes",
                            r"^causas de sistema")]},
    "2.1.9": {"nombre": "Causas presuntas inicialmente identificadas",
              "fuentes": [sec(r"^causas presuntas", r"^causas iniciales",
                              r"^hipotesis de causa", r"^causas preliminares")]},
    "2.1.11": {"nombre": "Medidas inmediatas adoptadas por la entidad",
               "fuentes": [sec(r"^medidas inmediatas", r"^actuaciones inmediatas",
                               r"^medidas adoptadas", r"^intervenciones")]},
    "2.2.1.B": {"nombre": "Terceros implicados",
                "fuentes": [sec(r"^viajeros, personal y terceros",
                                r"^personal y entidades", r"^terceros implicados",
                                r"^terceras personas", r"^terceros")]},
    "2.3.2": {"nombre": "Carga",
              "fuentes": [sec(r"^carga", r"^carga del tren", r"^estiba")]},
    "2.3.6": {"nombre": "Impacto económico",
              "fuentes": [sec(r"^impacto economico", r"^coste", r"^consecuencias economicas")]},
    "3.4.4": {"nombre": "Equipo de comunicaciones",
              "fuentes": [sec(r"^sistemas de comunicacion", r"^canales de comunicacion",
                              r"^comunicaciones$", r"^equipo de comunicaciones")]},
    "3.6.1": {"nombre": "Accidente con precursor o causa Factor Humano",
              "fuentes": [imp("precursores"),
                          sec(r"^interfaz hombre-maquina", r"^factores humanos")]},
    "3.6.2": {"nombre": "Tiempo de trabajo del personal implicado",
              "fuentes": [sec(r"^requisitos del personal", r"^tiempo de trabajo",
                              r"^jornada")]},
    "3.6.3": {"nombre": "Circunstancias médicas y personales con posible influencia",
              "fuentes": [sec(r"^circunstancias medicas", r"^circunstancias personales")]},
    "3.6.4": {"nombre": "Existencia de tensión física o psicológica",
              "fuentes": [sec(r"^tension fisica", r"^tension psicologica",
                              r"^tension en el trabajo")]},
    "3.6.5": {"nombre": "Diseño del equipo con efectos en la interfaz hombre-máquina",
              "fuentes": [sec(r"^interfaz hombre-maquina", r"^ergonomia")]},
    "3.6.6": {"nombre": "Factores humanos y organizativos relevantes",
              "fuentes": [sec(r"^factores humanos", r"^interfaz hombre-maquina",
                              r"^factores organizativos")]},
    "3.7.1": {"nombre": "Otros sucesos anteriores de carácter similar",
              "fuentes": [sec(r"^antecedentes", r"^sucesos anteriores",
                              r"^hechos similares")]},
    "3.7.3": {"nombre": "Información sobre riesgos, defectos o disconformidades",
              "fuentes": [sec(r"^riesgos comunicados", r"^defectos o disconformidades",
                              r"^informacion sobre riesgos", r"^riesgos")]},
    "4.3.3": {"nombre": "Causas subyacentes: cualificaciones y mantenimiento",
              "fuentes": [sec(r"^conclusiones", r"^causas subyacentes")]},
    "4.3.4": {"nombre": "Causas relacionadas con el marco normativo",
              "fuentes": [sec(r"^causas relacionadas con el marco normativo",
                              r"^conclusiones", r"^normativa")]},
    "4.4": {"nombre": "Observaciones adicionales",
            "fuentes": [sec(r"^observaciones adicionales", r"^observaciones")]},
    "4.5.2": {"nombre": "Medidas adoptadas después del análisis",
              "fuentes": [sec(r"^medidas adoptadas$", r"^medidas adoptadas",
                              r"^medidas posteriores")]},
    "4.5.3": {"nombre": "Medidas preventivas para evitar la repetición",
              "fuentes": [sec(r"^medidas preventivas", r"^medidas adoptadas")]},
})

CAMPOS_IMAGEN = {  # narrativos largos: se toman como bloque de sección
    "2.1.6": True, "4.1": True, "1.1": True,
}


# ------------------------------------------------------------------ extractores

def extraer_tablas(inf: Informe) -> list[dict]:
    """Filas de las tablas convertidas en la Fase 1 (recomendaciones, etc.)."""
    out = []
    rx = re.compile(r"### Tablas de la p[áa]gina (\d+)\n\n((?:\|.*\|\n)+)", re.M)
    for m in rx.finditer(inf.cuerpo):
        pagina = int(m.group(1))
        lineas = [l for l in m.group(2).strip().splitlines() if l.strip().startswith("|")]
        if len(lineas) < 3:
            continue
        cab = [c.strip() for c in lineas[0].strip("|").split("|")]
        filas = []
        for l in lineas[2:]:
            celdas = [c.strip() for c in l.strip("|").split("|")]
            if len(celdas) < len(cab):
                celdas += [""] * (len(cab) - len(celdas))
            filas.append({cab[i]: celdas[i] for i in range(len(cab)) if cab[i]})
        if filas:
            out.append({"pagina": pagina, "cabecera": cab, "filas": filas,
                        "cita": lineas[0][:200]})
    return out


def evaluar_fuente(inf: Informe, fu: dict, db: dict | None, tablas: list):
    """Devuelve (valor, pagina, cita, origen, regla) o None si no aporta."""
    t = fu["t"]

    if t == "imp" and db:
        val = rutas(db, fu["ruta"])
        if val in (None, "", [], {}):
            return None
        # NUNCA a_texto(val) aquí: para dicts/lists el concatenado ("0 0 0")
        # no existe en el md. Se pasa el valor CRUDO y localizar() recorre sus
        # partes una a una.
        pagina, cita = localizar(inf, val, contexto_rx=fu.get("ctx"))
        return {"valor": val, "pagina": pagina, "cita": cita or "",
                "origen": "importado", "regla": f"db:{fu['ruta']}"}

    if t == "portada":
        m = re.search(fu["rx"], inf.cuerpo[:6000])
        if m:
            v = m.group(1) if m.groups() else m.group(0)
            return {"valor": v.strip(), "pagina": inf.pagina_de(m.start()),
                    "cita": inf.cita_de(m.start()), "origen": "determinista",
                    "regla": "portada"}
        return None

    if t == "seccion_rx":
        m = re.search(fu["rx"], inf.cuerpo)
        if m:
            return {"valor": m.group(1).strip(), "pagina": inf.pagina_de(m.start()),
                    "cita": inf.cita_de(m.start()), "origen": "determinista",
                    "regla": "seccion_rx"}
        return None

    if t == "sec":
        texto, off = inf.bloque_con(*fu["anclas"])
        if not texto:
            return None
        if fu.get("rx"):
            m = re.search(fu["rx"], texto, re.I)
            if not m:
                return None
            off2 = off + m.start()
            return {"valor": m.group(0).strip()[:2000], "pagina": inf.pagina_de(off2),
                    "cita": inf.cita_de(off2), "origen": "determinista",
                    "regla": f"sec:{fu['anclas'][0]}"}
        cuerpo = texto.split("\n", 1)[1] if "\n" in texto else texto
        cuerpo = cuerpo.strip()
        if len(cuerpo) < 10:
            return None
        return {"valor": cuerpo[:6000], "pagina": inf.pagina_de(off),
                "cita": inf.cita_de(off), "origen": "determinista",
                "regla": f"sec:{fu['anclas'][0]}"}

    if t == "tabla":
        if not tablas:
            return None
        campo = fu.get("campo")
        vals, pagina, cita = [], None, None
        for tb in tablas:
            for f in tb["filas"]:
                if campo:
                    # cabeceras variantes: 'Destinatario', 'Implementador final'...
                    k = next((k for k in f if norm(k).startswith(norm(campo))), None)
                    if k and f[k]:
                        vals.append(f[k])
                else:
                    k = next((k for k in f if "recomend" in norm(k)), None)
                    if k and f[k]:
                        vals.append(f[k])
            if vals and pagina is None:
                pagina, cita = tb["pagina"], tb["cita"]
        if not vals:
            return None
        return {"valor": vals, "pagina": pagina, "cita": cita or "",
                "origen": "determinista", "regla": "tabla_md"}

    if t == "multi":
        partes, pagina, cita, verif = {}, None, None, True
        for nombre, rutas_db in fu["partes"]:
            for ruta in rutas_db:
                v = rutas(db, ruta) if db else None
                if v in (None, "", [], {}):
                    continue
                p, c = localizar(inf, v, contexto_rx=nombre)
                partes[nombre] = v
                if p and pagina is None:
                    pagina, cita = p, c
                if p is None:
                    verif = False
                break
            else:
                partes[nombre] = None
                verif = False
        if not any(v is not None for v in partes.values()):
            return None
        return {"valor": partes, "pagina": pagina, "cita": cita or "",
                "origen": "importado", "regla": "multi", "verificado": verif}

    return None


def construir(inf: Informe, db: dict | None, guia: dict) -> dict:
    tablas = extraer_tablas(inf)
    campos: dict[str, dict] = {}

    for ref, spec in guia.items():
        if ref not in CAMPOS:
            campos[ref] = {"nombre": spec.get("campo", ""), "valor_fuente": None,
                           "pagina": None, "cita": None, "origen": "sin_regla",
                           "estado": "pendiente", "verificado": False}
            continue

        resultado = None
        for fu in CAMPOS[ref]["fuentes"]:
            try:
                r = evaluar_fuente(inf, fu, db, tablas)
            except Exception as e:            # una regla rota no tumba el lote
                r = None
                r = None
            if r and r["valor"] not in (None, "", [], {}):
                resultado = r
                break

        if not resultado:
            campos[ref] = {"nombre": CAMPOS[ref]["nombre"], "valor_fuente": None,
                           "pagina": None, "cita": None, "origen": "sin_dato",
                           "estado": NO_CONSTA, "verificado": False}
            continue

        verificado = resultado.get("verificado")
        if verificado is None:
            verificado = bool(resultado["pagina"] and resultado["cita"])
        # DOS NIVELES DE TRAZABILIDAD (decisión de diseño, no un apaño):
        #   cita       → el valor está IMPRESO en el md: página + cita literal
        #   procedencia→ el valor lo derivó el pipeline LLM anterior (v3.*):
        #                 es trazable al INFORME pero no es cita literal, y
        #                marcarlo como verificado sería mentir.
        procedencia = None
        if resultado["valor"] is not None and not (resultado["pagina"] and resultado["cita"]):
            if resultado["origen"] == "importado":
                estado = "importado_llm"
                procedencia = "data/db/reports/ES.json → " + resultado["regla"]
            else:
                estado = "sin_evidencia"
        elif resultado["origen"] == "importado":
            estado = "importado"
        else:
            estado = "determinista"

        campos[ref] = {
            "nombre": CAMPOS[ref]["nombre"],
            "valor_fuente": resultado["valor"],
            "pagina": resultado["pagina"],
            "cita": resultado["cita"],
            "origen": resultado["origen"],
            "regla": resultado["regla"],
            "verificado": bool(verificado and resultado["pagina"]),
            "estado": estado,
        }
        if procedencia:
            campos[ref]["procedencia"] = procedencia

    # listado estructurado del análisis v3 que la guía no tiene como campo
    # propio (la guía pide 2.1.6 "descripción de los hechos" en texto corrido).
    # Se vertebra aquí para que el crudo sea autosuficiente y el Excel pueda
    # abrir la hoja Cronología sin tocar la DB directamente.
    cron = None
    if db:
        cron = rutas(db, "v3.cronologia") or db.get("cronologia")
    if isinstance(cron, list) and cron:
        campos["_cronologia"] = {
            "nombre": "Cronología minuto a minuto (análisis v3)",
            "valor_fuente": cron,
            "pagina": None, "cita": "", "origen": "importado",
            "regla": "db:v3.cronologia",
            "verificado": False, "estado": "importado_llm",
            "procedencia": "data/db/reports/ES.json → v3.cronologia",
        }

    return {
        "id": inf.stem,
        "url_oficial": inf.front.get("url_oficial", ""),
        "pdf": inf.front.get("pdf", ""),
        "md5_pdf": inf.front.get("md5_pdf", ""),
        "paginas_md": int(inf.front.get("paginas", 0) or 0),
        "fecha_proceso": date.today().isoformat(),
        "n_secciones": len(inf.secciones),
        "n_tablas": len(tablas),
        "tablas": tablas,
        "campos": campos,
    }


# ------------------------------------------------------------------ main

def main() -> int:
    argv = sys.argv[1:]
    refrescar = "--refrescar" in argv
    solo = argv[argv.index("--solo") + 1] if "--solo" in argv else None

    guia = {c["ref"]: c for c in json.loads(
        (DATA / "guia_campos.json").read_text(encoding="utf-8"))
        if str(c.get("ref", "")).strip()[:1].isdigit()            # ref numérica
        and (c.get("campo") or c.get("nombre") or "").strip()}    # no es título
    manifest = json.loads((DATA / "manifest_maestro.json").read_text(encoding="utf-8"))
    url_por_stem = {}
    info_por_stem = {}
    for r in manifest["informes"]:
        for ruta in r["pdf_local"] + r["md_local"]:
            url_por_stem[Path(ruta).stem] = r["url_oficial"]
            info_por_stem[Path(ruta).stem] = {
                "clave": r.get("clave", ""),
                "expediente": r.get("expediente") or r.get("expediente_db") or "",
                "anio": r.get("anio"),
                "titulo": r.get("titulo_db") or "",
                "cobertura": r.get("cobertura", ""),
                "estado_cobertura": r.get("cobertura", ""),
            }

    db_por_stem = {}
    if DB_REPORTS.exists():
        for reg in json.loads(DB_REPORTS.read_text(encoding="utf-8")):
            if reg.get("archivo_pdf"):
                db_por_stem[Path(reg["archivo_pdf"]).stem] = reg
            if reg.get("id"):
                db_por_stem.setdefault(reg["id"], reg)

    md_base = sorted(MD_BASE.glob("*.md"))
    if solo:
        md_base = [p for p in md_base if solo.lower() in p.stem.lower()]
    print(f"== Fase 2: crudo con página-evidencia ==  {len(md_base)} md_base")

    CRUDO.mkdir(parents=True, exist_ok=True)
    hechos, saltados, fallidos = 0, 0, 0
    fallos = []

    for ruta in md_base:
        salida = CRUDO / (ruta.stem + ".json")
        if salida.exists() and not refrescar and not solo:
            saltados += 1
            continue
        try:
            inf = Informe(ruta)
            doc = construir(inf, db_por_stem.get(ruta.stem), guia)
            if not doc["url_oficial"]:
                doc["url_oficial"] = url_por_stem.get(ruta.stem, "")
            # identificación (Fase 3 la necesita para abrir la fila del Excel)
            doc.update(info_por_stem.get(ruta.stem, {}))
            doc.setdefault("clave", "")
            doc.setdefault("expediente", "")
            doc.setdefault("anio", None)
            doc.setdefault("titulo", "")
            doc.setdefault("cobertura", "")
            doc["md"] = f"database/md_base/{ruta.name}"
            salida.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                              encoding="utf-8")
            hechos += 1
        except Exception as e:
            fallidos += 1
            fallos.append(f"{ruta.stem}: {type(e).__name__}: {e}")

    # ---------------- informe de cobertura por campo
    docs = []
    for p in sorted(CRUDO.glob("*.json")):
        try:
            docs.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    if docs:
        filas = []
        for ref, spec in guia.items():
            con_valor = sum(1 for d in docs if d["campos"].get(ref, {}).get("valor_fuente")
                            not in (None, "", [], {}))
            con_ev = sum(1 for d in docs if d["campos"].get(ref, {}).get("pagina"))
            verif = sum(1 for d in docs if d["campos"].get(ref, {}).get("verificado"))
            estado = "OK" if con_valor else ("pendiente" if ref in CAMPOS else "sin_regla")
            filas.append({"ref": ref, "campo": spec.get("campo", "")[:56],
                          "con_valor": con_valor, "con_evidencia": con_ev,
                          "verificados": verif, "estado": estado})
        n = len(docs)

        def cuentas(pred):
            return sum(1 for d in docs for r in guia if pred(d["campos"].get(r, {})))

        con_val = cuentas(lambda c: c.get("valor_fuente") not in (None, "", [], {}))
        con_evi = cuentas(lambda c: bool(c.get("pagina")))
        # deterministas: TODO el que tiene valor debe tener cita literal
        det = cuentas(lambda c: c.get("origen") == "determinista"
                      and c.get("valor_fuente") not in (None, "", [], {}))
        det_cita = cuentas(lambda c: c.get("origen") == "determinista"
                           and c.get("valor_fuente") not in (None, "", [], {})
                           and c.get("pagina"))
        # trazabilidad total: cita literal O procedencia declarada
        trazab = cuentas(lambda c: c.get("valor_fuente") not in (None, "", [], {})
                         and (c.get("pagina") or c.get("procedencia")))

        L = ["# Cobertura de la Fase 2 (crudo)", "",
             f"- md procesados: **{n}**",
             f"- escritos ahora: {hechos} · saltados: {saltados} · fallos: {fallidos}", "",
             "| Métrica | Valor |",
             "|---|---|",
             f"| campos con valor | {con_val} / {n * len(guia)} "
             f"({100 * con_val / max(1, n * len(guia)):.1f}%) |",
             f"| **deterministas con cita literal** | {det_cita}/{det} "
             f"(**{100 * det_cita / max(1, det):.1f}%** — gate: 100%) |",
             f"| con cita literal (cualquier origen) | {con_evi}/{con_val} "
             f"({100 * con_evi / max(1, con_val):.1f}%) |",
             f"| **con trazabilidad (cita o procedencia)** | {trazab}/{con_val} "
             f"(**{100 * trazab / max(1, con_val):.1f}%** — gate: 95%) |", "",
             "> `cita` = valor impreso en el md (página + texto literal).",
             "> `procedencia` = valor derivado por el pipeline LLM anterior (v3.*):",
             "> trazable al informe, pero NO es cita literal y por eso no se",
             "> marca como verificado.", "",
             "## Cobertura por campo", "",
             "| Ref | Campo | con valor | con evidencia | verificados | estado |",
             "|---|---|---|---|---|---|"]
        for f in sorted(filas, key=lambda x: (-x["con_valor"], x["ref"])):
            L.append(f"| {f['ref']} | {f['campo']} | {f['con_valor']}/{n} "
                     f"| {f['con_evidencia']}/{n} | {f['verificados']}/{n} | {f['estado']} |")
        if fallos:
            L += ["", "## Fallos", ""] + [f"- {x}" for x in fallos]
        INFORMES.mkdir(parents=True, exist_ok=True)
        (INFORMES / "crudo_cobertura.md").write_text("\n".join(L) + "\n",
                                                     encoding="utf-8")

    print(f"  escritos: {hechos}  saltados: {saltados}  fallos: {fallidos}")
    if fallos:
        for x in fallos[:8]:
            print(f"    - {x[:130]}")
    print("  → database/data/crudo/ + informes/crudo_cobertura.md")

    if fallidos:
        print("  GATE H3: FALLO — hay informes sin procesar")
        return 1
    if docs:
        def cuenta(pred):
            return sum(1 for d in docs for r in guia if pred(d["campos"].get(r, {})))

        con_val = cuenta(lambda c: c.get("valor_fuente") not in (None, "", [], {}))
        det = cuenta(lambda c: c.get("origen") == "determinista"
                    and c.get("valor_fuente") not in (None, "", [], {}))
        det_cita = cuenta(lambda c: c.get("origen") == "determinista"
                          and c.get("valor_fuente") not in (None, "", [], {})
                          and c.get("pagina"))
        trazab = cuenta(lambda c: c.get("valor_fuente") not in (None, "", [], {})
                        and (c.get("pagina") or c.get("procedencia")))
        pct_det = 100 * det_cita / max(1, det)
        pct_traz = 100 * trazab / max(1, con_val)
        print(f"  deterministas con cita literal: {pct_det:.1f}%  ({det_cita}/{det})")
        print(f"  con trazabilidad (cita o procedencia): {pct_traz:.1f}%  ({trazab}/{con_val})")
        if pct_det < 100:
            print("  GATE H3: FALLO — un campo determinista sin cita literal")
            return 1
        if pct_traz < 95:
            print("  GATE H3: PENDIENTE — <95% con trazabilidad (residuos → Fase 4C)")
        else:
            print("  GATE H3: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
