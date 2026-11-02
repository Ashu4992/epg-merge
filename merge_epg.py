import gzip, io, os, urllib.request
import xml.etree.ElementTree as ET

# Guides are merged in this order; the first copy of an overlapping channel wins.
URLS = [
    "https://avkb.short.gy/epg.xml.gz",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg2.xml.gz",
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=180).read()
    if data[:2] == b"\x1f\x8b":  # gzipped
        data = gzip.decompress(data)
    return ET.parse(io.BytesIO(data)).getroot()

out = ET.Element("tv")
seen_ch, seen_pg = set(), set()

for url in URLS:
    try:
        root = fetch(url)
    except Exception as e:
        print(f"WARNING: could not load {url}: {e}")
        continue
    for ch in root.findall("channel"):
        if ch.get("id") not in seen_ch:
            seen_ch.add(ch.get("id"))
            out.append(ch)
    for pg in root.findall("programme"):
        key = (pg.get("channel"), pg.get("start"))
        if key not in seen_pg:
            seen_pg.add(key)
            out.append(pg)
    print(f"Loaded {url}: {len(seen_ch)} channels, {len(seen_pg)} programmes so far")

if not seen_ch:
    raise SystemExit("No guide data loaded; not writing output.")

os.makedirs("site", exist_ok=True)
buf = io.BytesIO()
ET.ElementTree(out).write(buf, encoding="utf-8", xml_declaration=True)
with gzip.open("site/guide.xml.gz", "wb") as f:
    f.write(buf.getvalue())
print("Wrote site/guide.xml.gz")
