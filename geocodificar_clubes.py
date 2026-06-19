"""
Liga de Básquetbol — Geocodificador de clubes
----------------------------------------------
Lee clubes.csv (sin coordenadas) y agrega lat/lng automáticamente
consultando Nominatim (OpenStreetMap). Gratis, sin API key.

Uso:
    pip install requests
    python geocodificar_clubes.py

Archivos:
    clubes.csv         → entrada (vos editás con nombre, dirección, comuna)
    clubes_geo.csv     → salida  (mismo contenido + lat y lng)

Solo geocodifica clubes nuevos o que no tienen coordenadas todavía.
Los que ya tienen lat/lng se mantienen sin tocar.
"""

import csv
import time
import os
import requests

ARCHIVO_ENTRADA = "clubes.csv"
ARCHIVO_SALIDA  = "clubes.csv"   # sobreescribe el mismo archivo
ESPERA_ENTRE_REQUESTS = 1.1      # Nominatim pide mínimo 1 seg entre consultas


def geocodificar(direccion, comuna):
    """Convierte dirección + comuna → (lat, lng) usando Nominatim."""
    query = f"{direccion}, {comuna}, Santiago, Chile"
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "cl"
    }
    headers = {
        "User-Agent": "LigaBasquetbol/1.0"   # Nominatim requiere User-Agent
    }

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"     ⚠️  Error consultando Nominatim: {e}")

    return None, None


def procesar_clubes():
    if not os.path.exists(ARCHIVO_ENTRADA):
        print(f"❌  No se encontró '{ARCHIVO_ENTRADA}'")
        exit(1)

    # Leer clubes actuales
    with open(ARCHIVO_ENTRADA, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        clubes = list(reader)
        fieldnames = reader.fieldnames or []

    # Agregar columnas lat/lng si no existen
    if "lat" not in fieldnames:
        fieldnames = fieldnames + ["lat", "lng"]

    print()
    print("🏀  Geocodificador de clubes")
    print("─" * 45)
    print(f"   {len(clubes)} clubes en '{ARCHIVO_ENTRADA}'")
    print()

    cambios = 0

    for i, club in enumerate(clubes):
        nombre = club.get("nombre", f"Club #{i+1}")

        # Si ya tiene coordenadas, saltear
        lat_actual = club.get("lat", "").strip()
        lng_actual = club.get("lng", "").strip()
        if lat_actual and lng_actual:
            print(f"   ✓  {nombre} — ya tiene coordenadas ({lat_actual}, {lng_actual})")
            continue

        direccion = club.get("direccion", "").strip()
        comuna    = club.get("comuna", "").strip()

        if not direccion:
            print(f"   ⚠️  {nombre} — sin dirección, se omite")
            club["lat"] = ""
            club["lng"] = ""
            continue

        print(f"   📍 Buscando: {nombre} ({direccion}, {comuna})...")

        lat, lng = geocodificar(direccion, comuna)

        if lat and lng:
            club["lat"] = lat
            club["lng"] = lng
            cambios += 1
            print(f"      ✅ Encontrado: {lat:.5f}, {lng:.5f}")
        else:
            club["lat"] = ""
            club["lng"] = ""
            print(f"      ❌ No encontrado — revisá la dirección")

        # Respetar límite de Nominatim
        if i < len(clubes) - 1:
            time.sleep(ESPERA_ENTRE_REQUESTS)

    # Guardar resultado
    with open(ARCHIVO_SALIDA, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clubes)

    print()
    print(f"✅  {cambios} clubes geocodificados")
    print(f"✔   Guardado en '{ARCHIVO_SALIDA}'")
    print()


if __name__ == "__main__":
    procesar_clubes()
