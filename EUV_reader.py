
from netCDF4 import Dataset
from netCDF4 import ecef_to_enu
from calc_funcs import convert_time_format, orientations, positions

def czm_generator_euv(filename):
	euvdata = Dataset(filename,"r" )

	icon_x_hat = euvdata.variables["ICON_ANCILLARY_EUV_SC_XHAT"]
	icon_y_hat = euvdata.variables["ICON_ANCILLARY_EUV_SC_YHAT"]
	icon_z_hat = euvdata.variables["ICON_ANCILLARY_EUV_SC_ZHAT"]
	
	time = euvdata.variables["ICON_ANCILLARY_EUV_TIME_UTC_STRING"]
	
	# spacecraft position determines EUV FOV start position
	lat = euvdata.variables["ICON_ANCILLARY_EUV_LATITUDE"]
	lon = euvdata.variables["ICON_ANCILLARY_EUV_LONGITUDE"]
	alt = euvdata.variables["ICON_ANCILLARY_EUV_ALTITUDE"]

	unit_vector_vertical = euvdata.variables["ICON_ANCILLARY_EUV_FOV_UNITVECTORS_ECEF"]
   	
	vertical = vertical_time(unit_vector_vertical)

	position_list = positions(lat, lon, alt, time)
	orientation_list = orientations(icon_x_hat, icon_y_hat, icon_z_hat, time)

   	start_file = """[
	{"id" : "document",
	"name" : "EUV",
	"version" : "1.0",
	},
	{"id" : "cone",
	"availability" : "2012-08-04T16:00:00Z/2012-08-04T16:05:00Z"
	"position" : {
		"epoch" : "",
		"cartographicDegrees" :"""
    	middle_file =', "interpolationAlgorithm": "LAGRANGE"},"orientation":{"interpolationAlgorithm":"LINEAR", "interpolationDegree":1, "unitQuaternion":'
    	end_file = '}]'

    	start_file + str(position_list).replace("'",'') + middle_file + str(orientation_list).replace("'",'') + end_file
    	f = open(filename[: -3] + '.txt', "w+")
    	f.write(file_complete)
    	f.close();
    	return "file written for " + filename[:-3]

# orientations should be recalculated based on where the EUV is looking
def orientations():

# match all vertical positions
def vertical_time(matrix):
    	time_vertical_matrix = []
    	for i in range(len(matrix)):
        	time_vertical_matrix += list(map(list, list(zip(matrix[i][1], matrix[i][2]))))
    	return time_vertical_matrix
