# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Created on Sat Jun 10 12:17:08 2017

@author: Suzannah
"""

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint
import re
import csv
import codecs
import cerberus

import schema

OSM_PATH = "Oxfordshire.osm"

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

expected_speeds = ['5 mph', '10 mph', '15 mph', '20 mph', '25 mph', '30 mph', '40 mph',
            '50 mph', '60 mph', '70 mph']

mapping_speeds = {'10': '10 mph',
                  '20': '20 mph',
                  '30': '30 mph',
                  '50': '50 mph'}

#Function used to clean street names ussing regex and mapping             
def audit_street_type(street_name, mapping):
    m = street_type_re.search(street_name)
    s = Saint_street_re.search(street_name)
    if street_name in mapping.keys():
        street_name = mapping[street_name]
    if s:
        saint = s.group()
        street_name = re.sub(saint, 'St', street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type in mapping.keys():
                street_name = re.sub(street_type, mapping[street_type], street_name)             
    return street_name

#Function used to clean speed limits using mapping             
def audit_clean_speed_limits(speed_limit, mapping_speeds):
    if speed_limit not in expected_speeds:
        if speed_limit in mapping_speeds.keys():
            speed_limit = mapping_speeds[speed_limit]
        else:
            speed_limit = ""
    return speed_limit      
        
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        for node in NODE_FIELDS:
            try:
                node_attribs[node] = element.attrib[node]
            except:
                # see what the issue is, remove when done
                #print(node)
                # -> it seems that some 'node' elements do not have a 'user' and 'uid' attribute
                # to resolve issue -> if the attribute doesn't exist, fill it with something
                node_attribs[node] = '000'
                     
    elif element.tag == 'way':
        for way in WAY_FIELDS:
            way_attribs[way] = element.attrib[way]
   
    count = 0  
    for child in element:
        if child.tag == 'tag':
            tag = {}
            match = LOWER_COLON.search(child.attrib['k'])    
            problem = PROBLEMCHARS.search(child.attrib['k'])
                           
            if problem:
                continue
            elif match:
                tag['id'] = element.attrib['id']
                tag['value'] = child.attrib['v']
                #cleaning street names
                if child.attrib['k'] == 'addr:street':
                    tag['value'] = audit_street_type(child.attrib['v'], mapping)  
                match_clear = child.attrib['k'].split(":", 1)
                tag['type'] = match_clear[0]
                tag['key'] = match_clear[1] 
                
            else:                
                tag['key'] = child.attrib['k']
                tag['type'] = 'regular'
                tag['id'] = element.attrib['id']
                tag['value'] = child.attrib['v']
                #cleaning speed limits
                if child.attrib['k'] == 'maxspeed':
                    tag['value'] = audit_clean_speed_limits(child.attrib['v'], mapping_speeds)
                      
            tags.append(tag)
        
        if child.tag == 'nd':
            way_node = {}
            way_node['id'] = element.attrib['id']
            way_node['node_id'] = child.attrib['ref']
            way_node['position'] = count
            count += 1
            
            way_nodes.append(way_node)    
        
    if element.tag == 'node':        
        return {'node': node_attribs, 'node_tags': tags}
        
    if element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS, lineterminator = '\n')
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS, lineterminator = '\n')
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS, lineterminator = '\n')
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS, lineterminator = '\n')
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS, lineterminator = '\n')

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
