#!/usr/bin/env python3
"""
04_inventario.py — H1 del harness de exhaustividad (0 tokens de LLM).

Pregunta que responde: ¿QUÉ QUEDA POR EXTRAER todavía de forma
determinista de los .md brutos, y en qué estado está cada campo?

Por qué existe: antes de gastar un solo token en el LLM hay que agotar
lo que se puede sacar sin riesgo de alucinación. Si no medimos, el
"le falta" es una opinión.

Produce:
  database/data/inventario.json   (verdad máquina, reutilizable)
  database/informes/inventario.md (humano)

Tres cruces:
  1. SECCIONES  de md_base  × anclas de las reglas activas
     → cuántas secciones del informe ninguna regla lee aún.
  2. TABLAS     del crudo   × tablas ya consumidas por un campo
     → cuántas tablas se pierden hoy (las 197 de cronología, etc.).
  3. CAMPOS     de la guía  × estado en el crudo
     → extraído con cita / con procedencia / sin valor / sin regla.

Salida honesta: NO rellena nada, NO infiere. Solo inventaría y mide.
"""
import json
import re
import collections
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MD_BASE = RAIZ / "database" / "md_base"
CRUDO = RAIZ / "database" / "data" / "crudo"
DATA = RAIZ / "database" / "data"
INFO = RAIZ / "database" / "informes"

# ---------------------------------------------------------------- secciones
RX_SEC = re.compile(
    r"^[ \t]*(\d{1,2}(?:\.\d{1,2}){0,4}(?:\.[A-Da-d])?)\.?[ \t]+([^\n]{2,70})$",
    re.M)
RX_FM = re.compile(r"^---\n(.*?)\n---\n", re.S)


def norm(s: str) -> str:
    s = re.sub(r"\s+", " ", str(s)).lower().strip()
    return s


def secciones_de(texto: str):
    """Todas las secciones con su número, título y página (1-based)."""
    # página = nº de '## Página N' anterior al offset
    cabec = [(m.start(), int(m.group(1)))
             for m in re.finditer(r"^## Página (\d+)", texto, re.M)]
    out = []
    for m in RX_SEC.finditer(texto):
        tit = m.group(2).strip()
        if not tit or tit.startswith("Página"):
            continue
        pag = 1
        for off, n in cabec:
            if off <= m.start():
                pag = n
            else:
                break
        out.append({"num": m.group(1), "titulo": tit,
                    "titulo_norm": norm(tit), "pagina": pag})
    return out


def anclas_activas(campos: dict):
    """Todas las anclas/regex que las reglas de la Fase 2 ya cubren."""
    anclas = []
    for cfg in campos.values():
        for f in cfg.get("fuentes", []):
            if f.get("anclas"):
                anclas += list(f["anclas"])
            if f.get("rx") and f.get("t") in ("seccion", "sec", "portada"):
                anclas.append(f["rx"])
    return [a for a in anclas if a]


def main() -> int:
    guia_raw = json.loads((DATA / "guia_campos.json").read_text(encoding="utf-8"))
    # los títulos de bloque de la guía tienen campo vacío (no son campos)
    guia = {g["ref"]: g for g in guia_raw
            if str(g.get("ref", "")).strip()[:1].isdigit()
            and (g.get("campo") or "").strip()}

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "m02", RAIZ / "database" / "scripts" / "02_extraer_crudo.py")
    m02 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m02)
    anclas = anclas_activas(m02.CAMPOS)

    # ------------------------------------------------- 1) secciones
    tot_sec = sin_regla = 0
    ej_sec = collections.Counter()
    paginas_tot = 0
    n_md = 0
    for p in sorted(MD_BASE.glob("*.md")):
        txt = p.read_text(encoding="utf-8", errors="replace")
        n_md += 1
        paginas_tot += len(re.findall(r"^## Página \d+", txt, re.M))
        for s in secciones_de(txt):
            tot_sec += 1
            if not any(re.search(a, s["titulo_norm"], re.I) for a in anclas):
                sin_regla += 1
                ej_sec[s["titulo_norm"][:58]] += 1

    # ------------------------------------------------- 2) tablas
    tab_tot = tab_recos = tab_otras = 0
    fam_otras = collections.Counter()
    pag_tabla = 0
    for p in sorted(CRUDO.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for t in d.get("tablas", []):
            tab_tot += 1
            cab = [str(c) for c in (t.get("cabecera") or [])]
            cl = " ".join(cab).lower()
            es_reco = (("destinatario" in cl or "addressee" in cl)
                       and ("recomend" in cl or "implement" in cl))
            if es_reco:
                tab_recos += 1
            else:
                tab_otras += 1
                fam_otras[re.sub(r"\s+", " ", " | ".join(cab))[:70]] += 1
            if t.get("pagina"):
                pag_tabla += 1

    # ------------------------------------------------- 3) campos
    # Claves reales del crudo por campo: valor_fuente / cita / pagina /
    # origen / regla / estado / verificado. El desglose de `estado` separa
    # "no consta" (el informe no lo publica) de lo que sigue pendiente:
    # sin esa distinción un vacío es ambiguo para quien consuma el Excel.
    estados = collections.Counter()
    estados_sin_valor = collections.Counter()
    n_campos = len(guia)
    for p in sorted(CRUDO.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        campos = d.get("campos", {})
        for ref in guia:
            c = campos.get(ref) or {}
            v = c.get("valor_fuente")
            if v in (None, "", [], {}):
                estados["sin_valor"] += 1
                estados_sin_valor[str(c.get("estado") or "sin_estado")] += 1
                continue
            if c.get("cita"):
                estados["cita_literal"] += 1
            elif str(c.get("origen", "")) in ("importado", "db"):
                estados["solo_procedencia"] += 1
            else:
                estados["valor_sin_fuente"] += 1
    n_informes = len(list(CRUDO.glob("*.json")))

    inv = {
        "generado_por": "04_inventario.py",
        "sin_llm": True,
        "informes": n_informes,
        "md_base": n_md,
        "paginas_totales": paginas_tot,
        "secciones": {
            "total": tot_sec,
            "sin_regla": sin_regla,
            "cubiertas": tot_sec - sin_regla,
            "pct_cubiertas": round(100 * (tot_sec - sin_regla) / max(tot_sec, 1), 1),
            "top_sin_regla": [{"titulo": t, "n": n}
                              for t, n in ej_sec.most_common(40)],
        },
        "tablas": {
            "total": tab_tot,
            "consumidas_recomendaciones": tab_recos,
            "sin_consumir": tab_otras,
            "pct_consumidas": round(100 * tab_recos / max(tab_tot, 1), 1),
            "top_sin_consumir": [{"cabecera": c, "n": n}
                                 for c, n in fam_otras.most_common(40)],
        },
        "campos": {
            "guia": len(guia),
            "estados": dict(estados),
            "sin_valor_desglose": dict(estados_sin_valor),
            "pct_con_cita": round(100 * estados["cita_literal"]
                                  / max(n_informes * len(guia), 1), 1),
        },
        "pendiente_llm": {
            "campos_guia_parciales": sum(
                1 for g in guia_raw
                if str(g.get("ref", "")).strip()[:1].isdigit()
                and (g.get("campo") or "").strip()
                and str(g.get("cumplimentar", "")).strip() not in ("Sí", "Si", "sí")),
        },
    }

    (DATA / "inventario.json").write_text(
        json.dumps(inv, ensure_ascii=False, indent=2), encoding="utf-8")

    # ------------------------------------------------- informe humano
    L = []
    L.append("# Inventario de exhaustividad (harness H1)\n")
    L.append("Generado por `04_inventario.py` · **sin LLM**, sólo medición.\n")
    L.append("Antes de gastar tokens: agotar lo extraíble de forma determinista.\n")
    L.append("\n## Cobertura actual\n")
    L.append("| Qué | Total | Cubierto | % |")
    L.append("|---|---:|---:|---:|")
    L.append("| Secciones de los informes | %d | %d | %.1f%% |"
             % (tot_sec, tot_sec - sin_regla, inv["secciones"]["pct_cubiertas"]))
    L.append("| Tablas | %d | %d | %.1f%% |"
             % (tab_tot, tab_recos, inv["tablas"]["pct_consumidas"]))
    L.append("| Celdas de campo con cita literal | %d | %d | %.1f%% |"
             % (n_informes * len(guia), estados["cita_literal"],
                inv["campos"]["pct_con_cita"]))
    L.append("\n## Estados de los campos (por celda informe×campo)\n")
    L.append("| Estado | Celdas | Significado |")
    L.append("|---|---:|---|")
    leyenda = {
        "cita_literal": "valor + cita literal localizada en una página",
        "solo_procedencia": "valor importado (análisis v3) con procedencia",
        "valor_sin_fuente": "valor SIN fuente — a revisar, no es fiable",
        "sin_valor": "sin dato (no consta o pendiente)",
    }
    for k, v in sorted(estados.items(), key=lambda x: -x[1]):
        L.append("| %s | %d | %s |" % (k, v, leyenda.get(k, "")))
    if estados_sin_valor:
        L.append("\n### Desglose de los vacíos: ¿«no consta» o pendiente?\n")
        L.append("| Estado | Celdas |")
        L.append("|---|---:|")
        for k, v in sorted(estados_sin_valor.items(), key=lambda x: -x[1]):
            L.append("| %s | %d |" % (k, v))
    L.append("\n## Tablas sin consumir (determinista, 0 riesgo de alucinación)\n")
    L.append("Cada una lleva página y cita en el crudo.\n")
    L.append("| Nº | Cabecera |")
    L.append("|---:|---|")
    for c, n in fam_otras.most_common(25):
        L.append("| %d | `%s` |" % (n, c.replace("|", "\\|")))
    L.append("\n## Secciones sin ninguna regla\n")
    L.append("| Nº | Título |")
    L.append("|---:|---|")
    for t, n in ej_sec.most_common(25):
        L.append("| %d | %s |" % (n, t))
    L.append("")
    (INFO / "inventario.md").write_text("\n".join(L), encoding="utf-8")

    print("== H1 inventario (0 tokens) ==")
    print("  informes: %d | páginas: %d" % (n_informes, paginas_tot))
    print("  secciones: %d | cubiertas %d (%.1f%%) | SIN regla: %d"
          % (tot_sec, tot_sec - sin_regla, inv["secciones"]["pct_cubiertas"], sin_regla))
    print("  tablas: %d | recomendaciones %d | SIN consumir: %d"
          % (tab_tot, tab_recos, tab_otras))
    print("  estados:", dict(estados))
    print("  → database/data/inventario.json")
    print("  → database/informes/inventario.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
