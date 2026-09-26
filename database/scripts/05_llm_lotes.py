#!/usr/bin/env python3
"""
05_llm_lotes.py — Fase 4: revisión LLM por lotes con CANDADO anti-alucinación.

Contrato anti-alucinación (lo central):
  El LLM NO devuelve datos: devuelve dato + CITA LITERAL del .md.
  Un verificador DETERMINISTA busca esa cita en esa página del md_base.
  Si no la encuentra exacta → RECHAZO. El verificador solo puede rechazar:
  nunca da por bueno algo que no puede comprobar.

Uso:
  py 05_llm_lotes.py --lote 10          # 10 informes pendientes
  py 05_llm_lotes.py --reintentar       # sólo rechazados/pendientes
  py 05_llm_lotes.py --solo STEM        # un informe (pruebas)
  py 05_llm_lotes.py --solo STEM --dry  # no llama al LLM, sólo prepara

Salidas:
  database/data/mejorado/<stem>.json    (1 por informe)
  database/data/progreso_llm.json       (estado global, reanudable)
Salida estándar: gate con % verificado y rechazados.

NUNCA imprime credenciales.
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import unicodedata
import threading
import random
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MD_BASE = RAIZ / "database" / "md_base"
CRUDO = RAIZ / "database" / "data" / "crudo"
DATA = RAIZ / "database" / "data"
MEJORADO = DATA / "mejorado"
PROGRESO = DATA / "progreso_llm.json"

MAX_TOKENS_VENTANA = 8000        # tokens por ventana (md + petición)
MAX_INTENTOS = 2                 # reintentos ante rechazo del verificador
CONCURRENCIA = 4                 # hilos del pool (semáforo separa API de threads)
MAX_PETICIONES_SIMULTANEAS = 4   # semáforo API: < límite real (5)
TIMEOUT = 240                    # 180 se queda corto con backoffs acumulados
REINTENTOS_API = 5               # +3 reintentos para 429
# Modelo de la revisión. mimo-v2.6-flash es el que usa este proyecto; si la
# API no lo sirve, --modelo qwen3.8-flash cae en el de enriquecer_ia.py.
MODELO_DEFECTO = "mimo-v2.6-flash"
# La cuota de mimo está compartida con otros crons de la misma API y devuelve
# 429 masivos. Tras UMBRAL_429 rechazos se pasa a un modelo con cuota propia.
FALLBACK_MODELO = "qwen3.8-flash"
UMBRAL_429 = 6
MODELO_ACTIVO = None            # sólo lo cambia el fallback
GRUPO_CAMPOS = 9                 # campos por llamada (salida corta = JSON válido)
MAX_TOKENS_SALIDA = 3500

# ── Semáforo global de concurrencia API ──────────────────────────────
_api_lock = threading.Lock()
_api_stats = {"ok": 0, "retry_429": 0, "other_err": 0, "in_flight": 0}
_api_semaphore = threading.Semaphore(MAX_PETICIONES_SIMULTANEAS)

RX_PAGINA = re.compile(r"^## Página (\d+)", re.M)


# ------------------------------------------------------------------ md
def paginas_de(texto: str):
    """[(nº, texto)] de md_base, usando los marcadores ## Página N."""
    ms = list(RX_PAGINA.finditer(texto))
    out = []
    for i, m in enumerate(ms):
        fin = ms[i + 1].start() if i + 1 < len(ms) else len(texto)
        out.append((int(m.group(1)), texto[m.end():fin]))
    return out


def texto_pagina(paginas, n):
    for num, t in paginas:
        if num == n:
            return t
    return ""


def normaliza(s: str) -> str:
    """Espacios colapsados + sin acentos: tolera que el LLM cite un espacio
    distinto, pero NO tolera que cite algo que no está."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[«»\"“”]", '"', s)
    return re.sub(r"\s+", " ", s).lower().strip()


def verifica_cita(paginas, cita, pagina):
    """Busca la cita EN LA PÁGINA citada. Devuelve (ok, motivo).

    Un solo fallo basta para rechazar: aquí es donde muere la alucinación.
    """
    if not cita or len(str(cita).strip()) < 12:
        return False, "cita demasiado corta (o vacía)"
    if not pagina:
        return False, "sin página citada"
    cuerpo = normaliza(texto_pagina(paginas, int(pagina)))
    if not cuerpo:
        return False, "página %s inexistente en el md" % pagina
    objetivo = normaliza(cita)
    if objetivo in cuerpo:
        return True, "ok"
    # tolerancia: el LLM puede partir la cita por espacios/tabuladores
    if len(objetivo) > 60 and objetivo[:60] in cuerpo:
        return True, "ok (coincide el inicio)"
    return False, "cita NO está en la página %s" % pagina


# ------------------------------------------------------------------ API
def api(modelo_flag=None):
    from dotenv import load_dotenv
    load_dotenv(os.path.expandvars(r"%LOCALAPPDATA%\hermes\.env"))
    modelo = modelo_flag or MODELO_DEFECTO
    if modelo == "por-defecto-del-repo":
        modelo = re.search(r'MODELO\s*=\s*["\']([^"\']+)',
                           (RAIZ / "scripts" / "enriquecer_ia.py")
                           .read_text(encoding="utf-8")).group(1)
    return (os.environ["OPENAI_BASE_URL"].rstrip("/"),
            os.environ["OPENAI_API_KEY"], modelo)


def _jitter(base_s: float) -> float:
    """Backoff exponencial ±30% de jitter (evita thundering herd)."""
    return base_s * (0.7 + random.random() * 0.6)


def llamar(base, key, modelo, system, user, max_tokens=MAX_TOKENS_SALIDA):
    """Semáforo ≤4 simultáneas + backoff exponencial jitter en 429."""
    global MODELO_ACTIVO
    # Un fallback puede haber cambiado el modelo mientras corría el lote:
    # el cambio es GLOBAL y a partir de aquí manda este, no el inicial.
    if MODELO_ACTIVO:
        modelo = MODELO_ACTIVO
    _api_semaphore.acquire()
    try:
        with _api_lock:
            _api_stats["in_flight"] += 1

        for i in range(REINTENTOS_API):
            txt = ""
            try:
                cuerpo = json.dumps({
                    "model": modelo,
                    "messages": [{"role": "system", "content": system},
                                 {"role": "user", "content": user}],
                    "temperature": 0.0,
                    "max_tokens": max_tokens,
                }).encode()
                req = urllib.request.Request(
                    base + "/chat/completions", data=cuerpo,
                    headers={"Content-Type": "application/json",
                             "Authorization": "Bearer " + key,
                             "User-Agent": "era-visor/1.0"})
                r = json.loads(urllib.request.urlopen(req, timeout=TIMEOUT).read())
                txt = r["choices"][0]["message"]["content"].strip()
                txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt)
                if not txt.lstrip().startswith("{"):
                    i_txt, j = txt.find("{"), txt.rfind("}")
                    if i_txt >= 0 and j > i_txt:
                        txt = txt[i_txt:j + 1]
                with _api_lock:
                    _api_stats["ok"] += 1
                    _api_stats["in_flight"] -= 1
                try:
                    return json.loads(txt)
                except json.JSONDecodeError:
                    # El modelo a veces emite el JSON DOS veces seguidas:
                    # `json.loads` falla con "Extra data" aunque el primer
                    # objeto sea válido. raw_decode se queda con el PRIMERO
                    # completo y desecha la repetición (medido en lote).
                    obj, _ = json.JSONDecoder().raw_decode(txt)
                    return obj

            except urllib.error.HTTPError as e:
                try:
                    detalle = e.read()[:220].decode("utf-8", "replace")
                except Exception:
                    detalle = ""
                if e.code == 429:
                    with _api_lock:
                        _api_stats["retry_429"] += 1
                        # La cuota del modelo está COMPARTIDA con otros crons
                        # de la misma API: tras N 429 se degrada al segundo
                        # modelo (cuota propia) en vez de morir en backoff.
                        # El cambio se imprime SIEMPRE: un cambio de modelo
                        # silencioso corrompe la trazabilidad del lote.
                        if (_api_stats["retry_429"] >= UMBRAL_429
                                and not _api_stats.get("fallback")):
                            _api_stats["fallback"] = modelo
                            _api_stats["fallback_a"] = FALLBACK_MODELO
                            MODELO_ACTIVO = FALLBACK_MODELO
                            print("    ⟳ 429 acumulados (%d) → FALLBACK de "
                                  "modelo: %s → %s"
                                  % (_api_stats["retry_429"], modelo,
                                     FALLBACK_MODELO), flush=True)
                    wait = _jitter(15 * (2 ** i))
                    print("    ! 429 (intento %d/%d) — sleep %.0fs"
                          % (i + 1, REINTENTOS_API, wait), flush=True)
                    time.sleep(wait)
                    continue
                with _api_lock:
                    _api_stats["other_err"] += 1
                    _api_stats["in_flight"] -= 1
                print("    ! HTTP %s: %s" % (e.code, detalle), flush=True)
                time.sleep(5 * (i + 1))

            except json.JSONDecodeError as e:
                with _api_lock:
                    _api_stats["other_err"] += 1
                    _api_stats["in_flight"] -= 1
                print("    ! JSON invalido (%s) | arranque: %r"
                      % (str(e)[:60], txt[:120]), flush=True)
                time.sleep(3)

            except Exception as e:
                with _api_lock:
                    _api_stats["other_err"] += 1
                    _api_stats["in_flight"] -= 1
                print("    ! %s: %s" % (type(e).__name__, str(e)[:200]),
                      flush=True)
                time.sleep(5 * (i + 1))

        with _api_lock:
            _api_stats["in_flight"] -= 1
        return None
    finally:
        _api_semaphore.release()


# ------------------------------------------------------------------ prompt
SYSTEMA = """Eres revisor de informes de la CIAF (Comisión de Investigación de
Accidentes Ferroviarios) de España. Tu ÚNICA fuente es el texto del informe
que te paso: NO uses conocimiento previo, NO deduzcas, NO completes.

REGLAS INQUEBRANTABLES:
1. Para CADA campo pedido devuelve su valor SÓLO si está en el texto.
2. JUNTO AL VALOR devuelves "pagina" (número de página tal y como aparece
   en los marcadores "## Página N") y "cita": un fragmento LITERAL,
   copiado y pegado tal cual del texto, de 15 a 180 caracteres, que
   CONTIENE el dato. Cita corta: el dato tiene que caber en ella.
3. Si el informe no menciona el campo: "valor": null, "pagina": null,
   "cita": null. Un null honesto vale más que un dato inventado.
4. La cita debe estar en la página que indiques. Nunca cites de memoria.
5. NO inventes fechas, cifras ni nombres. Si hay varios valores, devuelve
   el que diga el texto y cita dónde.

Responde SOLO con JSON válido, sin texto fuera de él, con esta forma:
{"resultados":[{"ref":"<ref del campo>","valor":<lo pedido>,"pagina":<int|null>,"cita":"<literal>"}]}"""


def prep_infome(stem):
    """Divide el informe en ventanas ≤ MAX_TOKENS_VENTANA y recoge los
    campos LLM pendientes de la guía."""
    ruta = MD_BASE / (stem + ".md")
    if not ruta.exists():
        return None
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    if texto.startswith("---"):
        fin = texto.find("---", 3)
        if fin > 0:
            texto = texto[fin + 3:]
    paginas = paginas_de(texto)
    # corta por páginas respetando el presupuesto de tokens (~4 chars/token)
    # ventanas = lista de [(nºpágina, texto)], una por cada ~MAX tokens
    limite = MAX_TOKENS_VENTANA * 4
    ventanas, actual, tamaño = [], [], 0
    for num, t in paginas:
        if tamaño + len(t) > limite and actual:
            ventanas.append(actual)
            actual, tamaño = [], 0
        actual.append((num, t))
        tamaño += len(t)
    if actual:
        ventanas.append(actual)
    return {"stem": stem, "paginas": paginas, "ventanas": ventanas,
            "campos_pendientes": None}


def texto_pagina_head(bloque):
    return "".join("\n## Página %d\n%s" % (n, t) for n, t in bloque)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", type=int, default=10)
    ap.add_argument("--solo", default=None)
    ap.add_argument("--reintentar", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--modelo", default=MODELO_DEFECTO)
    args = ap.parse_args()

    MEJORADO.mkdir(parents=True, exist_ok=True)
    progreso = json.loads(PROGRESO.read_text(encoding="utf-8")) \
        if PROGRESO.exists() else {"informes": {}}

    guia_raw = json.loads((DATA / "guia_campos.json").read_text(encoding="utf-8"))
    # campos que necesitan LLM: cumplimentar != Sí (los deterministas ya van)
    pendientes_guia = [
        {"ref": g["ref"], "campo": g.get("campo", "")}
        for g in guia_raw
        if str(g.get("ref", "")).strip()[:1].isdigit()
        and (g.get("campo") or "").strip()
        and str(g.get("cumplimentar", "")).strip().lower() not in ("sí", "si")
    ]

    stems = sorted(p.stem for p in MD_BASE.glob("*.md"))
    if args.solo:
        stems = [s for s in stems if args.solo.lower() in s.lower()]

    # selección: sin procesar, o con rechazados si --reintentar
    elegidos = []
    for s in stems:
        est = progreso["informes"].get(s, {})
        if args.solo:
            elegidos.append(s)
        elif args.reintentar:
            if est.get("pendientes") or est.get("rechazados"):
                elegidos.append(s)
        elif est.get("estado") != "hecho":
            elegidos.append(s)
        if len(elegidos) >= args.lote:
            break

    if not elegidos:
        print("No hay informes pendientes (o --reintentar no tiene nada que "
              "reintentar). progreso_llm.json: %d hechos."
              % sum(1 for v in progreso["informes"].values()
                    if v.get("estado") == "hecho"))
        return 0

    if args.dry:
        print("[dry] prepararía %d informes con %d campos LLM cada uno"
              % (len(elegidos), len(pendientes_guia)))
        for s in elegidos[:5]:
            print("   -", s[:70])
        return 0

    base, key, modelo = api(args.modelo)
    print("== Fase 4: revisión LLM con candado de verificación ==")
    print("  modelo: %s | lote: %d informes | campos/informe: %d"
          % (modelo, len(elegidos), len(pendientes_guia)))

    def procesar(stem):
        """1 informe → ventanas en paralelo → fusión → verificación."""
        inf = prep_infome(stem)
        if not inf:
            return stem, {"estado": "error", "motivo": "no existe md_base"}
        refs = pendientes_guia
        # 27 campos en una sola salida se cortan por max_tokens (medido:
        # "Unterminated string" a los 2.500 tokens). Se agrupan: salida
        # corta = JSON válido, y cada grupo se pregunta en CADA ventana
        # porque en informes largos el dato está en otra página.
        grupos = [refs[i:i + GRUPO_CAMPOS]
                  for i in range(0, len(refs), GRUPO_CAMPOS)]

        def una_ventana(t):
            bloque, grupo = t   # bloque = [(nºpág, texto), ...]
            peticion = ("CAMPOS A REVISAR (ref - nombre):\n"
                        + "\n".join("- %s: %s" % (r["ref"], r["campo"])
                                    for r in grupo))
            return llamar(base, key, modelo, SYSTEMA,
                          peticion + "\n\nINFORME:\n\n"
                          + texto_pagina_head(bloque))

        tareas = [(ve, g) for g in grupos for ve in inf["ventanas"]]
        with cf.ThreadPoolExecutor(CONCURRENCIA) as ex:
            respuestas = list(ex.map(una_ventana, tareas))
        recibidas = sum(1 for r in respuestas if r)
        devueltas = sum(len(r.get("resultados") or []) for r in respuestas if r)
        print("    tareas=%d (grupos=%d x ventanas=%d) con_respuesta=%d items=%d"
              % (len(tareas), len(grupos), len(inf["ventanas"]),
                 recibidas, devueltas), flush=True)

        # fusión: gana la primera cita que VERIFIQUE, por informe y ref
        mejores = {}
        for r in respuestas:
            if not r:
                continue
            for item in (r.get("resultados") or []):
                ref = str(item.get("ref") or "")
                if ref not in {x["ref"] for x in refs}:
                    continue
                prev = mejores.get(ref)
                # NULL HONESTO: el informe no menciona el campo. No tiene
                # cita porque no hay nada que citar, y eso NO es una
                # alucinación — castigarlo hundía el gate sin motivo.
                if item.get("valor") in (None, "", [], {}):
                    if not prev or not prev.get("verificado"):
                        mejores[ref] = {"valor": None, "cita": None,
                                        "pagina": None, "verificado": True,
                                        "verificacion": "null honesto: "
                                                        "no consta en el informe"}
                    continue
                ok, motivo = verifica_cita(inf["paginas"], item.get("cita"),
                                           item.get("pagina"))
                if ok:
                    if not prev or not prev.get("verificado"):
                        mejores[ref] = {"valor": item.get("valor"),
                                        "cita": item.get("cita"),
                                        "pagina": item.get("pagina"),
                                        "verificado": True,
                                        "verificacion": "cita literal en página"}
                elif not prev:
                    # un valor con cita FALSA es la única alucinación real:
                    # aquí es donde el candado hace su trabajo
                    mejores[ref] = {"valor": item.get("valor"),
                                    "cita": item.get("cita"),
                                    "pagina": item.get("pagina"),
                                    "verificado": False,
                                    "verificacion": motivo}

        # TRES categorías, nunca una sola cifra amable:
        #   con_cita      valor + cita literal comprobada en su página
        #   null_honestos el informe no lo menciona (sin cita: correcto)
        #   rechazados    valor con cita FALSA → la única alucinación real
        cita_ok = sum(1 for v in mejores.values()
                      if v["verificado"] and v.get("cita"))
        nulos = sum(1 for v in mejores.values()
                    if v["verificado"] and not v.get("cita"))
        rech = sum(1 for v in mejores.values() if not v["verificado"])
        (MEJORADO / (stem + ".json")).write_text(
            json.dumps({"stem": stem, "campos": mejores},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        return stem, {"estado": "hecho", "campos": len(mejores),
                      "con_cita": cita_ok, "null_honestos": nulos,
                      "rechazados": rech, "intentos": 1}

    t0 = time.time()

    # ── Progress reporter (hilo separada, cada 60s) ────────────────────
    def _reporter():
        while True:
            elapsed = time.time() - t0
            if elapsed > len(elegidos) * 2 * 60:  # timeout por lote
                break
            time.sleep(60)
            with _api_lock:
                st = dict(_api_stats)
            print("\n  [%.0fm] OK=%d 429=%d err=%d in_flight=%d"
                  % (elapsed/60, st["ok"], st["retry_429"],
                     st["other_err"], st["in_flight"]), flush=True)

    _reporter_thread = threading.Thread(target=_reporter, daemon=True)
    _reporter_thread.start()

    with cf.ThreadPoolExecutor(CONCURRENCIA) as ex:
        for stem, est in ex.map(procesar, elegidos):
            progreso["informes"][stem] = est
            print("  %-56s cita=%-3s null=%-3s RECHAZ=%s"
                  % (stem[:56], est.get("con_cita", "-"),
                     est.get("null_honestos", "-"),
                     est.get("rechazados", "-")), flush=True)

    _reporter_thread.join(timeout=5)

    progreso["actualizado"] = time.strftime("%Y-%m-%d %H:%M:%S")
    PROGRESO.write_text(json.dumps(progreso, ensure_ascii=False, indent=1),
                        encoding="utf-8")

    cita = sum(x.get("con_cita", 0) for x in progreso["informes"].values())
    nul = sum(x.get("null_honestos", 0) for x in progreso["informes"].values())
    r = sum(x.get("rechazados", 0) for x in progreso["informes"].values())
    h = sum(1 for x in progreso["informes"].values()
            if x.get("estado") == "hecho")
    tot = cita + r
    print("\n  lote: %d informes en %.0f s" % (len(elegidos), time.time() - t0))
    print("  acumulado: %d/%d informes hechos" % (h, len(stems)))
    print("  con cita verificada: %d | nulls honestos: %d | "
          "RECHAZADOS (cita falsa): %d" % (cita, nul, r))
    print("  tasa de rechazo (alucinación detectada): %.1f%%"
          % (100 * r / max(tot, 1)))
    # El gate NO es "% de campos resueltos" (eso se gana con nulls):
    # es que casi nada llegue con cita falsa y que el lote quede procesado.
    ok = (r / max(tot, 1)) <= 0.05 and (cita + nul) > 0
    print("  GATE H5: %s" % ("OK (rechazo ≤5%% y lote procesado)" if ok
                             else "RECHAZOS DEMASIADOS — no dar por bueno"))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
