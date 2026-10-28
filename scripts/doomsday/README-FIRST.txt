HUNTER HOUSE ARCHIVE -- OFFLINE COPY

This drive is a complete, self-contained copy of the Hunter House archive (hunterhouse.org): every master file and image, the catalogue, the website, the full history of the website's code, and the Frances Hunter correspondence. It needs no internet connection and no accounts. It is a backup and a legacy copy: if the website, the image storage or the catalogue service ever disappears, everything needed to read the archive, and to rebuild it, is here.

This copy is CONFIDENTIAL. It contains private correspondence (the Frances Hunter letters) that is not public on the website. Handle it accordingly.


TO OPEN THE ARCHIVE

Windows: double-click START.bat.

Mac: double-click start.command. (If the Mac refuses the first time, right-click it, choose Open, then Open again.)

A small window opens and your web browser shows the archive. Leave that window open while you browse; close it when you are done. The address will be http://127.0.0.1:8787/browse.html (127.0.0.1 means "this computer"; nothing leaves the machine).

The letters: http://127.0.0.1:8787/browse.html?open=letters

The only requirement is Python 3, which is already on most Macs and is a free install on Windows from https://www.python.org/downloads/ (tick "Add python.exe to PATH" during install). On Linux, open a terminal in this folder and type: sh start.command

IF THE ARCHIVE WON'T START: double-click CATALOGUE.html. It is a plain page that opens in any web browser with no program, no Python and no internet, listing every object with its details, a picture, and links to the image and master files on this drive. LETTERS.html does the same for the correspondence. These two pages are the simplest way in and the one most likely to keep working decades from now.


TO CHECK THE DRIVE IS INTACT

Double-click VERIFY.bat (Windows) or verify.command (Mac). It re-reads every file and compares it with the fingerprints recorded when the drive was built (fixity/manifest-latest.sha256). "OK" means nothing has changed or decayed. Run it once a year, and before relying on the drive.


WHAT IS ON THE DRIVE

r2/  -- The archive's files, an exact byte-for-byte copy of the image storage (Cloudflare R2 bucket "hunter-house-archive"), in the same folders. Masters (full-resolution TIFF/JPEG scans) are in each collection's masters/ folder; previews/, large/ and thumbs/ are the smaller web versions; pdf/ holds the multi-page documents. These are ordinary files and open in any image viewer without the website.

r2/catalogue/catalogue.csv  -- The catalogue as a spreadsheet: one row per object, readable in Excel, Numbers or any text editor. This is the quickest way into the archive without the website.

wikibase/  -- The full catalogue database (Wikibase), one file per object, person and term, as JSON. Enough to rebuild the online catalogue item by item.

site/  -- The website, exactly as published at the commit recorded in BUILD-INFO.json.

gated/  -- The Frances Hunter correspondence: the letters' transcriptions and metadata (letters-dataset.json) and the page images (bucket/).

repo/HunterHouse.bundle  -- The website's complete version history (a git bundle). To unpack it: git clone HunterHouse.bundle HunterHouse

fixity/  -- Fingerprints (SHA-256) of every file, the image storage's own listing at build time, and the check that the copy matched it.

CATALOGUE.html, LETTERS.html  -- The no-program fallback pages described above.

serve.py, verify.py  -- The two small programs the launchers run. Plain Python, readable, no installs.

BUILD-INFO.json  -- When this copy was made, and which version of the website it holds.


HOW IT WORKS (FOR WHOEVER MAINTAINS IT)

The website normally loads its images from archive.hunterhousefoundation.com, its catalogue from hunterhouse.wikibase.cloud, and the letters from a Cloudflare Worker. serve.py stands in for all three: it serves site/ and r2/ from this drive and rewrites those web addresses to local ones as pages are sent to the browser. The files on the drive are never modified. The online catalogue query is deliberately disabled, so the site falls back to the catalogue snapshot (r2/catalogue/catalogue.json). Editing is off; this copy is read-only. The 3D explorer under forms/ loads a library from the internet and will not work offline; everything else does.

The copy is built and refreshed by scripts/build_doomsday.py in the HunterHouse repository. Refresh it whenever a new version of the website is published or new masters are ingested.

KEEPING IT ALIVE

USB sticks are not archival: flash memory can fade when left unplugged for years. So: plug this in and run VERIFY once a year; keep at least one other copy (an identical copy is kept on the BACKUP_MAST hard drive under BACKUPS\HH-ARCHIVE-DOOMSDAY, which is itself mirrored to a second drive); and every five years or so, copy the whole folder onto fresh media and run VERIFY there. The files themselves (TIFF, JPEG, PDF, CSV, JSON, HTML, plain text) are among the most durable formats there are and need no special software.
