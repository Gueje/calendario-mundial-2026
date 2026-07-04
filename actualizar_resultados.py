#!/usr/bin/env python3
"""
Diagnóstico: imprime ID, equipos y status de los partidos de LAST_16 (octavos).
Usar temporalmente en GitHub para obtener los IDs.
"""
import json, os, sys, urllib.request, urllib.error

API_TOKEN = os.environ.get("FOOTBALL_API_TOKEN")
if not API_TOKEN:
    print("ERROR: falta FOOTBALL_API_TOKEN")
    sys.exit(1)

req = urllib.request.Request(
    "https://api.football-data.org/v4/competitions/WC/matches",
    headers={"X-Auth-Token": API_TOKEN}
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.reason}"); sys.exit(1)

print("ID       | STAGE   | STATUS   | LOCAL                  | VISITANTE")
print("-" * 85)
for m in data.get("matches", []):
    if m.get("stage") not in ("LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL"):
        continue
    mid   = m["id"]
    stage = m.get("stage","")
    status= m.get("status","")
    home  = m["homeTeam"]["name"] or "TBD"
    away  = m["awayTeam"]["name"] or "TBD"
    print(f"{mid:<8} | {stage:<10} | {status:<8} | {home:<22} | {away}")
