
#Computes transformation from euler angles to quaternion and rotation of vectors by quaternion

import numpy as np
from math import sqrt

def euler_rotation_to_quaternion(matrix):
    """returns the quaternion of an euler rotation  as a list in the format theta + i + j + k"""
    quaternion = []
    quaternion.append(quaternion_angle(matrix))
    for i in range(len(matrix)):
        quaternion.append(quaternion_vector(matrix, matrix[i,i]))
    return quaternion 
    
    
def quaternion_vector(matrix, entry):
    """returns the vector component of quaternion"""
    trace = np.trace(matrix)
    vector = sqrt(entry/2 + (1 - trace)/4)
    return vector

def quaternion_angle(matrix):
    """returns the angle component of the quaternion"""
    trace = np.trace(matrix)
    angle = sqrt(trace + 1)/2
    return angle 





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
    
    
    






sample = np.eye(3) 
print(euler_rotation_to_quaternion(sample))
print(len(sample))
print(sample[1,1])
x = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
print(euler_rotation_to_quaternion(x))
print(quaternion_conjugate(euler_rotation_to_quaternion(x)))
y = euler_rotation_to_quaternion(x)
print(quaternion_rotation(y, [1,0,0]))



