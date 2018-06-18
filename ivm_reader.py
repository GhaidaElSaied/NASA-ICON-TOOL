from netCDF4 import Dataset
import math
import numpy

def czml_generator_ivm(filename):
	""" Writes a czml file with the orientation and posistion data for the cone defined by the field of view of the IVM"""
	fovdata = Dataset(filename,"r")
	type = filename.split("_")[2].split("-")[1]

	instra_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"]
	instra_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"]
	instra_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"]

	time = fovdata.variables["ICON_ANCILLARY_IVM_TIME_UTC"]
	lat = fovdata.variables["ICON_ANCILLARY_IVM_LATITUDE"]
	lon = fovdata.variables["ICON_ANCILLARY_IVM_LONGITUDE"]
	alt = fovdata.variables["ICON_ANCILLARY_IVM_ALTITUDE"]

	position_list = positions(lat,lon,alt,time)
	orientation_list = orientations(instra_x_hat,instra_y_hat,instra_z_hat,time)

	label_start = """[{"version": "1.0", "id": "document"}, {"label":
		{"text": "ICON",
		"pixelOffset": {
			"cartesian2": [0.0, 16.0]},
			"scale": 0.5,
			"show": true
		}, "position" : {
			"cartographicDegrees" :
	"""
	path_start = """[{"version": "1.0", "id": "document"}, {
		"id" : "orbitPath",
		"path": {
				"show" : true,
				"width": 2,
				"trailTime": 0,
				"resolution": 120,
				"leadTime": 0,
				"trailTime": 10000,
				"material": {
					"solidColor": {
						"color": {
							"rgba": [255, 0, 255, 125]
						}
					}
				}
			},
				"position": {
					"cartographicDegrees" :"""
	start_file = """[{"version": "1.0", "id": "document"},
		{"interpolationDegree": 5,
		"referenceFrame": "INERTIAL",
		"id" : "ivma",
		"name" : "IVM-""" + type + """FOV\"
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

	position_str = str(position_list).replace("'",'')
	orientation_str = str(orientation_list).replace("'",'')

	file_complete = start_file + position_str + middle_file + orientation_str + end_file
	label_file = label_start + position_str + end_file
	path_file = path_start + position_str + end_file

	f = open(filename[:-3] + '.txt', "w+")
	label_f = open("label.txt", "w+")
	path_f = open("path.txt", "w+")

	f.write(file_complete);
	label_f.write(label_file)
	path_f.write(path_file)

	f.close()
	label_f.close()
	path_f.close()

	return "files written for " + filename[:-2]

def positions(lat,lon,alt,time):
	"""Outputs a list with the positions of the satellite by time when given the lat,lon,alt,time variables from a netcdf file. """
	positions = []
	for i in range(len(lat)):
		position = convert_time_format(time[i]), lon[i].data.item(0), lat[i].data.item(0),(alt[i] * 1000)
		positions += position
	return positions

def convert_time_format(time):
	"""Converts time stamps from the netCDF to the form for czml "2018-02-09T00:00:00+00:00"""
	time_string = time[0:10] + "T" + time[11:19] +"+00:00"
	return ('"%s"' % time_string)

def orientations(instra_x_hat,instra_y_hat,instra_z_hat,time):
	"""Generates a unit Quaternion from the xhat,yhat,zhat,and time"""
	unitQuaternions = []
	for i in range(len(instra_x_hat)):
		x = instra_x_hat[i]
		y = instra_y_hat[i]
		z = instra_z_hat[i]
		rotation_matrix = numpy.matrix([x,y,z])
		quaternion = numpy.roll(quaternion_from_matrix(rotation_matrix),3)
		time_string = convert_time_format(time[i])
		unitQuaternions += time_string,(-1*quaternion[0]),(-1*quaternion[1]),(-1*quaternion[2]),quaternion[3]
	return unitQuaternions

def quaternion_from_matrix(matrix, isprecise=False):
    """Return quaternion from rotation matrix.
    If isprecise is True, the input matrix is assumed to be a precise rotation
    matrix and a faster algorithm is used.
 	"""
    M = numpy.array(matrix, dtype=numpy.float64, copy=False)[:4, :4]
    if isprecise:
        q = numpy.empty((4, ))
        t = numpy.trace(M)
        if t > M[3, 3]:
            q[0] = t
            q[3] = M[1, 0] - M[0, 1]
            q[2] = M[0, 2] - M[2, 0]
            q[1] = M[2, 1] - M[1, 2]
        else:
            i, j, k = 0, 1, 2
            if M[1, 1] > M[0, 0]:
                i, j, k = 1, 2, 0
            if M[2, 2] > M[i, i]:
                i, j, k = 2, 0, 1
            t = M[i, i] - (M[j, j] + M[k, k]) + M[3, 3]
            q[i] = t
            q[j] = M[i, j] + M[j, i]
            q[k] = M[k, i] + M[i, k]
            q[3] = M[k, j] - M[j, k]
            q = q[[3, 0, 1, 2]]
        q *= 0.5 / math.sqrt(t * M[3, 3])
    else:
        m00 = M[0, 0]
        m01 = M[0, 1]
        m02 = M[0, 2]
        m10 = M[1, 0]
        m11 = M[1, 1]
        m12 = M[1, 2]
        m20 = M[2, 0]
        m21 = M[2, 1]
        m22 = M[2, 2]
        # symmetric matrix K
        K = numpy.array([[m00-m11-m22, 0.0,         0.0,         0.0],
                         [m01+m10,     m11-m00-m22, 0.0,         0.0],
                         [m02+m20,     m12+m21,     m22-m00-m11, 0.0],
                         [m21-m12,     m02-m20,     m10-m01,     m00+m11+m22]])
        K /= 3.0
        # quaternion is eigenvector of K that corresponds to largest eigenvalue
        w, V = numpy.linalg.eigh(K)
        q = V[[3, 0, 1, 2], numpy.argmax(w)]
    if q[0] < 0.0:
        numpy.negative(q, q)
    return q
