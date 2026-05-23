#!/usr/bin/env python3
"""
Patch 18 undated archive items: add P82 date claim + update English description.
Run: python3 scripts/patch_dates.py
Loads bot credentials from ~/Documents/hh-wikibase-migration/.env automatically.

Migrated to scripts/_wikibase.py 2026-05-22 (ARCHITECTURE.md §11.2 LOW
dedup pass) — env loading + login + CSRF + retry now live in the shared
helper. This script's actual logic (the ITEMS list + the two write
helpers) is unchanged.
"""

import json

from _wikibase import WikibaseSession

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


def set_description(wb, qid, text):
    d = wb.post("wbsetdescription", id=qid, language="en", value=text)
    if "error" in d:
        return False, d["error"].get("info", d["error"])
    return True, d.get("description", {}).get("value", text)


def add_date(wb, qid, year):
    value = json.dumps({
        "time": f"+{year}-00-00T00:00:00Z",
        "timezone": 0, "before": 0, "after": 0,
        "precision": 9,
        "calendarmodel": "http://www.wikidata.org/entity/Q1985727",
    })
    d = wb.post("wbcreateclaim",
                entity=qid, snaktype="value",
                property="P82", value=value)
    if "error" in d:
        return False, d["error"].get("info", d["error"])
    return True, d.get("claim", {}).get("id", "ok")


def main():
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (patch_dates)")
    print(f"Using bot: {wb.user}\n")

    for qid, aid, year in ITEMS:
        desc = f"architectural drawing; HHC; {year}"
        ok_d, msg_d = set_description(wb, qid, desc)
        ok_c, msg_c = add_date(wb, qid, year)
        status = "OK" if (ok_d and ok_c) else "FAIL"
        print(f"[{status}] {aid} ({qid})  desc={'ok' if ok_d else msg_d}  P82={'ok' if ok_c else msg_c}")

    print("\nDone.")


if __name__ == "__main__":
    main()
