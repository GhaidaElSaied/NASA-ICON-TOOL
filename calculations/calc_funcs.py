
import math, numpy  as np
from math import sqrt
from math import cos, sin, pi, atan2 as arctan2, asin as arcsin


def convert_time_format(time):
	"""Converts time stamps from the netCDF to the form for czml "2018-02-09T00:00:00+00:00"""
	time_string = time[0:10] + "T" + time[11:19] + "Z"
	return ('"%s"' % time_string)

def positions(lat, lon, alt, time):
	"""Outputs a list with the positions of the satellite by time when given the lat, lon, alt, time variables from a netcdf file. """
	positions = []
	lat = lat[:].tolist()
	lon = lon[:].tolist()
	alt = alt[:].tolist()
	time = time[:].tolist()
	for i in range(len(lat)):
		positions += convert_time_format(time[i]), lon[i], lat[i], (alt[i] * 1000)
	return positions


def ivm_orientations_calc(x_hat, y_hat, z_hat, time):
	"Outputs the orientation list for ivm"
	unit_quaternions_list = []
	for i in range(len(x_hat)):
		x = x_hat[i]
		y = y_hat[i]
		z = z_hat[i]
		matrix = np.matrix([x,y,z])
		time_string = convert_time_format(time[i])
		theta, psi, phi = compute_euler_angles(matrix)
		quaternion = euler_angles_to_quaternion(theta, psi, phi)
		unit_quaternions_list +=time_string,  quaternion[0],  quaternion[1],  quaternion[2], quaternion[3]
	return unit_quaternions_list



def compute_euler_angles(matrix):
	"computes the euler angles for a 3x3 rotation matrix"
	if abs(matrix[2,0]) == 1:
		phi = 0 #in this case, phi value can be arbitrary
		if matrix[2,0] == -1:
			theta = pi/2
			psi = arctan2(matrix[0,1], matrix[0,2])
			return theta, psi, phi
		else:
			theta = -1 * pi/2
			psi = arctan2((-1* matrix[0,1]), (-1*matrix[0,2]))
			return theta, psi, phi
	else:
		theta_1 = -1 * arcsin(matrix[2,0])
		theta_2 = pi - theta_1
		psi_1, psi_2 = compute_psi(matrix, theta_1, theta_2)
		phi_1, phi_2 = compute_phi(matrix, theta_1, theta_2)
		return theta_1, psi_1, phi_1


def compute_psi(matrix, theta_1, theta_2):
	"Outputs psi computed from matrix"
	psi_1_num = matrix[2,1]/cos(theta_1)
	psi_1_denom = matrix[2,2]/cos(theta_1)
	psi_1 = arctan2(psi_1_num, psi_1_denom)
	psi_2_num = matrix[2,1]/cos(theta_2)
	psi_2_denom = matrix[2,2]/cos(theta_2)
	psi_2 = arctan2(psi_2_num, psi_2_denom)
	return psi_1, psi_2


def compute_phi(matrix, theta_1, theta_2):
	"""Outputs phi computed from matrix"""
	phi_1_num = matrix[1, 0]/cos(theta_1)
	phi_1_denom = matrix[0,0]/cos(theta_1)
	phi_1 = arctan2(phi_1_num, phi_1_denom)
	phi_2_num = matrix[1, 0]/cos(theta_2)
	phi_2_denom = matrix[0,0]/cos(theta_2)
	phi_2 = arctan2(phi_2_num, phi_2_denom)
	return phi_1, phi_2

def euler_angles_to_quaternion(theta, psi, phi):
	"computes quaternion from euler angles"
	q_0 = cos2(phi) * cos2(theta) * cos2(psi) + sin2(phi) * sin2(theta) * sin2(psi)
	q_1 = sin2(psi) * cos2(theta) * cos2(phi) - cos2(psi) * sin2(theta) * sin2(phi)
	q_2 = cos2(psi) * sin2(theta) * cos2(phi) + sin2(psi) * cos2(theta) * sin2(phi)
	q_3 = cos2(psi) * cos2(theta) * sin2(phi) - sin2(psi) * sin2(theta) * cos2(phi)
	return [ -1* q_1, -1 * q_2, -1 * q_3, q_0]


def sin2(angle):
	"""returns sin of angle divided by two"""
	return sin(angle/2)
def cos2(angle):
	"""returns cos of angle divided by two"""
	return cos(angle/2)

def hamilton_product(quat_1, quat_2):
    """"computes the product of two quaternions"""
    copy_sc_1, copy_sc_2 = quat_1[:], quat_2[:]
    copy_vec_1, copy_vec_2 = quat_1[:], quat_2[:]
    product_quat = []
    product_quat.append(scalar_compute_quat(copy_sc_1, copy_sc_2))
    product_quat += vector_compute_quat(copy_vec_1, copy_vec_2)
    return product_quat




def scalar_compute_quat(quat_1, quat_2):
    """computes the scalar component of hamilton product"""
    vector_1, vector_2 = quat_1[:], quat_2[:]
    del vector_1[0]
    del vector_2[0]
    new_scalar = 0
    new_scalar += quat_1[0] * quat_2[0]
    new_scalar -= np.dot(vector_1, vector_2)
    return new_scalar


def vector_compute_quat(quat_1, quat_2):
    """computes the vector component of hamilton product"""
    product_vector = []
    vector_1, vector_2 = quat_1[1:], quat_2[1:]
    scalar_1, scalar_2 = quat_1[0], quat_2[0]
    cross_product = np.cross(vector_1, vector_2)
    for i in range(3):
        vector_2[i] = vector_2[i] * scalar_1
    for j in range(3):
        vector_1[j] = vector_1[j] * scalar_2
    for k in range(3):
        product_vector += [vector_1[k] + vector_2[k] + cross_product[k]]
    return product_vector



def quaternion_conjugate(quat):
    """returns conjugate of quaternion"""
    quat_conjugate = []
    quat_conjugate = [quat[0]]
    for i in (range(1, len(quat))):
        quat_conjugate.append( -1 * quat[i])
    return quat_conjugate


def unit_quaternion(quat):
    """returns the unit quaternion of a non-zero quaternion"""
    unit_quat = []
    norm = quat[:]
    norm = quaternion_norm(norm)
    for i in range(4):
        unit_quat.append(quat[i] / norm)
    return unit_quat


def quaternion_norm(quat):
    norm = 0
    for i in range(4):
        norm +=  np.square(quat[i])
    norm = sqrt(norm)
    return norm

def sciquat_to_eng_quat(quaternion):
	scalar = quaternion[0]
	sci_quat = quaternion[1:]
	eng_quat = []
	for i in range(len(sci_quat)):
		eng_quat.append(sci_quat[i] * -1)
	eng_quat.append(scalar)
	return eng_quat


def euv_orientations_calc(azimuth,zenith, time):
	"Outputs the orientation list for EUV"
	quaternion_list = []
	for i in range(len(time)):
		time_string = convert_time_format(time[i])
		avg_azimuth = np.mean(azimuth[i])
		avg_zenith = np.mean(zenith[i])
		matrix = euv_horizontal_orientation_to_matrix(avg_azimuth, avg_azimuth)
		theta, psi, phi = compute_euler_angles(matrix)
		quat = euler_angles_to_quaternion(theta, psi, phi)
		quaternion_list += time_string, quat[0], quat[1], quat[2], quat[3]
	return quaternion_list

def euv_horizontal_orientation_to_matrix(azimuth, zenith):
	"Outputs the 3x3 rotation matrix from azimuth and zenith angles for EUV"
	phi = math.radians(zenith)
	theta = math.radians(azimuth)
	matrix = np.matrix([[cos(theta), -sin(theta), 0], [sin(theta), cos(theta), 0], [0, sin(phi), cos(phi)]])
	return matrix



def fuv_horizontal_orientation_to_euler_angle(azimuth, zenith):
	"Outputs the 3x3 rotation matrix from azimuth and zenith angles for FUV"
	matrix_list = []
	for i in range(len(azimuth)):
		phi = math.radians(azimuth[i])
		theta = math.radians(zenith[i])
		matrix = np.matrix([[cos(theta), -sin(theta), 0], [sin(theta), cos(theta), 0], [0, sin(phi), cos(phi)]])
		matrix_list.append(matrix)
	return matrix_list

def fuv_horizontal_to_quaternion(azimuth, zenith):
	"Outputs the quaternion corresponding to the azimuth and zenith angles"
	quaternion_list = []
	rotation_matrices = fuv_horizontal_orientation_to_euler_angle(azimuth, zenith)
	for i in range(len((rotation_matrices))):
		theta, psi, phi = compute_euler_angles(rotation_matrices[i])
		quat = euler_angles_to_quaternion(theta, psi, phi)
		quaternion_list.append(quat)
	return quaternion_list

def fuv_orientations_calc(b_l_quat, b_r_quat, t_r_quat, t_l_quat, time):
	"Outputs the orientation list for FUV"
	quat_product_list_1 = []
	quat_product_list_2 = []
	quat_product_list_3 = []
	quat_product_final = []
	orientation_final_list = []
	for i in range(len(b_l_quat)):
		quat_product_list_1.append(hamilton_product(b_r_quat[i], b_l_quat[i]))
	for j in range(len(t_r_quat)):
		quat_product_list_2.append(hamilton_product(t_r_quat[j], quat_product_list_1[j]))
	for k in range(len(t_l_quat)):
		quat_product_list_3.append(hamilton_product(t_l_quat[k], quat_product_list_2[k]))
	for l in range(len(quat_product_list_3)):
		quat_product_final.append(hamilton_product(b_l_quat[l], quat_product_list_3[l]))
	for m in range(len(quat_product_final)):
		time_string = convert_time_format(time[m])
		orientation_final_list += time_string + sciquat_to_eng_quat(_product_list_3[m])
	return orientation_final_list


def rotate_to_other_ivm(x_hat, y_hat):
	"Outputs the IVM rotated by 180 degrees"
	ivmb_x_hat = []
	ivmb_y_hat = []
	for i in range(len(x_hat)):
		ivmb_x_hat.append((np.multiply(x_hat[i], -1)))
		ivmb_y_hat.append((np.multiply(y_hat[i], -1)))
	return ivmb_x_hat, ivmb_y_hat

def vector_to_pure_quaternion(vector_list):
	"Outputs the pure quaternion of a vector"
	quaternion_list = []
	for i in range(len(vector_list)):
		quaternion_list.append([0] + vector_list[i])
	return quaternion_list

def mighti_orientation_calc(bottom_left_vectors, bottom_right_vectors, top_right_vectors, top_left_vectors, time):
	"Outputs the orientation list for MIGHTI"
	b_l_quat = vector_to_pure_quaternion(bottom_left_vectors)
	b_r_quat = vector_to_pure_quaternion(bottom_right_vectors)
	t_r_quat = vector_to_pure_quaternion(top_right_vectors)
	t_l_quat = vector_to_pure_quaternion(top_left_vectors)
	rotation_1 = []
	rotation_2 = []
	rotation_3 = []
	rotation_4 = []
	orientation_final_list = []
	orientation_time = []
	for i in range(len(b_l_quat)):
		rotation_1.append(hamilton_product(b_r_quat[i], b_l_quat[i]))
	for i in range(len(t_r_quat)):
		rotation_2.append(hamilton_product(t_r_quat[i], rotation_1[i]))
	for i in range(len(t_l_quat)):
		rotation_3.append(hamilton_product(t_l_quat[i], rotation_2[i]))
	for i in range(len(rotation_3)):
	 	rotation_4.append(hamilton_product(b_l_quat[i], rotation_3[i]))
	 	orientation_final_list.append(rotation_4[i])
	for i in range(len(orientation_final_list)):
	 	orientation_time += convert_time_format(time[i]) + sciquat_to_eng_quat(orientation_final_list[i])
	return orientation_time



def check_values(lst):
	"Outputs indices with unusuable data of a nest list"
	indexer = []
	for i in range(len(lst)):
		if isinstance(lst[i], list):
			vec = lst[i]
		else:
			vec = [lst[i]]
			for j in range(len(vec)):
				if not(isinstance(vec[j], float)):
					indexer.append(i)
					break
	return indexer

def ivm_check_values(x_hat, y_hat, z_hat, time):
	"Outputs the components of IVM orientation without unusuable data"
	index_lst = []
	index_lst += check_values(x_hat) + check_values(y_hat) + check_values(z_hat)
	index_lst.sort()
	count = 0
	while count < (len(index_lst) - 1):
	 if (index_lst[count] == index_lst[count + 1]):
	 	index_lst.pop(count)
	 else:
		 count += 1
	for j in range(len(index_lst)):
	 x_hat.pop(index_lst[j])
	 y_hat.pop(index_lst[j])
	 z_hat.pop(index_lst[j])
	 time.pop(index_lst[j])
	 for i in range(len(index_lst)):
			index_lst[i] -= 1
	return x_hat, y_hat, z_hat, time


def euv_check_values(azimuth, zenith, time):
	"Outputs the components of EUV orientation without unusuable data"
	index_lst = []
	index_lst += check_values(azimuth) + check_values(zenith)
	index_lst.sort()
	count = 0
	while count < (len(index_lst) - 1):
		if (index_lst[count] == index_lst[count +1]):
			index_lst.pop(count)
		else:
			count+=1
	for j in range(len(index_lst)):
		azimuth.pop(index_lst[j])
		zenith.pop(index_lst[j])
		time.pop(index_lst[j])
		for i in range(len(index_lst)):
			index_lst[i] -= 1
	return azimuth, zenith, time

def fuv_check_values(azimuth, zenith, time):
	"Outputs the components of FUV orientation without unusuable data"
	index_lst = []
	for i in range(4):
		index_lst +=check_values(azimuth[i]) + check_values(zenith[i])
	index_lst.sort()
	count = 0
	while count <  (len(index_lst) - 1):
		if (index_lst[count] == index_lst[count + 1]):
			index_lst.pop(count)
		else:
			count +=1
	for j in range(len(index_lst)):
			for k in range(4):
				azimuth[k].pop(index_lst[j])
				zenith[k].pop(index_lst[j])
			time.pop(index_lst[j])
			for i in range(len(index_lst)):
				index_lst[i] -= 1
	return azimuth[0], zenith[0], azimuth[1], zenith[1], azimuth[2], zenith[2], azimuth[3], zenith[3], time

def mighti_check_values(bottom_left_vectors, bottom_right_vectors, top_right_vectors, top_left_vectors, time):
	"Outputs the components of MIGHTI orientation without unusuable data"
	index_lst = []
	index_lst += check_values(bottom_left_vectors) + check_values(bottom_right_vectors) + check_values(top_right_vectors) + check_values(top_left_vectors)
	index_lst.sort()
	count = 0
	while count < (len(index_lst) - 1):
		if (index_lst[count] == index_lst[count +1]):
			index_lst.pop(count)
		else:
			count +=1
	for j in range(len(index_lst)):
		bottom_left_vectors.pop(index_lst[j])
		bottom_right_vectors.pop(index_lst[j])
		top_right_vectors.pop(index_lst[j])
		top_left_vectors.pop(index_lst[j])
		time.pop(index_lst[j])
		for i in range(len(index_lst)):
			index_lst[i] -= 1
	return bottom_left_vectors, bottom_right_vectors, top_right_vectors, top_left_vectors, time
