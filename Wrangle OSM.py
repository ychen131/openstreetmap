
import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re

osm_file = open("central-west-london.osm", "r")

#Iterative Parsing

def count_tags(filename):
    tags = {}
        # create a dictionary of tags with tag name as key and quantity of each tags as value

    for event, elem in  ET.iterparse(filename): 
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
            
    return tags
            
def Iter_parse():

    tags = count_tags(osm_file)
    pprint.pprint(tags)

#Audit street names
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
street_types = defaultdict(int)

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()

        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def audit():
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])    
    print_sorted_dict(street_types)    

if __name__ == "__main__":
    #Iter_parse() #call function iter_parse
    #osm_file.seek(0) #go back to the begining of the dataset
    audit() #call function audit

