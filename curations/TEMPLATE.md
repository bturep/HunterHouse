# {Selection title}

> Curated by **{Your name}** · {Your role} · {Your affiliation} · [{Link label}]({https://your-website})

## About this selection

The macro framing of this selection. Why these items, what binds them, the through-line you want a viewer to notice. One or two short paragraphs are plenty.

Paragraph breaks are blank lines, like this.

## About the curator

A short bio in your own words. The name you typed in the byline above will be highlighted automatically wherever it appears in this section.

Multi-paragraph is fine.

## Selection

Each item gets a third-level heading with its archive ID (`HH-HHC-NNNN`, `HH-CAA-NNNN`, `HH-EGC-NNNN`, etc.). The order you list them in IS the order a visitor experiences them in.

The text after each heading, until the next heading, is your note for that item. Multi-paragraph notes are fine — use blank lines between paragraphs.

### HH-HHC-0001

Why this item is here, what it does in the sequence. Write in prose, not in lists.

### HH-CAA-0028

A second item's note. As long or short as you'd like.

### HH-HHC-0115

A third item.

---

# Notes for the curator

- **Filename**: save this as `your-slug.md` (lowercase, hyphens, no spaces) in the `curations/` folder.
- **Section headings are part of the format.** Keep `## About this selection`, `## About the curator`, and `## Selection` exactly as written; the parser keys off them.
- **The byline line** (the `> Curated by …` line) is parsed for your name, role, affiliation, and link. Keep the `·` separators between fields. The `**bold**` around your name is what enables the name-highlight in the bio.
- **Item headings** must contain the archive ID (`HH-HHC-NNNN` style). Any extra text after the ID is ignored.
- **Markdown formatting in note bodies**: paragraph breaks (blank lines) are honoured. Italics, bold, and inline links work. Don't use headings or lists inside a note body — they confuse the parser.
- **Anything the parser doesn't recognise is silently skipped.** Better than misimporting.
- **Once you save**, hand the file back to the site maintainer; they drop it in `curations/` and add a one-line entry to `curations/index.json`.

This whole "Notes for the curator" section (anything after the `---` rule and below) is ignored by the parser — feel free to leave these instructions in the file as a reference, or strip them out, whichever you prefer.
