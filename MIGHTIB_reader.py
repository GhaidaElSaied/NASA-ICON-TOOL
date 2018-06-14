from netCDF4 import Dataset
import numpy as np
import math
import calc_funcs

def czml_generator_MIGHTIB(filename):
    mightibdata = Dataset(filename, "r")

    time = mightibdata.variables["ICON_ANCILLARY_MIGHTI_TIME_UTC_STRING"]
    #determine orientation of spacecraft
    instra_x_hat = mightibdata.variables["ICON_ANCILLARY_MIGHTI_INSTRA_X_ECEF]
    instra_y_hat = mightibdata.variables["ICON_ANCILLARY_MIGHTI_INSTRA_Y_ECEF"]
    instra_z_hat = mightibdata.variables["ICON_ANCILLARY_MIGHTI_INSTRA_Z_ECEF"]
    #determine position of spacecraft
    lon = mightibdata.variables["ICON_ANCILLARY_MIGHTI_LONGITUDE"]
    lat = mightibdata.variables["ICON_ANCILLARY_MIGHTI_LATITUDE"]
    alt = mightibdata.variables["ICON_ANCILLARY_MIGHTI_ALTITUDE"]

    position_list = calc_funcs.positions(lat, lon, alt, time)
    orientation_List = calc_funcs.orientations(instra_x_hat, instra_y_hat, instra_z_hat, time)

    start_file = '[{"version": "1.0", "id": "document"}, {"label": {"text": "ICON", "pixelOffset": {"cartesian2": [0.0, 16.0]}, "scale": 0.5, "show": true}, "path": {"show": false, "material": {"solidColor": {"color": {"rgba": [255, 0, 255, 125]}}}, "width": 2, "trailTime": 0, "resolution": 120, "leadTime": 0, "trailTime": 10000},  "cylinder" : { "length" : 1000000.0, "topRadius" : 100.0, "bottomRadius" : 500000.0, "material" : { "solidColor" : { "color" : { "rgba" : [0, 255, 0, 128] } } }, "outline" : true, "outlineColor" : { "rgba" : [0, 0, 0, 255] } }, "position": {"interpolationDegree": 5, "referenceFrame": "INTERTIAL", "cartographicDegrees":'
    middle_file =', "interpolationAlgorithm": "LAGRANGE"},"orientation":{"interpolationAlgorithm":"LINEAR", "interpolationDegree":1, "unitQuaternion":'
    end_file = '}, "id": "ICON"}]'
    file_complete = start_file + str(position_list).replace("'", '') + middle_file + str(orientation_list).replace("'",'')+ end_file
    f.write(file_complete)
    f.close;
    return "file written for" + filename
