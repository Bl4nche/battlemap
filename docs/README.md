# Battlemap

Mappa interattiva dei luoghi di battaglie storiche, costruita su dati aperti (Wikidata, OpenStreetMap). Pensata per appassionati di storia e di ricerca sul territorio.

**Scelta di progetto:** ogni luogo è mostrato come area approssimativa, con un indice di affidabilità della posizione, perché le coordinate di molte battaglie antiche sono incerte e per non facilitare scavi clandestini.

## Avvio

```bash
python -m http.server 8000     # poi apri http://localhost:8000
```

## Battaglie da Wikidata e cursore temporale

`data/battaglie_wikidata.geojson` contiene le battaglie in Italia con coordinate presenti su Wikidata (circa 400). Per ognuna: anno, oppure anni di inizio e fine (assedi, campagne), guerra o campagna di cui fa parte e link alla voce di Wikipedia, in italiano se esiste. Per aggiornarle:

```bash
python scripts/fetch_wikidata.py
```

Gli anni a.C. sono negativi (-216 = 216 a.C.): lo script converte la numerazione astronomica usata dal servizio SPARQL di Wikidata, dove l'anno 0 esiste ed è l'1 a.C. Se il file manca, la mappa usa il piccolo esempio in `data/battaglie.geojson`.

Nel pannello, il **cursore temporale** (Dal/Al) mostra solo le battaglie il cui periodo tocca l'intervallo scelto, in combinazione con i filtri per epoca. "Scorri nel tempo" fa avanzare da sola una finestra di anni; le battaglie senza data si possono includere o escludere.

## Fonti e licenze

- Wikidata: CC0
- OpenStreetMap (mappa di base): ODbL, attribuzione richiesta
- Leaflet: BSD-2

## Note legali

In Italia la ricerca con metal detector senza autorizzazione è vietata dal D.Lgs. 42/2004 e i reperti appartengono allo Stato. Altrove le regole variano. Questo strumento non incoraggia la ricerca di reperti.

## Roadmap

- [ ] Livello con aree protette e vincolate
- [x] Mappe storiche georeferenziate in trasparenza
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

## Mappe storiche

Nel pannello "Mappe storiche" si sceglie una carta da sovrapporre alla base, con trasparenza regolabile. Sono servite direttamente dagli enti che le pubblicano (nessun file nel repository):

| Carta | Copertura | Fonte |
|---|---|---|
| Impero romano verso il 200 d.C. | tutto l'Impero, dettaglio fino a zoom 11 | DARE, Digital Atlas of the Roman Empire (J. Åhlfeldt) |
| Carta geometrica della Toscana, Inghirami 1830 | Toscana | Regione Toscana, progetto CASTORE (WMS) |
| Catasto generale toscano, prima metà dell'Ottocento | Toscana, da zoom 14 | Regione Toscana, progetto CASTORE (WMS) |
| Carte topografiche austriache e sarde 1828–1853 | Emilia-Romagna, leggibile da zoom 12 | Regione Emilia-Romagna, Carta storica regionale (WMS) |
| Rilievo LiDAR ombreggiato 2014–2018 | Trentino, dettaglio da zoom 14 | Provincia autonoma di Trento (WMS) |
| Rilievo ombreggiato 0,5 m / 2,5 m | Alto Adige | Provincia autonoma di Bolzano (WMS) |

I servizi WMS regionali dichiarano "nessun costo e nessun vincolo di accesso". Per DARE il sito non indica una licenza esplicita per le tile: le citiamo come fonte.

Il rilievo LiDAR toglie la vegetazione e mostra la forma del terreno: sul fronte trentino e altoatesino della Prima guerra mondiale (Pasubio, Zugna, altipiani, Ortles-Cevedale) si leggono trincee, camminamenti, postazioni e strade militari. I resti della Grande Guerra sono tutelati dalla legge 78/2001.

Scartati per il rilievo: Friuli Venezia Giulia e Veneto (pubblicano i dati LiDAR solo da scaricare, non un rilievo ombreggiato consultabile via WMS) e Slovenia (l'ottima visualizzazione LiDAR di ZRC SAZU, che coprirebbe Caporetto e l'alto Isonzo, è servita solo nel sistema di coordinate sloveno EPSG:3794 e non si sovrappone a una mappa web standard).

Scartate dopo verifica: l'IGM 1:25.000 del Geoportale Nazionale (il servizio passa da HTTPS a HTTP, che il browser blocca su GitHub Pages, e il foglio della zona 33 restituisce errore) e i rilievi asburgici di Mapire/Arcanum (servizio a pagamento: senza accordo restituisce immagini vuote).

## Confini politici dell'epoca

Nella linea del tempo, "Confini politici dell'epoca" mostra gli Stati e i territori dal dataset **historical-basemaps** di A. Ourednik (https://github.com/aourednik/historical-basemaps). Il dataset ha istantanee per anni fissi (per esempio 300 a.C., 200 a.C., 1200, 1492, 1815, 1878, 1914): la mappa usa l'ultima istantanea non successiva al centro dell'intervallo scelto, così non mostra mai confini "dal futuro" (per il 1859 usa il 1815, non il 1878).

I territori soggetti alla stessa potenza hanno lo stesso colore; tratteggio = confine approssimativo secondo il dataset. I nomi sono in inglese, come nell'originale.

I file non sono nel repository: la pagina li scarica al bisogno da jsDelivr, bloccati su un commit preciso, perché il dataset è distribuito con licenza GPL-3.0. I confini sono pensati per la scala di continente: vanno letti come indicativi, specie nell'antichità e nel Medioevo.

## Luoghi antichi (Pleiades)

`data/luoghi_pleiades.geojson` contiene circa 4.500 luoghi del mondo antico in Italia dal gazetteer **Pleiades** (https://pleiades.stoa.org, CC BY 3.0). Sono raggruppati in città e insediamenti; ville, terme, teatri ed edifici; santuari, templi e necropoli; ponti, stazioni, porti, acquedotti e mura; forti, castelli e nuraghi; altri siti archeologici. Sono esclusi gli elementi naturali (fiumi, monti), le regioni, i popoli e i luoghi non localizzati. Bordo tratteggiato = posizione approssimativa secondo Pleiades.

Anche questi luoghi seguono il cursore temporale: un luogo è visibile se è attestato nell'intervallo scelto. Le date di Pleiades sono per periodi ampi (per esempio "romano", 30 a.C. – 300 d.C.), non anni precisi; i luoghi attestati fino all'età moderna sono considerati ancora esistenti.

Per aggiornarli (scarica circa 7 MB):

```bash
python scripts/import_pleiades.py
```

## Italia: strade romane (Itiner-e) e città scomparse

`data/strade_itinere.geojson` contiene 921 strade romane d'Italia dal dataset **Itiner-e** (de Soto et al., CC BY 4.0, https://zenodo.org/records/17122148), già ritagliate sull'Italia e semplificate (1,2 MB). Si caricano a ogni zoom, senza passare da Overpass. Linea continua = tracciato certo, tratteggiata = ricostruito da fonti e immagini (la grande maggioranza).

Per rigenerarle: scarica `itinere_roads.geojson` da Zenodo (78 MB) e lancia `python scripts/import_itinere.py itinere_roads.geojson`. Il ritaglio usa un contorno grossolano dell'Italia: vicino ai confini possono restare brevi tratti di Svizzera, Francia o Slovenia.

`data/italia.geojson` contiene 12 città scomparse, sepolte, abbandonate o sommerse, con posizioni approssimative. Per ampliare l'elenco: `python scripts/fetch_citta.py`.

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
