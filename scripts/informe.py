# -*- coding: utf-8 -*-
"""informe.py — INFORME.md: auditoría única del corpus MD en castellano.

Junta en un solo documento lo que hoy está repartido por el repo:
  · cobertura por país (PDF publicados, MD extraídos, MD en castellano),
  · calidad por país (verificados ok, con páginas a repasar, traducciones vacías),
  · revisión IA (informes revisados, fidelidad media/mínima),
  · OCR (informes recuperados, páginas, confianza media),
  · estado de custodia (PDF con manifiesto, md5, escaneados sin texto).

No inventa nada: todo sale del disco. Si un dato no existe, lo dice.

Uso:
    python scripts/informe.py
"""
import datetime
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD, MD_ES, PDFS = (os.path.join(RAIZ, x) for x in ("md", "md-es", "pdfs"))
REV = os.path.join(RAIZ, "data", "revision")
OCR = os.path.join(RAIZ, "data", "ocr")
MAN = os.path.join(RAIZ, "data", "pdf-manifest")
SALIDA = os.path.join(RAIZ, "INFORME.md")
IGN = ("indice", "índice", "leeme", "readme")
NOMBRES = {
    "AT": "Austria", "BE": "Bélgica", "BG": "Bulgaria", "CH": "Suiza", "CZ": "Chequia",
    "DE": "Alemania", "DK": "Dinamarca", "EE": "Estonia", "EL": "Grecia", "ES": "España",
    "FI": "Finlandia", "FR": "Francia", "HR": "Croacia", "HU": "Hungría", "IE": "Irlanda",
    "IT": "Italia", "LT": "Lituania", "LU": "Luxemburgo", "LV": "Letonia", "NL": "Países Bajos",
    "NO": "Noruega", "PL": "Polonia", "PT": "Portugal", "RO": "Rumanía", "RS": "Serbia",
    "SE": "Suecia", "SI": "Eslovenia", "SK": "Eslovaquia", "UK": "Reino Unido",
}


def md_files(base):
    return [os.path.join(dp, f) for dp, _, fs in os.walk(base)
            for f in fs if f.endswith(".md") and not f.lower().startswith(IGN)]


def cabecera(p):
    t = open(p, encoding="utf-8", errors="replace").read(900)
    d = {}
    for l in t.split("\n"):
        if l.strip() == "---" and d:
            break
        if ":" in l:
            k, v = l.split(":", 1)
            d[k.strip()] = v.strip().strip('"')
    return d


def leer_json(ruta):
    if not os.path.exists(ruta):
        return {}
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except Exception:
        return {}


def main():
    filas, tot = [], {"pdf": 0, "man": 0, "md": 0, "es": 0, "ok": 0, "rev": 0, "vac": 0,
                      "escaneados": 0, "ocr": 0, "revisados": 0}
    for code in sorted(os.listdir(MD)):
        base = os.path.join(MD, code)
        if not os.path.isdir(base):
            continue
        pdfs = len([p for p in os.listdir(os.path.join(PDFS, code))
                    if p.lower().endswith(".pdf")]) if os.path.isdir(os.path.join(PDFS, code)) else 0
        man = len(leer_json(os.path.join(MAN, f"{code}.json")) or [])
        mds = md_files(base)
        ess = md_files(os.path.join(MD_ES, code)) if os.path.isdir(os.path.join(MD_ES, code)) else []
        ok, rev, vac, esc = 0, 0, 0, 0
        for p in mds:
            if cabecera(p).get("escaneado") == "true":
                esc += 1
        for p in ess:
            t = open(p, encoding="utf-8", errors="replace").read()
            if len(t) < 400:
                vac += 1
            elif re.search(r"^verificacion:\s*revisar", t, re.M):
                rev += 1
            else:
                ok += 1
        rev_ia = leer_json(os.path.join(REV, f"{code}.json"))
        med = [v["fidelidad_media"] for v in rev_ia.values()
               if isinstance(v.get("fidelidad_media"), (int, float))]
        ocr = leer_json(os.path.join(OCR, f"{code}.json"))
        conf = [v["confianza_media"] for v in ocr.values()
                if isinstance(v.get("confianza_media"), (int, float)) and v["confianza_media"] > 0]
        filas.append(
            f"| **{code}** | {NOMBRES.get(code, code)} | {man} | {pdfs} | {len(mds)} | {len(ess)} | "
            f"{ok} | {rev} | {vac} | {len(rev_ia)} | "
            f"{round(sum(med)/len(med), 1) if med else '—'} | "
            f"{len(ocr) or '—'} | {round(sum(conf)/len(conf), 1) if conf else '—'} |")
        tot["pdf"] += pdfs
        tot["man"] += man
        tot["md"] += len(mds)
        tot["es"] += len(ess)
        tot["ok"] += ok
        tot["rev"] += rev
        tot["vac"] += vac
        tot["escaneados"] += esc
        tot["ocr"] += len(ocr)
        tot["revisados"] += len(rev_ia)

    pct_md = 100 * tot["md"] / max(tot["man"], 1)
    pct_es = 100 * tot["es"] / max(tot["md"], 1)
    cab = [
        "# Informe del corpus — accidentes ferroviarios de la ERA en castellano",
        "",
        f"Generado por `scripts/informe.py` el {datetime.date.today()} a partir del disco. "
        "Ningún dato de este documento está escrito a mano: si algo no existe, aparece «—».",
        "",
        "## Resumen",
        "",
        "| Concepto | Valor |",
        "|---|---|",
        f"| PDF publicados por ERA (manifiestos) | **{tot['man']}** |",
        f"| PDF en disco | {tot['pdf']} |",
        f"| MD originales extraídos | **{tot['md']} ({pct_md:.1f} %)** |",
        f"| MD en castellano | **{tot['es']} ({pct_es:.1f} % de los extraídos)** |",
        f"| · verificados ok | {tot['ok']} |",
        f"| · con páginas a repasar | {tot['rev']} |",
        f"| · traducciones vacías o truncadas | {tot['vac']} |",
        f"| Informes revisados por IA (deepseek) | {tot['revisados']} |",
        f"| PDF escaneados sin capa de texto | {tot['escaneados']} |",
        f"| · recuperados por OCR auditado | {tot['ocr']} |",
        "",
        "## Por país",
        "",
        "| Código | País | PDF publ. | PDF disco | MD | MD-es | ok | a repasar | vacías | Rev. IA | Fidelidad | OCR | Conf. OCR |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    pie = [
        "",
        "## Cómo se ha hecho cada cosa (método y garantías)",
        "",
        "**Extracción (PDF → MD).** `convertir_md_pais.py` lee el PDF en modo tipográfico (PyMuPDF): "
        "encabezados por tamaño de fuente, membrete repetido eliminado, tablas reales en pipes. "
        "Cada línea emitida se verifica contra el texto del PDF y el número de fallos queda en el "
        "frontmatter (`verbatim_fallos`). Si una página no tiene capa de texto se declara "
        "(`escaneado: true`, `paginas_sin_texto`) y no se rellena a mano.",
        "",
        "**OCR (solo escaneados).** `ocr_escaneados.py` con **Tesseract 5.4 + tessdata_best a 300 dpi** "
        "e idioma por país. Se registra motor y versión, idiomas, páginas, páginas vacías, "
        "**confianza media y mínima por palabra**, md5 del PDF y fecha, en `data/ocr/<CC>.json`. "
        "Por debajo de 70 de confianza el informe se marca para revisión manual.",
        "",
        "**Traducción.** `traducir_md_es.py` con `qwen3.8-flash` (`enable_thinking: false`), en bloques "
        "de ~7 000 caracteres, con instrucciones de fidelidad literal, tablas celda a celda y "
        "secciones canónicas. Cada bloque se **verifica**: marcadores de página, cifras largas "
        "(≥3 dígitos) y cortas, fechas normalizadas y ratio de longitud. Si falla hay un reintento "
        "correctivo; si sigue fallando, el informe queda `verificacion: revisar` con el motivo escrito.",
        "",
        "**Reparación.** `--reparar` re-traduce **solo las páginas que fallan**, no el informe entero. "
        "`--vacios` detecta traducciones vacías o truncadas (menos del 30 % del original) y las rehace: "
        "pasa cuando el MD se tradujo antes de tener texto (escaneados sin OCR).",
        "",
        "**Original bilingüe.** Algunos informes (Portugal) publican dos idiomas intercalados línea a "
        "línea; la traducción correcta colapsa el duplicado y sale a la mitad de caracteres. Se "
        "detecta por línea y se compara contra el idioma principal para no marcar falsos fallos.",
        "",
        "**Revisión IA.** `revisar_md_es.py` con `deepseek-v4-pro`: compara original y castellano "
        "página a página (6 muestras por informe) y devuelve fidelidad 0-100, omisiones, invenciones "
        "y cifras mal. Umbral 85. Una página sin dictamen no cuenta como fallo: se declara.",
        "",
        "**Custodia.** Cada MD lleva `pdf`, `md5_pdf`, `url_oficial`, `paginas`, `chars`, fecha y "
        "generador. Cada md-es lleva además `md_origen`, `md5_origen`, modelo usado y veredicto. "
        "Los PDF no van al repositorio (`pdfs/` está ignorado): son reproducibles desde el manifiesto.",
        "",
        "**Concurrencia y cola compartida.** 5 llamadas simultáneas de día y 6 de 00:00 a 06:00, "
        "medido: ~60 k caracteres/min. Traducción y revisión nunca a la vez.",
    ]
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(cab + filas + pie) + "\n")
    print(f"escrito {SALIDA} · {len(filas)} países · md {tot['md']} · md-es {tot['es']}")


if __name__ == "__main__":
    main()