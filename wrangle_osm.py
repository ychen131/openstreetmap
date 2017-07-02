
import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import string
import re

cw_london = "central-west-london.osm"

#Iterative Parsing--------------------------------------------------------------------------------

def count_tags(filename):
    tags = {}
        # create a dictionary of tags with tag name as key and quantity of each tags as value

    for event, elem in  ET.iterparse(filename): 
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
            
    return tags
        
# General data check, count number of tag types.
def Iter_parse():

    tags = count_tags(cw_london)
    pprint.pprint(tags)

#Audit street names------------------------------------------------------------------------------
# Regular expression to check for characters at end of string, including optional period.
# Eg "Street" or "St."
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

# Dictionary of unique street names. Defaults to empty set.
# street_types = defaultdict(set)

# Common street names
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Road", "Parkway", "Commons", "Close"]


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

# Iterate over the osmfile and create a dictionary mapping from expected street names
# to collected streets.
def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    osm_file.close()
    return street_types   

#Improving Street names

#Mapping for names to be updated
mapping = { "St": "Street",
            "Sreet":"Street",
            "St.":"Street",
            "Steet":"Street",
            "Strreet":"Street",
            "Sq":"Square",
            "Rd": "Road",
            "Wqalk":"Walk"
            }

# Function to perfom data cleansing on street name
def update_name(name, mapping):
    name = string.capwords(name) #Change all the street name to start with capital letter. 
    #In three cases, there is a space after the street name, for example, "Little New Street ". 
    #Function "string.capwords()" fixes this issue before street names is parsed for regular expression check.
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type not in expected and street_type in mapping:
            name = re.sub(street_type_re, mapping[street_type], name)
    else:
        print "Strange street name: " % name #print any strange street name does not match the regular expression

    if "Saint " in name or "St. " in name: 
    #having abbreviation of "Saint" is very common in the UK.
    #However there are inconsistency in abb: "St ", "Saint " and "St. ". They are changed to "St"

        name = name.replace("Saint ", "St ")
        name = name.replace("St. ", "St ")
    return name
 
def improve_street_name():
    st_types = audit(cw_london)
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name

#Double Postcode for one address---------------------------------------------------------------------------------------------------

#We noted there are 6 addresses have two postcodes. After performing some research, it is noted that they are the rare cases that
# both postcodes are for the same address. Therefore, we will keep the first postcode. eg. 'W2 1LN;W2 1LW'

#regular expression to check whether postcode is in appropriate format
postcode_re = re.compile('^[A-Z]{1,2}[0-9]{1,2}[A-Z]? [0-9][A-Z]{2}$') 

def is_postcode(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")


#search for postcodes within "way" and "node"
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
                        #print "Strange: %s" % str(tag.attrib['v'])

    osm_file.close()
    # pprint.pprint(odd_postcode)
    # print "Break----------------------\n"
    # pprint.pprint(postcode_types)


    return (postcode_types, odd_postcode)

#Drop area postcode and maintain only one postcode for those with two postcodes
area_postcode_re = re.compile('^[A-Z]{1,2}[0-9]{1,2}[A-Z]? ?[0-9]?$')

def update_postcode(odd_postcode):
    if area_postcode_re.search(odd_postcode):
        postcode = " "
    else:
        postcode = odd_postcode.split(";")[0]
    return postcode


def improve_postcode():
    postcode_all = find_postcode()

    for postcode in postcode_all[1]:
        better_postcode = update_postcode(postcode)
        print postcode, "=>", better_postcode


#Other unfixed problem------------------------------------------------------------------------------------------------------------- 
#1. apostrophe in the work. Many cases of inconsistency usage of apostrophe noted. 
#However, due to limited local knowledge and time-consuming nature to search for the correct names, 
#they remained unchanged in the data set.


if __name__ == "__main__":
    #Iter_parse() #call function iter_parse
    #osm_file.seek(0) #go back to the begining of the dataset
    #audit() #call function audit
    #improve_street_name()
    #find_postcode()
    improve_postcode()