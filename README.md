# German Law Obligations

A learning project that collects all German federal laws and regulations from
[gesetze-im-internet.de](https://www.gesetze-im-internet.de) and prepares them
for measuring how much binding language (obligations and prohibitions) they contain.

## Status

1. Download the index of all federal laws and regulations.
2. Download every law as XML with a polite crawler (1 second pause, caching, error log).
3. Parse each law into one row per provision.
4. Next: count binding language per law.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python crawl.py --limit 20        # test run: index plus the first 20 laws
python crawl.py                   # all laws, about two hours
python crawl.py --refresh-index   # fetch a fresh index first
```

Already downloaded laws are skipped. For a completely new snapshot, delete
`data/laws/` before running the crawler. The index date is stored in
`data/index_date.txt`.

## Data source

Consolidated federal law from gesetze-im-internet.de, provided by the German
Federal Ministry of Justice. Statutes are official works and not protected by
copyright (§ 5 UrhG). Snapshot: 16 November 2026, 6,144 laws and regulations
in the index, all downloaded successfully.

## Data decisions

**Unit of observation:** one provision per row (a §, an article or an annex).

**Excluded entries**

| What | Why |
|---|---|
| Law headers and section headings | contain no legal text |
| Tables of contents (Inhaltsübersicht, Inhaltsverzeichnis, Übersicht, Gliederung) | repeat headings only |
| Enacting and closing formulas, preambles (Eingangsformel, Schlussformel, Schlußformel, Präambel) | standard wording, not rules |
| Repealed provisions, marked "(weggefallen)" | empty text |
| Footnotes | editorial notes, not legal text |
| 179 laws without numbered provisions | 168 contain no text at all; 11 contain unnumbered text, mostly amending acts and notices of entry into force, in total 32,106 characters or 0.021% of the corpus |

**Groups of provisions**

| Group | Types | Provisions | Use |
|---|---|---|---|
| Rule | §, Art, Artikel | 93,718 | main analysis |
| Annex | Anlage, Anhang, Muster | 4,891 | analysed separately |
| Unnumbered | (XXXX) | 1,423 | excluded from main analysis; mostly notices repeated every year |
| Other | all remaining types | [OTHER] | spot-checked |

**Final corpus:** [TOTAL] provisions from 5,965 laws and regulations.

**Spelling:** Many older provisions still use pre-1996 spelling. In the GmbHG,
"muß" appears 13 times and "muss" 12 times. Any measure of binding language
must therefore count both spellings.
