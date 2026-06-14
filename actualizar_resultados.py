#!/usr/bin/env python3
"""
Consulta football-data.org por ID numerico de partido y genera resultados.json.
Ejecutado por GitHub Actions cada hora.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN")
if not API_TOKEN:
    print("ERROR: falta FOOTBALL_API_TOKEN")
    sys.exit(1)

# Mapa definitivo: ID numerico -> clave exacta del HTML
# Construido desde el log de diagnostico del 14 jun 2026
ID_TO_KEY = {
    537327: "México vs Sudáfrica",
    537328: "Corea del Sur vs Rep. Checa",
    537333: "Canadá vs Bosnia y Herz.",
    537345: "EE.UU. vs Paraguay",
    537334: "Qatar vs Suiza",
    537339: "Brasil vs Marruecos",
    537340: "Haití vs Escocia",
    537346: "Australia vs Turquía",
    537351: "Alemania vs Curazao",
    537357: "Países Bajos vs Japón",
    537352: "Costa de Marfil vs Ecuador",
    537358: "Suecia vs Túnez",
    537369: "España vs Cabo Verde",
    537363: "Bélgica vs Egipto",
    537370: "Arabia Saudita vs Uruguay",
    537364: "Irán vs Nueva Zelanda",
    537391: "Francia vs Senegal",
    537392: "Irak vs Noruega",
    537397: "Argentina vs Argelia",
    537398: "Austria vs Jordania",
    537403: "Portugal vs Congo RD",
    537409: "Inglaterra vs Croacia",
    537410: "Ghana vs Panamá",
    537404: "Colombia vs Uzbekistán",
    537329: "Rep. Checa vs Sudáfrica",
    537335: "Suiza vs Bosnia y Herz.",
    537336: "Canadá vs Qatar",
    537330: "México vs Corea del Sur",
    537348: "EE.UU. vs Australia",
    537342: "Escocia vs Marruecos",
    537341: "Brasil vs Haití",
    537347: "Turquía vs Paraguay",
    537359: "Países Bajos vs Suecia",
    537353: "Alemania vs Costa de Marfil",
    537354: "Ecuador vs Curazao",
    537360: "Túnez vs Japón",
    537371: "España vs Arabia Saudita",
    537365: "Bélgica vs Irán",
    537372: "Uruguay vs Cabo Verde",
    537366: "Nueva Zelanda vs Egipto",
    537399: "Argentina vs Austria",
    537393: "Francia vs Irak",
    537394: "Noruega vs Senegal",
    537400: "Jordania vs Argelia",
    537405: "Portugal vs Uzbekistán",
    537411: "Inglaterra vs Ghana",
    537412: "Panamá vs Croacia",
    537406: "Colombia vs Congo RD",
    537337: "Suiza vs Canadá",
    537338: "Bosnia y Herz. vs Qatar",
    537344: "Marruecos vs Haití",
    537343: "Escocia vs Brasil",
    537331: "Rep. Checa vs México",
    537332: "Sudáfrica vs Corea del Sur",
    537355: "Ecuador vs Alemania",
    537356: "Curazao vs Costa de Marfil",
    537361: "Túnez vs Países Bajos",
    537362: "Japón vs Suecia",
    537349: "Turquía vs EE.UU.",
    537350: "Paraguay vs Australia",
    537395: "Noruega vs Francia",
    537396: "Senegal vs Irak",
    537373: "Uruguay vs España",
    537374: "Cabo Verde vs Arabia Saudita",
    537367: "Nueva Zelanda vs Bélgica",
    537368: "Egipto vs Irán",
    537413: "Panamá vs Inglaterra",
    537414: "Croacia vs Ghana",
    537407: "Colombia vs Portugal",
    537408: "Congo RD vs Uzbekistán",
    537401: "Jordania vs Argentina",
    537402: "Argelia vs Austria",
    # Eliminatorias: IDs conocidos, claves se asignan cuando se definan equipos
    # Por ahora se omiten; se actualizaran en una segunda iteracion
}

def fetch_matches():
    url = "https://api.football-data.org/v4/competitions/WC/matches"
    req = urllib.request.Request(url, headers={"X-Auth-Token": API_TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"Error de red: {e}")
        sys.exit(1)

def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Consultando API...")
    data = fetch_matches()
    results = {}

    for match in data.get("matches", []):
        mid    = match.get("id")
        key    = ID_TO_KEY.get(mid)
        if not key:
            continue  # partido de eliminatoria sin clave asignada, se omite

        status = match.get("status")
        score  = match.get("score", {})
        full   = score.get("fullTime", {})
        hg     = full.get("home")
        ag     = full.get("away")

        results[key] = {
            "status":     status,
            "home_goals": hg,
            "away_goals": ag,
        }

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "matches": results,
    }

    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    terminados = sum(1 for v in results.values() if v["status"] == "FINISHED")
    print(f"Guardado resultados.json: {len(results)} partidos, {terminados} finalizados.")

if __name__ == "__main__":
    main()
