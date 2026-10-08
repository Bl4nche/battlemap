"""Converte l'export di Pleiades (luoghi del mondo antico) in un GeoJSON leggero con i soli luoghi in Italia.
Uso: python scripts/import_pleiades.py [pleiades-places-latest.csv.gz] [--out data/luoghi_pleiades.geojson]
Senza file lo scarica da https://atlantides.org/downloads/pleiades/dumps/ (circa 7 MB).
Pleiades (https://pleiades.stoa.org) è CC BY 3.0. Solo libreria standard.
Esclude elementi naturali (fiumi, monti...), regioni, popoli e luoghi non localizzati; raggruppa gli altri
in poche categorie. Il ritaglio sull'Italia è lo stesso, grossolano, di import_itinere.py."""
import argparse, csv, gzip, io, json, urllib.request
from import_itinere import in_italia

URL = "https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz"

# Tipo Pleiades -> (gruppo, etichetta italiana). L'ordine dei gruppi in PRIORITA decide quando un luogo ha più tipi.
TIPI = {
    "settlement": ("insediamento", "insediamento"), "settlement-modern": ("insediamento", "insediamento (oggi abitato)"),
    "urban": ("insediamento", "area urbana"), "fortified-settlement": ("insediamento", "insediamento fortificato"),
    "village": ("insediamento", "villaggio"), "estate": ("edificio", "tenuta"),
    "villa": ("edificio", "villa"), "townhouse": ("edificio", "domus"), "building": ("edificio", "edificio"),
    "architecturalcomplex": ("edificio", "complesso architettonico"), "bath": ("edificio", "terme"),
    "amphitheatre": ("edificio", "anfiteatro"), "theatre": ("edificio", "teatro"), "circus": ("edificio", "circo"),
    "forum": ("edificio", "foro"), "basilica": ("edificio", "basilica"), "plaza": ("edificio", "piazza"),
    "monument": ("edificio", "monumento"), "arch": ("edificio", "arco"), "garden-hortus": ("edificio", "giardino (hortus)"),
    "cistern": ("edificio", "cisterna"), "fountain": ("edificio", "fontana"), "production": ("edificio", "impianto produttivo"),
    "mine-2": ("edificio", "miniera"), "quarry": ("edificio", "cava"),
    "sanctuary": ("culto", "santuario"), "temple-2": ("culto", "tempio"), "temple": ("culto", "tempio"),
    "shrine": ("culto", "sacello"), "church": ("culto", "chiesa"), "church-2": ("culto", "chiesa"),
    "cemetery": ("culto", "necropoli"), "tomb": ("culto", "tomba"), "tumulus": ("culto", "tumulo"),
    "station": ("infrastruttura", "stazione di posta"), "bridge": ("infrastruttura", "ponte"),
    "road": ("infrastruttura", "strada"), "aqueduct": ("infrastruttura", "acquedotto"), "port": ("infrastruttura", "porto"),
    "canal": ("infrastruttura", "canale"), "city-gate": ("infrastruttura", "porta urbica"),
    "city-wall": ("infrastruttura", "mura"), "pass": ("infrastruttura", "valico"), "centuriation": ("infrastruttura", "centuriazione"),
    "fort": ("difesa", "forte"), "fort-2": ("difesa", "forte"), "castle": ("difesa", "castello"),
    "nuraghe": ("difesa", "nuraghe"), "fortress": ("difesa", "fortezza"), "watchtower": ("difesa", "torre di guardia"),
    "archaeological-site": ("sito", "sito archeologico"), "ruin": ("sito", "rovine"),
}
PRIORITA = ["difesa", "culto", "infrastruttura", "edificio", "insediamento", "sito"]

def num(s):
    try: return int(float(s))
    except (TypeError, ValueError): return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?"); ap.add_argument("--out", default="data/luoghi_pleiades.geojson")
    a = ap.parse_args()
    if a.src: raw = open(a.src, "rb").read()
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "battlemap/0.2 (progetto personale)"})
        raw = urllib.request.urlopen(req, timeout=180).read()
    csv.field_size_limit(10**8)
    rows = csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(raw)), encoding="utf-8"))
    out, tot = [], 0
    for r in rows:
        tot += 1
        if not r["reprLat"] or r["locationPrecision"] == "unlocated": continue
        if r["title"].startswith("Withdrawn"): continue   # schede ritirate o duplicate
        lon, lat = float(r["reprLong"]), float(r["reprLat"])
        if not in_italia(lon, lat): continue
        tipi = [TIPI[t.strip()] for t in r["featureTypes"].split(",") if t.strip() in TIPI]
        if not tipi: continue   # elementi naturali, regioni, popoli, tipi non classificati
        gruppo = min((g for g, _ in tipi), key=PRIORITA.index)
        name = r["title"].strip()
        if not name or name == "Untitled": name = tipi[0][1].capitalize() + " (senza nome)"
        props = {"name": name, "gruppo": gruppo,
                 "tipi": list(dict.fromkeys(e for _, e in tipi)),
                 "precisione": "precisa" if r["locationPrecision"] == "precise" else "approssimativa",
                 "pleiades": r["id"]}
        da, a_ = num(r["minDate"]), num(r["maxDate"])
        if da is not None: props["da"] = da
        # Pleiades chiude l'età moderna al 1999 (o al 2099): da lì in poi il luogo è considerato ancora esistente.
        if a_ is not None and a_ < 1700: props["a"] = a_
        out.append({"type": "Feature", "properties": props,
                    "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]}})
    out.sort(key=lambda f: PRIORITA.index(f["properties"]["gruppo"]))
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": out}, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(out)} luoghi in Italia su {tot} nel dataset -> {a.out}")

if __name__ == "__main__":
    main()
