#!/usr/bin/env python3
"""
Consulta football-data.org y genera resultados.json con los marcadores
del Mundial FIFA 2026. Lo ejecuta GitHub Actions cada hora.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN")
if not API_TOKEN:
    print("ERROR: falta la variable de entorno FOOTBALL_API_TOKEN")
    sys.exit(1)

# ID de la FIFA World Cup 2026 en football-data.org
# El código de competición es WC (World Cup)
COMPETITION_URL = "https://api.football-data.org/v4/competitions/WC/matches"

# Mapa de nombres de equipos: como los devuelve la API -> como aparecen en el HTML
# Se usa el atributo data-home / data-away para el cruce
# Mapa completo: cubre todas las variantes que devuelve la API (inglés y español mezclados)
TEAM_MAP = {
    # --- Variantes en inglés que la API devuelve ---
    "Mexico":              "México",
    "South Africa":        "Sudáfrica",
    "Canada":              "Canadá",
    "Switzerland":         "Suiza",
    "Brazil":              "Brasil",
    "Morocco":             "Marruecos",
    "Haiti":               "Haití",
    "Scotland":            "Escocia",
    "Germany":             "Alemania",
    "Netherlands":         "Países Bajos",
    "Ivory Coast":         "Costa de Marfil",
    "Sweden":              "Suecia",
    "Belgium":             "Bélgica",
    "Egypt":               "Egipto",
    "Saudi Arabia":        "Arabia Saudita",
    "Iran":                "Irán",
    "France":              "Francia",
    "Iraq":                "Irak",
    "Algeria":             "Argelia",
    "Jordan":              "Jordania",
    "England":             "Inglaterra",
    "Croatia":             "Croacia",
    "Ghana":               "Ghana",
    "Panama":              "Panamá",
    "Spain":               "España",
    "Norway":              "Noruega",
    "Tunisia":             "Túnez",
    "Japan":               "Japón",
    "Turkey":              "Turquía",
    "New Zealand":         "Nueva Zelanda",
    "Uzbekistan":          "Uzbekistán",
    "South Korea":         "Corea del Sur",
    "Czechia":             "Rep. Checa",
    "Congo DR":            "Congo RD",
    "Curaçao":             "Curazao",
    # --- Variantes ya en español que la API devuelve directamente ---
    "México":              "México",
    "Sudáfrica":           "Sudáfrica",
    "Canadá":              "Canadá",
    "Qatar":               "Qatar",
    "Brasil":              "Brasil",
    "Marruecos":           "Marruecos",
    "Haití":               "Haití",
    "Escocia":             "Escocia",
    "Australia":           "Australia",
    "Alemania":            "Alemania",
    "Países Bajos":        "Países Bajos",
    "Costa de Marfil":     "Costa de Marfil",
    "Suecia":              "Suecia",
    "Bélgica":             "Bélgica",
    "Egipto":              "Egipto",
    "Arabia Saudita":      "Arabia Saudita",
    "Irán":                "Irán",
    "Francia":             "Francia",
    "Irak":                "Irak",
    "Argelia":             "Argelia",
    "Jordania":            "Jordania",
    "Portugal":            "Portugal",
    "Inglaterra":          "Inglaterra",
    "Croacia":             "Croacia",
    "Ghana":               "Ghana",
    "Panamá":              "Panamá",
    "Colombia":            "Colombia",
    "Suiza":               "Suiza",
    "Ecuador":             "Ecuador",
    "España":              "España",
    "Uruguay":             "Uruguay",
    "Noruega":             "Noruega",
    "Túnez":               "Túnez",
    "Japón":               "Japón",
    "Turquía":             "Turquía",
    "Nueva Zelanda":       "Nueva Zelanda",
    "Argentina":           "Argentina",
    "Austria":             "Austria",
    "Senegal":             "Senegal",
    "Corea del Sur":       "Corea del Sur",
    "Rep. Checa":          "Rep. Checa",
    "Bosnia y Herz.":      "Bosnia y Herz.",
    "EE.UU.":              "EE.UU.",
    "Cabo Verde":          "Cabo Verde",
    "Congo RD":            "Congo RD",
    "Curazao":             "Curazao",
    "Uzbekistán":          "Uzbekistán",
    "Paraguay":            "Paraguay",
    "Senegal":             "Senegal",
    "Noruega":             "Noruega",
}


def fetch_matches():
    req = urllib.request.Request(
        COMPETITION_URL,
        headers={"X-Auth-Token": API_TOKEN}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"Error de red: {e}")
        sys.exit(1)


def normalize(name):
    """Convierte nombre de la API al nombre del HTML."""
    return TEAM_MAP.get(name, name)


def build_results(data):
    """
    Genera un dict con clave 'Local vs Visitante' (nombres en español)
    y valor con el marcador y estado del partido.
    """
    results = {}
    for match in data.get("matches", []):
        status = match.get("status")          # SCHEDULED, IN_PLAY, PAUSED, FINISHED, etc.
        score  = match.get("score", {})
        home_raw = match["homeTeam"]["name"]
        away_raw = match["awayTeam"]["name"]
        # Ignorar entradas basura de la API
        if not home_raw or not away_raw or home_raw == "None" or away_raw == "None":
            continue
        home   = normalize(home_raw)
        away   = normalize(away_raw)
        key    = f"{home} vs {away}"

        full   = score.get("fullTime", {})
        home_g = full.get("home")
        away_g = full.get("away")

        results[key] = {
            "status":    status,
            "home_goals": home_g,
            "away_goals": away_g,
        }

    return results


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Consultando API...")
    data = fetch_matches()
    results = build_results(data)

    # Guardar en resultados.json en la raiz del repo (directorio de trabajo del Action)
    output_path = "resultados.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated": datetime.now(timezone.utc).isoformat(),
            "matches": results
        }, f, ensure_ascii=False, indent=2)

    print(f"Guardado: {output_path} ({len(results)} partidos)")


if __name__ == "__main__":
    main()
