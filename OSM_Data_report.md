
# OpenStreetMap Data Case Study

## Map Area
-----
Oxfordshire, United Kingdom

The map data I explored was found via a Mapzen custom extract and can be downloaded via the following link:

https://mapzen.com/data/metro-extracts/your-extracts/bc9033c1da03

I studied in Oxford and in the end lived there for 8 years. I know the city quite well and I was interested to see what could be found by looking through the data.

## Problems Encountered in the Map
-----

### 1) Street names

Some of the problems encountered were due to inconsistencies in the street naming methods used, for example the abbreviations used for different street types ("St." *vs* "St" *vs* "Street"). There were also a number of streets with the prefix "Saint" or "St" (in this dataset examples include "St Aldate's", "St Clement's Street" and "St Giles"). These streets were also inconsistent in their use of apostrophes ("St Giles" *vs.* "St Giles'" and "St Aldates" *vs* "St Aldate's")

Whilst cleaning the data to correct for inconsistent street types I found that many street names do not have a 'type' (such as Street, Avenue or Lane) but instead are either just one word, the street name itself, or have the form "The *name*". Examples of such cases found in this dataset include "Larkhill", "Hillside" and "The Causeway". I am not sure how common street names of this type are worldwide, but this is a relatively common occurance in the UK.

Lastly, there were a handful of cases where the street name also included the town name, or a house number, or was just anamalous (e.g. '111'). These were cleaned easy enough on a case-by-case basis.

### 2) Speed limits

Other than the expected inconsistencies with the formatting of the units and data input, whilst auditing this data I found that a number of the speed limits recorded were actually above the national speed limit of 70 mph. It is possible that some of these values could have been mistakenly input as the speed limit in kilometers, however, some values were too high for this to be the case. Without collecting this raw data myself it was impossible to correct for these anomalous data points and so this data had to be ignored.


## Correcting the Street Names
-----

Regular expressions were used to correct for inconsistent street types, in doing so I opted to use non-abbreviated street types throughout. Regular expressions were also used to convert all instances of "Saint" to the more common 'St'. Direct mapping was used to account for misplaced commas, a forgotten 'Street' and the removal of misplaced town names and house numbers.

During initial auditing (before using the finished function to convert the osm data to a csv file) a third regular expression was used to determine whether the street name was of the type 'The *name*', the use of which ensured that streets of this type were not added to the street_types dictionary.

The following function was used to carry out these corrections:

```python
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
```

In this function, the regular expressions 'street_type_re', 'The_street_re' and 'Saint_street_re' are defined by:

```python
street_type_re = re.compile(r'\s\b\S+\.?$', re.IGNORECASE)
The_street_re = re.compile(r'^The', re.IGNORECASE)
Saint_street_re = re.compile(r'^Saint', re.IGNORECASE)
```

## Auditing Speed Limits
-----
The following code uses a mapping process to correct for inconsistent data input, and then counts the number of occurances of each speed limit. The result is a 'speed_limits' dictionary containing a count of speed limit values that are consistent with the law of British roads and an 'unexpected_speed_limits' dictionary, which includes counts of all the other values found. 

```python
def states_speed_limit(element):
    return (element.attrib['k']=='maxspeed')

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

def auditing_speed_limits():
    for event, element in ET.iterparse(osm_file, events=('start',)):
        if element.tag == 'way':
            for tag in element.iter('tag'):
                if states_speed_limit(tag):
                    cleaning_speed_limits(tag.attrib['v'], mapping)
    pprint.pprint(dict(speed_limits))
    pprint.pprint(dict(unexpected_speed_limits))
    return tag
```

The final contents of each dictionary was as follows:

```python
speed_limits = {'10 mph': 47,
                '15 mph': 15,
                '20 mph': 2450,
                '25 mph': 42,
                '30 mph': 1475,
                '40 mph': 330,
                '5 mph': 29,
                '50 mph': 261,
                '60 mph': 191,
                '70 mph': 322}
 
unexpected_speed_limits = {'100 mph': 12,
                           '113':     1,
                           '121':     3,
                           '125 mph': 26,
                           '145':     3,
                           '201':     8,
                           '75 mph':  20,
                           '80':      1,
                           '90 mph':  36,
                           'none':    9}
```

Ignoring the data in the unexpected_speed_limits dictionary, it seems that 48% of the roads in Oxford have a 20 mph speed limit. This is far higher than the national average, where a 30 mph speed limit usually applies.

## Data Overview
-----

### File sizes
The sizes of the files relevant to this report are as follows:

```python
Oxfordshire.osm........112 MB
Oxfordshire.db.........64 MB
nodes.csv..............40 MB
nodes_tags.csv.........2.5 MB
ways.csv...............4.5 MB
ways_nodes.csv.........16 MB
ways_tags.csv..........7.5 MB
```



### SQL queries
SQL queries were used to gather various data and statistics from the dataset, as described below.

#### Number of nodes

```SQL
SELECT COUNT (*) FROM nodes;
```
500947

#### Number of ways

```SQL
SELECT COUNT (*) FROM ways;
```
78808

#### Number of distinct users

##### Distinct users contributing to nodes

```SQL
SELECT COUNT(DISTINCT uid) as num       
FROM nodes;
```
735

##### Distinct users contributing to ways
```SQL
SELECT COUNT(DISTINCT uid) as num       
FROM ways;
```
676

##### Total number of unique users contributing to Oxfordshire.osm
```SQL
SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
881

The total number of unique users is not that much higher than the number of unique user contributions for nodes or ways alone. This indictates that most users contribute to both types of data rather than favouring only one.

#### Top 10 appearing amenities

```SQL
SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```
```python
bicycle_parking    512
post_box           472
bench              284
telephone          192
pub                157
restaurant         139
cafe               113
parking            100
fast_food          91
place_of_worship   72
```

#### Top 10 appearing highway types

```SQL
SELECT value, COUNT(*) as num
FROM ways_tags
WHERE key='highway'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```
```python
footway            7459
service            5549
residential        5424
unclassified       1146
track              1143
cycleway           1083
tertiary           914
path               836
primary            660
secondary          498
```

#### Top 10 appearing shops

```SQL
SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='shop'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```
```python
convenience        96
clothes            64
hairdresser        49
supermarket        33
car_repair         17
bicycle            16
estate_agent       14
newsagent          13
mobile_phone       12
beauty             11
```

## Additional Ideas and SQL queries
-----
The results for the top 10 appearing amenities, highway types and shops all include a result related to bicycle use, in fact the highest occuring amenity overall was bicycle parking.

Oxford is well known for being a cycling city and the number of people who opt to cycle around Oxford City is much higher than the UK average. According to a report published by We Are Cycling UK, 18.8% of the population of Oxford and 8.9% of the population of Oxfordshire cycle 3 or more times a week, compared to an average of 7% for the UK population as a whole (the report can be found via this link: http://www.cyclinguk.org/resources/cycling-uk-cycling-statistics). 

I thought it would be interesting to look at these results in relation to the fact that such a high proportion of roads in Oxfordshire have a 20 mph speed limit. 

```SQL
SELECT ways_tags.value, COUNT(*) as num
FROM ways_tags 
    JOIN (SELECT DISTINCT(id) FROM ways_tags WHERE key='highway' and value='cycleway') i
    ON ways_tags.id=i.id
WHERE ways_tags.key='maxspeed'
GROUP BY ways_tags.value
ORDER BY num DESC;
```
```python
20 mph                20
```
It seems that only a small number of roads designated as cycleways have a 20 mph speed limit (although, on the other hand, all designated cycleways do) so I wondered what else could be going on to account for such a large number of 20 mph speed limited roads.

```SQL
SELECT ways_tags.value, COUNT(*) as num
FROM ways_tags 
    JOIN (SELECT DISTINCT(id) FROM ways_tags WHERE key='maxspeed' and value='20 mph') i
    ON ways_tags.id=i.id
WHERE ways_tags.key = 'note' and ways_tags.type='maxspeed'
GROUP BY ways_tags.value
ORDER BY num DESC;
```
```python
Oxford 20 mph zone    2332
Oxford 20mph zone     2
```

The result above could be neatened up with a small amount of data cleaning (mapping "Oxford 20mph zone" to "Oxford 20 mph zone" would do the trick) but this result is clear enough to provide us with some useful information. It seems that Oxford has employed a city 20 mph zone. Some 2334 of the 2450 designated 20 mph roads can be attributed to this zone.

```SQL
SELECT ways_tags.value, COUNT(*) as num
FROM ways_tags 
    JOIN (SELECT DISTINCT(id) FROM ways_tags WHERE key='note' and value='Oxford 20 mph zone') i
    ON ways_tags.id=i.id
WHERE ways_tags.key = 'highway' and ways_tags.type='regular'
GROUP BY ways_tags.value
ORDER BY num DESC
LIMIT 10;
```
```python
residential           1706
unclassified          182
tertiary              140
primary               88
service               87
footway               39
secondary             37
cycleway              20
pedestrian            13
primary_link          10
```
The Oxford 20 mph zone is largely focused in residential areas and, although these areas would have a large number of cyclists in line with a high proportion of the population cycling regularly, it is hard to tell from this data what the driving force for such a large 20 mph city zone was (certainly there would have been a number of factors in its introduction).

## Summary and ideas for improving this dataset
-----
This report details the process taken to clean small part of the Oxfordshire.osm data and provides an initial look at the link between the large number of 20 mph speed limited streets and the high proportion of cyclists in the area. The analysis shows that the 20 mph city zone is largely in residential areas. How often these roads are frequented by cyclists is hard to tell from this data alone, but the cleaned street names and speed limit data, could be used alongside a cycling survey to provide a heat map of the roads popular with cyclists. 

One thing that surprised me when investigating this dataset was the relatively low number of unique users which have contributed the data, only 881 users have built up the dataset consisting of 500947 nodes and 78808 ways, a mean of 658 nodes and/or ways per user. Increasing the number of users that contribute to the data could significantly improve it. One way that this could be done is to use data collected from social media, such as Facebook's 'Check-in,' feature, to double check node description and location accuracy. Ths would help add a large amount of data to the dataset, as well as provide data to cross-check existing nodes against. User privacy concerns may be an issue with this method, but ensuring that all data is anomalous would go some way to addressing this.
