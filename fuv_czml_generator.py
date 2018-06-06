from netCDF4 import Dataset
from calc_funcs import convert_time_format

def czml_generator_fov_fuv(filename):
    fuv_data = Dataset(filename, "r")
    time = fuv_data.variables["ICON_ANCILLARY_FUV_TIME_UTC"]
    unitvecs = fuv_data.variables["ICON_ANCILLARY_FUV_FOV_UNITVECTORS_ECEF"]
    fuv_status = fuv_data.variables["ICON_ANCILLARY_FUV_STATUS"]
    fuv_space_env = fuv_data.variables["ICON_ANCILLARY_FUV_SPACE_ENVIRONMENT_REGION_STATUS"]
    fuv_activity = fuv_data.variables["ICON_ANCILLARY_FUV_ACTIVITY"]
    write_to_file(filename, time, unitvecs, fuv_status, fuv_space_env, fuv_activity)

def write_to_file(filename, time, unitvecs, fuv_status, fuv_space_env, fuv_activity):
    start_file = """[{"version": "1.0", "id": "document"}, {"label": {"text": "ICON", "pixelOffset":
    {"cartesian2": [0.0, 16.0]}, "scale": 0.5, "show": true}, "path": {"show": false, "material":
    {"solidColor": {"color": {"rgba": [255, 0, 255, 125]}}}, "width": 2, "trailTime": 0, "resolution": 120,
    "leadTime": 0, "trailTime": 10000},  "cylinder" : { "length" : 1000000.0, "topRadius" : 100.0,
    "bottomRadius" : 500000.0, "material" : { "solidColor" : { "color" : { "rgba" : [0, 255, 0, 128] } } },
    "outline" : true, "outlineColor" : { "rgba" : [0, 0, 0, 255] } }, "position": {"interpolationDegree": 5,
    "referenceFrame": "INTERTIAL", "cartographicDegrees":"""
    end_file = """"}, "id": "ICON"}]"""
    f = open(filename[: -3] + '.txt', "w+")
    f.write(start_file)
    if (len(time) == len(unitvecs) == len(fuv_status) == len(fuv_space_env) == len(fuv_activity)):
        for i in range(len(unitvecs)): # each epoch
            print(i)
            curr = [ convert_time_format(time[i]) , unitvecs[i] , fuv_status[i],
                        fuv_space_env[i] , fuv_activity[i] ]
            f.write(str(curr))
    f.write(end_file)
    f.close()
    print("file written for " + filename[: -3])
