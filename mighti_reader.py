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
  x_hat =mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_XHAT"]
  y_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_YHAT"]
  z_hat = mightidata.variables["ICON_ANCILLARY_MIGHTI_SC_ZHAT"]
  #read orientation of MIGHTI instrument in ECEF
  mighti_FOV = mightidata.variables["ICON_ANCILLARY_MIGHTI_FOV_UNITVECTORS_ECEF"]
  bottom_left =  mighti_FOV[:,0,0,:,1]
  bottom_right = mighti_FOV[:,2,0,:,1]
  top_left_= mighti_FOV[:,0,2,:,1]
  top_right= mighti_FOV[:,2,2,:,1]

  #position of spacecraft
  position_list = calc_funcs.positions(lat, lon, alt, time)
   #ECEF postion of spacecraft
  mighti_ecef_pos = ecef_position_list(sc_ecef_position)
  #FOV vectors in quaternion
  bottom_left_quat = mighti_orientations(bottom_left, bottom_right, top_left, top_right)[0]
  bottom_right_quat = mighti_orientations(bottom_left, bottom_right, top_left, top_right)[1]
  top_left_quat = mighti_orientations(bottom_left, bottom_right, top_left, top_right)[2]
  top_right_quat = mighti_orientations(bottom_left, bottom_right, top_left, top_right)[3]
  #rotate the ECEF positions by the various FOV quaternions and put in unit quaternion form
  bottom_left_quat_final = unit_quaternion_mighti_fov(bottom_left_quat, position_list)
  bottom_right_quat_final = unit_quaternion_mighti_fov(bottom_right_quat, position_list)
  top_left_quat_final = unit_quaternion_mighti_fov(top_left_quat, position_list)
  top_right_quat_final = unit_quaternion_mighti_fov(top_right_quat, position_list)




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
