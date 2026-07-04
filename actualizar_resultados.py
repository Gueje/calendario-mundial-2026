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
    537404: "Uzbekistán vs Colombia",
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
    # Ronda de 32 (knockout) — IDs confirmados via diagnostico el 28 jun 2026,
    # tras el cierre de la fase de grupos
    537417: "Sudáfrica vs Canadá",
    537423: "Brasil vs Japón",
    537415: "Alemania vs Paraguay",
    537418: "Países Bajos vs Marruecos",
    537424: "Costa de Marfil vs Noruega",
    537416: "Francia vs Suecia",
    537425: "México vs Ecuador",
    537426: "Inglaterra vs Congo RD",
    537422: "Bélgica vs Senegal",
    537421: "EE.UU. vs Bosnia y Herz.",
    537420: "España vs Austria",
    537419: "Portugal vs Croacia",
    537429: "Suiza vs Argelia",
    537428: "Australia vs Egipto",
    537427: "Argentina vs Cabo Verde",
    537430: "Colombia vs Ghana",
    # Octavos, Cuartos, Semis, 3er lugar y Final: la API ya asigna estos IDs
    # de antemano (537376-537382 Octavos, 537383-537386 Cuartos, 537387-537388
    # Semis, 537389 Tercer lugar, 537390 Final), pero los equipos siguen "TBD"
    # (To Be Determined) hasta que se jueguen las rondas anteriores. No se
    # pueden mapear a una clave fija porque esa clave depende del ganador de
    # otros partidos. Por eso bracket.json los resuelve dinamicamente via
    # actualizar_bracket(), sin necesidad de un ID_TO_KEY para ellos.
    # Octavos de final — IDs confirmados via diagnostico el 4 jul 2026
    537376: "Canadá vs Marruecos",       # M90
    537375: "Paraguay vs Francia",        # M89
    537377: "Brasil vs Noruega",          # M91
    537378: "México vs Inglaterra",       # M92
    537379: "Portugal vs España",         # M93
    537380: "EE.UU. vs Bélgica",          # M94
    537381: "Argentina vs Egipto",        # M95
    537382: "Suiza vs Colombia",          # M96
}

# IDs donde el orden local/visitante de la API es el INVERSO del orden
# usado en la clave del HTML (ej: API pone Uzbekistan de local, pero el
# HTML dice "Colombia vs Uzbekistán"). Para estos casos hay que voltear
# home_goals y away_goals al guardar el resultado.
IDS_INVERTIDOS = {
    # (vacio por ahora) - 537404 ya no necesita inversion: la clave del HTML
    # se corrigio a "Uzbekistán vs Colombia", que coincide con el orden de la API.
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

def fetch_standings():
    """Consulta la tabla de posiciones de los 12 grupos. Si falla, no afecta resultados.json."""
    url = "https://api.football-data.org/v4/competitions/WC/standings"
    req = urllib.request.Request(url, headers={"X-Auth-Token": API_TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"AVISO: no se pudo obtener standings ({e}). Se omite grupos.json esta corrida.")
        return None


# Mapa de nombres de equipo (API -> espanol del HTML), reutilizado para grupos
EQUIPO_ES = {v: v for v in []}  # se completa abajo dinamicamente desde ID_TO_KEY
for _key in ID_TO_KEY.values():
    for _team in _key.split(" vs "):
        EQUIPO_ES[_team] = _team
# Variantes en ingles que la API usa en standings (mismas que en partidos)
EQUIPO_ES.update({
    "Mexico": "México", "South Africa": "Sudáfrica", "Canada": "Canadá",
    "Switzerland": "Suiza", "Brazil": "Brasil", "Morocco": "Marruecos",
    "Haiti": "Haití", "Scotland": "Escocia", "Germany": "Alemania",
    "Netherlands": "Países Bajos", "Ivory Coast": "Costa de Marfil",
    "Sweden": "Suecia", "Belgium": "Bélgica", "Egypt": "Egipto",
    "Saudi Arabia": "Arabia Saudita", "Iran": "Irán", "France": "Francia",
    "Iraq": "Irak", "Algeria": "Argelia", "Jordan": "Jordania",
    "England": "Inglaterra", "Croatia": "Croacia", "Panama": "Panamá",
    "Spain": "España", "Norway": "Noruega", "Tunisia": "Túnez",
    "Japan": "Japón", "Turkey": "Turquía", "New Zealand": "Nueva Zelanda",
    "Uzbekistan": "Uzbekistán", "South Korea": "Corea del Sur",
    "Czechia": "Rep. Checa", "Congo DR": "Congo RD", "Curaçao": "Curazao",
    "Cape Verde Islands": "Cabo Verde", "Bosnia-Herzegovina": "Bosnia y Herz.",
    "United States": "EE.UU.",
})


def build_groups(data):
    """Convierte la respuesta de standings en un dict simple: {grupo: [equipos ordenados]}."""
    grupos = {}
    if not data:
        return grupos

    for standing in data.get("standings", []):
        group_name = standing.get("group")  # ej: "GROUP_A"
        if not group_name:
            continue
        letra = group_name.replace("GROUP_", "")
        tabla = standing.get("table", [])

        filas = []
        for row in tabla:
            nombre_api = row.get("team", {}).get("name", "")
            nombre_es  = EQUIPO_ES.get(nombre_api, nombre_api)
            filas.append({
                "equipo":   nombre_es,
                "pj":       row.get("playedGames"),
                "g":        row.get("won"),
                "e":        row.get("draw"),
                "p":        row.get("lost"),
                "gf":       row.get("goalsFor"),
                "gc":       row.get("goalsAgainst"),
                "dg":       row.get("goalDifference"),
                "pts":      row.get("points"),
            })
        grupos[letra] = filas

    return grupos


def determinar_ganador(home, away, info):
    """
    Determina el ganador de un partido de eliminatoria.
    info viene de 'results' (home_goals, away_goals, pen_home, pen_away, status).
    Retorna el nombre del equipo ganador, o None si el partido no ha terminado.
    """
    if not info or info.get("status") != "FINISHED":
        return None

    hg, ag = info.get("home_goals"), info.get("away_goals")
    if hg is None or ag is None:
        return None

    if hg > ag:
        return home
    if ag > hg:
        return away

    # Empate en tiempo reglamentario: decide por penales
    ph, pa = info.get("pen_home"), info.get("pen_away")
    if ph is not None and pa is not None:
        if ph > pa:
            return home
        if pa > ph:
            return away

    return None  # empate sin penales registrados todavia


def actualizar_bracket(results):
    """
    Lee bracket.json, propaga ganadores segun 'results' (de resultados.json)
    y guarda el bracket actualizado. Totalmente independiente: si falla,
    no afecta resultados.json ni grupos.json.
    """
    bracket_path = "bracket.json"
    try:
        with open(bracket_path, "r", encoding="utf-8") as f:
            bracket = json.load(f)
    except FileNotFoundError:
        print("AVISO: no existe bracket.json en el repo, se omite esta seccion.")
        return
    except Exception as e:
        print(f"AVISO: error leyendo bracket.json ({e}).")
        return

    matches = bracket.get("matches", {})

    # Procesar en orden de ronda para que los ganadores se propaguen en cascada
    orden_rondas = ["32", "16", "8", "4", "1"]
    for ronda in orden_rondas:
        for mid, m in matches.items():
            if m.get("ronda") != ronda:
                continue

            # Resolver home
            if m.get("home_fuente") == "ganador":
                origen = matches.get(m.get("home_de"), {})
                m["home"] = origen.get("ganador")
            # Resolver away
            if m.get("away_fuente") == "ganador":
                origen = matches.get(m.get("away_de"), {})
                m["away"] = origen.get("ganador")

            home, away = m.get("home"), m.get("away")
            if not home or not away:
                m["ganador"] = None
                m["status"] = "PENDIENTE"
                continue

            key = f"{home} vs {away}"
            info = results.get(key)
            if not info:
                # Probar el orden inverso por si la clave esta volteada
                key_inv = f"{away} vs {home}"
                info = results.get(key_inv)

            if info:
                m["status"]      = info.get("status")
                m["home_goals"]  = info.get("home_goals")
                m["away_goals"]  = info.get("away_goals")
                m["pen_home"]    = info.get("pen_home")
                m["pen_away"]    = info.get("pen_away")
                m["ganador"]     = determinar_ganador(home, away, info)
            else:
                m["status"]  = "SCHEDULED"
                m["ganador"] = None

    bracket_output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "matches": matches,
    }
    with open(bracket_path, "w", encoding="utf-8") as f:
        json.dump(bracket_output, f, ensure_ascii=False, indent=2)

    resueltos = sum(1 for m in matches.values() if m.get("ganador"))
    print(f"Guardado bracket.json: {resueltos}/{len(matches)} partidos con ganador determinado.")


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

        # Penales (decisivos en eliminatorias si hay empate tras tiempo extra)
        pen    = score.get("penalties", {}) or {}
        pen_h  = pen.get("home")
        pen_a  = pen.get("away")

        # football-data.org incluye los goles de penales dentro de fullTime.
        # Cuando hay tanda de penales, restamos para obtener el marcador real
        # del partido (90min + tiempo extra, sin contar los penales).
        if pen_h is not None and pen_a is not None and hg is not None and ag is not None:
            hg = hg - pen_h
            ag = ag - pen_a

        # Si el orden de la API es inverso al del HTML, voltear los goles y penales
        if mid in IDS_INVERTIDOS:
            hg, ag = ag, hg
            pen_h, pen_a = pen_a, pen_h

        results[key] = {
            "status":      status,
            "home_goals":  hg,
            "away_goals":  ag,
            "pen_home":    pen_h,
            "pen_away":    pen_a,
        }

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "matches": results,
    }

    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    terminados = sum(1 for v in results.values() if v["status"] == "FINISHED")
    print(f"Guardado resultados.json: {len(results)} partidos, {terminados} finalizados.")

    # --- Bracket: propaga ganadores. Independiente, si falla no afecta lo anterior. ---
    try:
        actualizar_bracket(results)
    except Exception as e:
        print(f"AVISO: error actualizando bracket.json ({e}). No afecta resultados.json.")

    # --- Grupos: independiente de resultados.json. Si falla, no interrumpe nada arriba. ---
    try:
        standings_data = fetch_standings()
        grupos = build_groups(standings_data)
        if grupos:
            grupos_output = {
                "updated": datetime.now(timezone.utc).isoformat(),
                "groups": grupos,
            }
            with open("grupos.json", "w", encoding="utf-8") as f:
                json.dump(grupos_output, f, ensure_ascii=False, indent=2)
            print(f"Guardado grupos.json: {len(grupos)} grupos.")
        else:
            print("AVISO: grupos.json no actualizado (sin datos de standings).")
    except Exception as e:
        print(f"AVISO: error generando grupos.json ({e}). No afecta resultados.json.")

if __name__ == "__main__":
    main()
