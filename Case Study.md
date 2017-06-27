# OpenStreetMap Data Case Study

### Map Area
Central West London
- [http://www.openstreetmap.org/export#map=12/51.4935/-0.0783](http://www.openstreetmap.org/export#map=12/51.4935/-0.0783)
- [http://overpass-api.de/api/map?bbox=-0.2101,51.4596,-0.0807,51.5540](http://overpass-api.de/api/map?bbox=-0.2101,51.4596,-0.0807,51.5540) (This is the link to download the data set)

After living in the surburban for 4 years, my husband and I have decided to move to central west London. Hence I would like to this opportunity to explore the area on OpendStreetMap.



## Problems Encountered in the Map
After downloading the data set for central west London, I had a a quick scan through of the data and audit the street name and postcodes in the data set. The following problems were noted:

- Inconsistent case and typo in street names
- Over­abbreviated street names 
- Inconsistent abbreviation for "Saint"
- Inappropriate apostrophies within address
- Irrelevent postcodes
- Address with double postcodes

### Problems with street names
A list of expected street names, such as "Street" and "Road", are created. Regular expression is used to identify different types of street names. For any street names match the item within the lists are not investigated further. 

After ruing the "audit" function (see below), we noted there are a few issues with the street names.
```python
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
```

#### Inconsistent case and typo in street name
Some street names are written in lower cases (eg. street). A few obvious typos also noted among street names, such as "Wqalk" and "Strreet".

#### Over abbreviation
A commen example for this paritular issue is "
