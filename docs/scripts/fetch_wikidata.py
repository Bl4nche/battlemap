"""Scarica da Wikidata le battaglie con coordinate (default: Italia) e scrive un GeoJSON.
Uso: python scripts/fetch_wikidata.py [--out data/battaglie_wikidata.geojson]
Wikidata è CC0. Serve connessione internet; nessuna dipendenza esterna."""
import argparse, json, re, urllib.parse, urllib.request

QUERY = """
SELECT ?item ?itemLabel ?coord ?date WHERE {
  ?item wdt:P31/wdt:P279* wd:Q178561 ;   # istanza di battaglia
        wdt:P625 ?coord ;                # coordinate
        wdt:P17 wd:Q38 .                 # paese: Italia (cambia il Q-id per altri paesi)
  OPTIONAL { ?item wdt:P585 ?date . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
}
LIMIT 2000
"""

def period(year):
    if year is None: return "altro"
    if year < 476: return "antica"
    if year < 1492: return "medievale"
    if year < 1789: return "moderna"
    if year < 1914: return "ottocento"
    if year <= 1918: return "wwi"
    if 1939 <= year <= 1945: return "wwii"
    return "altro"

def parse_year(s):
    m = re.match(r"^(-?)(\d{4,})", s or "")
    if not m: return None
    return -int(m.group(2)) if m.group(1) else int(m.group(2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/battaglie_wikidata.geojson")
    out = ap.parse_args().out
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": QUERY, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "battlemap/0.1 (progetto personale)"})
    rows = json.load(urllib.request.urlopen(req, timeout=90))["results"]["bindings"]
    feats, seen = [], set()
    for r in rows:
        qid = r["item"]["value"].rsplit("/", 1)[-1]
        m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", r["coord"]["value"])
        if qid in seen or not m: continue   # deduplica ed esclude coordinate non valide
        seen.add(qid)
        year = parse_year(r.get("date", {}).get("value"))
        feats.append({"type": "Feature",
            "properties": {"name": r["itemLabel"]["value"], "year": year, "period": period(year),
                           "reliability": "media", "wikidata": qid},
            "geometry": {"type": "Point", "coordinates": [float(m.group(1)), float(m.group(2))]}})
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, "w"), ensure_ascii=False)
    print(f"{len(feats)} battaglie salvate in {out}")

if __name__ == "__main__":
    main()
