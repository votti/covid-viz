# covid-viz

Some quick exploration of Covid data from Switzerland.

Trying to keeping it tidy - in Python.

Play with the code interactively with Binder: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fgithub.com%2Fvotti%2Fcovid-viz.git/master)

## Data sources
Datasets are added as Git submodules if possible. This allowes to be reproducible in frequently changing resources.

### COVID19
Data about covid cases

- covid_19: Swiss data about COVID maintained by openZH: https://github.com/openZH/covid_19

- COVID-20: Worldwide COVID-19 data from  Johns Hopkins CSSE: https://github.com/CSSEGISandData/COVID-19

### Monitoring
Additional metadata about populations

- covid19monitoring: Data for diverse mobility indicators for Switzerland, provided by statistikZH: https://github.com/statistikZH/covid19monitoring/

- google_covid19_mobility_reports: contains worldwide mobility reports scraped by from the pdf mobility reports: https://github.com/philshem/scrape_covid19_mobility_reports

- Varia: single files with additional information

### Maps
Mapping data
- GeoJson of Switzerland: https://github.com/ZHB/switzerland-geojson

Note: https://github.com/interactivethings/swiss-maps might be a better source - but needs to be built.

## Resources

- How to map swiss cantons: https://rsandstroem.github.io/tag/folium.html
