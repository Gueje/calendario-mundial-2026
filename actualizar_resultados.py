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
TEAM_MAP = {
    "Mexico":              "México",
    "South Africa":        "Sudáfrica",
    "Korea Republic":      "Corea del Sur",
    "Czech Republic":      "Rep. Checa",
    "Canada":              "Canadá",
    "Bosnia and Herzegovina": "Bosnia y Herz.",
    "USA":                 "EE.UU.",
    "Paraguay":            "Paraguay",
    "Qatar":               "Qatar",
    "Switzerland":         "Suiza",
    "Brazil":              "Brasil",
    "Morocco":             "Marruecos",
    "Haiti":               "Haití",
    "Scotland":            "Escocia",
    "Australia":           "Australia",
    "Turkey":              "Turquía",
    "Germany":             "Alemania",
    "Curaçao":             "Curazao",
    "Netherlands":         "Países Bajos",
    "Japan":               "Japón",
    "Ivory Coast":         "Costa de Marfil",
    "Ecuador":             "Ecuador",
    "Sweden":              "Suecia",
    "Tunisia":             "Túnez",
    "Spain":               "España",
    "Cape Verde":          "Cabo Verde",
    "Belgium":             "Bélgica",
    "Egypt":               "Egipto",
    "Saudi Arabia":        "Arabia Saudita",
    "Uruguay":             "Uruguay",
    "Iran":                "Irán",
    "New Zealand":         "Nueva Zelanda",
    "France":              "Francia",
    "Senegal":             "Senegal",
    "Iraq":                "Irak",
    "Norway":              "Noruega",
    "Argentina":           "Argentina",
    "Algeria":             "Argelia",
    "Austria":             "Austria",
    "Jordan":              "Jordania",
    "Portugal":            "Portugal",
    "DR Congo":            "Congo RD",
    "England":             "Inglaterra",
    "Croatia":             "Croacia",
    "Ghana":               "Ghana",
    "Panama":              "Panamá",
    "Colombia":            "Colombia",
    "Uzbekistan":          "Uzbekistán",
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
        home   = normalize(match["homeTeam"]["name"])
        away   = normalize(match["awayTeam"]["name"])
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

    # Guardar en resultados.json en la raiz del repo
    output_path = os.path.join(os.path.dirname(__file__), "..", "resultados.json")
    output_path = os.path.normpath(output_path)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "updated": datetime.now(timezone.utc).isoformat(),
            "matches": results
        }, f, ensure_ascii=False, indent=2)

    print(f"Guardado: {output_path} ({len(results)} partidos)")


if __name__ == "__main__":
    main()
