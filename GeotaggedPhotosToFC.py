#!/usr/bin/env python
#
# GeocodedPhotosToFC.py
# version: 1.0 (2010 May 28)
# author: John Reiser <reiser@rowan.edu>
#
# Script takes three arguments, a directory of JPGs with GPS EXIF tags,
# an output workspace, and an output feature class (gdb or shp). 
# An ArcToolbox file has been included to make using this script easier.
#
# Requires the Python Imaging Library (PIL)
# freely available at http://www.pythonware.com/products/pil/
#
# Feel free to contact the author with questions or comments.
# Any feedback or info on how this is being used is greatly appreciated.
#
# Copyright (C) 2010, John Reiser
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import arcgisscripting, sys, os, string
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    try:
        info = i._getexif()
        for t, v in info.items():
            try:
                decoded = TAGS.get(t, t)
                ret[decoded] = v
            except:
                pass
        if "GPSInfo" in ret:
            return ret["GPSInfo"]
    except:
        return {}

# EXIF GPS TAGS
# 1: Latitude N/S
# 2: Latitude coordinates
# 3: Longitude E/W
# 4: Longitude coordinates
# 8: Number of satellites
# 18: Datum

def process_gps(tags):
    gps = {}
    if (1 in tags) and (not tags[1] == "\x00"): # 1 and 3 are not present if the coords keys are not present and will be null if no coords
        gps["y"] = dmsdec(tags[2][0][0], tags[2][0][1], tags[2][1][0], tags[2][1][1], tags[2][2][0], tags[2][2][1], tags[1])
        gps["x"] = dmsdec(tags[4][0][0], tags[4][0][1], tags[4][1][0], tags[4][1][1], tags[4][2][0], tags[4][2][1], tags[3])
        print gps
    return gps

def dmsdec(dn, dd, mn, md, sn, sd, o="N"):
    degree = float(dn)/float(dd)
    minute = float(mn)/float(md)/60
    second = float(sn)/float(sd)/3600
    coord = degree + minute + second
    if(o == "S" or o == "W"):
        coord = coord * -1
    return coord


gp = arcgisscripting.create(9.3)
if len(sys.argv) < 4:
    gp.AddError("Insufficient arguments.")
    print "Usage:", os.path.basename(sys.argv[0]), "path_to_directory", "output_workspace", "output_feature_class"
    sys.exit()

lenname = 0 # variables for the longest file name
lenpath = 0 # and longest path name

if os.path.exists(sys.argv[1]):
    files = []
    gp.SetProgressor("default", "Examining Photos...")
    for f in os.listdir(sys.argv[1]):
        if len(f) > lenname:
            lenname = len(f)        
        if os.path.splitext(f)[1].lower() == ".jpg":
            fp = os.path.join(sys.argv[1], f)
            if len(fp) > lenpath:
                lenpath = len(fp)
            gpsinfo = process_gps(get_exif(fp))
            if not len(gpsinfo) == 0:
                gpsinfo["name"] = f
                gpsinfo["path"] = fp
                files.append(gpsinfo)
            else:
                gp.AddWarning(f+" has no GPS infomation.")
                
gp.SetProgressor("default", "Creating point feature class...")

# Create the new feature class
gp.CreateFeatureclass_management(sys.argv[2], sys.argv[3], "POINT", "", "DISABLED", "DISABLED", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];IsHighPrecision", "", "0", "0", "0")

# Create the new fields
# Name field
gp.AddField_management(os.path.join(sys.argv[2], sys.argv[3]), "NAME", "TEXT", "", "", str(lenname), "Photo Filename", "NULLABLE", "NON_REQUIRED", "")
# Path field
gp.AddField_management(os.path.join(sys.argv[2], sys.argv[3]), "PATH", "TEXT", "", "", str(lenpath), "Photo Pathname", "NULLABLE", "NON_REQUIRED", "")

# Stuff the points into the new feature class
descript = gp.Describe(os.path.join(sys.argv[2], sys.argv[3]))
sfn = descript.ShapeFieldName

rows = gp.InsertCursor(os.path.join(sys.argv[2], sys.argv[3]))
gp.SetProgressor("step", "Writing points...", 0, len(files), 1)
for f in files:
    row = rows.NewRow()
    row.NAME = f["name"]
    row.PATH = f["path"]
    pnt = gp.CreateObject("Point")
    pnt.x = f["x"]
    pnt.y = f["y"]
    row.SetValue(sfn, pnt)
    rows.InsertRow(row)
    gp.SetProgressorPosition()
    
