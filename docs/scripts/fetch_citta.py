"""Scarica da Wikidata città antiche e centri abbandonati d'Italia e scrive un GeoJSON (kind=citta).
Uso: python scripts/fetch_citta.py [--out data/citta_wikidata.geojson]
Q-id usati: Q15661340 (città antica), Q74047 (città fantasma), Q38 (Italia): verificali su wikidata.org."""
import argparse, json, re, urllib.parse, urllib.request
from fetch_wikidata import period, parse_year

QUERY = """
SELECT ?item ?itemLabel ?coord ?end WHERE {
  VALUES ?cls { wd:Q15661340 wd:Q74047 }
  ?item wdt:P31/wdt:P279* ?cls ; wdt:P625 ?coord ; wdt:P17 wd:Q38 .
  OPTIONAL { ?item wdt:P576 ?end . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
} LIMIT 3000
"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="data/citta_wikidata.geojson")
    out = ap.parse_args().out
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": QUERY, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "battlemap/0.1 (progetto personale)"})
    rows = json.load(urllib.request.urlopen(req, timeout=90))["results"]["bindings"]
    feats, seen = [], set()
    for r in rows:
        qid = r["item"]["value"].rsplit("/", 1)[-1]
        m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", r["coord"]["value"])
        if qid in seen or not m or re.fullmatch(r"Q\d+", r["itemLabel"]["value"]): continue
        seen.add(qid)
        feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(m.group(1)), float(m.group(2))]},
            "properties": {"kind": "citta", "name": r["itemLabel"]["value"], "wikidata": qid,
                           "period": period(parse_year(r.get("end", {}).get("value")))}})
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, "w"), ensure_ascii=False)
    print(f"{len(feats)} città salvate in {out}")

if __name__ == "__main__":
    main()
