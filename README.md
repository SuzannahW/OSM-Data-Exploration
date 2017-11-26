# OSM-Data-Exploration

This project is an exploration of OpenStreetMap data covering the Oxfordshire area.

The map extract explored was a Mapzen custom extract and can be downloaded via the following link:
https://mapzen.com/data/metro-extracts/your-extracts/bc9033c1da03The 

The project write-up can be found in the file **OSM Data report.md**

This repository also contians a number of other files which were created as part of this project:

1. Python code used in auditing and cleaning the dataset:
    - **fixing_street_names_submission.py** -> For auditing street names
    - **auditing_speed_limits_submission.py** -> For auditing speed limits
    - **Cleaning_and_loading_to_csv_submission.py** -> For cleaning and converting the data to a csv file


2. Sample_OSM_file.osm -> this is a .osm file containing a sample part of the map region used.

### References

To help complete this project, the following were referred to:

  - A huge number of Udacity discussion forums, for example: https://discussions.udacity.com/t/use-update-name-in-shape-element-function-for-project/284766/2, https://discussions.udacity.com/t/creating-db-file-from-csv-files-with-non-ascii-unicode-characters/174958/7, https://discussions.udacity.com/t/upload-csv-to-sqlite-you-must-not-use-8-bit-bytestrings-unless-you-use-a-text-factory/201236/2
  - For help with regex - https://docs.python.org/2/library/re.html
  - For help with SQL - https://www.w3schools.com/SQL/default.asp
  - For general help with how to set the project out, I referred to the sample project given as an example on the Udacity website, https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md
  
