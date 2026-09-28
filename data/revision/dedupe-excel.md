# Dedupe del Excel — un expediente, una fila

Regla de David (2026-09-28): «quédate siempre con el que tenga más páginas e información».

Los 21 expedientes con DOS documentos (IF + resumen de 2 pág, final vs interim, español vs inglés) resueltos por (paginas, campos). El documento descartado NO se borra: está en `database/data/duplicados_excel/` y su ficha dice qué era.

| Expediente | Se queda | Descartado | Motivo |
|---|---|---|---|
| 0005/14 | ES 23.01.2014 IF_230114_270115_CIAF.pdf (IF, 23p, 45 campos) | IF_230114_270115_CIAF.pdf (IF, 23p, 18 campos) | más páginas e información: 23p/45 campos contra 23p/18 |
| 0007/09 | IF-300109-140709-CIAF.pdf (IF, 11p, 42 campos) | RS-300109-140709-CIAF.pdf (RS, 2p, 1 campos) | más páginas e información: 11p/42 campos contra 2p/1 |
| 0009/09 | IF-140209-290909-CIAF.pdf (IF, 18p, 43 campos) | RS-140209-290909-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 18p/43 campos contra 2p/5 |
| 0010/09 | IF-020209-221209-CIAF.pdf (IF, 12p, 46 campos) | RS-020209-221209-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 12p/46 campos contra 2p/5 |
| 0012/09 | IF-220209-140709-CIAF.pdf (IF, 10p, 44 campos) | RS-220209-140709-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 10p/44 campos contra 2p/5 |
| 0013/09 | IF-230209-140709-CIAF.pdf (IF, 11p, 42 campos) | RS-230209-140709-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 11p/42 campos contra 2p/5 |
| 0015/09 | IF-040309-140709-CIAF.pdf (IF, 11p, 41 campos) | RS-040309-140709-CIAF.pdf (RS, 2p, 1 campos) | más páginas e información: 11p/41 campos contra 2p/1 |
| 0017/09 | IF-240309-140709-CIAF_ALGEMESÍ.pdf (IF, 12p, 41 campos) | RS-240309-140709-CIAF.pdf (RS, 2p, 1 campos) | más páginas e información: 12p/41 campos contra 2p/1 |
| 0018/09 | IF-240309-290909-CIAF_VILLARGORDO Y GRAÑENA.pdf (IF, 10p, 48 campos) | RS-240309-290909-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 10p/48 campos contra 2p/5 |
| 0019/09 | IF-070409-271009-CIAF.pdf (IF, 10p, 41 campos) | RS-070409-271009-CIAF.pdf (RS, 2p, 1 campos) | más páginas e información: 10p/41 campos contra 2p/1 |
| 0022/09 | IF-170409-221209-CIAF.pdf (IF, 11p, 50 campos) | RS-170409-221209-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 11p/50 campos contra 2p/5 |
| 0025/09 | IF-050609-221209-CIAF.pdf (IF, 12p, 45 campos) | RS-050609-221209-CIAF.pdf (RS, 2p, 1 campos) | más páginas e información: 12p/45 campos contra 2p/1 |
| 0027/09 | IF-180609-221209-CIAF.pdf (IF, 11p, 50 campos) | RS-180609-221209-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 11p/50 campos contra 2p/5 |
| 0028/09 | IF-220609-221209-CIAF.pdf (IF, 11p, 42 campos) | RS-220609-221209-CIAF.pdf (RS, 2p, 1 campos) | más páginas e información: 11p/42 campos contra 2p/1 |
| 0030/09 | IF-260609-221209-CIAF_ALUCHE.pdf (IF, 16p, 50 campos) | RS-260609-221209-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 16p/50 campos contra 2p/5 |
| 0031/09 | IF-060709-221209-CIAF.pdf (IF, 11p, 51 campos) | RS-060709-221209-CIAF.pdf (RS, 2p, 1 campos) | más páginas e información: 11p/51 campos contra 2p/1 |
| 0036/14 | ES 11 07 2014 150525-140711-IF-CIAF-1.pdf (IF, 19p, 46 campos) | ES 11 07 2014 150525-140711-IF-CIAF.pdf (IF, 19p, 18 campos) | más páginas e información: 19p/46 campos contra 19p/18 |
| 0043/2023 | ES-10479 - Final Report - 2023-43-0518-IF.pdf (IF, 27p, 55 campos) | ES-10479 - Interim Staatement -NotaAvanceInvesti (INTERIM, 2p, 0 campos) | más páginas e información: 27p/55 campos contra 2p/0 |
| 0053/08 | IF-231008-140709-CIAF.pdf (IF, 11p, 47 campos) | RS-231008-140709-CIAF.pdf (RS, 2p, 5 campos) | más páginas e información: 11p/47 campos contra 2p/5 |
| 0054/08 | IF-241008-140709-CIAF.pdf (IF, 16p, 44 campos) | RS-241008-140709-CIAF.pdf (RS, 3p, 5 campos) | más páginas e información: 16p/44 campos contra 3p/5 |
| 0054/13 | IF_240713_200514_CIAF.pdf (IF, 266p, 47 campos) | IF_240713_ERA-2014-0070-EN.pdf (IF, 110p, 0 campos) | más páginas e información: 266p/47 campos contra 110p/0 |
