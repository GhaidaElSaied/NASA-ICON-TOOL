import math, numpy

def convert_time_format(time):
	"""Converts time stamps from the netCDF to the form for czml "2018-02-09T00:00:00+00:00"""
	time_string = time[0:10] + "T" + time[11:19] +"+00:00"
	return ('"%s"' % time_string)

def convert_time_format(time):
	"""Converts time stamps from the netCDF to the form for czml "2018-02-09T00:00:00+00:00"""
	time_string = time[0:10] + "T" + time[11:19] +"+00:00"
	return ('"%s"' % time_string) 

def positions(lat, lon, alt, time):
	"""Outputs a list with the positions of the satellite by time when given the lat, lon, alt, time variables from a netcdf file. """
	positions = []
	for i in range(len(lat)):
		positions += [convert_time_format(time[i]), lon[i], lat[i], (alt[i] * 1000)]
	return positions

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



def euler_rotation_to_quaternion(matrix):
    """returns the quaternion of an euler rotation  as a list in the format theta + i + j + k"""
    quaternion = []
    quaternion.append(quaternion_scalar(matrix))
    for i in range(len(matrix)):
        quaternion.append(quaternion_vector(matrix, matrix[i,i]))
    return quaternion 
    
    
def quaternion_vector(matrix, entry):
    """returns the vector component of quaternion"""
    trace = numpy.trace(matrix)
    vector = math.sqrt(entry/2 + (1 - trace)/4)
    return vector

def quaternion_scalar(matrix):
    """returns the scalar component of the quaternion"""
    trace = numpy.trace(matrix)
    scalar = math.sqrt(trace + 1)/2
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
    cross_product = numpy.cross(vector_1, vector_2)
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
        norm +=  numpy.square(quat[i])
    norm = sqrt(norm)
    return norm



def quaternion_rotation_time(quaternion, vector, time):
    """Gives the orientation of a particular vector rotated by a quaternion given at some time"""
    new_vector = vector[:]
    for i in range(time):
        new_vector = quaternion_rotation(quaternion, new_vector)
    return new_vector



def orientation_to_unit_quaternion(azimuth, zenith):
    """takes in orientation data and converts to a unit quaternion"""
    euler_angles = angular_to_euler_angle(azimuth, zenith)
    quaternion = euler_rotation_to_quaternion(euler_angles)
    unit_quat = unit_quaternion(quaternion)
    return unit_quat



def orientation_to_euler_angle(azimuth, zenith):
    """Takes EUV data and returns and euler angle matrix"""
    phi = math.radians(azimuth)
    theta = math.radians(zenith)
    euler_angles = numpy.array([[-1*math.sin(phi), math.cos(phi), 0], [-math.cos(theta) * math.cos(phi), -math.cos(theta) * math.sin(phi), math.sin(theta)], [math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)]])
    return euler_angles
   
def orientations(azimuth, zenith, time):
	orients = []
	for pair in map(list, zip(azimuth, zenith, time)):
		orients += [convert_time_format(pair[2])] + UV_to_unit_quaternion(np.mean(pair[0].data), np.mean(pair[1].data))
	return orients
    

