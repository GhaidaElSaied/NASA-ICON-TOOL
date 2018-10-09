from netCDF4 import Dataset
import calc_funcs

def czml_generator_mighti(filename):
  mightidata = Dataset(filename, "r")
  type = filename.split("_")[2].split("-")[1]
  #read position of spacecraft in longitude, latitude, altitude
  lat = mightidata.variables["ICON_ANCILLARY_MIGHTI_LATITUDE"][:, 1]
  lon = mightidata.variables["ICON_ANCILLARY_MIGHTI_LONGITUDE"][:, 1]
  alt = mightidata.variables["ICON_ANCILLARY_MIGHTI_ALTITUDE"][:, 1]
  time = mightidata.variables["ICON_ANCILLARY_MIGHTI_TIME_UTC_STRING"][:, 1]
  position_list = calc_funcs.positions(lat, lon, alt, time)
  #read orientation of spacecraft in ECEF
  mighti_fov = mightidata.variables["ICON_ANCILLARY_MIGHTI_FOV_UNITVECTORS_ECEF"]
  #extract vectors for four corners
  bottom_left_vectors = mighti_fov[:,1, :, 0, 0].tolist()
  bottom_right_vectors = mighti_fov[:,1, :, 0, 2].tolist()
  top_right_vectors = mighti_fov[:,1, :, 2, 2].tolist()
  top_left_vectors = mighti_fov[:,1, :, 2, 0].tolist()
  b_l_vectors, b_r_vectors, t_r_vectors, t_l_vectors, time_orient = calc_funcs.mighti_check_values(bottom_left_vectors, bottom_right_vectors, top_right_vectors, top_left_vectors, time.tolist())

  orientation_list = calc_funcs.mighti_orientation_calc(b_l_vectors, b_r_vectors, t_r_vectors, t_l_vectors, time_orient)


  # start_file = """[{"version": "1.0", "id": "document"},
	# 	{"interpolationDegree": 5,
	# 	"referenceFrame": "INERTIAL",
	# 	"id" : "mighti",
	# 	"name" : "MIGHTI-""" + type + """FOV\"
	# 	"model" : {
	# 		"gltf": "Models/mighti.gltf",
  #           "color" : "black",
  #           "silhouetteColor": "black",
  #           "scale" : "50000000",
  #           }
	# 	},
	# 	"position": {
	# 		"cartographicDegrees":"""
  #
  # middle_file = """,
	# 		"interpolationAlgorithm": "LAGRANGE"
	# 	},
	# 	"orientation": {
	# 		"interpolationAlgorithm":"LINEAR",
	# 		"interpolationDegree":1,
	# 		"unitQuaternion":"""
  # end_file = '}}]'
  #
  # file_complete = start_file + str(position_list).replace("'", '') + middle_file + str(orientation_list).replace("'",'')+ end_file
  # f = open(filename[:-3] + '.txt', "w+")
  # f.write(file_complete)
  # f.close()


  return orientation_list, lat, lon, alt

a, b, c, d = czml_generator_mighti("ICON_L0P_MIGHTI-A_Ancillary_2017-05-27_v01r001.NC")
