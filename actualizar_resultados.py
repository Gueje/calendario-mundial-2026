#!/usr/bin/env python3
"""
Script de diagnostico temporal: imprime ID y equipos de partidos
de la Ronda de 32 (knockout) del Mundial 2026.
"""

import json
import os
import sys
import urllib.request
import urllib.error

API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN")
if not API_TOKEN:
    print("ERROR: falta FOOTBALL_API_TOKEN")
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

print("Partidos NO de fase de grupos (Ronda de 32 y siguientes):")
print()
print("ID       | STAGE         | LOCAL                        | VISITANTE                    | STATUS")
print("-" * 110)
for m in data.get("matches", []):
    stage = m.get("stage", "")
    if stage == "GROUP_STAGE":
        continue
    mid    = m["id"]
    home   = m["homeTeam"]["name"] or "TBD"
    away   = m["awayTeam"]["name"] or "TBD"
    status = m.get("status", "")
    print(f"{mid:<8} | {stage:<13} | {home:<28} | {away:<28} | {status}")
