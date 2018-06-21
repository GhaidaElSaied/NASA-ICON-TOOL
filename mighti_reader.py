from netCDF4 import Dataset
import calc_funcs, numpy as np

def czml_generator_mighti(filename):
  mightidata = Dataset(filename, "r")
  type = filename.split("_")[2].split("-")[1]


  time = mightidata.variables["ICON_ANCILLARY_MIGHTI_TIME_UTC_STRING"][:, 1]


  #read position of spacecraft in longitude, latitude, altitude
  lat = ["ICON_ANCILLARY_MIGHTI_LATITUDE"]
  lon = ["ICON_ANCILLARY_MIGHTI_LONGITUDE"]
  alt = ["ICON_ANCILLARY_MIGHTI_ALTITUDE"]

  #read orientation of MIGHTI instrument in ECEF
  mighti_FOV = mightidata.variables["ICON_ANCILLARY_MIGHTI_FOV_UNITVECTORS_ECEF"]
  bottom_left_x, bottom_left_y, bottom_left_z = mighti_FOV[0, 0, :][0], mighti_FOV[0, 0, :][1], mighti_FOV[0, 0, :][2]
  bottom_right_x, bottom_right_y, bottom_right_z = mighti_FOV[2, 0, :][0], mighti_FOV[2, 0, :][1], mighti_FOV[2, 0, :][2]
  top_left_x, top_left_y, top_left_z= mighti_FOV[0, 2, :][0], mighti_FOV[0, 2, :][1], mighti_FOV[0, 2, :][2]
  top_right_x, top_right_y, top_right_z= mighti_FOV[2, 2, :][0], mighti_FOV[2, 2, :][1], mighti_FOV[2, 2, :][2]

  #position of spacecraft
  position_list = calc_funcs.positions(lat, lon, alt, time)
  #unit vectors in ECEF for bottom left, bottom right, top left, top right to unit quaternions
  bottom_left = calc_funcs.orientations(bottom_left_x, bottom_left_y, bottom_left_z, time)
  bottom_right = calc_funcs.orientations(bottom_right_x, bottom_right_y, bottom_right_z, time)
  top_left = calc_funcs.orientations(top_left_x, top_left_y, top_left_z, time)
  top_right = calc_funcs.orientations(top_right_x, top_right_y, top_right_z, time)
  #puts unit quaternions for FOV into array
  orientation_list = calc_funcs.get_fov_mighti(bottom_left, bottom_right, top_left, top_right)


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
  f = open(filename + '.txt', "w+")
  f.write(file_complete)
  f.close();


  return "file written for" + filename
