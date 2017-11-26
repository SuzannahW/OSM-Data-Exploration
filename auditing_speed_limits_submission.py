# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Created on Sat Jun 03 18:21:40 2017

@author: Suzannah
"""
import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint
from collections import defaultdict

osm_file = open('Oxfordshire.osm', 'r')
speed_limits = defaultdict(set)
unexpected_speed_limits = defaultdict(set)
expected = ['5 mph', '10 mph', '15 mph', '20 mph', '25 mph', '30 mph', '40 mph',
            '50 mph', '60 mph', '70 mph']

mapping = {'10': '10 mph',
           '20': '20 mph',
           '30': '30 mph',
           '50': '50 mph'}
                
def states_speed_limit(element):
    return (element.attrib['k']=='maxspeed')

#For auditing and setting up the mapping before adding to 'loading_to_CSV' file procedure        
def cleaning_speed_limits(speed_limit, mapping):
    if speed_limit not in expected:
        if speed_limit in mapping.keys():
            speed_limit = mapping[speed_limit]
    if speed_limit not in expected:
        if speed_limit not in unexpected_speed_limits:
            unexpected_speed_limits[speed_limit] = 1
        else:
            unexpected_speed_limits[speed_limit] += 1 
    elif speed_limit not in speed_limits:
        speed_limits[speed_limit] = 1
    else:
        speed_limits[speed_limit] += 1
    return speed_limit, unexpected_speed_limits, speed_limits    

#Produces two dictionaries, one with the number of occurances of expected speed limits, and one with
#the number of occurances of unexpected speed limits.
def auditing_speed_limits():
    for event, element in ET.iterparse(osm_file, events=('start',)):
        if element.tag == 'way':
            for tag in element.iter('tag'):
                if states_speed_limit(tag):
                    cleaning_speed_limits(tag.attrib['v'], mapping)
    pprint.pprint(dict(speed_limits))
    pprint.pprint(dict(unexpected_speed_limits))
    return tag

auditing_speed_limits()