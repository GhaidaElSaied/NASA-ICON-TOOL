from netCDF4 import Dataset
import calc_funcs, numpy as np

def czml_generator_mighti(filename):
  mightidata = Dataset(filename, "r")
  type = filename.split("_")[2].split("-")[1]


  time = mightidata.variables["ICON_ANCILLARY_MIGHTI_TIME_UTC_STRING"][:, 1]


  #read position of spacecraft in longitude, latitude, altitude
  lat = mightidata.variables["ICON_ANCILLARY_MIGHTI_LATITUDE"]
  lon = mightidata.variables["ICON_ANCILLARY_MIGHTI_LONGITUDE"]
  alt = mightidata.variables["ICON_ANCILLARY_MIGHTI_ALTITUDE"]

  #read position of spacecraft in ECEF
  sc_ecef_position = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_POSITION_ECEF"][:, :, 1]

  #read orientation of spacecraft in ECEF
  x_hat =mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_XHAT"][:][1]
  y_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_YHAT"][:][1]
  z_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_ZHAT"][:][1]
  #read orientation of MIGHTI instrument in ECEF
  mighti_FOV = mightidata.variables["ICON_ANCILLARY_MIGHTI_FOV_UNITVECTORS_ECEF"]
  bottom_left =  mighti_FOV[:,0,0,:,1]
  bottom_right = mighti_FOV[:,2,0,:,1]
  top_left= mighti_FOV[:,0,2,:,1]
  top_right= mighti_FOV[:,2,2,:,1]

  #position of spacecraft
  position_list = calc_funcs.positions(lat, lon, alt, time)
   #ECEF postion of spacecraft
  ecef_pos = calc_funcs.ecef_position_list(sc_ecef_position)

  #put FOV vectors in quaternion
  bottom_left_quat = calc_funcs.mighti_orientations(bottom_left, bottom_right, top_left, top_right)[0]
  bottom_right_quat = calc_funcs.mighti_orientations(bottom_left, bottom_right, top_left, top_right)[1]
  top_left_quat = calc_funcs.mighti_orientations(bottom_left, bottom_right, top_left, top_right)[2]
  top_right_quat = calc_funcs.mighti_orientations(bottom_left, bottom_right, top_left, top_right)[3]
  #rotate the ECEF positions by the various FOV quaternions and put in unit quaternion form
  bottom_left_quat_final = calc_funcs.unit_quaternion_mighti_fov(bottom_left_quat, ecef_pos)
  bottom_right_quat_final = calc_funcs.unit_quaternion_mighti_fov(bottom_right_quat, ecef_pos)
  top_left_quat_final = calc_funcs.unit_quaternion_mighti_fov(top_left_quat, ecef_pos)
  top_right_quat_final = calc_funcs.unit_quaternion_mighti_fov(top_right_quat, ecef_pos)
  #compute the final orientation FOV
  quaternion_list = [bottom_left_quat_final, bottom_right_quat_final, top_left_quat_final, top_right_quat_final]
  orientation_FOV = quaternion_final = calc_funcs.final_mighti_quat(quaternion_list, x_hat, y_hat, z_hat, time)



  start_file = """[{"version": "1.0", "id": "document"},
		{"interpolationDegree": 5,
		"referenceFrame": "INERTIAL",
		"id" : "mighti",
		"name" : "MIGHTI-""" + type + """FOV\"
		"model" : {
			"gltf": "MIGHTI_FOV.gltf",
            "color" : "black",

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
  file_complete = start_file + str(position_list).replace("'", '') + middle_file + str(orientation_FOV).replace("'",'')+ end_file
  f = open("mighti_test" + '.txt', "w+")
  f.write(file_complete)
  f.close();


  return "file written for" + filename

czml_generator_mighti("ICON_L0P_MIGHTI-A_Ancillary_2017-05-27_v01r000.NC")
