# -*- coding: utf-8 -*-
"""
Created on Sat Jun 03 18:21:40 2017

@author: Suzannah
"""

#!/usr/bin/env python
import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint
import re
from collections import defaultdict

osm_file = open('Oxfordshire.osm', 'r')

street_type_re = re.compile(r'\s\b\S+\.?$', re.IGNORECASE)
The_street_re = re.compile(r'^The', re.IGNORECASE)
Saint_street_re = re.compile(r'^Saint', re.IGNORECASE)

expected = [' Street', ' Avenue', ' Road', ' Drive', ' Way', ' Close', ' Place',  ' Court',
            ' Crescent', ' Down', ' End', ' Furze', ' Lane', ' Mews', ' Park', ' Gardens',
            ' Hill', ' Meadow', ' Square', ' Town', ' Parade', ' Walk', ' Rise', ' East',
            ' Mead', ' Turn', ' Valley', ' View', ' West', ' Wharf', ' Terrace', ' South',
            ' Moors', ' Fields', ' Entry', ' Driftway', ' Bridge', ' Area', ' Centre']

mapping = {' Ave': ' Avenue',
          ' Rd': ' Road',
          ' St': ' Street',
          ' road': ' Road',
          ' way': ' Way',
          ' Way,': ' Way',
          ' Way?': ' Way',
          " Giles'": " Giles",
          "St Clements": "St Clement's Street",
          "St Clements Street": "St Clement's Street",
          "Saint Giles'": "St Giles",
          'Milton Gate, Milton': 'Milton Gate',
          'Milton Gate, Milton Park': 'Milton Park',
          '111': "",
          'Unit 1, Seacourt Towers, West Way': 'West Way',
          '41 Woodlands Road': 'Woodland Road',
          '2 Savile Road': 'Savile Road'}

street_types = defaultdict(set)

def is_street_name(element):
    return (element.attrib['k']=='addr:street')

def audit_street_type(street_types, street_name, mapping):
    m = street_type_re.search(street_name)
    t = The_street_re.search(street_name)
    s = Saint_street_re.search(street_name)
    if street_name in mapping.keys():
        street_name = mapping[street_name]
    if s:
        saint = s.group()
        saint = re.sub(saint, "St", street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type in mapping.keys():
                street_name = re.sub(street_type, mapping[street_type], street_name)  
            else:
                if not t:
                    street_types[street_type].add(street_name)              
    return street_name, street_types 
               
def audit():
    for event, element in ET.iterparse(osm_file, events=('start',)):
        if element.tag == 'way':
            for tag in element.iter('tag'):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'], mapping)
    pprint.pprint(dict(street_types)) 
    return tag

audit()
  