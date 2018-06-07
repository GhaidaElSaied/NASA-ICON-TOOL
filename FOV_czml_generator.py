
from netCDF4 import Dataset
from calc_funcs import convert_time_format, orientations, quaternion_from_matrix
import math
import numpy 

def czml_generator_fov_ivm(filename):
	""" Writes a czml file with the orientation and posistion data for the cone defined by the field of view of the IVM"""
	fovdata = Dataset(filename,"r")
	instra_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"]
	instra_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"]
	instra_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"]
	time = fovdata.variables["ICON_ANCILLARY_IVM_TIME_UTC"]
	lat = fovdata.variables["ICON_ANCILLARY_IVM_LATITUDE"]
	lon = fovdata.variables["ICON_ANCILLARY_IVM_LONGITUDE"]
	alt = fovdata.variables["ICON_ANCILLARY_IVM_ALTITUDE"]
	posistion_list = posistions(lat,lon,alt,time)
	orientation_list = orientations(instra_x_hat,instra_y_hat,instra_z_hat,time)
	start_file = '[{"version": "1.0", "id": "document"}, {"label": {"text": "ICON", "pixelOffset": {"cartesian2": [0.0, 16.0]}, "scale": 0.5, "show": true}, "path": {"show": false, "material": {"solidColor": {"color": {"rgba": [255, 0, 255, 125]}}}, "width": 2, "trailTime": 0, "resolution": 120, "leadTime": 0, "trailTime": 10000},  "cylinder" : { "length" : 1000000.0, "topRadius" : 100.0, "bottomRadius" : 500000.0, "material" : { "solidColor" : { "color" : { "rgba" : [0, 255, 0, 128] } } }, "outline" : true, "outlineColor" : { "rgba" : [0, 0, 0, 255] } }, "position": {"interpolationDegree": 5, "referenceFrame": "INTERTIAL", "cartographicDegrees":'
	middle_file =', "interpolationAlgorithm": "LAGRANGE"},"orientation":{"interpolationAlgorithm":"LINEAR", "interpolationDegree":1, "unitQuaternion":'
	end_file = '}, "id": "ICON"}]'
	file_complete = start_file + str(posistion_list).replace("'",'') + middle_file + str(orientation_list).replace("'",'') + end_file
	f = open(filename + '.txt', "w+")
	f.write(file_complete);
	f.close();
	return "file written for " + filename[:-2]

print(czml_generator_fov_ivm("ICON_L0P_IVM-A_Ancillary_2017-05-28_v01r000.NC"))
