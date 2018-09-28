import calc_funcs
import math
from netCDF4 import Dataset

def czml_generator_fuv(filename):
    fuvdata = Dataset(filename, "r")
    lat = fuvdata.variables["ICON_ANCILLARY_FUV_LATITUDE"]
    lon = fuvdata.variables["ICON_ANCILLARY_FUV_LONGITUDE"]
    alt = fuvdata.variables["ICON_ANCILLARY_FUV_ALTITUDE"]
    time = fuvdata.variables["ICON_ANCILLARY_FUV_TIME_UTC"]
    positions_list = calc_funcs.positions(lat, lon, alt, time)
    #find azimuth,zenith angles for botton left, bottom right, top right, and top left of instrument
    azimuth_bottom_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 0, 0].tolist()
    zenith_bottom_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 0, 0].tolist()
    azimuth_bottom_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 0, 5].tolist()
    zenith_bottom_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 0, 5].tolist()
    azimuth_top_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 255, 5].tolist()
    zenith_top_right = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 255, 5].tolist()
    azimuth_top_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_AZIMUTH_ANGLE"][:, 255, 0].tolist()
    zenith_top_left = fuvdata.variables["ICON_ANCILLARY_FUV_FOV_ZENITH_ANGLE"][:, 255, 0].tolist()
    #check to make sure no values are missing
    azimuth_list = [azimuth_bottom_left, azimuth_bottom_right, azimuth_top_right, azimuth_top_left]
    zenith_list = [zenith_bottom_left, zenith_bottom_right, zenith_top_right, zenith_top_left]
    a_b_l, z_b_l, a_b_r, z_b_r, a_t_r, z_t_r, a_t_l, z_t_l, orient_time = calc_funcs.fuv_check_values(azimuth_list, zenith_list, time[:].tolist())
    #compute quaternions from azimuth, zenith angles for four positions in FOV
    b_l_quat = calc_funcs.fuv_horizontal_to_quaternion(a_b_l, z_b_l)
    b_r_quat = calc_funcs.fuv_horizontal_to_quaternion(a_b_r, z_b_r)
    t_r_quat = calc_funcs.fuv_horizontal_to_quaternion(a_t_r, z_t_r)
    t_l_quat = calc_funcs.fuv_horizontal_to_quaternion(a_t_l, z_t_l)
    #rotate quaternions of FOV positions in counterclockwise direction; creates a list with time string followed by quaternion
    orientations_list = calc_funcs.fuv_orientations_calc(b_l_quat, b_r_quat, t_r_quat, t_l_quat, orient_time)
    return orientations_list
