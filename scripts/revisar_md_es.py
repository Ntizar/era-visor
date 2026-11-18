# -*- coding: utf-8 -*-
"""revisar_md_es.py — revisor IA del castellano contra el original, informe a informe.

Para cada md-es/<CC>/<AAAA>/<slug>.md:
  · localiza el md original (campo md_origen del frontmatter),
  · empareja páginas por el marcador `## Página N`,
  · elige N páginas de muestra (las de más texto, repartidas por el documento:
    portada, hechos, causas, recomendaciones...),
  · pide al modelo revisor que compare ORIGINAL vs CASTELLANO y devuelva JSON:
      fidelidad 0-100, omisiones[], invenciones[], numeros_ok, terminos[], veredicto,
  · agrega el veredicto del informe y lo guarda en data/revision/<CC>.json.

Uso:
    python scripts/revisar_md_es.py LU --muestras 6 --modelo deepseek-v4-pro
    python scripts/revisar_md_es.py PT FR --workers 3

Veredicto del informe:
    ok        → todas las muestras con fidelidad >= 85 y sin invenciones ni números mal
    revisar   → cualquier otra cosa (se lista el motivo, no se maquilla)
"""
import argparse
import concurrent.futures as cf
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_ES = os.path.join(RAIZ, "md-es")
REV = os.path.join(RAIZ, "data", "revision")
MODELO_DEF = "deepseek-v4-pro"
UMBRAL = 85

SISTEMA = """Eres revisor jefe de una base de datos de accidentes ferroviarios. Recibes dos
fragmentos de un mismo informe: el ORIGINAL y su TRADUCCIÓN al castellano. Tu trabajo es
detectar defectos de traducción, no mejorar el estilo.

Criterios:
- omision: contenido del original que falta en la traducción (frases, cifras, filas de tabla).
- invencion: contenido en la traducción que NO está en el original.
- numeros_ok: false si alguna cifra, hora, fecha, PK, código o referencia cambia.
- terminos: términos técnicos mal traducidos o no normalizados (ej. "descarrilamiento" vs
  "descarrilamiento por rotura de eje" cuando el original distingue).
- fidelidad: 0-100 (100 = traducción completa y exacta).

Devuelve SOLO un objeto JSON con esta forma exacta:
{"fidelidad": 0-100, "omisiones": ["..."], "invenciones": ["..."], "numeros_ok": true,
 "terminos": ["..."], "veredicto": "ok"|"revisar", "comentario": "una frase"}"""


def cargar_api():
    from dotenv import load_dotenv
    ruta = os.path.expandvars(r"%LOCALAPPDATA%\hermes\.env")
    if os.path.exists(ruta):
        load_dotenv(ruta)
    return (os.environ["OPENAI_BASE_URL"].strip().strip('"').rstrip("/"),
            os.environ["OPENAI_API_KEY"].strip())


def fm_y_cuerpo(texto):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", texto, re.S)
    fm = {}
    if m:
        for l in m.group(1).splitlines():
            if ":" in l:
                k, v = l.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
        return fm, texto[m.end():]
    return fm, texto


def paginas(cuerpo):
    out = {}
    trozos = re.split(r"(?m)^## Página (\d+)\s*$", cuerpo)
    for i in range(1, len(trozos) - 1, 2):
        out[int(trozos[i])] = trozos[i + 1].strip()
    return out


def elegir(pags, n):
    """Portada + reparto uniforme por el documento, sólo páginas con texto útil."""
    util = [(k, t) for k, t in pags.items() if len(t) > 400]
    if not util:
        return []
    util.sort()
    if len(util) <= n:
        return util
    paso = len(util) / n
    return [util[min(int(i * paso), len(util) - 1)] for i in range(n)]


def llamar(base, key, modelo, mensajes, intentos=4):
    payload = json.dumps({"model": modelo, "messages": mensajes, "temperature": 0.0,
                          "max_tokens": 2000, "enable_thinking": False}).encode()
    for i in range(intentos):
        req = urllib.request.Request(
            base + "/chat/completions", data=payload,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        try:
            r = json.loads(urllib.request.urlopen(req, timeout=300).read())
            return r["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < intentos - 1:
                time.sleep(6 * (i + 1))
                continue
            raise
        except Exception:
            if i < intentos - 1:
                time.sleep(4 * (i + 1))
                continue
            raise


def json_de(txt):
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def revisar_uno(ruta, base, key, modelo, n_muestras):
    t_es = open(ruta, encoding="utf-8").read()
    fm, cuerpo_es = fm_y_cuerpo(t_es)
    origen = fm.get("md_origen", "")
    ruta_origen = os.path.join(RAIZ, origen.replace("/", os.sep))
    if not origen or not os.path.exists(ruta_origen):
        return {"estado": "error", "motivo": f"sin original ({origen})"}
    _, cuerpo_or = fm_y_cuerpo(open(ruta_origen, encoding="utf-8").read())
    p_or, p_es = paginas(cuerpo_or), paginas(cuerpo_es)

    muestras, evaluaciones = elegir(p_or, n_muestras), []
    for num, txt_or in muestras:
        txt_es = p_es.get(num, "")
        if not txt_es:
            evaluaciones.append({"pagina": num, "fidelidad": 0, "veredicto": "revisar",
                                 "comentario": "página ausente en el castellano"})
            continue
        user = (f"PÁGINA {num}\n\n=== ORIGINAL ===\n{txt_or[:6000]}\n\n"
                f"=== TRADUCCIÓN (castellano) ===\n{txt_es[:6000]}")
        ev = None
        for intento in range(3):
            try:
                raw = llamar(base, key, modelo,
                             [{"role": "system", "content": SISTEMA}, {"role": "user", "content": user}])
                ev = json_de(raw)
                if ev and isinstance(ev.get("fidelidad"), (int, float)):
                    break
            except Exception as e:
                ev = {"comentario": f"error LLM: {e}"[:200]}
            time.sleep(2)
        if not ev or not isinstance(ev.get("fidelidad"), (int, float)):
            # No se inventa una nota: la página queda sin dictamen y se dice.
            ev = {"fidelidad": None, "veredicto": "sin_dictamen",
                  "comentario": (ev or {}).get("comentario", "respuesta no parseable")}
        ev["pagina"] = num
        evaluaciones.append(ev)

    con_nota = [e for e in evaluaciones if isinstance(e.get("fidelidad"), (int, float))]
    fids = [e["fidelidad"] for e in con_nota] or [0]
    graves = [e for e in evaluaciones
              if (isinstance(e.get("fidelidad"), (int, float)) and e["fidelidad"] < UMBRAL)
              or e.get("invenciones") or e.get("numeros_ok") is False
              or e.get("veredicto") == "sin_dictamen"]
    notas = [e for e in evaluaciones if e.get("terminos") and e not in graves]
    estado = "revisar" if graves else ("aviso" if notas else "ok")
    return {
        "estado": estado,
        "idioma_origen": fm.get("idioma_origen", ""),
        "paginas_revisadas": [e["pagina"] for e in evaluaciones],
        "fidelidad_media": round(sum(fids) / len(fids), 1),
        "fidelidad_min": min(fids),
        "sin_dictamen": [e["pagina"] for e in evaluaciones
                         if e.get("veredicto") == "sin_dictamen"],
        "terminos": [t for e in notas for t in (e.get("terminos") or [])][:6],
        "fallos": [{"pagina": e.get("pagina"), "fidelidad": e.get("fidelidad"),
                    "omisiones": (e.get("omisiones") or [])[:3],
                    "invenciones": (e.get("invenciones") or [])[:3],
                    "numeros_ok": e.get("numeros_ok"),
                    "terminos": (e.get("terminos") or [])[:3],
                    "comentario": e.get("comentario", "")} for e in graves][:6],
        "fecha": datetime.date.today().isoformat(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paises", nargs="+")
    ap.add_argument("--modelo", default=MODELO_DEF)
    ap.add_argument("--muestras", type=int, default=6)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limite", type=int, default=0)
    a = ap.parse_args()
    base, key = cargar_api()
    os.makedirs(REV, exist_ok=True)

    for code in [c.upper() for c in a.paises]:
        raiz = os.path.join(MD_ES, code)
        if not os.path.isdir(raiz):
            print(f"[{code}] sin md-es")
            continue
        ficheros = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(raiz)
                          for f in fs if f.endswith(".md")
                          and not f.lower().startswith(("indice", "índice", "readme", "leeme")))
        if a.limite:
            ficheros = ficheros[:a.limite]
        print(f"[{code}] revisando {len(ficheros)} informes · {a.muestras} muestras · {a.modelo}")
        res = {}
        with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(revisar_uno, f, base, key, a.modelo, a.muestras): f for f in ficheros}
            for k, fut in enumerate(cf.as_completed(futs), 1):
                f = futs[fut]
                try:
                    r = fut.result()
                except Exception as e:
                    r = {"estado": "error", "motivo": str(e)[:200]}
                rel = os.path.relpath(f, RAIZ).replace("\\", "/")
                r["md_es"] = rel
                res[rel] = r
                if r["estado"] != "ok":
                    print(f"  [{k}/{len(ficheros)}] {r['estado']:7s} {os.path.basename(f)} "
                          f"· fidelidad {r.get('fidelidad_media','-')} · {r.get('motivo','')[:80]}")
        salida = os.path.join(REV, f"{code}.json")
        json.dump(res, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        ok = sum(1 for r in res.values() if r["estado"] == "ok")
        av = sum(1 for r in res.values() if r["estado"] == "aviso")
        mal = len(res) - ok - av
        medias = [r["fidelidad_media"] for r in res.values() if "fidelidad_media" in r]
        print(f"[{code}] REVISADOS {len(res)} · ok {ok} · aviso {av} · revisar {mal} · "
              f"fidelidad media {round(sum(medias)/len(medias),1) if medias else '-'} → {salida}")


if __name__ == "__main__":
    main()
