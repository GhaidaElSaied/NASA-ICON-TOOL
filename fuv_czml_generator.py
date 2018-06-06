from netCDF4 import Dataset
import math, numpy

def czml_generator_fov_fuv(filename):
    fovdata = Dataset(filename, "r")

# important variables
# ICON_ANCILLARY_FUV_FOV_UNITVECTORS_ECEF
# ICON_ANCILLARY_FUV_STATUS
# ICON_ANCILLARY_FUV_SPACE_ENVIRONMENT_REGION_STATUS
# ICON_ANCILLARY_FUV_ACTIVITY
