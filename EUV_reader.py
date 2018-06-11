from netCDF4 import Dataset
from calc_funcs import convert_time_format, EUV_to_unit_quaternion

def czml_generator_euv(filename):
	euvdata = Dataset(filename,"r" )

	icon_x_hat = euvdata.variables["ICON_ANCILLARY_EUV_SC_XHAT"]
	icon_y_hat = euvdata.variables["ICON_ANCILLARY_EUV_SC_YHAT"]
	icon_z_hat = euvdata.variables["ICON_ANCILLARY_EUV_SC_ZHAT"]

	time = euvdata.variables["ICON_ANCILLARY_EUV_TIME_UTC_STRING"]

	# spacecraft position determines EUV FOV start position
	lat = euvdata.variables["ICON_ANCILLARY_EUV_LATITUDE"]
	lon = euvdata.variables["ICON_ANCILLARY_EUV_LONGITUDE"]
	alt = euvdata.variables["ICON_ANCILLARY_EUV_ALTITUDE"]

	azimuth = euvdata.variables["ICON_ANCILLARY_EUV_FOV_AZIMUTH_ANGLE"] # 'latitude'
	zenith = euvdata.variables["ICON_ANCILLARY_EUV_FOV_ZENITH_ANGLE"] # 'longitude'

	position_list = positions(lat, lon, alt, time)
	orientation_list = orientations(azimuth, zenith)
	time_str = time_string(time[0], time[len(time) - 1])
	print(time_str)
	start_file = """[{
	"id" : "document",
	"name" : "EUV",
	"version" : "1.0",
	"cylinder" : {
		"id" : "cone",
		"name" : "EUV FOV",
		"length" : 400000.0,
    	"topRadius" : 0.0,
    	"bottomRadius" : 200000.0,
    	"material" : {
        	"solidColor" : {
            	"color" : {
                	"rgba" : [255, 0, 0, 255]
            	}
        	}
    	},
		"availability" : """ + time_str + """,
		"position" : {
		"interpolationDegree" : 5,
		"referenceFrame" : "INERTIAL",
		"cartographicDegrees" : """
	middle_file = """,
	"interpolationAlgorithm": "LAGRANGE"},
	"orientation": {
		"interpolationAlgorithm":"LINEAR",
		"interpolationDegree": 1,
		"unitQuaternion": """
	end_file = """}}}]"""
	file_complete = start_file + str(position_list).replace("'",'') + middle_file + str(orientation_list).replace("'",'') + end_file
	f = open(filename[: -3] + '.txt', "w+")
	f.write(file_complete)
	f.close();
	return "file written for " + filename[:-3]

# orientations should be recalculated based on where the EUV is looking
def orientations(azimuth, zenith):
	orients = []
	for pair in map(list, zip(azimuth, zenith)):
		orients += EUV_to_unit_quaternion(pair[0].data.item(0), pair[1].data.item(0))
	return orients

# match all times to azimuth & zenith ranges
def fov_range_time(time, azimuth, zenith, rad_dist):
    time_fov_match_matrix = zip(convert_time_format(time) , [[min(i), max(i)] for i in azimuth], [[min(i), max(i)] for i in zenith], rad_dist)
    return time_fov_match_matrix

def positions(lat,lon,alt,time):
	"""Outputs a list with the positions of the satellite by time when given the lat,lon,alt,time variables from a netcdf file. """
	positions = []
	for i in range(len(lat)):
		positions += [convert_time_format(time[i]),lon[i].data.item(0),lat[i].data.item(0),(alt[i].data * 1000)]
	return positions

def time_string(start_time, end_time):
	"""Converts time stamps from the netCDF to the form for czml "2018-02-09T00:00:00+00:00"""
	start_time_string = start_time[0:10] + "T" + start_time[11:19] +"+00:00"
	end_time_string = end_time[0:10] + "T" + end_time[11:19] +"+00:00"
	return ('"%s/%s"' % (start_time_string, end_time_string))
