"""Scarica da OpenStreetMap (Overpass) trincee, campi di battaglia e strade romane in un'area
e scrive un GeoJSON compatibile con data/livelli.geojson.
Uso: python scripts/fetch_osm.py --bbox 45.7,13.3,46.3,13.8 --out data/livelli_osm.geojson
bbox = sud,ovest,nord,est. Tieni l'area piccola: Overpass rifiuta richieste troppo grandi.
Dati OSM: licenza ODbL (attribuzione obbligatoria). Solo way; le relation non sono gestite."""
import argparse, json, urllib.parse, urllib.request

KINDS = [("military", "trench", "trincea", "wwi"),
         ("historic", "battlefield", "area", "altro"),
         ("historic", "roman_road", "strada", "antica")]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bbox", default="45.7,13.3,46.3,13.8")
    ap.add_argument("--out", default="data/livelli_osm.geojson")
    a = ap.parse_args()
    parts = "".join(f'way["{k}"="{v}"]({a.bbox});' for k, v, _, _ in KINDS)
    q = f"[out:json][timeout:90];({parts});out geom;"
    req = urllib.request.Request("https://overpass-api.de/api/interpreter",
        data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "battlemap/0.1"})
    elems = json.load(urllib.request.urlopen(req, timeout=120))["elements"]
    feats = []
    for e in elems:
        tags, g = e.get("tags", {}), e.get("geometry", [])
        if len(g) < 2: continue
        coords = [[p["lon"], p["lat"]] for p in g]
        for k, v, kind, period in KINDS:
            if tags.get(k) == v: break
        closed = coords[0] == coords[-1] and len(coords) > 3
        geom = {"type": "Polygon", "coordinates": [coords]} if (kind == "area" and closed) \
               else {"type": "LineString", "coordinates": coords}
        feats.append({"type": "Feature", "geometry": geom, "properties": {
            "kind": kind, "name": tags.get("name", "Senza nome"), "period": period, "osm_id": e["id"]}})
    json.dump({"type": "FeatureCollection", "features": feats}, open(a.out, "w"), ensure_ascii=False)
    print(f"{len(feats)} elementi salvati in {a.out}")

if __name__ == "__main__":
    main()
