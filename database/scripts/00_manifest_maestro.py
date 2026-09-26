#!/usr/bin/env python3
"""
00_manifest_maestro.py — Fase 0: manifiesto maestro + cruce de cobertura.

Objetivo (gate H1):
  1. Barre la web oficial del CIAF (transportes.gob.es) por año y extrae el
     listado maestro: expediente, fecha, provincia, municipio, tipo,
     fecha de publicación y URL del PDF oficial.
  2. Cruza ese listado contra lo que ya tenemos local (pdfs/, md/, data/db/).
  3. Emite:
       database/data/manifest_maestro.json  → 1 registro por informe conocido
       database/informes/cobertura.md       → explicación de cada diferencia

Resolución de clave por FICHERO (en este orden — cada nivel alimenta al siguiente):
  1. DB consolidada por `archivo_pdf`  (349/349 casan, expediente ya verificado)
  2. Nombre del fichero ⊃ nombre del PDF de la web  (ej. "ES-5925 - 210624-190208-
     if-sn_ciaf.pdf" contiene "210624-190208-if-sn_ciaf.pdf" del listado)
  3. Regex sobre el .md con ANTI-NORMA (descarta "RD 623/2014", "R.D 2387/2004",
     "R.D. 810/2007"... que aparecen en casi todos los informes)
  4. El propio stem si ya es un expediente
  → si nada casa: residuo documentado en cobertura.md (no se inventa clave)

Reglas:
  - Nunca borrar nada; solo crear/modificar.
  - Cortesía: 0,4 s entre peticiones a transportes.gob.es.
  - Reanudable: el HTML de cada año se cachea en data/cache_web/.
  - UA de navegador + Referer obligatorios (403 en caso contrario).

Uso:
  python 00_manifest_maestro.py              # usa cache si existe
  python 00_manifest_maestro.py --refrescar  # re-scrapea la web
"""

import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import urllib.request
import urllib.error

BASE = "https://www.transportes.gob.es"
ERA_BASE = "https://www.era.europa.eu"
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.transportes.gob.es/",
    "Accept-Language": "es-ES,es;q=0.9",
}

RAIZ = Path(__file__).resolve().parent.parent.parent   # era-visor/
DB_DIR = RAIZ / "database"
DATA = DB_DIR / "data"
CACHE = DATA / "cache_web"
INFORMES = DB_DIR / "informes"

ANIO_MIN, ANIO_MAX = 2007, date.today().year

# Patrones de URL por era (verificados 2026-09 contra la web real).
# Se prueban en orden hasta que la página devuelva filas de tabla.
PATRONES = [
    ("infofin", "/organos-colegiados/ciaf/informes-finales-de-sucesos-investigados/infofin-{a}"),
    ("anio", "/organos-colegiados/ciaf/informes-finales-de-sucesos-investigados/{a}"),
    ("sub", "/organos-colegiados/ciaf/informes-finales-de-sucesos-investigados/{a}/informes-accidentes-ferroviarios-{a}"),
    ("mfom", "/MFOM/LANG_CASTELLANO/ORGANOS_COLEGIADOS/CIAF/INFORMES/{a}/"),
]

ESCALPE = re.compile(r"href=(['\"])([^'\"]+\.pdf)\1", re.I)

# Trampas de cruce: cifras que son NORMAS citadas en casi todos los informes,
# no expedientes. Casar con ellas agrupa ficheros ajenos bajo una clave falsa
# (bug real corregido: 20 informes acabaron en "0623/2014" por el RD 623/2014).
CONTEXTO_NORMA = re.compile(
    r"(R\.?\s?D\.?|Real Decreto|Reglamento|Reg\.?|Directiva|Ley|art[ií]culo|"
    r"Norma|ISO|UIC|ANELEC|Código|Anexo)\s*$",
    re.I,
)

# Formatos reales de expediente: "0012/19", "0012/2019", "64/2024", "013/2007"
RX_EXP = re.compile(r"(\d{1,4})\s*/\s*(\d{2,4})")


# ---------------------------------------------------------------- utilidades

def get(path: str, forzar_cache: bool = False) -> str:
    """Devuelve el HTML de una ruta de transportes.gob.es, con cache en disco."""
    CACHE.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", path).strip("_") or "index"
    destino = CACHE / f"{slug}.html"
    if destino.exists() and not forzar_cache:
        return destino.read_text(encoding="utf-8", errors="replace")

    req = urllib.request.Request(BASE + path, headers=UA)
    ultimo = None
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                html = r.read().decode("utf-8", errors="replace")
            destino.write_text(html, encoding="utf-8")
            time.sleep(0.4)
            return html
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code in (404, 403):
                break
            time.sleep(2 + 3 * intento)
        except Exception as e:  # red, timeout
            ultimo = e
            time.sleep(2 + 3 * intento)
    raise RuntimeError(f"GET {path} falló: {ultimo}")


def filas_tabla(html: str) -> list[dict]:
    """Extrae las filas de la tabla de informes (expediente|fecha|...|PDF).

    La web usa la misma tabla en todas las eras; las columnas varían:
      2017+ → expediente | fecha | provincia | municipio | tipo | fecha_pub
      ≤2016 → expediente | fecha | provincia | municipio | tipo
    El enlace al PDF vive DENTRO de la fila (una sola celda lo enlaza).
    """
    filas = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I):
        celdas = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)
        if len(celdas) < 3:
            continue
        txt = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip() for c in celdas]
        txt = [t for t in txt if t]
        if len(txt) < 3:
            continue
        if txt[0].lower().startswith("número de expediente"):
            continue  # cabecera
        if not re.match(r"^\d+/\d{2,4}$", txt[0]):
            continue  # no es una fila de datos
        href = ESCALPE.search(tr)
        filas.append({
            "expediente_web": txt[0],
            "fecha_web": txt[1] if len(txt) > 1 else "",
            "provincia_web": txt[2] if len(txt) > 2 else "",
            "municipio_web": txt[3] if len(txt) > 3 else "",
            "tipo_web": txt[4] if len(txt) > 4 else "",
            "fecha_publicacion_web": txt[5] if len(txt) > 5 else "",
            "url_pdf_web": (BASE + href.group(2)) if href else "",
        })
    return filas


def clave(expediente) -> tuple | None:
    """Normaliza un expediente a (número:int, año:int).

    Acepta los formatos reales: '0012/19', '0012/2019', '64/2024'.
    """
    if not expediente:
        return None
    m = re.match(r"^\s*(\d{1,4})\s*/\s*(\d{2,4})\s*$", str(expediente).strip())
    if not m:
        return None
    num = int(m.group(1))
    anio = int(m.group(2))
    if anio < 100:                       # 2 dígitos → siglo
        anio += 2000 if anio < 70 else 1900
    return (num, anio)


def a_iso(fecha: str) -> str:
    """'08/02/2019' → '2019-02-08'. Devuelve '' si no se puede."""
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", (fecha or "").strip())
    if not m:
        return ""
    d, mes, a = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return date(a, mes, d).isoformat()
    except ValueError:
        return ""


def clave_desde_md(texto: str) -> tuple | None:
    """Extrae el expediente del texto de un informe DESCARTANDO normas citadas.

    Sin este filtro, '(RD 623/2014, artículo 4.5)' devolvía (623, 2014) y 20
    informes distintos acababan agrupados bajo la misma clave falsa.
    """
    for m in RX_EXP.finditer(texto[:6000]):
        ctx = texto[max(0, m.start() - 60):m.start()]
        if CONTEXTO_NORMA.search(ctx):
            continue
        k = clave(m.group(0))
        if k and 2004 <= k[1] <= date.today().year:
            return k
    return None


# ------------------------------------------------------------ scrape web CIAF

def scrape_web_ciaf(refrescar: bool = False) -> list[dict]:
    """Recorre todos los años y devuelve el listado maestro de la web."""
    cache_json = DATA / "listado_web_ciaf.json"
    if cache_json.exists() and not refrescar:
        datos = json.loads(cache_json.read_text(encoding="utf-8"))
        print(f"[cache] listado web ya presente ({datos.get('n', '?')} informes, "
              f"scrape {datos.get('fecha_scrape', '?')}): {cache_json.name}")
        return datos["informes"]

    filas: list[dict] = []
    patron_por_anio: dict[int, str] = {}

    for anio in range(ANIO_MIN, ANIO_MAX + 1):
        encontradas: list[dict] = []
        usado = ""
        for nombre, plantilla in PATRONES:
            ruta = plantilla.format(a=anio)
            try:
                html = get(ruta, forzar_cache=refrescar)
            except Exception:
                continue
            cands = filas_tabla(html)
            if cands:
                encontradas, usado = cands, nombre
                break  # el primer patrón que da filas manda
        if encontradas:
            for f in encontradas:
                f["anio_web"] = anio
                f["patron_url"] = usado
            filas.extend(encontradas)
            patron_por_anio[anio] = usado
            print(f"  {anio}: {len(encontradas):3} informes  [{usado}]")
        else:
            patron_por_anio[anio] = "ninguno"
            print(f"  {anio}:   0 informes  [sin patrón válido]")

    # Dedupe por clave de expediente (una misma URL puede repetirse en 2 páginas)
    vistos, unicas = set(), []
    for f in filas:
        k = clave(f["expediente_web"])
        if k is None:
            unicas.append(f)
            continue
        if k in vistos:
            continue
        vistos.add(k)
        unicas.append(f)

    DATA.mkdir(parents=True, exist_ok=True)
    out = {
        "fecha_scrape": date.today().isoformat(),
        "fuente": BASE + "/organos-colegiados/ciaf/informes-finales-de-sucesos-investigados",
        "patrones_por_anio": patron_por_anio,
        "n": len(unicas),
        "informes": unicas,
    }
    cache_json.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[guardado] {cache_json.name} → {len(unicas)} informes de la web")
    return unicas


# --------------------------------------------------------------- inventario local

def inventario_local(listado_web: list[dict]) -> tuple[dict, dict, dict]:
    """Lee el estado local: PDFs, .md, registros DB y URLs de ERA.

    Devuelve:
      unidades  → {clave: {"pdfs":[], "mds":[], "db":reg, "url_era":str}}
      db        → {clave: registro_DB}
      stats     → desglose de por qué se resolvió cada fichero
    """
    pdfs = {p.stem: p for p in (RAIZ / "pdfs" / "ES").glob("*.pdf")}
    mds = {p.stem: p for p in (RAIZ / "md" / "ES").glob("*.md")}

    # --- índice 1: DB consolidada por fichero (349/349 casan) -------------
    db_por_stem, db = {}, {}
    ruta_db = RAIZ / "data" / "db" / "reports" / "ES.json"
    if ruta_db.exists():
        for r in json.loads(ruta_db.read_text(encoding="utf-8")):
            k = clave(r.get("expediente", ""))
            if k:
                db[k] = r
            ruta = str(r.get("archivo_pdf") or "")
            if ruta:
                db_por_stem[Path(ruta).stem] = k

    # --- índice 2: nombre del PDF de la web --------------------------------
    web_por_nombre: dict[str, tuple] = {}
    for w in listado_web:
        nombre = Path(w.get("url_pdf_web") or "").name.lower()
        k = clave(w["expediente_web"])
        if len(nombre) >= 8 and k:
            web_por_nombre.setdefault(nombre, k)

    # --- índice 3: URL de ERA por fichero (manifest del scraper) ----------
    # OJO: las rutas del manifest vienen URL-encoded (ID-...-DGF_El%20Carri%C3%B3n);
    # sin decodificar, el stem no casa con el fichero local y se pierde la URL.
    import urllib.parse

    url_era_por_stem: dict[str, str] = {}
    ruta_man = RAIZ / "data" / "pdf-manifest" / "ES.json"
    if ruta_man.exists():
        for m in json.loads(ruta_man.read_text(encoding="utf-8")):
            ruta = str(m.get("pdf") or "")
            if ruta:
                # la URL de salida queda encoded (es la válida); solo decodificamos
                # para indexar por nombre de fichero
                url_era_por_stem[Path(urllib.parse.unquote(ruta)).stem] = ERA_BASE + ruta

    stats = {"db": 0, "nombre_web": 0, "contenido_md": 0, "stem": 0, "sin_clave": 0}
    resuelta: dict[str, tuple | None] = {}   # stem → clave (o None)

    for stem in sorted(set(pdfs) | set(mds)):
        k = None
        origen = ""

        # 1) DB por fichero
        if stem in db_por_stem and db_por_stem[stem]:
            k, origen = db_por_stem[stem], "db"

        # 2) el nombre del fichero contiene el nombre del PDF de la web
        if k is None:
            bajo = stem.lower()
            for nombre, kw in web_por_nombre.items():
                if nombre.startswith(".pdf"):
                    continue
                base = nombre[:-4]                      # sin extensión
                if len(base) >= 8 and base in bajo:
                    k, origen = kw, "nombre_web"
                    break

        # 3) contenido del .md (con anti-norma)
        if k is None and stem in mds:
            texto = mds[stem].read_text(encoding="utf-8", errors="replace")
            k = clave_desde_md(texto)
            if k:
                origen = "contenido_md"

        # 4) el stem ya es un expediente
        if k is None:
            k = clave(stem)
            if k:
                origen = "stem"

        resuelta[stem] = k
        stats[origen or "sin_clave"] += 1

    # --- agrupa por clave ---------------------------------------------------
    unidades: dict[str, dict] = {}

    def u(k):
        return unidades.setdefault(k, {"pdfs": [], "mds": [], "db": None, "url_era": ""})

    for stem, k in resuelta.items():
        if k is None:
            u(None)
        if stem in pdfs:
            u(k)["pdfs"].append(str(pdfs[stem].relative_to(RAIZ)).replace("\\", "/"))
            if not u(k)["url_era"]:
                u(k)["url_era"] = url_era_por_stem.get(stem, "")
        if stem in mds:
            u(k)["mds"].append(str(mds[stem].relative_to(RAIZ)).replace("\\", "/"))
    for k, reg in db.items():
        u(k)["db"] = reg
        if not u(k)["url_era"]:
            u(k)["url_era"] = reg.get("url_pdf") or ""

    n_sin = sum(1 for k in resuelta if k is None)
    print(f"[local] {len(pdfs)} PDFs · {len(mds)} .md · {len(db)} registros DB")
    print(f"[claves] db={stats['db']} nombre_web={stats['nombre_web']} "
          f"contenido_md={stats['contenido_md']} stem={stats['stem']} "
          f"sin_clave={stats['sin_clave']}  (ficheros: {len(resuelta)})")
    if n_sin:
        print(f"[AVISO] {n_sin} ficheros sin clave de expediente → residuo documentado")
    return unidades, db, stats


# ------------------------------------------------------------------- manifiesto

def construir_manifest(listado_web: list[dict], unidades: dict, db: dict) -> dict:
    """Une web + local en un manifiesto 1-registro-por-informe."""
    claves_web = set()
    registros = []

    def fila(k, origen):
        reg = unidades.get(k, {"pdfs": [], "mds": [], "db": None, "url_era": ""})
        dbreg = reg.get("db")
        return {
            "clave": f"{k[0]:04d}/{k[1]}" if k else "",
            "expediente": "",
            "anio": k[1] if k else None,
            # --- fuentes ---
            "url_oficial_ciaf": "",
            "url_oficial_era": reg.get("url_era", ""),
            "url_oficial": "",           # la que usará el Excel (prioridad CIAF)
            "origen_url": "",
            # --- estado local ---
            "pdf_local": reg["pdfs"],
            "md_local": reg["mds"],
            "en_db": bool(dbreg),
            "url_era_db": (dbreg or {}).get("url_pdf") or "",
            "expediente_db": (dbreg or {}).get("expediente") or "",
            "fecha_suceso_db": (dbreg or {}).get("fecha") or "",
            "titulo_db": ((dbreg or {}).get("titulo") or "")[:200],
            "id_db": (dbreg or {}).get("id") or "",
            # --- datos de la web (listado maestro) ---
            "fecha_suceso_web": "",
            "provincia_web": "",
            "municipio_web": "",
            "tipo_web": "",
            "fecha_publicacion_web": "",
            "presente_en_web": False,
            "cobertura": "",
            "_origen_cruce": origen,
        }

    # 1) filas del listado maestro (la web manda en expediente/fecha/provincia)
    for w in listado_web:
        k = clave(w["expediente_web"])
        claves_web.add(k)
        r = fila(k, "web+local" if k in unidades else "solo_web")
        r.update({
            "expediente": w["expediente_web"],
            "url_oficial_ciaf": w["url_pdf_web"],
            "fecha_suceso_web": a_iso(w["fecha_web"]),
            "provincia_web": w["provincia_web"],
            "municipio_web": w["municipio_web"],
            "tipo_web": w["tipo_web"],
            "fecha_publicacion_web": a_iso(w["fecha_publicacion_web"]),
            "presente_en_web": True,
        })
        r["url_oficial"] = r["url_oficial_ciaf"] or r["url_oficial_era"]
        r["origen_url"] = "CIAF" if r["url_oficial_ciaf"] else ("ERA" if r["url_oficial_era"] else "")
        registros.append(r)

    # 2) unidades locales que la web no lista (o no se pudieron cruzar)
    for k, reg in unidades.items():
        if k in claves_web:
            continue
        r = fila(k, "solo_local" if k else "sin_expediente")
        r["expediente"] = r["expediente_db"] or (r["clave"] or "")
        r["url_oficial"] = r["url_oficial_era"] or r["url_era_db"]
        r["origen_url"] = "ERA" if r["url_oficial"] else ""
        registros.append(r)

    # 3) url_oficial obligatoria + estado de cobertura
    sin_url = 0
    for r in registros:
        if not r["url_oficial"]:
            r["url_oficial"] = r["url_oficial_ciaf"] or r["url_oficial_era"] or r["url_era_db"]
            r["origen_url"] = ("CIAF" if r["url_oficial_ciaf"]
                               else ("ERA" if r["url_oficial"] else ""))
        if not r["url_oficial"]:
            sin_url += 1
        tiene_local = bool(r["pdf_local"] or r["md_local"])
        if r["presente_en_web"] and tiene_local:
            r["cobertura"] = "completo"
        elif r["presente_en_web"]:
            r["cobertura"] = "en_web_falta_local"
        elif tiene_local:
            r["cobertura"] = "solo_local"
        else:
            r["cobertura"] = "referencia_vacia"

    registros.sort(key=lambda r: (r["anio"] or 0, r["expediente"] or ""))
    return {
        "version": date.today().isoformat(),
        "n": len(registros),
        "sin_url_oficial": sin_url,
        "por_cobertura": {
            c: sum(1 for r in registros if r["cobertura"] == c)
            for c in ("completo", "en_web_falta_local", "solo_local", "referencia_vacia")
        },
        "informes": registros,
    }


def escribir_cobertura(manifest: dict, listado_web: list[dict], stats: dict) -> Path:
    """Informe legible: cuadra o no la cobertura contra la web oficial."""
    regs = manifest["informes"]
    from collections import Counter, defaultdict

    cob = manifest["por_cobertura"]
    faltan = [r for r in regs if r["cobertura"] == "en_web_falta_local"]
    sobran = [r for r in regs if r["cobertura"] == "solo_local"]
    sin_url = [r for r in regs if not r["url_oficial"]]
    sin_exp = [r for r in regs if not r["clave"]]

    por_anio = defaultdict(lambda: Counter())
    for r in regs:
        if r["anio"]:
            por_anio[r["anio"]][r["cobertura"]] += 1

    L = []
    L.append("# Cobertura — base de datos CIAF España\n")
    L.append(f"Generado: {manifest['version']} · fuente maestra: web oficial del CIAF "
             f"({len(listado_web)} informes listados)\n")
    L.append("## Resumen\n")
    L.append("| Estado | N.º | Significado |")
    L.append("|---|---:|---|")
    L.append(f"| completo | {cob['completo']} | en la web + PDF/md local |")
    L.append(f"| en_web_falta_local | {cob['en_web_falta_local']} | **publicado en la web y no lo tenemos** |")
    L.append(f"| solo_local | {cob['solo_local']} | lo tenemos y la web no lo lista |")
    L.append(f"| referencia_vacia | {cob['referencia_vacia']} | entrada sin fichero ni registro |")
    L.append(f"| **total** | **{manifest['n']}** | |")
    L.append(f"| sin url oficial | {manifest['sin_url_oficial']} | debe ser 0 para el gate H1 |")
    L.append("")

    L.append("## Cómo se resolvió la clave de cada fichero\n")
    L.append("| Vía | Ficheros | Fiabilidad |")
    L.append("|---|---:|---|")
    L.append(f"| DB consolidada (`archivo_pdf`) | {stats['db']} | alta — expediente verificado |")
    L.append(f"| nombre ⊃ PDF de la web | {stats['nombre_web']} | alta — nombre único de la web |")
    L.append(f"| contenido del .md (anti-norma) | {stats['contenido_md']} | media — revisar residuos |")
    L.append(f"| el stem ya era expediente | {stats['stem']} | media |")
    L.append(f"| **sin clave (residuo)** | **{stats['sin_clave']}** | requiere revisión manual |")
    L.append("")

    if faltan:
        L.append(f"## En la web y falta local ({len(faltan)})\n")
        L.append("| Expediente | Año | Fecha | Provincia | Municipio | PDF oficial |")
        L.append("|---|---|---|---|---|---|")
        for r in faltan:
            L.append(f"| {r['expediente']} | {r['anio']} | {r['fecha_suceso_web']} | "
                     f"{r['provincia_web']} | {r['municipio_web']} | [pdf]({r['url_oficial_ciaf']}) |")
        L.append("")
    else:
        L.append("## En la web y falta local\n\nNinguno. ✔\n")

    if sin_exp:
        L.append(f"## Sin clave de expediente ({len(sin_exp)}) — residuo\n")
        L.append("Ficheros que ninguna vía pudo identificar. Revisión manual, no se inventa clave.\n")
        L.append("| PDF local | MD local | url ERA |")
        L.append("|---|---|---|")
        for r in sin_exp:
            L.append(f"| {r['pdf_local'][0] if r['pdf_local'] else '—'} | "
                     f"{r['md_local'][0] if r['md_local'] else '—'} | "
                     f"{r['url_oficial'] or '—'} |")
        L.append("")

    if sobran:
        L.append(f"## En local y no está en la web ({len(sobran)})\n")
        L.append("Casos legítimos esperados: informes anteriores a 2007 publicados solo en ERA "
                 "o informes de organismos distintos al CIAF (DGF, FEVE). Revisar los que no "
                 "encajen en esa descripción.\n")
        L.append("| Expediente | Año | PDF local | url | En DB |")
        L.append("|---|---|---|---|---|")
        for r in sobran:
            pdf = r["pdf_local"][0] if r["pdf_local"] else (r["md_local"][0] if r["md_local"] else "—")
            L.append(f"| {r['clave'] or '(sin clave)'} | {r['anio'] or '?'} | {pdf} | "
                     f"{r['url_oficial'] or '—'} | {'sí' if r['en_db'] else 'no'} |")
        L.append("")

    if sin_url:
        L.append(f"## Sin URL oficial ({len(sin_url)}) — bloquea el gate H1\n")
        for r in sin_url:
            L.append(f"- `{r['clave']}` {r['pdf_local']} {r['md_local']}")
        L.append("")

    L.append("## Cobertura por año\n")
    L.append("| Año | completo | falta local | solo local | total |")
    L.append("|---:|---:|---:|---:|---:|")
    for anio in sorted(por_anio):
        c = por_anio[anio]
        tot = sum(c.values())
        L.append(f"| {anio} | {c['completo']} | {c['en_web_falta_local']} | "
                 f"{c['solo_local']} | {tot} |")
    L.append("")

    INFORMES.mkdir(parents=True, exist_ok=True)
    destino = INFORMES / "cobertura.md"
    destino.write_text("\n".join(L), encoding="utf-8")
    print(f"[informe] {destino.relative_to(RAIZ)}")
    return destino


def main() -> int:
    refrescar = "--refrescar" in sys.argv
    DATA.mkdir(parents=True, exist_ok=True)

    print("== 1. Scraping del listado maestro (web CIAF) ==")
    listado = scrape_web_ciaf(refrescar=refrescar)

    print("\n== 2. Inventario local (pdfs/md/db/urls ERA) ==")
    unidades, db, stats = inventario_local(listado)

    print("\n== 3. Cruce y manifiesto ==")
    manifest = construir_manifest(listado, unidades, db)
    out = DATA / "manifest_maestro.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[guardado] {out.relative_to(RAIZ)} → {manifest['n']} registros")

    print("\n== 4. Informe de cobertura ==")
    escribir_cobertura(manifest, listado, stats)

    cob = manifest["por_cobertura"]
    print("\n== RESULTADO ==")
    print(f"  web (maestro)     : {len(listado)}")
    print(f"  total manifiesto  : {manifest['n']}")
    print(f"  completo          : {cob['completo']}")
    print(f"  falta local       : {cob['en_web_falta_local']}")
    print(f"  solo local        : {cob['solo_local']}")
    print(f"  sin url oficial   : {manifest['sin_url_oficial']}")

    if manifest["sin_url_oficial"]:
        print("  GATE H1: FALLO — hay informes sin url oficial (ver cobertura.md)")
        return 1
    print("  GATE H1: OK — 100% con url oficial")
    return 0


if __name__ == "__main__":
    sys.exit(main())
