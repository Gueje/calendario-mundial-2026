#!/usr/bin/env python3
"""
Script de diagnóstico: imprime ID y equipos de cada partido del Mundial 2026.
Solo para obtener los IDs numericos. Reemplazar por la version final despues.
"""

import json
import os
import sys
import urllib.request
import urllib.error

API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN")
if not API_TOKEN:
    print("ERROR: falta la variable de entorno FOOTBALL_API_TOKEN")
    sys.exit(1)

COMPETITION_URL = "https://api.football-data.org/v4/competitions/WC/matches"

req = urllib.request.Request(
    COMPETITION_URL,
    headers={"X-Auth-Token": API_TOKEN}
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.reason}")
    sys.exit(1)

print(f"Total partidos: {len(data.get('matches', []))}")
print()
print("ID       | LOCAL                        | VISITANTE")
print("-" * 65)
for m in data.get("matches", []):
    mid   = m["id"]
    home  = m["homeTeam"]["name"]
    away  = m["awayTeam"]["name"]
    stage = m.get("stage", "")
    print(f"{mid:<8} | {home:<28} | {away}  [{stage}]")
