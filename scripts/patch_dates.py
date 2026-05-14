#!/usr/bin/env python3
"""
Patch 18 undated archive items: add P82 date claim + update English description.
Run: python3 scripts/patch_dates.py
Loads bot credentials from ~/Documents/hh-wikibase-migration/.env automatically.
"""

import json
import os
import requests

API = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env

ITEMS = [
    # (QID, archive_id, year)
    # Dining Room Schemes I-VIII + Undated East Wing Design Dev → 2018
    ("Q393", "HH-A-75",  2018),
    ("Q409", "HH-A-76",  2018),
    ("Q420", "HH-A-77",  2018),
    ("Q417", "HH-A-78",  2018),
    ("Q412", "HH-A-79",  2018),
    ("Q406", "HH-A-80",  2018),
    ("Q402", "HH-A-81",  2018),
    ("Q410", "HH-A-82",  2018),
    ("Q419", "HH-A-83",  2018),
    ("Q416", "HH-A-84",  2018),
    ("Q411", "HH-A-85",  2018),
    ("Q401", "HH-A-86",  2018),
    ("Q418", "HH-A-87",  2018),
    ("Q407", "HH-A-88",  2018),
    ("Q408", "HH-A-89",  2018),
    ("Q414", "HH-A-90",  2018),
    # East Wing Construction Fragments → 2020
    ("Q462", "HH-A-143", 2020),
    ("Q470", "HH-A-144", 2020),
]


def login(s, username, password):
    r = s.get(API, params={"action": "query", "meta": "tokens",
                           "type": "login", "format": "json"})
    token = r.json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": username,
                          "lgpassword": password, "lgtoken": token,
                          "format": "json"})
    result = r.json()["login"]["result"]
    if result != "Success":
        raise SystemExit(f"Login failed: {result}")
    print(f"Logged in as {r.json()['login']['lgusername']}\n")


def csrf(s):
    r = s.get(API, params={"action": "query", "meta": "tokens", "format": "json"})
    return r.json()["query"]["tokens"]["csrftoken"]


def set_description(s, token, qid, text):
    r = s.post(API, data={
        "action": "wbsetdescription",
        "id": qid, "language": "en", "value": text,
        "token": token, "format": "json",
    })
    d = r.json()
    if "error" in d:
        return False, d["error"].get("info", d["error"])
    return True, d.get("description", {}).get("value", text)


def add_date(s, token, qid, year):
    value = json.dumps({
        "time": f"+{year}-00-00T00:00:00Z",
        "timezone": 0, "before": 0, "after": 0,
        "precision": 9,
        "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
    })
    r = s.post(API, data={
        "action": "wbcreateclaim",
        "entity": qid, "snaktype": "value",
        "property": "P82", "value": value,
        "token": token, "format": "json",
    })
    d = r.json()
    if "error" in d:
        return False, d["error"].get("info", d["error"])
    return True, d.get("claim", {}).get("id", "ok")


def main():
    env = load_env(ENV_FILE)
    bot_user = env.get("WIKIBASE_BOT_USER", "")
    bot_pass = env.get("WIKIBASE_BOT_PASSWORD", "")
    if not bot_user or not bot_pass:
        raise SystemExit(f"Missing WIKIBASE_BOT_USER or WIKIBASE_BOT_PASSWORD in {ENV_FILE}")
    print(f"Using bot: {bot_user}\n")

    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0"})

    login(s, bot_user, bot_pass)
    token = csrf(s)

    for qid, aid, year in ITEMS:
        desc = f"architectural drawing; HHC; {year}"
        ok_d, msg_d = set_description(s, token, qid, desc)
        ok_c, msg_c = add_date(s, token, qid, year)
        status = "OK" if (ok_d and ok_c) else "FAIL"
        print(f"[{status}] {aid} ({qid})  desc={'ok' if ok_d else msg_d}  P82={'ok' if ok_c else msg_c}")

    print("\nDone.")


if __name__ == "__main__":
    main()
