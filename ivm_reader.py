from netCDF4 import Dataset
import math, import numpy as np, import calc_funcs

def czml_generator_ivm(filename):
	""" Writes a czml file with the orientation and posistion data for the cone defined by the field of view of the IVM"""
	fovdata = Dataset(filename,"r")
	type = filename.split("_")[2].split("-")[1]

	instra_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"]
	instra_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"]
	instra_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"]

	time = fovdata.variables["ICON_ANCILLARY_IVM_TIME_UTC"]
	lat = fovdata.variables["ICON_ANCILLARY_IVM_LATITUDE"]
	lon = fovdata.variables["ICON_ANCILLARY_IVM_LONGITUDE"]
	alt = fovdata.variables["ICON_ANCILLARY_IVM_ALTITUDE"]
	ivmb_x, ivmb_y, ivmb_z = rotate_ivm_fov(instra_x_hat, instra_y_hat, instra_z_hat)
	
	position_list = calc_funcs.positions(lat,lon,alt,time)
	ivma_orientation_list = calc_funcs.orientations(instra_x_hat,instra_y_hat,instra_z_hat,time)
	ivmb_orientation_list = calc_funcs.orientatins(ivmb_x, ivmb_y, ivmb_z, time)

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
		"id" : "ivma",
		"name" : "IVM-""" + type + """FOV\"
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

	position_str = str(position_list).replace("'",'')
	orientation_str = str(orientation_list).replace("'",'')

	file_complete = start_file + position_str + middle_file + orientation_str + end_file
	label_file = label_start + position_str + end_file
	path_file = path_start + position_str + end_file

	f = open(filename[:-3] + '.txt', "w+")
	label_f = open("label.txt", "w+")
	path_f = open("path.txt", "w+")

	f.write(file_complete);
	label_f.write(label_file)
	path_f.write(path_file)

	f.close()
	label_f.close()
	path_f.close()

	return "files written for " + filename[:-2]

def positions(lat,lon,alt,time):
	"""Outputs a list with the positions of the satellite by time when given the lat,lon,alt,time variables from a netcdf file. """
	positions = []
	for i in range(len(lat)):
		position = convert_time_format(time[i]), lon[i].data.item(0), lat[i].data.item(0),(alt[i] * 1000)
		positions += position
	return positions

def convert_time_format(time):
	"""Converts time stamps from the netCDF to the form for czml "2018-02-09T00:00:00+00:00"""
	time_string = time[0:10] + "T" + time[11:19] +"+00:00"
	return ('"%s"' % time_string)



