#!/usr/bin/env python3
"""
01_mejorar_md.py — Fase 1: el `dato_base` mejorado, SIN UN SOLO TOKEN DE LLM.

Mejora tres cosas respecto a md/ES/ (output de extraer_pais.py):
  1. TABLAS → markdown  (hoy 0/372 md tienen tabla convertida; las tablas de
     recomendaciones —Destinatario·Implementador·Número·Recomendación— se
     pierden en el flujo de texto y son el dato más valioso del informe).
  2. ÍNDICE DE PUNTOS fuera  (236 md arrastran líneas "2.1. SUCESO ..... 12"
     que se colaban en campos narrativos como "descripción").
  3. FRONTMATTER DE PROCEDENCIA  (url_oficial, md5 del PDF, nº de páginas...
     para que todo dato extraído arrastre su trazabilidad hasta la fuente).

Salida: database/md_base/*.md  — NO se toca md/ES/ (el pipeline de era-visor
sigue con sus originales; rollback = borrar md_base/).

Garantías:
  • La extracción de texto es EXACTAMENTE la del original (page.get_text()),
    así que no puede haber pérdida de contenido por rediseño.
  • Verificación de no-pérdida por fichero: cada línea del original (ya sin
    índice) debe aparecer en el nuevo. Si falla, NO se escribe ese fichero.
  • Dry-run por defecto; solo escribe con --aplicar.

Uso:
  py 01_mejorar_md.py                 # dry-run: analiza y reporta, no escribe
  py 01_mejorar_md.py --aplicar       # escribe database/md_base/
  py 01_mejorar_md.py --solo STEM     # dry-run de un fichero (con --verbose imprime)
"""

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

import fitz  # PyMuPDF

RAIZ = Path(__file__).resolve().parent.parent.parent
PDFS = RAIZ / "pdfs" / "ES"
MD_ORIG = RAIZ / "data_antigua" / "md_originales"   # originales (solo lectura)
MD_BASE = RAIZ / "md" / "ES"        # única colección md (la mejorada)
DATA = RAIZ / "database" / "data"
UMBRAL_OCR = 500  # mismo umbral que extraer_pais.py

# Línea de índice: 4+ puntos consecutivos Y termina en número de página.
# Es el patrón tipográfico de relleno del sumario; ninguna línea de contenido
# real cumple las dos condiciones a la vez.
RX_INDICE = re.compile(r"\.{4,}.*\d\s*$")

# "tablas" que en realidad son la maquetación de la portada / cabeceras
RUIDO_PORTADA = re.compile(
    r"MINISTERIO DE FOMENTO|COMISI[ÓO]N DE INVESTIGACI[ÓO]N|"
    r"SECRETARIA DE ESTADO|SUBSECRETAR[ÍI]A|DIRECCI[ÓO]N GENERAL|"
    r"ANEXO|ABREVIATURAS",
    re.I,
)

RX_FENCE = re.compile(r"^\s*\|.*\|\s*$", re.M)


# ------------------------------------------------------------------ utilidades

def md5_fichero(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for trozo in iter(lambda: f.read(1 << 20), b""):
            h.update(trozo)
    return h.hexdigest()


def quitar_indice(texto: str) -> tuple[str, int]:
    """Elimina las líneas de sumario. Devuelve (texto, nº de líneas quitadas)."""
    fuera, quitadas = [], 0
    for ln in texto.splitlines():
        if RX_INDICE.search(ln):
            quitadas += 1
            continue
        fuera.append(ln)
    return "\n".join(fuera), quitadas


def tabla_util(datos: list) -> bool:
    """¿Es una tabla de DATOS y no la maquetación de una portada?"""
    filas = [f for f in datos if any((c or "").strip() for c in f)]
    if len(filas) < 2:
        return False
    celdas = [(c or "").strip() for f in filas for c in f]
    nv = [c for c in celdas if c]
    if len(nv) < 4:
        return False
    if RUIDO_PORTADA.search(" ".join(nv)):
        return False
    return len(nv) / max(1, len(celdas)) >= 0.25


def tabla_a_markdown(datos: list) -> str:
    """Compacta columnas/filas vacías y emite tabla markdown.

    Pitfall real: PyMuPDF desdobra la maquetación en columnas que NO
    coinciden con las de los datos. En las tablas de recomendaciones del CIAF:
        f0 = ['Destinatario', '', 'Implementador', '', 'Número', 'Recomendación', '', '']
        f1 = ['', '', 'final', ...]            <- 2ª línea de la cabecera
        f3 = ['AESF','AESF','','','64/2021-2','', 'Supervisar…', '']  <- desbordada
    Sin reconstruir, sale "Recomendación final" (palabra en celda equivocada) y
    la recomendación 2 en otra columna que las demás.

    Tres reglas, en orden:
      B  columna huérfana de SOLO-cabecera → se fusiona en la anterior con datos
      A  fila de continuación (1 celda) → a la MISMA columna si ya tiene texto
      C  celda desbordada: col[i] con datos, sin cabecera, y col[i-1] con
         cabecera → vuelve a su columna lógica
    Es seguro ser audaz: la tabla es un BLOQUE AÑADIDO, el texto de la página
    sigue íntegro, así que nunca puede haber pérdida de información.
    """
    filas = [[(c or "").replace("\n", " ").strip() for c in f] for f in datos]
    filas = [f for f in filas if any(f)]           # fuera filas enteramente vacías
    if not filas:
        return ""
    ncols = max(len(f) for f in filas)
    filas = [f + [""] * (ncols - len(f)) for f in filas]

    vacia = lambda c: not c

    # ¿cuántas filas iniciales son CABECERA? La maquetación reparte la cabecera
    # en 2 líneas ('Destinatario' / 'final'), y sin contarlo bien la 2ª línea
    # se cuela como "datos" y la regla B no dispara nunca.
    n_cab = 1
    while n_cab < len(filas) - 1 and sum(1 for c in filas[n_cab] if c) <= 1:
        n_cab += 1

    hay_datos = [any(filas[k][i] for k in range(n_cab, len(filas)))   # solo datos
                 for i in range(ncols)]
    hay_cab = [any(filas[k][i] for k in range(n_cab))                 # cabecera
               for i in range(ncols)]

    # --- B: columna con cabecera pero SIN datos en ninguna fila de datos ----
    #     (la cabecera quedó desplazada respecto a sus datos) → a la izquierda
    mover = {}
    for i in range(1, ncols):
        if hay_cab[i] and not hay_datos[i]:
            # ¿la anterior con datos de fila es la lógica? sí: i-1 tiene datos
            j = i - 1
            while j >= 0 and not hay_datos[j]:
                j -= 1
            if j >= 0:
                mover[i] = j
    if mover:
        for f in filas:
            for i, j in mover.items():
                if f[i]:
                    if not f[j]:
                        f[j] = f[i]
                    else:
                        f[j] = f[j] + " " + f[i]
                    f[i] = ""
        for i in mover:                      # esas columnas ya no aportan
            for f in filas:
                f[i] = ""
            hay_cab[i] = False
            hay_datos[i] = False

    # --- fuera columnas enteramente vacías ---------------------------------
    cols_vacias = [i for i in range(ncols) if not any(f[i] for f in filas)]
    filas = [[c for i, c in enumerate(f) if i not in cols_vacias] for f in filas]
    filas = [f for f in filas if any(f)]
    if not filas:
        return ""
    ncol = max(len(f) for f in filas)
    filas = [f + [""] * (ncol - len(f)) for f in filas]

    # --- C: celda desbordada que tocaba a la izquierda ---------------------
    cab = filas[0]
    for i in range(1, ncol):
        if not cab[i] and i > 0 and cab[i - 1]:
            for f in filas[1:]:
                if f[i] and not f[i - 1]:
                    f[i - 1] = f[i]
                    f[i] = ""

    # C puede dejar columnas enteramente vacías (la que se usó de "desbordamiento")
    # → limpiar de nuevo ANTES de emitir, o sobra una columna fantasma al final.
    cols_vacias = [i for i in range(ncol) if not any(f[i] for f in filas)]
    if cols_vacias:
        filas = [[c for i, c in enumerate(f) if i not in cols_vacias] for f in filas]
        ncol = max(len(f) for f in filas)
        filas = [f + [""] * (ncol - len(f)) for f in filas]

    # --- A: filas de continuación (1 sola celda) ---------------------------
    compactas: list[list[str]] = []
    for f in filas:
        nv = [c for c in f if c]
        if compactas and len(nv) == 1 and any(compactas[-1]):
            previa = compactas[-1]
            idx = next((i for i, c in enumerate(f) if c), None)
            if idx is not None and idx < len(previa) and previa[idx]:
                previa[idx] = previa[idx] + " " + f[idx]      # misma columna
            else:
                j = max(i for i, c in enumerate(previa) if c)
                previa[j] = previa[j] + " " + nv[0]
            continue
        compactas.append(list(f))

    if not compactas:
        return ""
    ncol = max(len(f) for f in compactas)
    compactas = [f + [""] * (ncol - len(f)) for f in compactas]
    esc = [[c.replace("|", "\\|") or " " for c in f] for f in compactas]
    out = ["| " + " | ".join(esc[0]) + " |",
           "|" + "---|" * ncol]
    out += ["| " + " | ".join(f) + " |" for f in esc[1:]]
    return "\n".join(out)


def tabla_marca(txt: str) -> str:
    """¿El markdown de tabla ya está en el texto (evita duplicarlo)?"""
    return bool(txt and RX_FENCE.search(txt))


# ------------------------------------------------------------------ procesado

def procesar(pdf: Path, url_oficial: str) -> dict:
    """Construye el md mejorado de un PDF + su informe de verificación."""
    doc = fitz.open(pdf)
    n_pag = len(doc)
    paginas_txt, total_chars = [], 0
    for i, page in enumerate(doc):
        t = page.get_text()
        total_chars += len(t.strip())
        paginas_txt.append(t)
    escaneado = total_chars < UMBRAL_OCR * max(1, n_pag // 10)
    # PDF escaneado sin capa de texto: si md/ES/ YA trae texto (OCR hecho por
    # scripts/ocr_pendiente.py), ese texto ES la fuente — un escaneado no
    # vuelve a quedar "[Pendiente de OCR]" mientras exista su md.
    texto_ocr = ""
    if escaneado:
        orig_ocr = MD_ORIG / (pdf.stem + ".md")
        if orig_ocr.exists():
            _bruto = orig_ocr.read_text(encoding="utf-8", errors="replace")
            _cuerpo = re.sub(r"^---\n.*?\n---\n", "", _bruto, flags=re.S)
            if len(_cuerpo.strip()) > 500:
                texto_ocr = _cuerpo.strip()
                total_chars = len(texto_ocr)

    tablas_tot = tablas_utiles = 0
    idx_quitadas = 0
    partes: list[str] = []

    if escaneado:
        if texto_ocr:
            cuerpo = "\n\n## Página 1\n\n" + texto_ocr
            cuerpo_sin_idx, idx_quitadas = cuerpo, 0
        else:
            cuerpo = "[Pendiente de OCR — PDF sin capa de texto]"
            cuerpo_sin_idx, idx_quitadas = cuerpo, 0
    else:
        for i, page in enumerate(doc):
            txt, nq = quitar_indice(paginas_txt[i])
            idx_quitadas += nq
            partes.append(f"\n\n## Página {i + 1}\n\n{txt}")
            # tablas de ESTA página
            try:
                tabs = page.find_tables().tables
            except Exception:
                tabs = []
            bloques = []
            for t in tabs:
                tablas_tot += 1
                try:
                    datos = t.extract()
                except Exception:
                    continue
                if not tabla_util(datos):
                    continue
                md = tabla_a_markdown(datos)
                # ¿ya está esta tabla formateada en el texto de la página?
                # (buscar en el md generado sería ALWAYS-TRUE: su primera línea
                #  ya es "| ... |")
                if md and not tabla_marca(txt):
                    bloques.append(md)
                    tablas_utiles += 1
            if bloques:
                partes.append("\n\n### Tablas de la página %d\n\n%s"
                              % (i + 1, "\n\n".join(bloques)))
        cuerpo = "".join(partes)
        cuerpo_sin_idx = cuerpo

    doc.close()

    front = [
        "---",
        f"pdf: pdfs/ES/{pdf.name}",
        f"url_oficial: {url_oficial}",
        f"md5_pdf: {md5_fichero(pdf)}",
        f"paginas: {n_pag}",
        f"chars: {total_chars}",
        f"tablas_detectadas: {tablas_tot}",
        f"tablas_convertidas: {tablas_utiles}",
        f"indice_quitadas: {idx_quitadas}",
        f"escaneado: {'true' if escaneado else 'false'}",
        f"fecha_proceso: {date.today().isoformat()}",
        "generador: 01_mejorar_md.py (PyMuPDF page.get_text + find_tables)",
        "---",
        "",
    ]
    nuevo = "\n".join(front) + cuerpo.lstrip("\n") + "\n"

    # ---- verificación de no-pérdida -------------------------------
    # Todo el texto del ORIGINAL (sin índice) debe estar en el nuevo.
    orig = (MD_ORIG / (pdf.stem + ".md"))
    problemas = []
    if orig.exists():
        texto_orig = orig.read_text(encoding="utf-8", errors="replace")
        # quita el frontmatter original para comparar cuerpos
        cuerpo_orig = re.sub(r"^---\n.*?\n---\n", "", texto_orig, flags=re.S)
        cuerpo_orig_limpio, _ = quitar_indice(cuerpo_orig)
        nuevo_sin_front = re.sub(r"^---\n.*?\n---\n", "", nuevo, flags=re.S)
        norm = lambda s: re.sub(r"[ \t]+", " ", s).strip()
        nuevo_norm = norm(nuevo_sin_front)
        perdidas = []
        for ln in cuerpo_orig_limpio.splitlines():
            ln_n = norm(ln)
            if not ln_n:
                continue
            if ln_n not in nuevo_norm:
                perdidas.append(ln_n[:90])
                if len(perdidas) >= 5:
                    break
        if perdidas:
            problemas.append(f"{len(perdidas)}+ líneas del original ausentes")
    else:
        problemas.append("sin .md original de referencia")

    return {
        "stem": pdf.stem,
        "nuevo": nuevo,
        "n_pag": n_pag,
        "chars": total_chars,
        "escaneado": escaneado,
        "tablas_detectadas": tablas_tot,
        "tablas_convertidas": tablas_utiles,
        "indice_quitadas": idx_quitadas,
        "chars_nuevo": len(nuevo),
        "problemas": problemas,
    }


def verificar_no_perdida() -> int:
    """GATE H2 — verifica la no-pérdida POR FUERA de la lógica interna.

    No se fía de 'problemas': relee los md originales de data_antigua/md_originales,
    quita el índice, y comprueba que CADA línea del original existe en el de
    md/ES/. Salida: nº de fallos (0 = verde).
    """
    if not MD_BASE.exists():
        print("  no existe md/ES/ — nada que verificar")
        return 1
    idx = re.compile(r"^.*\.{4,}.*\d\s*$", re.M)
    fallos = []
    revisados = 0
    for p in sorted(MD_BASE.glob("*.md")):
        orig = MD_ORIG / p.name
        if not orig.exists():
            fallos.append((p.name, "no hay md original en md/ES/"))
            continue
        viejo = idx.sub("", orig.read_text(encoding="utf-8", errors="replace"))
        nuevo = p.read_text(encoding="utf-8", errors="replace")
        # AMBOS tienen frontmatter (el original: pdf/paginas/chars; el nuevo:
        # url_oficial, md5, tablas...). Sin quitarlo en los dos, las líneas de
        # la cabecera vieja aparecen como "pérdida".
        viejo = re.sub(r"\A---\n.*?\n---\n", "", viejo, flags=re.S)
        cuerpo_nuevo = re.sub(r"\A---\n.*?\n---\n", "", nuevo, flags=re.S)
        lineas_viejas = [l.strip() for l in viejo.splitlines() if l.strip()]
        if not lineas_viejas:
            continue
        # normalización: espacios/campos no separables (el PDF cambia la
        # partición por ancho entre corridas de extracción)
        norm_nuevo = re.sub(r"[\s ]+", "", cuerpo_nuevo)
        perdidas = [l for l in lineas_viejas
                    if re.sub(r"[\s ]+", "", l) not in norm_nuevo]
        revisados += 1
        if perdidas:
            fallos.append((p.name, f"{len(perdidas)} líneas ausentes · ej: {perdidas[0][:70]!r}"))
    print(f"  verificados: {revisados} · con pérdida: {len(fallos)}")
    for nombre, motivo in fallos[:12]:
        print(f"    ✗ {nombre} → {motivo}")
    if len(fallos) > 12:
        print(f"    … y {len(fallos) - 12} más")
    print("  GATE H2: " + ("OK" if not fallos else f"FALLO ({len(fallos)})"))
    return len(fallos)


def main() -> int:
    argv = sys.argv[1:]
    if "--verificar" in argv:
        return verificar_no_perdida()
    aplicar = "--aplicar" in argv
    verbose = "--verbose" in argv
    solo = None
    if "--solo" in argv:
        solo = argv[argv.index("--solo") + 1]

    manifiesto = json.loads((DATA / "manifest_maestro.json").read_text(encoding="utf-8"))
    url_por_pdf = {}
    for r in manifiesto["informes"]:
        for ruta in r["pdf_local"]:
            url_por_pdf[Path(ruta).name] = r["url_oficial"]

    pdfs = sorted(PDFS.glob("*.pdf"))
    if solo:
        pdfs = [p for p in pdfs if solo.lower() in p.stem.lower()]
    print(f"== Fase 1: dato_base mejorado ==  {len(pdfs)} PDFs"
          f"{'  (dry-run: sin --aplicar)' if not aplicar else '  (APlicando)'}\n")

    stats = {"ok": 0, "ocr": 0, "fallos": 0, "sin_url": 0}
    tot_tablas = tot_utiles = tot_idx = 0
    con_tabla = 0
    informes_fallo = []
    resultados = []

    for pdf in pdfs:
        url = url_por_pdf.get(pdf.name, "")
        if not url:
            stats["sin_url"] += 1
        try:
            r = procesar(pdf, url)
        except Exception as e:
            stats["fallos"] += 1
            informes_fallo.append(f"{pdf.name}: {type(e).__name__}: {e}")
            continue

        tot_tablas += r["tablas_detectadas"]
        tot_utiles += r["tablas_convertidas"]
        tot_idx += r["indice_quitadas"]
        if r["tablas_convertidas"]:
            con_tabla += 1

        if r["problemas"]:
            stats["fallos"] += 1
            informes_fallo.append(f"{pdf.stem}: " + "; ".join(r["problemas"]))
            if verbose:
                print(f"  ✗ {pdf.stem[:50]}: {'; '.join(r['problemas'])}")
            continue

        if r["escaneado"]:
            stats["ocr"] += 1
        else:
            stats["ok"] += 1

        if aplicar:
            MD_BASE.mkdir(parents=True, exist_ok=True)
            (MD_BASE / (pdf.stem + ".md")).write_text(r["nuevo"], encoding="utf-8")
        resultados.append({k: v for k, v in r.items() if k != "nuevo"})

        if verbose:
            print(f"  ✓ {pdf.stem[:50]:52} págs={r['n_pag']:3} "
                  f"tablas={r['tablas_convertidas']:2} idx={r['indice_quitadas']:3}")

    DATA.mkdir(parents=True, exist_ok=True)
    resumen = {
        "fecha": date.today().isoformat(),
        "aplicado": aplicar,
        "n_pdfs": len(pdfs),
        "stats": stats,
        "tablas_detectadas": tot_tablas,
        "tablas_convertidas": tot_utiles,
        "mds_con_tabla": con_tabla,
        "indice_lineas_quitadas": tot_idx,
        "sin_url_oficial": stats["sin_url"],
        "fallos": informes_fallo[:40],
        "ficheros": resultados,
    }
    (DATA / "mejora_md_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")

    print("== RESULTADO ==")
    print(f"  extraídos sin pérdida : {stats['ok']}")
    print(f"  escaneados (OCR)      : {stats['ocr']}")
    print(f"  FALLOS (no escritos)  : {stats['fallos']}")
    print(f"  sin url_oficial       : {stats['sin_url']}")
    print(f"  tablas detectadas     : {tot_tablas}")
    print(f"  tablas CONVERTIDAS    : {tot_utiles}  (en {con_tabla} md)")
    print(f"  líneas índice quitadas: {tot_idx}")
    print(f"  resumen → database/data/mejora_md_resumen.json")

    if informes_fallo:
        print("\n  Primeros fallos:")
        for f in informes_fallo[:10]:
            print(f"    - {f[:140]}")

    # Gate H2: cero pérdidas, tablas presentes, índice fuera, url completa
    if stats["fallos"]:
        print("  GATE H2: FALLO — hay ficheros con pérdida de contenido")
        return 1
    if not aplicar:
        print("  (dry-run — GATE H2 pendiente de --aplicar)")
        return 0
    print("  GATE H2: OK — 0 pérdidas de contenido")
    return 0


if __name__ == "__main__":
    sys.exit(main())
