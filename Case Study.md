# OpenStreetMap Data Case Study

### Map Area
Central West London
- [http://www.openstreetmap.org/export#map=12/51.4935/-0.0783](http://www.openstreetmap.org/export#map=12/51.4935/-0.0783)
- [http://overpass-api.de/api/map?bbox=-0.2101,51.4596,-0.0807,51.5540](http://overpass-api.de/api/map?bbox=-0.2101,51.4596,-0.0807,51.5540) (This is the link to download the data set)

After living in the surburbs for 4 years, my husband and I have decided to move to central west London. Hence I would like to use this opportunity to explore the area on OpendStreetMap.




## Problems Encountered in the Map
After downloading the data set for central west London, I had a quick scan through of a small segment of data. It is noted immediately, some of the street names seem to be out of the ordinary.  After running a provisional python file, the following problems were noted:

- Inconsistent case and typo in street names
- Over-abbreviated street names 
- Inconsistent abbreviation for "Saint"
- Irrelevent postcodes
- Inappropriate apostrophes within address
- Addresses with double postcodes


### Problems with street names
A list of expected street names, such as "Street" and "Road", is created. A regular expression is used to identify different types of street names within our data set. Any street names matching an item within the expected lists are not investigated further.  

After running the `audit` function (see below), we noted there are a few issues with the street names.
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
Some street names are written in lower cases *("street")*. A few obvious typos also noted among street names, such as "Wqalk" and "Strreet".

#### Over abbreviation
A common example for this particular issue is showing "St" rather than "Street".

#### Inconsistent abbreviation for "Saint"
The word "Saint" is very common among street names within UK. It is usually displayed as an abbreviated version of "St". Two other versions also appeared within the data set, "Saint" and "St." *("Saint Alban's Grove" and "St Alban's Grove")*

In order to eliminate the above three issues, an `update_name` function is used:
```python
def update_name(name, mapping):
    name = string.capwords(name) 
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected and street_type in mapping:
            name = re.sub(street_type_re, mapping[street_type], name)
    else:
        print "Strange street name: " % name #print any strange street name does not match the regular expression

    if "Saint " in name or "St. " in name: 
        name = name.replace("Saint ", "St ")
        name = name.replace("St. ", "St ")
    return name
```

This updated all the street names so that they all start with a capital letter. Typos noted were fixed using a list of mapping. Different versions of "Saint" are all converted to "St" in the data set.

#### Inappropriate use of apostrophes
Apart from the issues noted above, it is also noted that some street names have inappropriate use of apostrophes. *(Princes Gardens", "Prince's Gardens" and "Princes's Gardens")*. Due to limited local knowledge and time comsuing nature of finding all the correct version of those street names containing apostrophes, these street names are left unfixed in the data set.


### Problems with postcodes
A similar approach is taken to identify problems with postcode. Firstly, regular expression is used to identify postcodes under "way" and "node". Subsequently, the following function is used to identify postcodes.

```python
def find_postcode():
    osm_file = open(cw_london, "r")
    postcode_types = set()
    odd_postcode = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    m = postcode_re.search(tag.attrib['v'])
                    if m:
                        postcode_types.add(tag.attrib['v'])  
                    else:
                        odd_postcode.add(tag.attrib['v'])

    osm_file.close()

    return (postcode_types, odd_postcode)
```

After investigating the result, we noted two major problems with the postcpde. Area postcodes appears among postcode which is the post code for the entire are rather than a specific address *("SW6")*. In addition to are postcodes, we noted afew addres have two postcode *("W2 1NE;W2 1NF")*. In London, there are a few address containing two postcodes and both of them are correct. 

To fix the problems with postcode, the following function was written:
```python
def update_postcode(odd_postcode):
    if area_postcode_re.search(odd_postcode):
        postcode = " "
    else:
        postcode = odd_postcode.split(";")[0]
    return postcode
```

Area post codes are dropped from the data set and the first postcode is kept if two postcodes were identified for the same address. "W2 1NE;W2 1NF" is changed to "W2 1NE".




## Overview of the data
This section contains basic statistics about the dataset, the SQL queries used to gather them, and some additional ideas about the data in context.

```
central-west-london.osm ..... 184M B
open_street_map.db .......... 86 MB
nodes.csv  .................. 55 MB
nodes_tags.csv .............. 11 MB
ways.csv .................... 7.8 MB
ways_nodes.csv .............. 22 MB
ways_tags.csv ............... 17 MB
```
### Number of ways
```sql
sqlite> SELECT COUNT(*) FROM nodes;
```
688069

### Number of ways
```sql
sqlite> SELECT COUNT(*) FROM ways;
```
135019

### Number of unique users
```sql
sqlite> SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
2466

### Top 10 contributing users
```sql
sqlite> SELECT e.user, COUNT(*) as num 
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
```

```sql
user                  num       
--------------------  ----------
Derick Rethans        104466    
Paul The Archivist    94982     
Ed Avis               62638     
Amaroussi             51996     
Tom Chance            40994     
ecatmur               31292     
Harry Wood            26272     
Blumpsy               26166     
abc26324              19572     
sladen                14960 
```

### Number of restaurants, cafes and pubs

```sql
sqlite> SELECT value, count(*) as num 
FROM nodes_tags 
WHERE value = 'restaurant' OR value = 'pub' OR value = 'cafe' 
GROUP BY value 
ORDER BY num DESC limit 15;
```

```sql
value       num       
----------  ----------
restaurant  1788      
cafe        1224      
pub         733  
```
### Top 10 most popular cusines
```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i 
ON nodes_tags.id=i.id
WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10;
```

```sql
value       num       
----------  ----------
italian     158       
indian      106       
japanese    65        
pizza       55        
chinese     52        
french      50        
thai        34        
burger      31        
asian       23        
mexican     23    
```

## Additional Ideas
During data cleansing process, it is noted that there are cases where inappropriate aprostrophes were identified. Likewise, there are also street names that are extremely similar *(eg. "Snowfields" and "Snowsfields")*. They are not fixed within the this project due to insufficient local knowledge as well as the time consuming nature of this task.

One possible solution, is to standardise these street names in during the data wrangling proces. This is a fast solution to the problem but the accuracy of the street name is comprimised.

An alternative method is to use machine learning identifying potential duplication of street names based on certain degree of similarity. Subsequently, carry out research to find out the accurate name for a particular street.

We can see evidence of this issue by using the following self-join:
```sql
sqlite> SELECT DISTINCT n1.value, n2.value 
FROM nodes_tags n1, nodes_tags n2
WHERE n1.key is 'street' AND n2.key is 'street' 
AND n1.value like '%''%' AND n2.value like replace(n1.value, '''', '');

value                           value                         
------------------------------  ------------------------------
Gray's Inn Road                 Grays Inn Road                
St Peter's Street               St Peters Street              
King's Road                     Kings Road                    
John Prince's Street            John Princes Street           
Earl's Court Square             Earls Court Square            
Prince's Square                 Princes Square                
King's Cross Road               Kings Cross Road   
```
Here the query is finding all street names containing apostrophes which match some other street name but with the apostrophe omitted.
