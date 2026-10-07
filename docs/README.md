# Battlemap

Mappa interattiva dei luoghi di battaglie storiche, costruita su dati aperti (Wikidata, OpenStreetMap). Pensata per appassionati di storia e di ricerca sul territorio.

**Scelta di progetto:** ogni luogo è mostrato come area approssimativa, con un indice di affidabilità della posizione, perché le coordinate di molte battaglie antiche sono incerte e per non facilitare scavi clandestini.

## Avvio

```bash
python -m http.server 8000     # poi apri http://localhost:8000
```

Per scaricare più dati da Wikidata (default: Italia):

```bash
python scripts/fetch_wikidata.py --out data/battaglie_wikidata.geojson
```

Poi punta `fetch(...)` in `index.html` al nuovo file. I dati in `data/battaglie.geojson` sono un esempio con coordinate approssimative.

## Fonti e licenze

- Wikidata: CC0
- OpenStreetMap (mappa di base): ODbL, attribuzione richiesta
- Leaflet: BSD-2

## Note legali

In Italia la ricerca con metal detector senza autorizzazione è vietata dal D.Lgs. 42/2004 e i reperti appartengono allo Stato. Altrove le regole variano. Questo strumento non incoraggia la ricerca di reperti.

## Roadmap

- [ ] Livello con aree protette e vincolate
- [ ] Mappe storiche georeferenziate in trasparenza
- [ ] Dati da OpenStreetMap (`historic=battlefield`, trincee, bunker)
- [ ] Verifica manuale e pulizia dei dati con test
- [ ] Pubblicazione su GitHub Pages

## Livelli sovrapposti

La mappa ha un controllo livelli con: luoghi di battaglie, aree di battaglia, strade antiche, trincee e fortificazioni, più la base "Terreno" (OpenTopoMap) utile per leggere rilievi e tracciati.

I livelli sono letti da `data/livelli.geojson` (campo `kind`: `area`, `strada` o `trincea`). **I 4 elementi inclusi sono dimostrativi e schematici, non storici**: sostituiscili con dati reali.

Fonti per dati reali:

- **OpenStreetMap**: `python scripts/fetch_osm.py --bbox sud,ovest,nord,est` scarica trincee (`military=trench`), campi di battaglia (`historic=battlefield`) e strade romane (`historic=roman_road`) di un'area piccola.
- **Itiner-e**: dataset aperto delle strade romane (CC BY 4.0), da convertire in GeoJSON.
- **Catalogo Generale dei Beni Culturali / Vincoli in Rete**: per aree archeologiche e vincolate.

## Italia: strade antiche e città scomparse

`data/italia.geojson` contiene 8 strade romane (Appia, Flaminia, Emilia, Aurelia, Cassia, Salaria, Popilia, Postumia) e 12 città scomparse, sepolte, abbandonate o sommerse. **Tracciati e posizioni sono approssimativi**: le strade sono schematiche per tappe principali. Per tracciati precisi usa OSM (`scripts/fetch_osm.py`, una regione per volta) o Itiner-e.

Per ampliare l'elenco delle città: `python scripts/fetch_citta.py`, poi aggiungi il file in `index.html` accanto agli altri.

## Dati precisi da OpenStreetMap (dal vivo)

Da zoom 11 in su la mappa scarica da Overpass, per l'area visibile, i dati OSM reali:

| Livello | Tag OSM |
|---|---|
| Strade antiche | `historic=roman_road`, `road`, `trackway` |
| Rovine e siti archeologici | `historic=ruins`, `archaeological_site`, `aqueduct`, `city_gate`, `temple`, `amphitheatre`, `theatre` |
| Catacombe e ipogei | `historic=catacombs`, `tomb=catacomb` |
| Campi di battaglia | `historic=battlefield` |
| Trincee, bunker | `military=trench/bunker/pillbox` |
| Castelli, forti, mura | `historic=castle/fort/city_walls/fortification/tower` |

Sotto zoom 11 restano i tracciati schematici di `data/`, solo come panoramica. Il server pubblico Overpass può essere lento o rifiutare richieste: l'app riprova da sola e segnala cosa manca. Se una zona appare vuota, di solito è perché in OSM non è ancora mappata.
