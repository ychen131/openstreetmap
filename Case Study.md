# OpenStreetMap Data Case Study

### Map Area
Central West London
- [http://www.openstreetmap.org/export#map=12/51.4935/-0.0783](http://www.openstreetmap.org/export#map=12/51.4935/-0.0783)
- [http://overpass-api.de/api/map?bbox=-0.2101,51.4596,-0.0807,51.5540](http://overpass-api.de/api/map?bbox=-0.2101,51.4596,-0.0807,51.5540) (This is the link to download the data set)

After living in the surburban for 4 years, my husband and I have decided to move to central west London. Hence I would like to this opportunity to explore the area on OpendStreetMap.



## Problems Encountered in the Map
After downloading the data set for central west London, I have run a few audit trial using "wrangle_osm.py". Ther following issues were noted:

- Inconsistent case and typo in street names
- Over­abbreviated street names 
- Inconsistent abbreviation for "Saint"
- Inappropriate apostrophies within address
- Irrelevent postcodes
- Address with double postcodes

### Inconsistent case and typo in street names
After running 
