
from netCDF4 import Dataset
import math
from math import asin
import numpy as np
import cesium

a = 6378137
b = 6356752.3142
f = (a - b) / a
e_sq = f * (2-f)

fovdata = Dataset("ICON_L0P_IVM-A_Ancillary_2018-03-21_v01r000.NC","r")

for variables in fovdata.variables:
	print(variables)

	
instra_x_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_XHAT_ECEF"]
instra_y_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_YHAT_ECEF"]
instra_z_hat = fovdata.variables["ICON_ANCILLARY_IVM_INSTRA_ZHAT_ECEF"]



def ecef_to_enu(x, y, z, lat0, lon0, h0):
    lamb = math.radians(lat0)
    phi = math.radians(lon0)
    s = math.sin(lamb)
    N = a / math.sqrt(1 - e_sq * s * s)

    sin_lambda = math.sin(lamb)
    cos_lambda = math.cos(lamb)
    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)

    x0 = (h0 + N) * cos_lambda * cos_phi
    y0 = (h0 + N) * cos_lambda * sin_phi
    z0 = (h0 + (1 - e_sq) * N) * sin_lambda

    xd = x - x0
    yd = y - y0
    zd = z - z0

    xEast = -sin_phi * xd + cos_phi * yd
    yNorth = -cos_phi * sin_lambda * xd - sin_lambda * sin_phi * yd + cos_lambda * zd
    zUp = cos_lambda * cos_phi * xd + cos_lambda * sin_phi * yd + sin_lambda * zd

    return xEast, yNorth, zUp



def dotproduct(v1, v2):
  return np.dot(v1,np.transpose(v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
  return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def heading(x,y,z):
	x_1 = (x[0])
	y_1 = (y[0])
	z_1 = (z[0])
	denominator = ((x_1 ** 2) + (y_1 ** 2) + (z_1 ** 2))**.5
	alpha = x_1 / denominator
	angle = math.acos(alpha)
	return angle


def pitch(x,y,z):
	x_2 = (x[1])
	y_2 = (y[1])
	z_2 = (z[1])
	print(x_2,y_2,z_2)
	denominator_2 = ((x_2 ** 2.0) + (y_2 ** 2.0) + (z_2 ** 2.0)) ** (1/2)
	alpha_2 = y_2 /(denominator_2)
	angle_2 = math.acos(alpha_2)
	return angle_2


def orientations(instra_x_hat,instra_y_hat,instra_z_hat):
	orientations = []
	for i in range(10):
		x = instra_x_hat[i]
		y = instra_y_hat[i]
		z = instra_z_hat[i]
		heading = heading(x,y,z)
		pitch = pitch(x,y,z)
		hpr = Cesium.HeadingPitchRoll(heading, pitch, 0)
		orientation = Cesium.Transforms.headingPitchRollQuaternion(Cesium.Cartesian3(0, 0, 0), hpr)
		orientations += [orientation]
	return orientation


print(orientations(instra_x_hat,instra_y_hat,instra_z_hat))



