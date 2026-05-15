# Wikidata draft items — Hunter House Foundation

These are prepared for submission to wikidata.org. Review before submitting.
Submit via https://www.wikidata.org/wiki/Special:NewItem or QuickStatements.

Do NOT submit until reviewed. Once live on Wikidata, the Q-numbers become
permanent identifiers — update P139 on the corresponding items in our Wikibase.

---

## 1. Richard Hunter (person)

**Wikidata QuickStatements format:**

```
CREATE
LAST|Len|"Richard Hunter"
LAST|Den|"Canadian architect; designer of the Hunter Residence, Victoria, British Columbia"
LAST|P31|Q5
LAST|P21|Q6581097
LAST|P106|Q42973
LAST|P19|Q40278
LAST|P570|+2023-01-14T00:00:00Z/11
LAST|P27|Q16
LAST|P69|Q1075124
LAST|P973|"https://searcharchives.ucalgary.ca/richard-hunter-accession"
```

**Property notes:**
- P31 Q5 = instance of: human
- P21 Q6581097 = sex or gender: male
- P106 Q42973 = occupation: architect
- P19 Q40278 = place of birth: Phoenix, Arizona
- P570 = date of death: 14 January 2023 (day precision /11)
- P27 Q16 = country of citizenship: Canada
- P69 Q1075124 = educated at: University of Oklahoma
- P973 = described at URL: the CAA finding aid

**Once the Wikidata item is created:**
- Note the Q-number
- Add P139 to Q201 in our Wikibase: `Q201|P139|"<wikidata Q-number>"`

---

## 2. Canadian Architectural Archives (institution)

```
CREATE
LAST|Len|"Canadian Architectural Archives"
LAST|Den|"architectural archives held at the University of Calgary"
LAST|P31|Q7972
LAST|P131|Q36091
LAST|P17|Q16
LAST|P749|Q1472854
LAST|P856|"https://library.ucalgary.ca/caa"
LAST|P973|"https://searcharchives.ucalgary.ca/canadian-architectural-archives"
```

**Property notes:**
- P31 Q7972 = instance of: archive
- P131 Q36091 = located in: Calgary
- P17 Q16 = country: Canada
- P749 Q1472854 = parent organisation: University of Calgary
- P856 = official website
- P973 = described at URL

**Once created:**
- Note the Q-number
- Update P94 (held by) label mapping in our Wikibase if needed
- The CAA Q-number can be added to Q116 (Canadian Architectural Archives item in our Wikibase) via P139

---

## 3. Richard Hunter fonds (archival fonds)

Create this after items 1 and 2 are live, so you can reference their Q-numbers.

```
CREATE
LAST|Len|"Richard Hunter fonds"
LAST|Den|"archival fonds at the Canadian Architectural Archives, University of Calgary; F0076"
LAST|P31|Q11351825
LAST|P485|<CAA Q-number>
LAST|P170|<Richard Hunter Q-number>
LAST|P973|"https://searcharchives.ucalgary.ca/richard-hunter-accession"
```

**Property notes:**
- P31 Q11351825 = instance of: archival fonds
- P485 = archives at: Canadian Architectural Archives (use Q from item 2)
- P170 = creator: Richard Hunter (use Q from item 1)
- P973 = described at URL: the finding aid root

---

## Property mapping: our Wikibase → Wikidata

| Our PID | Our label | Wikidata PID | Wikidata label |
|---|---|---|---|
| P1 | instance of | P31 | instance of |
| P2 | HH archive ID | P217 | inventory number |
| P62 | part of | P361 | part of |
| P79 | source collection | P195 | collection |
| P80 | creator | P170 | creator |
| P82 | date created | P571 | inception |
| P86 | set position | P1545 | series ordinal |
| P87 | area | P180 | depicts |
| P88 | drawing type | P136 | genre |
| P91 | medium | P186 | material used |
| P92 | built status | — | (no direct equivalent) |
| P93 | rights | P6216 | copyright status |
| P94 | held by | P485 | archives at |
| P95 | master image URL | P18 | image |
| P96 | preview image URL | P18 | image |
| P97 | legacy identifier | P217 | inventory number |
| P99 | archive link | P973 | described at URL |
| P100 | notes | — | (use Wikidata description) |
| P139 | Wikidata QID | — | (this IS the bridge) |

