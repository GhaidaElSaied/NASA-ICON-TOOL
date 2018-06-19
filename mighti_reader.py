from netCDF4 import Dataset
import numpy as np
import math
import calc_funcs

def czml_generator_mighti(filename):
  mightidata = Dataset(filename, "r")
  type = filename.split("_")[2].split("-")[1]

  time = mightidata.variables["ICON_ANCILLARY_MIGHTI_TIME_UTC_STRING"]
  #determine orientation of MIGTHI instrument
  azimuth  = mightidata.variables["ICON_ANCILLARY_MIGHTI_FOV_AZIMUTH"]
  #determine position of spacecraft
  lat = mightidata.variables["ICON_ANCILLARY_MIGHTI_LATITUDE"]
  lon = mightidata.variables["ICON_ANCILLARY_MIGHTI_LONGITUDE"]
  alt = mightidata.variables["ICON_ANCILLARY_MIGHTI_ALTITUDE"]

  position_list = calc_funcs.positions(lat, lon, alt, time)
  orientation_list = calc_funcs.orientation_to_unit_quaternion(azimuth, 0, time)
  start_file = """[{"version": "1.0", "id": "document"},
		{"interpolationDegree": 5,
		"referenceFrame": "INERTIAL",
		"id" : "mighti",
		"name" : "MIGHTI-""" + type + """FOV\"
		"cylinder" : {
			"length" : 1000000.0,
			"topRadius" : 0.0,
			"bottomRadius" : 500000.0,
			"material" : {
				"solidColor" : {
					"color" : {
						"rgba" : [0, 255, 0, 128]
					}
				}
			},
			"outline" : true,
			"outlineColor" : {
				"rgba" : [0, 0, 0, 255]
			}
		},
		"position": {
			"cartographicDegrees":"""
  middle_file = """,
			"interpolationAlgorithm": "LAGRANGE"
		},
		"orientation": {
			"interpolationAlgorithm":"LINEAR",
			"interpolationDegree":1,
			"unitQuaternion":"""
  end_file = '}}]'
  file_complete = start_file + str(position_list).replace("'", '') + middle_file + str(orientation_list).replace("'",'')+ end_file

  f.write(file_complete)
  f.close()

   
  return "file written for" + filename
