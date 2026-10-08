"""Converte il dataset Itiner-e (strade dell'Impero romano) in un GeoJSON leggero con le sole strade italiane.
Uso: python scripts/import_itinere.py itinere_roads.geojson [--out data/strade_itinere.geojson]
Scarica prima itinere_roads.geojson da https://zenodo.org/records/17122148 (CC BY 4.0).
Passi: EPSG:3395 (metri) -> lon/lat, ritaglio sull'Italia, semplificazione (Douglas-Peucker), coordinate a 5 decimali.
Solo libreria standard. Il ritaglio usa un contorno grossolano dell'Italia con un margine: ai confini
possono restare tratti di Svizzera, Francia o Slovenia vicini alla frontiera."""
import argparse, json, math

A, E = 6378137.0, 0.0818191908426215  # WGS84: semiasse maggiore, eccentricità (Mercatore ellissoidale)

def to_lonlat(x, y):
    lon = math.degrees(x / A)
    ts = math.exp(-y / A)
    phi = math.pi / 2 - 2 * math.atan(ts)
    for _ in range(8):
        phi = math.pi / 2 - 2 * math.atan(ts * ((1 - E * math.sin(phi)) / (1 + E * math.sin(phi))) ** (E / 2))
    return lon, math.degrees(phi)

# Contorno grossolano (lon, lat) di penisola + Sicilia, con margine. Sardegna: rettangolo a parte.
ITALIA = [(6.5, 43.9), (6.9, 45.2), (6.8, 45.9), (7.9, 46.1), (8.5, 46.5), (9.0, 46.5), (9.6, 46.6), (10.5, 47.0),
          (11.2, 46.95), (12.3, 47.1), (13.1, 46.7), (13.7, 46.6), (13.95, 45.75), (13.7, 45.5), (13.2, 45.7),
          (12.2, 45.3), (12.6, 44.6), (13.6, 43.6), (14.3, 42.4), (15.2, 41.95), (16.2, 41.9), (18.6, 40.5),
          (18.6, 39.7), (17.2, 39.0), (17.2, 38.4), (16.2, 37.9), (15.8, 37.9), (15.7, 36.9), (15.0, 36.6),
          (14.1, 36.6), (12.3, 37.3), (12.3, 38.4), (13.5, 38.4), (14.4, 38.2), (15.8, 38.3), (15.7, 39.3),
          (15.4, 40.0), (14.5, 40.5), (13.4, 41.2), (12.2, 41.6), (11.1, 42.3), (10.5, 42.9), (9.8, 43.9),
          (8.3, 43.8), (7.5, 43.7), (6.5, 43.9)]
SARDEGNA = (8.0, 38.8, 9.9, 41.4)

def in_poly(lon, lat, poly=ITALIA):
    ins, n = False, len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins

def in_italia(lon, lat):
    s = SARDEGNA
    return in_poly(lon, lat) or (s[0] <= lon <= s[2] and s[1] <= lat <= s[3])

def dp(pts, tol):
    """Douglas-Peucker iterativo (evita il limite di ricorsione sulle linee lunghe)."""
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1; norm = math.hypot(dx, dy)
        dmax, idx = 0.0, None
        for i in range(a + 1, b):
            x, y = pts[i]
            d = math.hypot(x - x1, y - y1) if norm == 0 else abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm
            if d > dmax: dmax, idx = d, i
        if idx is not None and dmax > tol:
            keep[idx] = True; stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(pts, keep) if k]

TIPI = {"Main Road": "principale", "Secondary Road": "secondaria"}
CERT = {"Certain": "certo", "Conjectured": "ricostruito", "Hypothetical": "ipotetico"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--out", default="data/strade_itinere.geojson")
    ap.add_argument("--tol", type=float, default=0.00015, help="tolleranza in gradi (~15 m)")
    a = ap.parse_args()
    feats = json.load(open(a.src, encoding="utf-8"))["features"]
    out, n_in = [], 0
    for f in feats:
        g = f["geometry"]
        if not g: continue
        lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        parts = []
        for ln in lines:
            ll = [to_lonlat(p[0], p[1]) for p in ln]
            run = []
            for pt in ll:               # spezza la linea dove esce dall'Italia
                if in_italia(*pt): run.append(pt)
                else:
                    if len(run) > 1: parts.append(run)
                    run = []
            if len(run) > 1: parts.append(run)
        parts = [[[round(x, 5), round(y, 5)] for x, y in dp(p, a.tol)] for p in parts]
        parts = [p for p in parts if len(p) > 1]
        if not parts: continue
        n_in += 1
        p = f["properties"]
        props = {"kind": "strada", "period": "antica", "source": "itiner-e",
                 "name": (p.get("Name") or "Strada romana").strip(),
                 "tipo": TIPI.get(p.get("Type"), "altro"),
                 "certezza": CERT.get(p.get("Segment_s"), "n.d.")}
        if p.get("Descriptio"): props["note"] = p["Descriptio"]
        out.append({"type": "Feature", "properties": props,
                    "geometry": {"type": "MultiLineString", "coordinates": parts}})
    json.dump({"type": "FeatureCollection", "features": out}, open(a.out, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"{n_in} strade su {len(feats)} nel dataset -> {a.out}")

if __name__ == "__main__":
    main()
