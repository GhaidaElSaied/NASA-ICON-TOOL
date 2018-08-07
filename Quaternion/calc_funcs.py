
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


def quaternion_from_matrix(matrix, isprecise=False):
    """Return quaternion from rotation matrix.
    If isprecise is True, the input matrix is assumed to be a precise rotation
    matrix and a faster algorithm is used.
 	"""
    M = np.array(matrix, dtype=np.float64, copy=False)[:4, :4]
    if isprecise:
        q = np.empty((4, ))
        t = np.trace(M)
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
        K = np.array([[m00-m11-m22, 0.0,         0.0,         0.0],
                         [m01+m10,     m11-m00-m22, 0.0,         0.0],
                         [m02+m20,     m12+m21,     m22-m00-m11, 0.0],
                         [m21-m12,     m02-m20,     m10-m01,     m00+m11+m22]])
        K /= 3.0
        # quaternion is eigenvector of K that corresponds to largest eigenvalue
        w, V = np.linalg.eigh(K)
        q = V[[3, 0, 1, 2], np.argmax(w)]
    if q[0] < 0.0:
        np.negative(q, q)
    return q

def orientations_horizontal_coordinate(azimuth, zenith, time):
	orients = []
	for pair in map(list, zip(azimuth, zenith, time)):
		orients += [convert_time_format(pair[2])] + orientation_to_unit_quaternion(np.mean(pair[0].data), np.mean(pair[1].data))
	return orients


matrix = np.matrix([[2,3], [4,5]])

def gram_schmidt(matrix):
	Q, R = np.linalg.qr(matrix)
	return Q


def FOV_ivm_orientations(x_hat, y_hat, z_hat, time):
	unit_quaternions_list = []
	for i in range(len(x_hat)):
		x = x_hat[i].tolist()
		y = y_hat[i].tolist()
		z = z_hat[i].tolist()
		matrix = np.matrix([x,y,z])
		time_string = convert_time_format(time[i])
		#if check_orthogonality(matrix):
			#if .99 <= np.linalg.det(matrix) <=1:
				#quaternion = proper_rotation_matrix_quaternion(matrix)
		if .99 <= abs(matrix[2,0]) <= 1:
			phi = 0 #in this case, phi value can be arbitrary
			if  np.sign(matrix[2,0]) == -1:
				theta = pi/2
				psi = arctan2(matrix[0,1], matrix[0,2])
				quaternion = euler_angles_to_quaternion(theta, phi, psi)
				unit_quaternions_list +=time_string, -1* quaternion[1],  -1 *quaternion[2],  -1 *quaternion[3], quaternion[0]
			else:
				theta = -1 * pi/2
				psi = arctan2((-1* matrix[0,1])/(-1*matrix[0,2]))
				quaternion = euler_angles_to_quaternion(theta, phi, psi)
				unit_quaternions_list +=time_string,  -1 * quaternion[1],  -1 * quaternion[2],  -1 * quaternion[3], quaternion[0]
		else:
			theta_1 = -1 * arcsin(matrix[2,0])
			theta_2 = pi - theta_1
			psi_1, psi_2 = compute_psi(matrix, theta_1, theta_2)
			phi_1, phi_2 = compute_phi(matrix, theta_1, theta_2)
			quaternion = euler_angles_to_quaternion(theta_1, phi_1, psi_2)
			unit_quaternions_list +=time_string,  -1* quaternion[1],  -1* quaternion[2],  -1 *quaternion[3], quaternion[0]
	return unit_quaternions_list



def compute_euler_angles(matrix):
	if abs(matrix[2,0]) == 1:
		phi = 0 #in this case, phi value can be arbitrary
		if matrix[2,0] == -1:
			theta = pi/2
			psi = arctan2(matrix[0,1], matrix[0,2])
			return theta, phi, psi
		else:
			theta = -1 * pi/2
			psi = arctan2((-1* matrix[0,1])/ (-1*matrix[0,2]))
			return theta, phi, psi
	else:
		theta_1 = -1 * arcsin(matrix[0,2])
		theta_2 = pi - theta_1
		psi_1, psi_2 = compute_psi(matrix, theta_1, theta_2)
		phi_1, phi_2 = compute_phi(matrix, theta_1, theta_2)
		return theta_1, phi_1, psi_1


def compute_psi(matrix, theta_1, theta_2):
	psi_1_num = matrix[2,1]/cos(theta_1)
	psi_1_denom = matrix[2,2]/cos(theta_1)
	psi_1 = arctan2(psi_1_num, psi_1_denom)
	psi_2_num = matrix[2,1]/cos(theta_2)
	psi_2_denom = matrix[2,2]/cos(theta_2)
	psi_2 = arctan2(psi_2_num, psi_2_denom)
	return psi_1, psi_2


def compute_phi(matrix, theta_1, theta_2):
	"""compute phi for euler matrix"""
	phi_1_num = matrix[1, 0]/cos(theta_1)
	phi_1_denom = matrix[0,0]/cos(theta_1)
	phi_1 = arctan2(phi_1_num, phi_1_denom)
	phi_2_num = matrix[1, 0]/cos(theta_2)
	phi_2_denom = matrix[0,0]/cos(theta_2)
	phi_2 = arctan2(phi_2_num, phi_2_denom)
	return phi_1, phi_2

def euler_angles_to_quaternion(theta, phi, psi):
	q_0 = cos2(phi) * cos2(theta) * cos2(psi) + -1* sin2(phi) * sin2(theta) * sin2(psi)
	q_1 = sin2(theta) * cos2(phi) * cos2(psi) + sin2(phi) * cos2(theta) * sin2(psi)
	q_2 = -1 * cos2(phi) * sin2(theta) * sin2(psi) + sin2(phi) * cos2(theta) * cos2(psi)
	q_3 = sin2(phi) * cos2(psi) * sin2(theta) + sin2(psi) * cos2(theta) * cos2(phi)
	return [ -1* q_1, -1 * q_2, -1 * q_3, q_0]


def sin2(angle):
	"""returns sin of angle divided by two"""
	return sin(angle/2)
def cos2(angle):
	"""returns cos of angle divided by two"""
	return cos(angle/2)

def euler_rotation_to_quaternion(matrix):
    """returns the quaternion of an euler rotation  as a list in the format theta + i + j + k"""
    quaternion = []
    quaternion.append(quaternion_scalar(matrix))
    for i in range(len(matrix)):
        quaternion.append(quaternion_vector(matrix, matrix[i,i]))
    return quaternion


def quaternion_vector(matrix, entry):
    """returns the vector component of quaternion"""
    trace = np.trace(matrix)
    vector = math.sqrt(((entry/2) + ((1 - trace)/4)))
    return vector

def quaternion_scalar(matrix):
    """returns the scalar component of the quaternion"""
    trace = np .trace(matrix)
    scalar = math.sqrt(((trace + 1)/2))
    return scalar


def quaternion_rotation(quaternion, vector):
    """rotates vector by a quaternion, returning the rotated vector"""
    quat_conjugate = quaternion_conjugate(quaternion)
    vector = [0] + vector
    new_quat = hamilton_product(quaternion, vector)
    rotated_vector = hamilton_product(new_quat, quat_conjugate)
    return rotated_vector[1:]



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
        norm +=  np .square(quat[i])
    norm = sqrt(norm)
    return norm

def sciquat_to_engquat(quaternion):
	scalar = quaternion[0]
	sci_quat = quaternion[1:]
	eng_quat = []
	for i in range(len(sci_quat)):
		eng_quat.append(sci_quat[i] * -1)
	eng_quat.append(scalar)
	return eng_quat




def quaternion_rotation_time(quaternion, vector, time):
    """Gives the orientation of a particular vector rotated by a quaternion given at some time"""
    new_vector = vector[:]
    for i in range(time):
        new_vector = quaternion_rotation(quaternion, new_vector)
    return new_vector


def orientation_to_unit_quaternion(azimuth, zenith):
	"""Converts horizontal coordinate data to unit quaternion by determining Euler angles"""
	euler_angles = horizontal_orientation_to_euler_angle(azimuth, zenith)
	quat = euler_rotation_to_quaternion(euler_angles)
	return -1 * quat[1], -1 * quat[2], -1 * quat[3], quat[0]

def horizontal_orientation_to_euler_angle(azimuth, zenith):
    """Takes horizontal coordinate data and returns and euler angle matrix"""
    phi = math.radians(azimuth)
    theta = math.radians(zenith)
    euler_angles = np.array([[-1*math.sin(phi), math.cos(phi), 0], [-math.cos(theta) * math.cos(phi), -math.cos(theta) * math.sin(phi), math.sin(theta)], [math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)]])
    return euler_angles

def ecef_position_list(positions):
	"""gives ecef position as list"""
	positions_list = []
	for i in range(len(positions)):
		position = positions[i].tolist()
		positions_list.append(position)
	return positions

def rotate_for_ivmb(x_hat, y_hat):
	ivmb_x_hat = []
	ivmb_y_hat = []
	for i in range(len(x_hat)):
		ivmb_x_hat.append((np.multiply(x_hat[i], -1)))
		ivmb_y_hat.append((np.multiply(y_hat[i], -1)))
	return ivmb_x_hat, ivmb_y_hat

def mighti_orientations(bottom_left, bottom_right, top_left, top_right):
	master_list = [bottom_left, bottom_right, top_left, top_right]
	master_quat_list = []
	for j in range(len(master_list)):
		quat_list = []
		for i in range(len(master_list[j])):
			matrix = np.diag(master_list[j][i].tolist())
			theta, phi, psi = compute_euler_angles(matrix)
			quat_list.append((euler_angles_to_quaternion(theta, phi, psi)))
		master_quat_list.append(quat_list)
	return master_quat_list

def unit_quaternion_mighti_fov(quaternions, positions):
	norm_quats = []
	for i in range(len(positions)):
		vec = positions[i].tolist()
		quat = quaternions[i]
		rotated_vector = quaternion_rotation(quat, vec)
		rotated_quat = [0] + rotated_vector
		final_quat = unit_quaternion(rotated_quat)
		norm_quats.append(final_quat)
	return norm_quats

def final_mighti_quat(quat_list, x_hat, y_hat, z_hat, time):
	final_quaternion_list = []
	for i in range(len(x_hat)):
		time_string = convert_time_format(time[i])
		matrix = np.matrix([x_hat[i].tolist(), y_hat[i].tolist(), z_hat[i].tolist()])
		theta, phi, psi = compute_euler_angles(matrix)
		quaternion = euler_angles_to_quaternion(theta, phi, psi)
		quat_matrix = np.matrix([quat_list[0][i], quat_list[1][i], quat_list[2][i], quat_list[3][i]])
		quat_product = np.matmul(quat_matrix, quaternion).tolist()
		final_quaternion_list += quat_product[0][1], quat_product[0][2], quat_product[0][3], quat_product[0][0], time_string
	return final_quaternion_list
