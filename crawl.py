"""Download all German federal laws listed in the gesetze-im-internet.de index."""
import argparse
import io
import time
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from lxml import etree
from tqdm import tqdm

DATA = Path("data")
LAWS = DATA / "laws"
INDEX_URL = "https://www.gesetze-im-internet.de/gii-toc.xml"
HEADERS = {"User-Agent": "german-law-obligations (learning project; github.com/pfeifer99)"}
PAUSE = 1.0  # Sekunden Pause nach jedem Download


def fetch_index():
    """Lädt den Index aller Gesetze und speichert ihn als XML und CSV."""
    r = requests.get(INDEX_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    DATA.mkdir(exist_ok=True)
    (DATA / "gii-toc.xml").write_bytes(r.content)

    root = etree.fromstring(r.content)
    toc = pd.DataFrame([
        {"title": item.findtext("title"), "link": item.findtext("link")}
        for item in root.findall("item")
    ])
    toc["link"] = toc["link"].str.replace("http://", "https://", n=1)
    toc["slug"] = toc["link"].str.split("/").str[-2]

    if toc["slug"].duplicated().any():
        raise ValueError("Doppelte Kennungen im Index, bitte prüfen")

    today = date.today().isoformat()
    toc.to_csv(DATA / "toc.csv", index=False)
    (DATA / "index_date.txt").write_text(today)
    print(f"Index neu geladen: {len(toc)} Gesetze, Stand {today}")
    return toc


def load_index(refresh=False):
    """Nimmt den vorhandenen Index oder lädt ihn neu."""
    path = DATA / "toc.csv"
    if refresh or not path.exists():
        return fetch_index()
    toc = pd.read_csv(path)
    date_file = DATA / "index_date.txt"
    stand = date_file.read_text() if date_file.exists() else "unbekannt"
    print(f"Vorhandener Index: {len(toc)} Gesetze, Stand {stand}")
    return toc


def download_law(slug, link):
    """Lädt ein Gesetz und entpackt es. Gibt True zurück, wenn es neu geladen wurde."""
    law_dir = LAWS / slug
    if law_dir.exists() and any(law_dir.glob("*.xml")):
        return False  # schon vorhanden, nicht nochmal laden
    r = requests.get(link, headers=HEADERS, timeout=30)
    r.raise_for_status()
    law_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(law_dir)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="nur die ersten N Gesetze")
    parser.add_argument("--refresh-index", action="store_true", help="Index neu herunterladen")
    args = parser.parse_args()

    toc = load_index(refresh=args.refresh_index)
    if args.limit:
        toc = toc.head(args.limit)

    failures = []
    for row in tqdm(toc.itertuples(), total=len(toc)):
        try:
            if download_law(row.slug, row.link):
                time.sleep(PAUSE)
        except Exception as e:
            failures.append({"slug": row.slug, "link": row.link, "error": repr(e)})

    pd.DataFrame(failures, columns=["slug", "link", "error"]).to_csv(DATA / "failures.csv", index=False)
    print(f"Fertig. {len(failures)} Fehler, Details in data/failures.csv")


if __name__ == "__main__":
    main()
