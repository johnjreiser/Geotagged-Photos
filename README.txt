Scripts for Geotagged Photographs
author: John Reiser <jreiser@njgeo.org>

This toolkit contains scripts to help you deal with processing a directory of geotagged
(JPG photographs containing GPS information within the Exif metadata) and producing GIS-
ready data, enabling you to produce maps of the photographs' locations. 

Currently, there is one script in this project that requires ArcGIS Desktop (9.3 or later)
and there are plans to include additional scripts that work with open source software to 
prepare data in GeoJSON, KML and ESRI Shapefile. The .tbx file included in the project is
an ArcToolbox file that is pre-configured to use the included script.

The scripts require PIL, the Python Imaging Library, which is available from:
http://www.pythonware.com/products/pil/
Please make sure you download & install the correct PIL version for your version of
Python. (ArcGIS 9.3/9.3.1 users will have Python 2.5 installed, 10 will have 2.6, and 10.1
will have 2.7.)

Please email the author with any questions. 
John Reiser
6 February 2013
