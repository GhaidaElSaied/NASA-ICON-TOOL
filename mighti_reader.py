from netCDF4 import Dataset
import numpy as np
import math
import calc-funcs

def czml_generator_mighti(filename):
  mightidata = Dataset(filename, "r")

  time = mightidata.variables["ICON_ANCILLARY_MIGHTI_TIME_UTC_STRING"]
  #determine orientation of spacecraft
  instra_x_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_INSTRA_X_ECEF"]
  instra_y_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_INSTRA_Y_ECEF"]
  instra_z_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_INSTRA_Z_ECEF"]
  
  #determine position of spacecraft
  lat = mightidata.variables["ICON_ANCILLARY_MIGHTI_LATITUDE"]
  lon = mightidata.variables["ICON_ANCILLARY_MIGHTI_LONGITUDE"]
  alt = mightidata.variables["ICON_ANCILLARY_MIGHTI_ALTITUDE"]

  position_list = calc-funcs.positions(lat, lon, alt, time)
  orientation_list = calc-funcs.orientations(instra_x_hat, instra_y_hat, instra_z_hat, time)

  label_start = """[{"version": "1.0", "id": "document"}, {"label":
		{"text": "ICON",
		"pixelOffset": {
			"cartesian2": [0.0, 16.0]},
			"scale": 0.5,
			"show": true
		}, "position" : {
			"cartographicDegrees" :
	"""
   path_start = """[{"version": "1.0", "id": "document"}, {
		"id" : "orbitPath",
		"path": {
				"show" : true,
				"width": 2,
				"trailTime": 0,
				"resolution": 120,
				"leadTime": 0,
				"trailTime": 10000,
				"material": {
					"solidColor": {
						"color": {
							"rgba": [255, 0, 255, 125]
						}
					}
				}
			},
				"position": {
					"cartographicDegrees" :"""
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
  label_file = label_start + position_str + end_file
  path_file = path_start + position_str + end_file
  label_f = open("label.txt", "w+")
  path_f = open("path.txt", "w+")
  f.write(file_complete)
  label_f.write(label_file)
  path_f.write(path_file)
  f.close()
  label_f.close()
  path_f.write()
  
  return "file written for" + filename
