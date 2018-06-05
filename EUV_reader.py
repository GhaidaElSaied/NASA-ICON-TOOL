from netCDF4 import Dataset
import math
import numpy
def czm_generator_euv(filename):
    """Writes a czml file from the unit vectors of the 108 vertical positions with epoch along with lon,lat, alt"""
    euvdata = Dataset(filename,"r" )
    unit_vector_vertical = euvdata.variables["ICON_ANCILLARY_EUV_FOV_UNITVECTORS_ECEF"]
    vertical_time = vertical_time(unit_vector_vertical)
    start_file = '[{"version": "1.0", "id": "document"}, {"label": {"text": "ICON", "pixelOffset": {"cartesian2": [0.0, 16.0]}, "scale": 0.5, "show": true}, "path": {"show": false, "material": {"solidColor": {"color": {"rgba": [255, 0, 255, 125]}}}, "width": 2, "trailTime": 0, "resolution": 120, "leadTime": 0, "trailTime": 10000},  "cylinder" : { "length" : 1000000.0, "topRadius" : 100.0, "bottomRadius" : 500000.0, "material" : { "solidColor" : { "color" : { "rgba" : [0, 255, 0, 128] } } }, "outline" : true, "outlineColor" : { "rgba" : [0, 0, 0, 255] } }, "position": {"interpolationDegree": 5, "referenceFrame": "INTERTIAL", "cartographicDegrees":'
	end_file = '}, "id": "ICON"}]'
	file_complete = start_file + str(posistion_list).replace("'",'') + str(orientation_list).replace("'",'') + end_file
	f = open(filename + '.txt', "w+")
	f.write(file_complete);
	f.close();
	return "file written for " + filename[:-2]
    
    

        


def vertical_time(matrix):
    time_vertical_matrix = list(map(list, list(zip(matrix[1], matrix[2]))))
    return time_vertical_matrix


    
                                                                    
                



  #netcdfICON_L0P_EUV_ANCILLARY_2017-05-28_v01r000
                                                                           
                                                                        
    
    





    

    
    
