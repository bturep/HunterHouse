#!/usr/bin/env python3
"""
One-off: bring hunterhouse.wikibase.cloud into line with the Wikibase Cloud
Hosting Policy (effective 2026-08-27) before submitting it for review.

What it does (idempotent -- safe to re-run; skips anything already done):
  1. Removes P26 (sex or gender) from every Person item except those whose
     death is documented in the record (living-people rule).
  2. Softens the descriptions of the two current owners so no living person
     is tied to the private residence they own.
  3. Writes Project:Copyrights, Project:About, Project:Living people.
  4. Replaces the Main Page "Rights" section to point at those pages and to
     declare the wiki-text licence (CC BY-SA 4.0).
  5. Tries MediaWiki:Copyright (the site footer). Needs admin rights, so the
     bot may be refused; the text is printed for a manual paste if so.

Restore point taken first: data/snapshots/wikibase_full_20260930/.

Usage:  py -3 scripts/hosting_policy_2026.py [--dry-run]
"""

import re
import sys

from _wikibase import WikibaseSession

DRY = "--dry-run" in sys.argv
SUMMARY = "Wikibase Cloud hosting policy compliance (2026-08-27 policy)"

# Persons whose death is documented in the record keep P26; everyone else
# (living, or not known to be deceased) loses it.
KEEP_P26 = {
    "Q201",  # Richard Morrow Hunter (d. 2023)
    "Q224",  # Bruce Goff (1904-1982)
    "Q225",  # Erich Mendelsohn (1887-1953)
    "Q228",  # Hendrik Wijdeveld (1885-1987)
    "Q231",  # Euine Fay Jones (1921-2004)
    "Q232",  # Marcel Breuer (1902-1981)
}

DESCRIPTIONS = {
    "Q205": "patron of the Hunter House Stewardship Project",  # Floyd Marinescu
    "Q206": "patron of the Hunter House Stewardship Project",  # Olivia Jol
}

SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"

COPYRIGHTS = """This page sets out the licences that apply to this Wikibase instance (hunterhouse.wikibase.cloud).

== Structured data ==
All structured data on this instance (items, properties, labels, descriptions, aliases, statements, qualifiers and references) is released under the [https://creativecommons.org/publicdomain/zero/1.0/ Creative Commons CC0 1.0 Universal Public Domain Dedication]. It may be copied, modified, redistributed and reused for any purpose, including commercially, without asking permission.

== Text ==
Text in all other namespaces, including the [[Main Page]] and the pages of this project namespace, is available under the [https://creativecommons.org/licenses/by-sa/4.0/ Creative Commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0)]. Contributors release their text under this licence.

== Media ==
This instance hosts no uploaded files. The digitised drawings, photographs and documents that the catalogue describes are served from the Hunter House Foundation's own storage, not from this wiki, and carry their own terms:
* Holdings of the Hunter House Foundation and the family collections, digitised with rights granted by Frances Hunter: [https://creativecommons.org/licenses/by-nc-nd/4.0/ CC BY-NC-ND 4.0].
* Material held by the [https://asc.ucalgary.ca/ Canadian Architectural Archives, University of Calgary]: remains under their stewardship; contact them about reuse.
These terms apply only to the media files themselves. The structured data that describes them, including the links to them, is CC0 as above.

== Private correspondence ==
Private correspondence is not held in this Wikibase. See [[Project:Living people]].

== Contact ==
Questions about rights: [mailto:contact@hunterhouse.org contact@hunterhouse.org].
"""

LIVING = """This instance describes people connected to Richard Hunter's practice and to the archive. Some of them are living. These rules govern how living people are described here.

== What is recorded ==
For a living person, this Wikibase records only:
* their name;
* a short description of their role in relation to the archive or to Hunter's work (for example: collaborator, correspondent, photographer, collection holder);
* their occupation, where it is public and relevant to that role;
* their authorship or custody of archive items (as creator, photographer or collection holder).

== What is not recorded ==
For living people, this Wikibase does not record:
* dates or places of birth;
* sex or gender;
* home addresses, contact details, or any link between a named living person and a private residence they currently own or occupy;
* family, health, religious, political or financial information.

== Sources ==
Statements about living people are drawn from the archive materials themselves, from published sources, or from the person's own confirmation.

== Private papers ==
Correspondence and other private papers involving living people are not held in this Wikibase. Where the Hunter House Foundation holds such material, access to it is managed outside this instance.

== Corrections and removal ==
Any living person described here may ask for statements about them to be corrected or removed by writing to [mailto:contact@hunterhouse.org contact@hunterhouse.org]. Requests are acted on promptly. Where a person is the creator of an archive item, the attribution may be kept, reduced to their name alone, so that the archival record stays accurate.

== Who applies these rules ==
Editing is restricted: account creation is closed and anonymous editing is disabled. All edits are made by the instance manager or by a maintenance account (MyBot) acting under the manager's direction, and these rules are applied at the point of entry.
"""

ABOUT = """'''Hunter House Archive''' is an open, structured catalogue of the architectural records of the Hunter Residence (203 Goward Road, Saanich, British Columbia) and the wider work of the architect [[Item:Q201|Richard Morrow Hunter]] (1930-2023).

== Purpose ==
The instance describes drawings, photographs, surveys, permits and related records held across several collections (an institutional archive at the University of Calgary and a number of family and personal collections), so that a fifty-year drawing record of a single house can be searched, cited and reused as open data. See the [[Main Page]] for the arrangement, the collections and the data model.

== Who it is for ==
Architectural historians and researchers, heritage and planning bodies, students, and the public. The catalogue is read directly by the public site [https://hunterhouse.org/ hunterhouse.org], is queryable at the [https://hunterhouse.wikibase.cloud/query SPARQL endpoint], and its items are linked from Wikidata.

== Who runs it ==
The instance is maintained by the [[Item:Q187|Hunter House Foundation]]. The instance manager is Brandon Poole ([mailto:contact@hunterhouse.org contact@hunterhouse.org]). Editing is restricted to accounts created by the manager.

== Policies ==
* [[Project:Copyrights]]: structured data CC0; wiki text CC BY-SA 4.0; media hosted elsewhere under its own terms.
* [[Project:Living people]]: what is and is not recorded about living people, and how to request corrections or removal.
"""

RIGHTS = """= Rights =

Structured data: [https://creativecommons.org/publicdomain/zero/1.0/ CC0]. Wiki text: [https://creativecommons.org/licenses/by-sa/4.0/ CC BY-SA 4.0]. This wiki hosts no media files: the digitised drawings, documents and photographs it describes are served by the Foundation under their own terms ([https://creativecommons.org/licenses/by-nc-nd/4.0/ CC BY-NC-ND 4.0] for Foundation and family holdings, rights granted by Frances Hunter), and material held by the [https://asc.ucalgary.ca/ Canadian Architectural Archives, University of Calgary] remains under their stewardship. Full statement: [[Project:Copyrights]]. People: [[Project:Living people]]. About this instance: [[Project:About]].

"""

FOOTER = ("Structured data is available under [https://creativecommons.org/publicdomain/zero/1.0/ CC0]; "
          "text is available under [https://creativecommons.org/licenses/by-sa/4.0/ CC BY-SA 4.0] "
          "unless otherwise noted. See [[Project:Copyrights]].")


def check(res, what):
    if "error" in res:
        print(f"  ! {what}: {res['error'].get('code')}: {res['error'].get('info')}")
        return False
    print(f"  ok {what}")
    return True


def persons_with_p26(wb):
    q = ("PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/> "
         "PREFIX wd: <https://hunterhouse.wikibase.cloud/entity/> "
         "SELECT DISTINCT ?i WHERE { ?i wdt:P1 wd:Q1 ; wdt:P26 ?g . }")
    r = wb.session.get(SPARQL, params={"query": q, "format": "json"}).json()
    return sorted(b["i"]["value"].rsplit("/", 1)[1] for b in r["results"]["bindings"])


def page_text(wb, title):
    r = wb.get("query", titles=title, prop="revisions", rvprop="content",
               rvslots="main", formatversion=2)
    p = r["query"]["pages"][0]
    if p.get("missing"):
        return None
    return p["revisions"][0]["slots"]["main"]["content"]


def put(wb, title, text):
    if page_text(wb, title) == text:
        print(f"  = {title} unchanged")
        return True
    if DRY:
        print(f"  (dry) would write {title} ({len(text)} chars)")
        return True
    return check(wb.post("edit", title=title, text=text, summary=SUMMARY), f"edit {title}")


def main():
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (hosting_policy_2026)")

    print("1. P26 on persons")
    for qid in persons_with_p26(wb):
        if qid in KEEP_P26:
            print(f"  keep {qid}")
            continue
        ent = wb.get("wbgetentities", ids=qid, props="claims")["entities"][qid]
        guids = [c["id"] for c in ent["claims"].get("P26", [])]
        if not guids:
            continue
        if DRY:
            print(f"  (dry) would remove P26 from {qid}")
            continue
        check(wb.post("wbremoveclaims", claim="|".join(guids), summary=SUMMARY),
              f"remove P26 from {qid}")

    print("2. owner descriptions")
    for qid, desc in DESCRIPTIONS.items():
        cur = wb.get("wbgetentities", ids=qid, props="descriptions")["entities"][qid]
        if cur.get("descriptions", {}).get("en", {}).get("value") == desc:
            print(f"  = {qid} unchanged")
        elif DRY:
            print(f"  (dry) would set {qid} description")
        else:
            check(wb.post("wbsetdescription", id=qid, language="en", value=desc,
                          summary=SUMMARY), f"describe {qid}")

    print("3. project pages")
    put(wb, "Project:Copyrights", COPYRIGHTS)
    put(wb, "Project:Living people", LIVING)
    put(wb, "Project:About", ABOUT)

    print("4. Main Page rights section")
    main_text = page_text(wb, "Main Page")
    new_main, n = re.subn(r"= Rights =\n.*?(?== Endpoints =)", lambda m: RIGHTS,
                          main_text, count=1, flags=re.S)
    if n != 1:
        print("  ! Rights section not found; Main Page left alone")
    else:
        put(wb, "Main Page", new_main)

    print("5. footer")
    if not put(wb, "MediaWiki:Copyright", FOOTER):
        print("  -> paste this into MediaWiki:Copyright by hand (needs admin):")
        print("     " + FOOTER)


if __name__ == "__main__":
    main()
