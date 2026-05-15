# Wikidata items — Hunter House Foundation

Three items to create, in order. Create items 1 and 2 first, note their Q-numbers,
then fill in the placeholders in item 3 before submitting.

Submit via QuickStatements: https://www.wikidata.org/wiki/Special:QuickStatements
Or one at a time via: https://www.wikidata.org/wiki/Special:NewItem

---

## 1. Richard Hunter (person)

```
CREATE
LAST|Len|"Richard Morrow Hunter"
LAST|Den|"Canadian architect; designer of the Hunter Residence, Victoria, British Columbia (1923?–2023)"
LAST|P31|Q5
LAST|P21|Q6581097
LAST|P106|Q42973
LAST|P19|Q40278
LAST|P570|+2023-01-14T00:00:00Z/11
LAST|P27|Q16
LAST|P69|Q736674
LAST|P69|Q1075124
LAST|P737|Q553804
LAST|P737|Q76730
LAST|P737|Q315963
LAST|P973|"https://searcharchives.ucalgary.ca/richard-hunter"
LAST|P973|"https://searcharchives.ucalgary.ca/richard-hunter-accession"
```

**Property key:**
| Statement | Meaning |
|---|---|
| P31 Q5 | instance of: human |
| P21 Q6581097 | sex or gender: male |
| P106 Q42973 | occupation: architect |
| P19 Q40278 | place of birth: Phoenix, Arizona |
| P570 +2023-01-14/11 | date of death: 14 January 2023 |
| P27 Q16 | country of citizenship: Canada |
| P69 Q736674 | educated at: University of Colorado Boulder |
| P69 Q1075124 | educated at: University of Oklahoma |
| P737 Q553804 | influenced by: Bruce Goff |
| P737 Q76730 | influenced by: Erich Mendelsohn |
| P737 Q315963 | influenced by: Gary Snyder |
| P973 | described at URL: AtoM authority record (richard-hunter) |
| P973 | described at URL: fonds finding aid (richard-hunter-accession) |

**After creating:** note the Q-number → add to Q201 in our Wikibase: `P139 = "Q??????"`

---

## 2. Canadian Architectural Archives (institution)

```
CREATE
LAST|Len|"Canadian Architectural Archives"
LAST|Den|"architectural archive held at the University of Calgary, Alberta"
LAST|P31|Q7972
LAST|P131|Q36091
LAST|P17|Q16
LAST|P749|Q1067471
LAST|P856|"https://library.ucalgary.ca/caa"
LAST|P973|"https://searcharchives.ucalgary.ca/canadian-architectural-archives"
```

**Property key:**
| Statement | Meaning |
|---|---|
| P31 Q7972 | instance of: archive |
| P131 Q36091 | located in: Calgary |
| P17 Q16 | country: Canada |
| P749 Q1067471 | parent organisation: University of Calgary |
| P856 | official website |
| P973 | described at URL: AtoM finding aid root |

**After creating:** note the Q-number → add to Q116 in our Wikibase: `P139 = "Q??????"`

---

## 3. Richard Hunter fonds (archival fonds)

Create after items 1 and 2 are live. Replace the two placeholders with actual Q-numbers.

```
CREATE
LAST|Len|"Richard Hunter fonds"
LAST|Den|"archival fonds at the Canadian Architectural Archives, University of Calgary; F0076; donated 2019 and 2021"
LAST|P31|Q11351825
LAST|P485|Q??????-CAA
LAST|P170|Q??????-Hunter
LAST|P571|+2019-00-00T00:00:00Z/9
LAST|P973|"https://searcharchives.ucalgary.ca/richard-hunter-accession"
```

**Property key:**
| Statement | Meaning |
|---|---|
| P31 Q11351825 | instance of: archival fonds |
| P485 | archives at: Canadian Architectural Archives (Q from item 2) |
| P170 | creator: Richard Hunter (Q from item 1) |
| P571 2019/9 | inception: 2019 (first donation year) |
| P973 | described at URL: finding aid |

---

## After all three items are created

Add Wikidata QIDs back to our Wikibase via QuickStatements
(at https://hunterhouse.wikibase.cloud/tools/quickstatements):

```
Q201|P139|"Q??????"    ← Richard Hunter person item
Q116|P139|"Q??????"    ← Canadian Architectural Archives item
```

---

## Property mapping: our Wikibase → Wikidata

| Our PID | Label | Wikidata PID | Wikidata label |
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
| P93 | rights | P6216 | copyright status |
| P94 | held by | P485 | archives at |
| P95 | master image URL | P18 | image |
| P96 | preview image URL | P18 | image |
| P97 | legacy identifier | P217 | inventory number |
| P99 | archive link | P973 | described at URL |
| P139 | Wikidata QID | — | (the bridge property) |
