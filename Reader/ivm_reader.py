from netCDF4 import Dataset
import math
import numpy as np
import calc_funcs

def czml_generator_ivm(filename):
	""" Writes a czml file with the orientation and posistion data for the cone defined by the field of view of the IVM"""
	fovdata = Dataset(filename,"r")
	split_filename = filename.split("_")
	type = split_filename[2].split("-")[1]
	time = fovdata.variables["ICON_ANCILLARY_IVM_TIME_UTC"]
	lat = fovdata.variables["ICON_ANCILLARY_IVM_LATITUDE"]
	lon = fovdata.variables["ICON_ANCILLARY_IVM_LONGITUDE"]
	alt = fovdata.variables["ICON_ANCILLARY_IVM_ALTITUDE"]
	position_list = calc_funcs.positions(lat,lon,alt,time)
	if type == "A":
		ivma_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"][:].tolist()
		ivma_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"][:].tolist()
		ivma_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"][:].tolist()
		time = time[:].tolist()
		#check to make sure there is no missing/corrupt data
		ivma_x_hat, ivma_y_hat, ivma_z_hat, time_orient = calc_funcs.ivm_check_values(ivma_x_hat, ivma_y_hat, ivma_z_hat, time)
		#convert ivma fov unit vectors to ivmb fov unit vectors
		ivmb_x_hat, ivmb_y_hat = calc_funcs.rotate_to_other_ivm(ivma_x_hat, ivma_y_hat)
		ivmb_z_hat = ivma_z_hat
	else:
		ivmb_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"][:].tolist()
		ivmb_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"][:].tolist()
		ivmb_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"][:].tolist()
		#check to make sure there is no missing/corrupt data
		ivmb_x_hat, ivmb_y_hat, ivmb_z_hat, time_orient = calc_funcs.ivm_check_values(ivma_x_hat, ivma_y_hat, ivma_z_hat, time)
		#convert ivma fov unit vectors to ivmb fov unit vectors
		ivma_x_hat, ivma_y_hat = calc_funcs.rotate_to_other_ivm(ivma_x_hat, ivma_y_hat)
		ivma_z_hat = ivmb_z_hat


	ivma_orientations = calc_funcs.ivm_orientations_calc(ivma_x_hat, ivma_y_hat, ivma_z_hat, time_orient)
	ivmb_orientations = calc_funcs.ivm_orientations_calc(ivmb_x_hat, ivmb_y_hat, ivmb_z_hat, time_orient)



	position_str = str(position_list).replace("'",'')
	ivma_orientation_str = str(ivma_orientations).replace("'", '')
	ivmb_orientation_str = str(ivmb_orientations).replace("'", '')
	ivma_file_complete = ivma_file + position_str + middle_file + ivma_orientation_str + end_file
	ivmb_file_complete = ivmb_file + position_str + middle_file + ivmb_orientation_str + end_file
	label_file = label_start + position_str + end_file
	path_file = path_start + position_str + end_file

	f_a = open(filename + '.txt', "w+")
	f_b = open(filename + "B" + '.txt', "w+")

	f_a.write(ivma_file_complete);
	f_b.write(ivmb_file_complete)


	f_a.close()
	f_b.close()
	return "file written for"  + filename[:-2]
