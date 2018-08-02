from netCDF4 import Dataset
import numpy as np
import calc_funcs

def czml_generator_sc(filename):
    sc_data = Dataset(filename, "r")
    sc_x_hat = sc_data.variables["ICON_ANCILLARY_IVM_SC_XHAT_ECEF"][:].tolist()
    sc_y_hat = sc_data.variables["ICON_ANCILLARY_IVM_SC_YHAT_ECEF"][:].tolist()
    sc_z_hat = sc_data.variables["ICON_ANCILLARY_IVM_SC_ZHAT_ECEF"][:].tolist()
    time = sc_data.variables["ICON_ANCILLARY_IVM_TIME_UTC"]
    position_list = calc_funcs.positions(lat,lon,alt,time)
    orientation = []
    for i in range(len(sc_x_hat)):
        rotation_matrix = np.matrix([sc_x_hat[i], sc_y_hat[i], sc_z_hat[i]])
        theta, phi, psi = calc_funcs.compute_euler_angles(rotation_matrix)
        quaternion = euler_angles_to_quaternion(theta, phi, psi)
        orientation += calc_funcs.convert_time_format(time[i]) + quaternion

    start_file = """[{"version": "1.0", "id": "document"},
    	 {"interpolationDegree": 5,
    	"referenceFrame": "INERTIAL",
          "id" : "spacecraft",
        "name" : "spacecraft_orientation",
         "model" :{
            "show": true,
             "gltf": "icon.gltf",
             "scale:": 2,
            }
            "position" : {
            "cartographicDegrees":"""
    middle_file = """,
            "interpolationAlgorithm": "LAGRANGE"
            }
            	"orientation": {
        			"interpolationAlgorithm":"LINEAR",
        			"interpolationDegree":1,
        			"unitQuaternion":"""
    end_file = '}}]'

    position_str = position_str = str(position_list).replace("'",'')
    sc_orientation_str = str(orientation).replace("'", '')
    sc_file_complete = start_file + position_str + middle_file + sc_orientation_str + end_file

    f_sc.open('sc' + '_' + filename[25:-3] + '.txt', "w+")
    f_sc.write(sc_file_complete)
    f_sc.close()
