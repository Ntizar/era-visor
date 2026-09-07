# -*- coding: utf-8 -*-
"""
Sistema de limpieza y comprobación integral del visor.

Verifica la cadena PDF → md → json → DB y la calidad geográfica, y emite un
informe accionable en markdown: data/revision/{PAIS}-verificacion.md

Comprobaciones (cada una detectó un bug real en era-visor, 2026-09):
  1. Integridad 1:1 de la cadena (huérfanos en cada dirección; OCR pendiente
     se clasifica aparte, no como pérdida)
  2. Duplicados por contenido (md5 de PDFs)
  3. Salud de los PDFs (magic bytes %PDF-, tamaño, capa de texto)
  4. Salud de la DB (ids duplicados, fantasmas index vs reports, campos)
  5. Schema: cada json de la colección viva tiene su v3 en json/ES/v3/
  6. Auditoría geográfica: los MAL y DUDOSOS se listan SIEMPRE en el informe
     con su motivo (requisito expreso del usuario)
  7. Cache-busting: VERSION_DATOS vs fecha de regeneración de la DB

Limpieza (opt-in):  --limpiar  archiva (NUNCA borra) los PDFs duplicados por
contenido y sus md/json sobrantes en */_duplicados_descartados/, conservando
el stem que vive en la DB.

Uso:   python scripts/verificar_todo.py ES [--limpiar]
Salida: 0 sin errores críticos, 1 con errores.
"""
import hashlib
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

args = [a for a in sys.argv[1:]]
PAIS = next((a.upper() for a in args if not a.startswith("--")), "ES")
LIMPIAR = "--limpiar" in args
RAIZ = Path(__file__).resolve().parent.parent
DESCARTE = "_duplicados_descartados"
UMBRAL_PDF_KB = 10
CLAVES_V3 = ["hechos", "cronologia", "causas", "lecciones"]

_informe = []
_stats = {"ERROR": 0, "AVISO": 0, "OK": 0}


def check(nombre):
    def registrar(nivel, detalle=""):
        _stats[nivel] += 1
        _informe.append(f"- **[{nivel}]** {nombre}: {detalle}")
    return registrar


def section(titulo):
    _informe.append(f"\n## {titulo}\n")


def vivo(p: Path, base: Path) -> bool:
    """Fichero de la colección viva (no archivado en _duplicados_descartados)."""
    return DESCARTE not in str(p.relative_to(base))


def dir_or_create(d: Path):
    d.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------- 1. Integridad cadena
def comprobar_cadena():
    section("1. Integridad de la cadena PDF ↔ md ↔ json ↔ DB")
    dpdf, dmd = RAIZ / "pdfs" / PAIS, RAIZ / "md" / PAIS
    djson, dv3 = RAIZ / "json" / PAIS, RAIZ / "json" / PAIS / "v3"

    pdfs = {p.stem for p in dpdf.glob("*.pdf") if vivo(p, dpdf)} if dpdf.exists() else set()
    mds_all = {p.stem for p in dmd.glob("*.md") if vivo(p, dmd)} if dmd.exists() else set()
    jsons = {p.stem for p in djson.glob("*.json") if vivo(p, djson)} if djson.exists() else set()
    v3s = {p.stem for p in dv3.glob("*.json")} if dv3.exists() else set()

    # .md marcados como escaneados pendientes de OCR: no son pérdida
    ocr = {s for s in (mds_all - jsons)
           if "Pendiente de OCR" in (dmd / f"{s}.md").read_text(encoding="utf-8", errors="ignore")}
    md_huerfano = (mds_all - jsons) - ocr

    check("pdf→md")("OK" if pdfs <= mds_all else "AVISO",
                    f"{len(pdfs & mds_all)}/{len(pdfs)} PDFs con .md; sin md: "
                    + (", ".join(sorted(pdfs - mds_all)[:5]) or "ninguno"))
    if not md_huerfano:
        check("md→json")("OK", f"{len(mds_all & jsons)} .md estructurados en json")
    else:
        check("md→json")("ERROR", f"{len(md_huerfano)} .md reales sin json: "
                      + ", ".join(sorted(md_huerfano)[:5]))
    if ocr:
        check("OCR pendiente")("AVISO", f"{len(ocr)} escaneados sin capa de texto, sin estructurar: "
                            + ", ".join(sorted(ocr)[:5]))
    extra_json = jsons - mds_all
    if extra_json:
        check("json→md")("AVISO", f"{len(extra_json)} json sin .md (imports antiguos): "
                       + ", ".join(sorted(extra_json)[:5]))

    # json ↔ v3
    sin_v3 = jsons - v3s
    if not sin_v3:
        check("json→v3")("OK", f"{len(v3s & jsons)} json con análisis v3")
    else:
        check("json→v3")("AVISO", f"{len(sin_v3)} json sin v3: " + ", ".join(sorted(sin_v3)[:6]))

    # DB ↔ json
    rp = RAIZ / "data" / "db" / "reports" / f"{PAIS}.json"
    if not rp.exists():
        check("DB")("ERROR", "no existe data/db/reports/%s.json — ejecutar consolidar.py" % PAIS)
        return None
    db = json.loads(rp.read_text(encoding="utf-8"))
    stems_db = {r["id"].split("-", 1)[1] for r in db if r["id"].startswith(PAIS + "-")}
    db_sin_json = {s for s in stems_db if s not in jsons}
    if db_sin_json:
        check("DB→json")("ERROR", f"{len(db_sin_json)} registros DB cuyo stem json ya no está (¿archivado sin reconsolidar?): "
                      + ", ".join(sorted(db_sin_json)[:5]))
    else:
        check("DB→json")("OK", f"{len(db)} registros DB con json origen")
    return db


# --------------------------------------------------------------- 2. Duplicados
def comprobar_dupes_pdfs(db):
    section("2. Duplicados por contenido (md5 de PDFs)")
    dpdf = RAIZ / "pdfs" / PAIS
    if not dpdf.exists():
        check("dupes")("AVISO", "sin carpeta pdfs/")
        return
    grupos = {}
    for p in dpdf.glob("*.pdf"):
        if not vivo(p, dpdf):
            continue
        grupos.setdefault(hashlib.md5(p.read_bytes()).hexdigest(), []).append(p)
    repetidos = [g for g in grupos.values() if len(g) > 1]
    db_ids = {r["id"] for r in db} if db else set()
    sobrantes = []
    for g in repetidos:
        # conservador: el stem que vive en la DB; si ninguno, el nombre más corto
        keeper = next((p for p in g if f"{PAIS}-{p.stem}" in db_ids), min(g, key=lambda p: len(p.stem)))
        sobrantes += [p for p in g if p != keeper]

    if not repetidos:
        check("md5")("OK", f"{sum(len(g) for g in grupos.values())} PDFs, 0 duplicados por contenido")
        return
    if not sobrantes:
        return
    nombres = ", ".join(p.name for p in sobrantes)
    if not LIMPIAR:
        check("md5")("ERROR", f"{len(sobrantes)} PDFs sobrantes idénticos (ejecutar con --limpiar para archivar): {nombres}")
        return
    movidos = 0
    for p in sobrantes:
        for base, glob in ((RAIZ / "pdfs" / PAIS, p.name),
                           (RAIZ / "md" / PAIS, p.stem + ".md"),
                           (RAIZ / "json" / PAIS, p.stem + ".json"),
                           (RAIZ / "json" / PAIS / "v3", p.stem + ".json")):
            f = base / glob
            if f.exists():
                dest = base / DESCARTE
                dir_or_create(dest)
                shutil.move(str(f), str(dest / f.name))
                movidos += 1
    check("md5")("AVISO", f"--limpiar: {len(sobrantes)} stems duplicados archivados ({movidos} ficheros movidos a */{DESCARTE}/); NUNCA se borra nada")


# ---------------------------------------------------------------------- 3. PDFs
def comprobar_pdfs():
    section("3. Salud de los PDFs")
    dpdf = RAIZ / "pdfs" / PAIS
    if not dpdf.exists():
        check("pdfs")("AVISO", "sin carpeta pdfs/")
        return
    pdfs = [p for p in dpdf.glob("*.pdf") if vivo(p, dpdf)]
    malos = [p.name for p in pdfs if not p.read_bytes()[:5] == b"%PDF-"]
    pequenos = [p.name for p in pdfs if p.stat().st_size < UMBRAL_PDF_KB * 1024]
    if not malos:
        check("magic bytes")("OK", f"{len(pdfs)} PDFs válidos (los bloqueos HTML llegarían aquí)")
    else:
        check("magic bytes")("ERROR", f"{len(malos)} PDFs corruptos o HTML-bloqueo: " + ", ".join(malos[:5]))
    if pequenos:
        check("tamaño")("AVISO", f"{len(pequenos)} PDFs < {UMBRAL_PDF_KB} KB: " + ", ".join(pequenos[:5]))
    else:
        check("tamaño")("OK", f"todos ≥ {UMBRAL_PDF_KB} KB")


# ------------------------------------------------------------------------ 4. DB
def comprobar_db(db):
    section("4. Salud del índice de la DB")
    ip = RAIZ / "data" / "db" / "index.json"
    if not ip.exists() or db is None:
        check("index")("ERROR", "falta index.json o reports")
        return
    index = json.loads(ip.read_text(encoding="utf-8"))
    ids = [x["id"] for x in index]
    dupes = {i for i in ids if ids.count(i) > 1}
    check("ids únicos")("OK" if not dupes else "ERROR",
                        f"{len(ids)} entradas" if not dupes else "repetidos: " + ", ".join(sorted(dupes)[:5]))
    idx_pais = {x["id"] for x in index if x.get("pais") == PAIS}
    ids_db = {r["id"] for r in db}
    fan, hue = idx_pais - ids_db, ids_db - idx_pais
    check("fantasmas")("OK" if not fan else "ERROR",
                       f"index {PAIS} == reports ({len(ids_db)}), 0 fantasmas" if not fan
                       else f"{len(fan)} entradas index sin ficha (el visor las pinta 'None'): " + ", ".join(sorted(fan)[:5]))
    if hue:
        check("sin index")("ERROR", f"{len(hue)} fichas sin entrada index")
    mala = [x["id"] for x in index if x.get("pais") == PAIS
            and (not x.get("fecha") or not x.get("titulo") or not isinstance(x.get("fallecidos"), int))]
    check("campos index")("OK" if not mala else "AVISO",
                          "fecha/título/fallecidos OK" if not mala
                          else f"{len(mala)} con campos inválidos: " + ", ".join(mala[:5]))
    # consecuencias v3 propagadas (el gráfico de víctimas depende de esto)
    sin_v3prop = [r["id"] for r in db
                  if r.get("v3", {}).get("consecuencias", {}).get("fallecidos") is not None
                  and r["fallecidos"] != r["v3"]["consecuencias"]["fallecidos"]]
    check("víctimas v3→DB")("OK" if not sin_v3prop else "ERROR",
                            "las consecuencias v3 mandan en todos los registros" if not sin_v3prop
                            else f"{len(sin_v3prop)} registros con fallecidos ≠ v3: " + ", ".join(sin_v3prop[:5]))
    # un solo registro por expediente (el dedupe de consolidar debe ser hermético)
    dexp = defaultdict(list)
    for r in db:
        if r.get("expediente"):
            dexp[r["expediente"]].append(r["id"])
    rep = {k: v for k, v in dexp.items() if len(v) > 1}
    check("1 registro por expediente")("OK" if not rep else "ERROR",
        f"{len(dexp)} expedientes, 0 duplicados" if not rep
        else f"{len(rep)} expedientes duplicados: " + "; ".join(f"{k}→{v}" for k, v in list(rep.items())[:4]))
    # coords calcadas entre registros: legitimas si el PK coincide (varios
    # accidentes en el mismo punto, ej. paso a nivel conflictivo); sospechosas
    # si los PK difieren (>50 m) y aun asi cayeron en la misma coordenada
    def _pk_num(s):
        m = re.search(r"(\d+)\s*[+,.]\s*(\d{1,3})", s or "")
        if m:
            return int(m.group(1)) + float("0." + m.group(2))
        m = re.search(r"\d+", s or "")
        return float(m.group()) if m else None
    por_c = defaultdict(list)
    for r in db:
        if r.get("lat") and r.get("lng"):
            por_c[(round(r["lat"], 4), round(r["lng"], 4))].append(r)
    leg, sos = 0, []
    for rs in por_c.values():
        if len(rs) < 2:
            continue
        pks = [_pk_num(x.get("pk")) for x in rs]
        known = [p for p in pks if p is not None]
        if not known or max(known) - min(known) <= 0.05 or len(known) != len(rs):
            leg += 1  # mismo PK, o sin PK (ambos por estacion) -> punto legitimo
        else:
            sos.append("≡".join(f"{x.get('expediente')}(PK {x.get('pk')})" for x in rs))
    check("coords gemelas")("AVISO" if sos else "OK",
        f"{leg} grupos de informes distintos en el mismo punto (PK coincidente o estación)" if not sos
        else f"{leg} legítimas; SOSPECHOSAS {len(sos)} (PK distintos, misma coord): " + "; ".join(sos[:5]))


# ------------------------------------------------------------------ 5-6-7 etc.
def comprobar_geografia():
    section("5. Auditoría geográfica — los mal geolocalizados, SIEMPRE a la vista")
    ruta = RAIZ / "data" / "revision" / f"{PAIS}-localizacion.json"
    if not ruta.exists():
        check("auditor")("ERROR", "no existe el informe del auditor — ejecutar revisar_localizacion.py")
        return
    rev = json.loads(ruta.read_text(encoding="utf-8"))
    por = {}
    for e in rev:
        por.setdefault(e.get("veredicto", "?"), []).append(e)
    resumen = " · ".join(f"{k}={len(v)}" for k, v in sorted(por.items()))
    check("veredictos")("AVISO" if por.get("mal") else "OK", f"{len(rev)} informes auditados: {resumen}")
    pmal = [e for e in rev if e.get("provincia_ok") is False]
    check("provincia")("AVISO" if pmal else "OK",
                       (f"{len(pmal)} con provincia declarada ≠ provincia de la red" if pmal
                        else "provincia OK en todos los comparables"))

    for etiqueta, clave in (("MAL GEOLocalIZADOS", "mal"), ("DUDOSOS", "duda")):
        casos = sorted(por.get(clave, []), key=lambda e: -(e.get("dist_via_m") or 0))
        if not casos:
            _informe.append(f"\n**{etiqueta}: ninguno.**\n")
            continue
        _informe.append(f"\n**{etiqueta} — {len(casos)} informes** (verificar contra el PDF original):\n")
        _informe.append("| Informe | Provincia | PK | Línea | A la vía | Motivo |\n|---|---|---|---|---|---|")
        for e in casos:
            _informe.append(
                f"| `{e.get('id','?')}` | {e.get('provincia') or '—'} | {e.get('pk') or '—'} "
                f"| {str(e.get('linea') or '—')[:26]} | {e.get('dist_via_m','?')} m "
                f"| {(e.get('motivo') or '—').replace('|','/')} |")
        _informe.append("")


def comprobar_version():
    section("6. Cache-busting del frontend")
    p, db = RAIZ / "frontend" / "index.html", RAIZ / "data" / "db" / "index.json"
    if not p.exists() or not db.exists():
        check("version")("AVISO", "sin frontend o index de DB")
        return
    m = re.search(r'VERSION_DATOS\s*=\s*"([^"]+)"', p.read_text(encoding="utf-8"))
    if not m:
        check("VERSION_DATOS")("ERROR", "no se encuentra la constante en el frontend")
        return
    version = m.group(1)
    try:
        vfecha = datetime.strptime(version.rsplit("-", 1)[0], "%Y-%m-%d")
    except ValueError:
        check("VERSION_DATOS")("AVISO", f"formato insólito: {version}")
        return
    mtime = datetime.fromtimestamp(db.stat().st_mtime)
    check("VERSION_DATOS")("OK" if vfecha.date() >= mtime.date() else "ERROR",
                           f"{version} cubre la DB ({mtime.date()})"
                           if vfecha.date() >= mtime.date()
                           else f"{version} es anterior a la DB regenerada ({mtime.date()}) — bump antes de desplegar")


def main():
    print(f"[VERIF] Comprobación integral de {PAIS}{' con limpieza' if LIMPIAR else ''} …")
    db = comprobar_cadena()
    comprobar_dupes_pdfs(db)
    comprobar_pdfs()
    comprobar_db(db)
    comprobar_geografia()
    comprobar_version()

    veredicto = "APTO" if _stats["ERROR"] == 0 else f"NO APTO — {_stats['ERROR']} errores críticos"
    informe = (f"# Informe de verificación — {PAIS}\n\n"
               f"> `scripts/verificar_todo.py` · {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
               f"**{veredicto}** · {_stats['AVISO']} avisos · {_stats['OK']} checks OK\n"
               + "\n".join(_informe) + "\n")
    salida = RAIZ / "data" / "revision" / f"{PAIS}-verificacion.md"
    salida.write_text(informe, encoding="utf-8")
    print(f"[VERIF] {veredicto} · {_stats['AVISO']} avisos · informe → {salida.relative_to(RAIZ)}")
    sys.exit(1 if _stats["ERROR"] else 0)


if __name__ == "__main__":
    main()
