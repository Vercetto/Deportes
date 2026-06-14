"""
Liga de Básquetbol — Calculador de posiciones
----------------------------------------------
Lee partidos.csv y genera posiciones.csv automáticamente.

Uso:
    python calcular_posiciones.py

Archivos:
    partidos.csv   → entrada (vos lo editás con los resultados)
    posiciones.csv → salida  (se genera solo)
"""

import csv
import os
from collections import defaultdict

# ── Configuración ──────────────────────────────────────────────────
ARCHIVO_PARTIDOS   = "partidos.csv"
ARCHIVO_POSICIONES = "posiciones.csv"

# Sistema de puntos (estándar FIBA)
PUNTOS_VICTORIA = 2
PUNTOS_DERROTA  = 1
# ──────────────────────────────────────────────────────────────────


def leer_partidos(archivo):
    """Lee el CSV de partidos y devuelve una lista de diccionarios."""
    if not os.path.exists(archivo):
        print(f"❌  No se encontró el archivo '{archivo}'")
        print(f"    Asegurate de que esté en la misma carpeta que este script.")
        exit(1)

    partidos = []
    with open(archivo, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for fila in reader:
            partidos.append(fila)

    print(f"✅  {len(partidos)} partidos leídos desde '{archivo}'")
    return partidos


def calcular_posiciones(partidos):
    """Calcula las estadísticas de cada equipo a partir de los partidos finalizados."""
    stats = defaultdict(lambda: {
        'pj': 0, 'pg': 0, 'pp': 0,
        'pf': 0, 'pc': 0, 'pts': 0
    })

    finalizados = 0

    for p in partidos:
        if p.get('estado', '').strip().lower() != 'finalizado':
            continue

        local     = p['local'].strip()
        visitante = p['visitante'].strip()

        try:
            pts_local = int(p['pts_local'])
            pts_visit = int(p['pts_visitante'])
        except (ValueError, KeyError):
            print(f"⚠️   Partido #{p.get('id','?')}: puntos inválidos, se omite.")
            continue

        finalizados += 1

        # Partidos jugados
        stats[local]['pj']     += 1
        stats[visitante]['pj'] += 1

        # Puntos a favor y en contra
        stats[local]['pf']     += pts_local
        stats[local]['pc']     += pts_visit
        stats[visitante]['pf'] += pts_visit
        stats[visitante]['pc'] += pts_local

        # Victoria / derrota
        if pts_local > pts_visit:
            stats[local]['pg']     += 1
            stats[visitante]['pp'] += 1
        else:
            stats[visitante]['pg'] += 1
            stats[local]['pp']     += 1

    # Calcular puntos de tabla
    for equipo, s in stats.items():
        s['pts'] = (s['pg'] * PUNTOS_VICTORIA) + (s['pp'] * PUNTOS_DERROTA)

    print(f"✅  {finalizados} partidos finalizados procesados")
    return stats


def ordenar_ranking(stats):
    """Ordena los equipos por: puntos → diferencia → puntos a favor."""
    ranking = []
    for equipo, s in stats.items():
        ranking.append({
            'equipo': equipo,
            'pts':    s['pts'],
            'pg':     s['pg'],
            'pp':     s['pp'],
            'pj':     s['pj'],
            'pf':     s['pf'],
            'pc':     s['pc'],
            'dif':    s['pf'] - s['pc']
        })

    ranking.sort(key=lambda x: (x['pts'], x['dif'], x['pf']), reverse=True)
    return ranking


def guardar_posiciones(ranking, archivo):
    """Escribe el CSV de posiciones."""
    columnas = ['equipo', 'pts', 'pg', 'pp', 'pj', 'pf', 'pc', 'dif']

    with open(archivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        for i, fila in enumerate(ranking, start=1):
            writer.writerow({k: fila[k] for k in columnas})

    print(f"✅  Posiciones guardadas en '{archivo}'")


def imprimir_tabla(ranking):
    """Muestra la tabla en la terminal de forma legible."""
    print()
    print("=" * 62)
    print(f"  {'#':<3} {'EQUIPO':<15} {'PTS':>4} {'PG':>4} {'PP':>4} {'PJ':>4} {'PF':>5} {'PC':>5} {'DIF':>5}")
    print("=" * 62)
    for i, r in enumerate(ranking, start=1):
        dif = f"+{r['dif']}" if r['dif'] > 0 else str(r['dif'])
        print(f"  {i:<3} {r['equipo']:<15} {r['pts']:>4} {r['pg']:>4} {r['pp']:>4} {r['pj']:>4} {r['pf']:>5} {r['pc']:>5} {dif:>5}")
    print("=" * 62)
    print()


def main():
    print()
    print("🏀  Liga de Básquetbol — Calculador de posiciones")
    print("─" * 50)

    partidos = leer_partidos(ARCHIVO_PARTIDOS)
    stats    = calcular_posiciones(partidos)
    ranking  = ordenar_ranking(stats)

    imprimir_tabla(ranking)
    guardar_posiciones(ranking, ARCHIVO_POSICIONES)

    print("✔   Listo. Podés subir 'posiciones.csv' a tu carpeta del proyecto.")
    print()


if __name__ == "__main__":
    main()
