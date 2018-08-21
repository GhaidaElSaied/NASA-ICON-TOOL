import calc_funcs
import math
from netCDF4 import Dataset

def czml_generator_fuv(filename):
    fuvdata = Dataset(filename, "r")
    lat = fuvdata.variables["ICON_ANCILLARY_FUV_LATITUDE"]
    lon = fuvdata.variables["ICON_ANCILLARY_FUV_LONGITUDE"]
    alt = fuvdata.variables["ICON_ANCILLARY_FUV_ALTITUDE"]
    time = fuvdata.variables["ICON_ANCILLARY_FUV_TIME_UTC"]
    azimuth_bottom_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 0, 0].tolist()
    zenith_bottom_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 0, 0].tolist()
    azimuth_bottom_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 0, 5].tolist()
    zenith_bottom_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 0, 5].tolist()
    azimuth_top_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 255, 5].tolist()
    zenith_top_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 255, 5].tolist()
    azimuth_top_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 255, 0].tolist()
    zenith_top_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 255, 0].tolist()
    bottom_left_quat = calc_funcs.fuv_orientation_to_unit_quaternion(azimuth_bottom_left, zenith_bottom_left)
    bottom_right_quat = calc_funcs.fuv_orientation_to_unit_quaternion(azimuth_bottom_right, zenith_bottom_right)
    top_right_quat = calc_funcs.fuv_orientation_to_unit_quaternion(azimuth_top_right, zenith_top_right)
    top_left_quat = calc_funcs.fuv_orientation_to_unit_quaternion(azimuth_top_left, zenith_top_left)
    orientations_list = calc_funcs.final_fuv_orientations(bottom_left_quat, bottom_right_quat, top_right_quat, top_left_quat, time)
    positions_list = positions(lat, lon, alt, time)

    start_file = """[{"version": "1.0", "id": "document"},
        {"interpolationDegree": 5,
        "referenceFrame": "INERTIAL",
        "id" : "FUV",
        "name" : "FUV-FOV,"
        "model" : {
           "gltf": "cone.gltf,
           "RGBA" : [225, 0, 0, 0],
           "silhouetteColor": [128, 0, 0, 0],
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
file_complete = start_file + str(position_list).replace("'",'') + middle_file + str(orientation_list).replace("'",'') + end_file
f = open(filename[: -3] + '.txt', "w+")
f.write(file_complete)
f.close();
return "file written for " + filename[:-3]



czml_generator_fuv("ICON_L0P_FUV_Ancillary_2017-05-27_v01r000.NC")
