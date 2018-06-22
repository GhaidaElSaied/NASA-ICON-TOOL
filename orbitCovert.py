import argparse
from netCDF4 import Dataset
import datetime

parser = argparse.ArgumentParser(description='Date:')
parser.add_argument('-d', type=str, help='day of year')
parser.add_argument('-y', type=str, help='year')
parser.add_argument('-v', type=str, help='version')
parser.add_argument('-e', type=str, help='ephemeris type')

args = parser.parse_args()

year = args.y
num = args.d
version = args.v
ephemeris = int(args.e)

if args.e == None:
	print('No emphemeris type specified.')
	print('Please add -e flag with 0 for definitive, 1 for predictive, and 2 for guess')

if args.d == None:
	print('No date inputted.')
	print('Please enter date in the format: -d YYYY-MM-DD')

if args.v == None:
	#default version
	version = 'v01r000'
else:
	version = 'v%sr%s' % (version[:1].zfill(2), version[1:])

# get info based on ephemeris
ephemerisTypes = ['EPHEMERIS', 'EPHEMERIS.PREDICTIVE']
ephemerisType = ephemerisTypes[ephemeris]
ephemFileTypes = ['Definitive', 'Predictive']
ephem = ephemFileTypes[ephemeris]

# rgb color codes
# 0: green (definitve ephemeris), 1: blue (predictive ephemeris), 2: fuscia (guess)
pathColors = [[124, 252, 0, 125], [0,191,255, 125], [255, 0, 255, 125]]
pathColor = pathColors[ephemeris]

#loading in the NC
path = "/disks/icondata/Repository/Archive/LEVEL.0.PRIME/GROUND/%s/" % ephemerisType
try:
	iconData = Dataset("%s/%s/ICON_L0P_Ephemeris_%s_%s-%s_%s.NC" % (path, year, ephem, year, num, version))
except:
	raise Exception('No matching file.')

# netcdf variables
lat = iconData.variables['LONGITUDE']
lon = iconData.variables['LATITUDE']
alt = iconData.variables['HEIGHT']
hour = iconData.variables['HOUR']
mins = iconData.variables['MINS']
sec = iconData.variables['SEC']
q0 = iconData.variables['Q0_ECEF']
q1 = iconData.variables['Q1_ECEF']
q2 = iconData.variables['Q2_ECEF']
q3 = iconData.variables['Q3_ECEF']

# initialize lists to save netcdf data to
# add opening bracket to first day, then continue into loop
coords = []
orient = []

#datetime to get date from year and day number
date = datetime.datetime.strptime(str(year) + str(num),'%Y%j').strftime('%Y-%m-%d')

print('Creating czml for %s' % date)
for i in range(len(lat)):
	if str(lat[i]) != '--' and str(lon[i]) != '--' and str(alt[i]) != '--':
		position = (str(round(lat[i],10)) + ', ' + str(round(lon[i],10))+ ', ' + str(round(float(alt[i]) * 1000, 10)))

	if str(q0[i]) != '--' and str(q1[i]) != '--' and str(q2[i]) != '--' and str(q3[i]) != '--':
		q = (str(round(q0[i], 10)) + ', ' + str(round(q1[i], 10)) + ', ' + str(round(q2[i], 10)) + ', ' + str(round(q3[i], 10)))

	if str(hour[i]) != '--' and str(mins[i]) != '--' and str(sec[i]) != '--':
		datetimes = date + 'T' + str(datetime.time(hour[i], mins[i], sec[i])) + '+00:00'
		value = ', "' + datetimes + '", ' +  position
		quat = ', "' + datetimes + '", ' +  q
		orient.append(quat)
		coords.append(value)

#fix extra comma at 0th index
coords[0] = coords[0][1:]
orient[0] = orient[0][1:]

#stop reading in netcdf
iconData.close()

#formatting of the czml
formatting = """[{"version": "1.0", "id": "document"}, {"label": {"text": "ICON", "pixelOffset": {"cartesian2": [0.0, 16.0]}, "scale": 0.5, "show": true}, "path": {"show": true, "material": {"solidColor": {"color": {"rgba": %s}}}, "width": 2, "trailTime": 0, "resolution": 120, "leadTime": 0, "trailTime": 10000},
"model": {"gltf" : "icon.glb", "scale": 15000.0, "minimumPixelSize":64, "color": {"rgba": [255, 0, 0, 125]}, "show": true},
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
		}
"position": {"interpolationDegree": 5, "referenceFrame": "INTERTIAL", "cartographicDegrees": [""" % pathColor
orient_format = '''], "interpolationAlgorithm": "LAGRANGE"},"orientation":{"interpolationAlgorithm":"LINEAR", "interpolationDegree":1, "unitQuaternion": ['''
final_format = ''' ]},"id": "ICON"}]'''

# add tag to identify ephemeris of different czml files
ephemTags = ['-d', '-p', '-g']
ephemTag = ephemTags[ephemeris]

#writing to file
name = '%s-%s_%s' % (year, num, version)
f = open('../public_html/orbitViz/ICON/ICONData/czml/' + name + ephemTag +'.czml', 'w')
f.write(formatting)
for i in range(len(coords)):
	f.write(coords[i])
f.write(orient_format)
for i in range(len(orient)):
	f.write(orient[i])
f.write(final_format)
print('Data saved in ' + name + '.czml')
f.close()
