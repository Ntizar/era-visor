# -*- coding: utf-8 -*-
"""estado_paises.py — genera ESTADO.md y los índices por país/año.

Lee del disco lo que hay de verdad (manifiestos, pdfs, md, md-es, revisiones) y
escribe:
  · ESTADO.md                → tabla maestra por país (progreso de la fase)
  · md-es/<CC>/INDICE.md     → índice del país por años, informe a informe

Uso:
    python scripts/estado_paises.py
"""
import json
import os
import re
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(RAIZ, "data", "pdf-manifest")
PDFS = os.path.join(RAIZ, "pdfs")
MD = os.path.join(RAIZ, "md")
MD_ES = os.path.join(RAIZ, "md-es")
REV = os.path.join(RAIZ, "data", "revision")

NOMBRES = {
    "AT": "Austria", "BE": "Bélgica", "BG": "Bulgaria", "CH": "Suiza", "CZ": "Chequia",
    "DE": "Alemania", "DK": "Dinamarca", "EE": "Estonia", "EL": "Grecia", "ES": "España",
    "FI": "Finlandia", "FR": "Francia", "HR": "Croacia", "HU": "Hungría", "IE": "Irlanda",
    "IT": "Italia", "LT": "Lituania", "LU": "Luxemburgo", "LV": "Letonia", "NL": "Países Bajos",
    "NO": "Noruega", "PL": "Polonia", "PT": "Portugal", "RO": "Rumanía", "RS": "Serbia",
    "SE": "Suecia", "SI": "Eslovenia", "SK": "Eslovaquia", "UK": "Reino Unido",
}


def frontmatter(ruta, campos=("paginas", "chars", "idioma", "idioma_origen",
                              "verificacion", "escaneado", "anio")):
    out = {}
    with open(ruta, encoding="utf-8") as f:
        if f.readline().strip() != "---":
            return out
        for linea in f:
            if linea.strip() == "---":
                break
            if ":" in linea:
                k, v = linea.split(":", 1)
                if k.strip() in campos:
                    out[k.strip()] = v.strip().strip('"')
    return out


def contar_md(raiz):
    """{codigo: {"total":n, "por_anio":{a:n}, "escaneados":n, "chars":n, "ficheros":[...]}}"""
    res = {}
    if not os.path.isdir(raiz):
        return res
    for code in sorted(os.listdir(raiz)):
        base = os.path.join(raiz, code)
        if not os.path.isdir(base):
            continue
        por_anio = defaultdict(int)
        fich, esc, chars = [], 0, 0
        for dp, _, fs in os.walk(base):
            for f in sorted(fs):
                if not f.endswith(".md"):
                    continue
                ruta = os.path.join(dp, f)
                anio = os.path.basename(dp)
                por_anio[anio] += 1
                fm = frontmatter(ruta)
                if fm.get("escaneado") == "true":
                    esc += 1
                try:
                    chars += int(fm.get("chars", 0))
                except ValueError:
                    pass
                fich.append({"anio": anio, "fichero": f, "fm": fm})
        res[code] = {"total": len(fich), "por_anio": dict(sorted(por_anio.items())),
                     "escaneados": esc, "chars": chars, "ficheros": fich}
    return res


def revisiones():
    res = {}
    if not os.path.isdir(REV):
        return res
    for f in os.listdir(REV):
        # sólo los informes por país que escribe revisar_md_es.py (<CC>.json);
        # en data/revision/ viven también los artefactos históricos de España
        if not re.fullmatch(r"[A-Z]{2}\.json", f):
            continue
        codes = f[:-5]
        try:
            d = json.load(open(os.path.join(REV, f), encoding="utf-8"))
        except Exception:
            continue
        ok = sum(1 for v in d.values() if v.get("estado") == "ok")
        med = [v["fidelidad_media"] for v in d.values() if "fidelidad_media" in v]
        res[codes] = {"revisados": len(d), "ok": ok,
                      "media": round(sum(med) / len(med), 1) if med else None}
    return res


def main():
    man = {f[:-5]: len(json.load(open(os.path.join(MAN, f), encoding="utf-8")))
           for f in os.listdir(MAN) if f.endswith(".json")}
    md = contar_md(MD)
    md_es = contar_md(MD_ES)
    rev = revisiones()
    codes = sorted(set(man) | set(md) | set(md_es), key=lambda c: -(man.get(c) or 0))

    filas = []
    for c in codes:
        pdfs = len(os.listdir(os.path.join(PDFS, c))) if os.path.isdir(os.path.join(PDFS, c)) else 0
        m, e, r = md.get(c, {}), md_es.get(c, {}), rev.get(c, {})
        anios = sorted(set(list(m.get("por_anio", {})) + list(e.get("por_anio", {}))))
        anios = [a for a in anios if a.isdigit()]
        rango = f"{anios[0]}-{anios[-1]}" if anios else "—"
        filas.append(
            f"| **{c}** | {NOMBRES.get(c, c)} | {man.get(c, 0)} | {pdfs} | {m.get('total', 0)} | "
            f"{e.get('total', 0)} | {r.get('revisados', 0)} | {r.get('ok', 0)} | "
            f"{r.get('media', '—') if r else '—'} | {m.get('escaneados', 0)} | {rango} |")

    tot = lambda k, d: sum(v.get(k, 0) for v in d.values())  # noqa: E731
    cab = f"""# Estado del proyecto — MD de la ERA por país y año

Generado por `scripts/estado_paises.py` el {__import__('datetime').date.today()}.
No editar a mano: se regenera.

## Cómo se lee

- `md/<CC>/<AAAA>/` — extracción **original** del PDF (idioma de origen), tipográfica, verbatim verificado.
- `md-es/<CC>/<AAAA>/` — **castellano normalizado** (traducción IA + verificación numérica).
- `data/revision/<CC>.json` — revisión IA del castellano contra el original (fidelidad por página).

## Totales

| Concepto | Valor |
|---|---|
| Países con manifiesto | {len([c for c in man if man[c]])} |
| PDFs en manifiesto | {sum(man.values())} |
| PDFs descargados | {sum((len(os.listdir(os.path.join(PDFS, c))) if os.path.isdir(os.path.join(PDFS, c)) else 0) for c in codes)} |
| MD originales | {tot('total', md)} |
| MD en castellano | {tot('total', md_es)} |
| Informes revisados por IA | {sum(v['revisados'] for v in rev.values())} (ok {sum(v['ok'] for v in rev.values())}) |

## Tabla por país

| Código | País | PDFs manifiesto | Descargados | MD orig. | MD-es | Revisados | Rev. ok | Fidelidad media | Escaneados | Años |
|---|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(filas) + "\n"

    with open(os.path.join(RAIZ, "ESTADO.md"), "w", encoding="utf-8") as f:
        f.write(cab)

    # índices por país
    for c in codes:
        e = md_es.get(c)
        if not e:
            continue
        lineas = [f"# {NOMBRES.get(c, c)} — índice de informes en castellano",
                  "",
                  f"Fuente: ERA · {e['total']} informes · {sum(e['por_anio'].values())} ficheros.",
                  "Fidelidad = revisión IA del castellano contra el original (0-100).",
                  ""]
        por_anio = defaultdict(list)
        for it in e["ficheros"]:
            por_anio[it["anio"]].append(it)
        for anio in sorted(por_anio, reverse=True):
            lineas += [f"## {anio} ({len(por_anio[anio])})", "",
                       "| Informe | Págs | Caracteres | Verificación |", "|---|---|---|---|"]
            for it in sorted(por_anio[anio], key=lambda x: x["fichero"]):
                fm = it["fm"]
                ver = fm.get("verificacion", "—")
                if fm.get("idioma_origen", "").upper() == "ES":
                    ver = "original ES"
                lineas.append(f"| [{it['fichero']}]({anio}/{it['fichero'].replace(' ', '%20')}) | "
                              f"{fm.get('paginas', '—')} | {fm.get('chars', '—')} | {ver} |")
            lineas.append("")
        with open(os.path.join(MD_ES, c, "INDICE.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))

    print(f"ESTADO.md escrito · países {len(codes)} · md {tot('total', md)} · md-es {tot('total', md_es)}")


if __name__ == "__main__":
    main()
