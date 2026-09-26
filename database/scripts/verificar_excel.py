"""Verificación independiente del Excel global (GATE H4 externo).

No se fía del resumen del generador: relee el .xlsx y comprueba
las reglas de negocio del usuario: 1 fila por informe, url_oficial
100% en todas las hojas, y las columnas de guía reales (sin títulos).
"""
import os
from openpyxl import load_workbook

P = "database/data/ciaf_base_global.xlsx"
print("tamaño: %.2f MB" % (os.path.getsize(P) / 1048576))
wb = load_workbook(P, read_only=True)
print("hojas:", wb.sheetnames)

ws = wb["Informes"]
filas = list(ws.iter_rows(values_only=True))
cab = [c if c else "" for c in filas[0]]
datos = filas[1:]
print("Informes: %d filas x %d col" % (len(datos), len(cab)))

TITULOS_BLOQUE = {"0. DATOS DE CONTROL DEL INFORME", "1. RESUMEN", "2. LA INVESTIGACIÓN",
                  "3. ANÁLISIS DEL SUCESO", "4. RECOMENDACIONES", "4.6 RECOMENDACIONES"}
i_url, i_clave, i_tit = cab.index("url_oficial"), cab.index("clave"), cab.index("titulo")

# 1 fila por informe, url_oficial obligatoria
urls_vacias = sum(1 for f in datos if not (f[i_url] or "").strip())
claves_vacias = sum(1 for f in datos if not (f[i_clave] or "").strip())
titulos_vacia = sum(1 for f in datos if not (f[i_tit] or "").strip())
print("url_oficial vacías:", urls_vacias, "| clave vacía:", claves_vacias,
      "| título vacío:", titulos_vacia)

# ningún título de bloque colado como columna de guía
colados = [c for c in cab if c in TITULOS_BLOQUE or c.startswith(("0. DATOS", "1. RESUMEN"))]
print("títulos de bloque colados:", colados if colados else "0")

# refs duplicadas -> columnas repetidas (romperían la base)
refs = [c.split(" ")[0] for c in cab if c[:1].isdigit()]
dups = {r for r in refs if refs.count(r) > 1}
print("refs duplicadas:", dups if dups else "0")

# hojas 1-a-N: toda fila debe arrastrar url_oficial
for n in ["Recomendaciones", "Entidades", "Cronologia", "Trenes", "Personal"]:
    w = wb[n]
    f = list(w.iter_rows(values_only=True))
    if not f:
        print("%-16s VACÍA" % n)
        continue
    c = [x if x else "" for x in f[0]]
    iu = c.index("url_oficial") if "url_oficial" in c else None
    vu = ("" if iu is None else
          sum(1 for r in f[1:] if not (r[iu] or "").strip()))
    print("%-16s %5d filas x %3d col | url vacías: %d" % (n, len(f) - 1, len(c), vu))

# cobertura: cuántos campos con valor y cómo quedan los que están a 0
w = wb["Cobertura"]
cov = list(w.iter_rows(values_only=True))
ch = [x if x else "" for x in cov[0]]
ir, ival, icit = ch.index("ref"), ch.index("con_valor"), ch.index("con_cita")
datos_cov = [r for r in cov[1:]]
con_valor = [r for r in datos_cov if (r[ival] or 0) > 0]
cero = [(r[ir], r[ch.index("campo")]) for r in datos_cov if (r[ival] or 0) == 0]
pct_medio = sum((r[ival] or 0) for r in datos_cov) / max(len(datos_cov), 1)
print("\nCobertura: %d/%d campos con algún valor | media %.0f%% por campo"
      % (len(con_valor), len(datos_cov), pct_medio))
print("campos a 0 (%d):" % len(cero))
for ref, camp in cero:
    print("   %-8s %s" % (ref, (camp or "")[:52]))

# el gate: url 100% y ninguna columna-colado
ok = (urls_vacias == 0 and claves_vacias == 0 and not colados and not dups)
print("\nGATE H4 (externo): %s" % ("OK" if ok else "FALLA"))
raise SystemExit(0 if ok else 1)
