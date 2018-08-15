from netCDF4 import Dataset
import calc_funcs, numpy as np

def czml_generator_mighti(filename):
  mightidata = Dataset(filename, "r")
  type = filename.split("_")[2].split("-")[1]


  #read position of spacecraft in longitude, latitude, altitude
  lat = mightidata.variables["ICON_ANCILLARY_MIGHTI_LATITUDE"][:, 1]
  lon = mightidata.variables["ICON_ANCILLARY_MIGHTI_LONGITUDE"][:, 1]
  alt = mightidata.variables["ICON_ANCILLARY_MIGHTI_ALTITUDE"][:, 1]
  time = mightidata.variables["ICON_ANCILLARY_MIGHTI_TIME_UTC_STRING"][:, 1]

  #read position of spacecraft in ECEF
  sc_ecef_position = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_POSITION_ECEF"][:, :, 1]

  #read orientation of spacecraft in ECEF
  #x_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_XHAT"][:, 1].tolist()
  #y_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_YHAT"][:, 1].tolist()
  #z_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_ZHAT"][:, 1].tolist()
  #read orientation of MIGHTI instrument in ECEF
  mighti_FOV = mightidata.variables["ICON_ANCILLARY_MIGHTI_FOV_UNITVECTORS_ECEF"]
  middle_middle = mighti_FOV[:,1,1,:,1].tolist()
  #check to make sure there are no missing data points
  time_orientation = time
  missing_index = calc_funcs.check_values(middle_middle)
  for k in range(len(missing_index)):
    middle_middle.pop(missing_index[k])
    time_orientation.pop(missing_index[k])
  orientation_list = calc_funcs.mighti_fov(middle_middle, time_orientation)

  #position of spacecraft
  position_list = calc_funcs.positions(lat, lon, alt, time)
   #ECEF postion of spacecraft
  #ecef_pos = calc_funcs.ecef_position_list(sc_ecef_position)
  #put FOV vectors in quaternion
  ##bottom_right_quat = calc_funcs.mighti_orientations(orient_list[0], orient_list[1], orient_list[2], orient_list[3])[1]
  #top_left_quat = calc_funcs.mighti_orientations(orient_list[0], orient_list[1], orient_list[2], orient_list[3])[2]
  #top_right_quat = calc_funcs.mighti_orientations(orient_list[0], orient_list[1], orient_list[2], orient_list[3])[3]
  #rotate the ECEF positions by the various FOV quaternions and put in unit quaternion form
  #bottom_left_quat_final = calc_funcs.unit_quaternion_mighti_fov(bottom_left_quat, ecef_pos)
  #bottom_right_quat_final = calc_funcs.unit_quaternion_mighti_fov(bottom_right_quat, ecef_pos)
  #top_left_quat_final = calc_funcs.unit_quaternion_mighti_fov(top_left_quat, ecef_pos)
  #top_right_quat_final = calc_funcs.unit_quaternion_mighti_fov(top_right_quat, ecef_pos)
  #compute the final orientation FOV
  #quaternion_list = [bottom_left_quat_final, bottom_right_quat_final, top_left_quat_final, top_right_quat_final]
  #orientation_FOV = calc_funcs.final_mighti_quat(quaternion_list, x_hat, y_hat, z_hat, time)


  start_file = """[{"version": "1.0", "id": "document"},
		{"interpolationDegree": 5,
		"referenceFrame": "INERTIAL",
		"id" : "mighti",
		"name" : "MIGHTI-""" + type + """FOV\"
		"model" : {
			"gltf": "Models/mighti.gltf",
            "color" : "black",
            "silhouetteColor": "black",
            "scale" : "50000000",
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
  f = open(filename[:-3] + '.txt', "w+")
  f.write(file_complete)
  f.close()


  return "file written for" + filename

czml_generator_mighti("ICON_L0P_MIGHTI-A_Ancillary_2017-05-27_v01r001.NC")
