from netCDF4 import Dataset
import numpy as np
import calc_funcs

def czml_generator_euv(filename):
	euvdata = Dataset(filename,"r" )

	time = euvdata.variables["ICON_ANCILLARY_EUV_TIME_UTC_STRING"]

	# spacecraft position determines EUV FOV start position
	lat = euvdata.variables["ICON_ANCILLARY_EUV_LATITUDE"]
	lon = euvdata.variables["ICON_ANCILLARY_EUV_LONGITUDE"]
	alt = euvdata.variables["ICON_ANCILLARY_EUV_ALTITUDE"]

	azimuth = euvdata.variables["ICON_ANCILLARY_EUV_FOV_AZIMUTH_ANGLE"][:, ].tolist()
	zenith = euvdata.variables["ICON_ANCILLARY_EUV_FOV_ZENITH_ANGLE"].[:, ]tolist()

	position_list = calc_funcs.positions(lat, lon, alt, time)
	azimuth, zenith, time_orient = calc_funcs.euv_check_values(azimuth, zenith, time[:].tolist())
	orientation_list = calc_funcs.euv_orientations_calc(azimuth, zenith, time_orient)

	start_file = """[{"version": "1.0", "id": "document"},
  		{"interpolationDegree": 5,
  		"referenceFrame": "INERTIAL",
  		"id" : "uv",
		"interpolationDegree" : 5,
		"referenceFrame" : "INERTIAL",
		"id" : "model",
		"name" : """ + type + "UV FOV"""",
		"availability" : """ + time_str + """,
		"model" : {
			"show" : true,
			"gltf" : "EUV_FOV.GLTF",
    		"scale": 150000000.0,
    		"silhouetteColor" : {
        		"rgba" : [255, 0, 0, 255]
				}
        		"color" : {
                		"rgba" : [255, 0, 0, 255]
            		}
        		}
    		}
		},
		"position" : {
			"cartographicDegrees" : """
	middle_file = """, "interpolationAlgorithm": "LAGRANGE"},
	"orientation": {
		"interpolationAlgorithm": "LINEAR",
		"interpolationDegree": 1,
		"unitQuaternion": """
	end_file = """}}]"""
	file_complete = start_file + str(position_list).replace("'",'') + middle_file + str(orientation_list).replace("'",'') + end_file
	f = open(filename[: -3] + '.txt', "w+")
	f.write(file_complete)
	f.close();
	return "file written for " + filename[:-3]
euvdata = Dataset("ICON_L0P_EUV_Ancillary_2017-05-27_v01r001.NC", "r")
azimuth = euvdata.variables["ICON_ANCILLARY_EUV_FOV_AZIMUTH_ANGLE"]
zenith = euvdata.variables["ICON_ANCILLARY_EUV_FOV_ZENITH_ANGLE"]
time = euvdata.variables["ICON_ANCILLARY_EUV_TIME_UTC_STRING"]
