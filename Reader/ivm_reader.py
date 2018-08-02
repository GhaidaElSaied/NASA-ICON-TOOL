from netCDF4 import Dataset
import math
import numpy as np
import calc_funcs

def czml_generator_ivm(filename):
	""" Writes a czml file with the orientation and posistion data for the cone defined by the field of view of the IVM"""
	fovdata = Dataset(filename,"r")
	type = filename.split("_")[2].split("-")[1]
	#extract ivma fov unit vectors
	ivma_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"][:, ]
	ivma_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"][:, ]
	ivma_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"][:, ]
	#convert ivma fov unit vectors to ivmb fov unit vectors
	sc_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_SC_XHAT_ECEF"][:].tolist()
	ivmb_x_hat, ivmb_y_hat = calc_funcs.rotate_for_ivmb(ivma_x_hat, ivma_y_hat)

	time = fovdata.variables["ICON_ANCILLARY_IVM_TIME_UTC"]
	lat = fovdata.variables["ICON_ANCILLARY_IVM_LATITUDE"]
	lon = fovdata.variables["ICON_ANCILLARY_IVM_LONGITUDE"]
	alt = fovdata.variables["ICON_ANCILLARY_IVM_ALTITUDE"]
	position_list = calc_funcs.positions(lat,lon,alt,time)
	ivma_orientations = calc_funcs.FOV_ivm_orientations(ivma_x_hat, ivma_y_hat, ivma_z_hat, time)
	ivmb_orientations = calc_funcs.orientations(ivmb_x_hat, ivmb_y_hat, ivma_z_hat, time)


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
	ivma_file = """[{"version": "1.0", "id": "document"},
		{"interpolationDegree": 5,
		"referenceFrame": "INERTIAL",
		"id" : "ivma",
		"name" : "IVM-AFOV",
		"model" : {
			"show" : true,
			"gltf" : "cone.gltf",
			"scale" : 50000000.0,
			"silhouetteColor" : {
				"rgba" : [0, 0, 0, 255]
			},
			"color": {
			 	"rgba" : [0, 255, 0, 128]
			}
		},
		"position": {
			"cartographicDegrees":"""
	ivmb_file = """[{"version": "1.0", "id": "document"},
		{"interpolationDegree": 5,
		"referenceFrame": "INERTIAL",
		"id" : "ivma",
		"name" : "IVM-AFOV",
		"model" : {
			"show" : true,
			"gltf" : "cone.gltf",
			"scale" : "50000000.0",
			"silhouetteColor" : {
				"rgba" : [0, 0, 0, 255]
			},
			"color": {
			 	"rgba" : [0, 255, 0, 128]
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
	ivma_orientation_str = str(ivma_orientations).replace("'", '')
	ivmb_orientation_str = str(ivmb_orientations).replace("'", '')
	ivma_file_complete = ivma_file + position_str + middle_file + ivma_orientation_str + end_file
	ivmb_file_complete = ivmb_file + position_str + middle_file + ivmb_orientation_str + end_file
	label_file = label_start + position_str + end_file
	path_file = path_start + position_str + end_file

	f_a = open(filename[:-3] + '.txt', "w+")
	f_b = open(filename[:-3] + 'B' + '.txt', "w+")
	#label_f = open("label.txt", "w+")
	#path_f = open("path.txt", "w+")

	f_a.write(ivma_file_complete);
	f_b.write(ivmb_file_complete)
	#label_f.write(label_file)
	#path_f.write(path_file)

	f_a.close()
	f_b.close()
	#label_f.close()
	#path_f.close()

	return "files written for " + filename[:-2]
#czml_generator_ivm("ICON_L0P_IVM-A_Ancillary_2017-05-27_v01r001.NC")
#czml_generator_ivm("ICON_L0P_IVM-A_Ancillary_2017-05-28_v01r001.NC")
#czml_generator_ivm("ICON_L0P_IVM-A_Ancillary_2017-05-29_v01r001.NC")


ivma_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"][:, ]
ivma_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"][:, ]
ivma_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"][:, ]
