"""Scarica da Wikidata le battaglie con coordinate (default: Italia) e scrive un GeoJSON.
Per ogni battaglia: nome, anno (o anni di inizio e fine), guerra o campagna di cui fa parte,
voce di Wikipedia (italiana, altrimenti inglese).
Uso: python scripts/fetch_wikidata.py [--out data/battaglie_wikidata.geojson]
Wikidata è CC0. Serve connessione internet; nessuna dipendenza esterna."""
import argparse, json, re, urllib.parse, urllib.request

# Una riga per battaglia: i valori multipli (più date, più guerre) sono aggregati.
QUERY = """
SELECT ?item (SAMPLE(?coord) AS ?c) (SAMPLE(?labIt) AS ?li) (SAMPLE(?labEn) AS ?le)
       (MIN(?date) AS ?d) (MIN(?start) AS ?s) (MAX(?end) AS ?e)
       (GROUP_CONCAT(DISTINCT ?warName; separator="|") AS ?wars)
       (SAMPLE(?wpIt) AS ?wi) (SAMPLE(?wpEn) AS ?we)
WHERE {
  ?item wdt:P31/wdt:P279* wd:Q178561 ;   # istanza di battaglia
        wdt:P625 ?coord ;                # coordinate
        wdt:P17 wd:Q38 .                 # paese: Italia (cambia il Q-id per altri paesi)
  OPTIONAL { ?item rdfs:label ?labIt FILTER(LANG(?labIt) = "it") }
  OPTIONAL { ?item rdfs:label ?labEn FILTER(LANG(?labEn) = "en") }
  OPTIONAL { ?item wdt:P585 ?date . }    # data puntuale
  OPTIONAL { ?item wdt:P580 ?start . }   # inizio
  OPTIONAL { ?item wdt:P582 ?end . }     # fine
  OPTIONAL { ?item wdt:P361 ?war .       # parte di (guerra, campagna)
             OPTIONAL { ?war rdfs:label ?warIt FILTER(LANG(?warIt) = "it") }
             OPTIONAL { ?war rdfs:label ?warEn FILTER(LANG(?warEn) = "en") }
             BIND(COALESCE(?warIt, ?warEn) AS ?warName) }
  OPTIONAL { ?wpIt schema:about ?item ; schema:isPartOf <https://it.wikipedia.org/> . }
  OPTIONAL { ?wpEn schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . }
}
GROUP BY ?item
LIMIT 5000
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
    # Il servizio SPARQL usa la numerazione astronomica (0 = 1 a.C., -215 = 216 a.C.):
    # la convertiamo in quella storica, senza anno zero (-216 = 216 a.C.).
    m = re.match(r"^(-?)(\d{4,})", s or "")
    if not m: return None
    y = -int(m.group(2)) if m.group(1) else int(m.group(2))
    return y - 1 if y <= 0 else y

def val(r, k):
    return r.get(k, {}).get("value") or None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/battaglie_wikidata.geojson")
    out = ap.parse_args().out
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": QUERY, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "battlemap/0.2 (progetto personale)"})
    rows = json.load(urllib.request.urlopen(req, timeout=120))["results"]["bindings"]
    feats = []
    for r in rows:
        qid = r["item"]["value"].rsplit("/", 1)[-1]
        m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", val(r, "c") or "")
        if not m: continue   # esclude coordinate non valide
        name = val(r, "li") or val(r, "le")
        if not name: continue   # senza etichetta in italiano o inglese
        year = parse_year(val(r, "d")) if val(r, "d") else parse_year(val(r, "s"))
        end = parse_year(val(r, "e"))
        props = {"name": name, "year": year, "period": period(year), "reliability": "media", "wikidata": qid}
        if end is not None and year is not None and end > year: props["year_end"] = end
        wars = [w for w in (val(r, "wars") or "").split("|") if w]
        if wars: props["part_of"] = sorted(wars)
        wp = val(r, "wi") or val(r, "we")
        if wp: props["wikipedia"] = wp
        feats.append({"type": "Feature", "properties": props,
            "geometry": {"type": "Point", "coordinates": [round(float(m.group(1)), 5), round(float(m.group(2)), 5)]}})
    feats.sort(key=lambda f: (f["properties"]["year"] is None, f["properties"]["year"] or 0))
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh, ensure_ascii=False)
    print(f"{len(feats)} battaglie salvate in {out} "
          f"({sum(f['properties']['year'] is not None for f in feats)} con anno, "
          f"{sum('part_of' in f['properties'] for f in feats)} con guerra, "
          f"{sum('wikipedia' in f['properties'] for f in feats)} con voce Wikipedia)")

if __name__ == "__main__":
    main()
