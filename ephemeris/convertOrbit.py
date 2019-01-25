import argparse
from netCDF4 import Dataset
import datetime 

#year format: 2017 or 2018
#num format: 001 (day num)
#version format: v01r000
#ephemeris: 0 - definitive, 1 - predictive, 2 - guess
def create_orbit(year, num, version, ephemeris):

	# get info based on ephemeris
	ephemerisTypes = ['EPHEMERIS', 'EPHEMERIS.PREDICTIVE']
	ephemerisType = ephemerisTypes[ephemeris]
	ephemFileTypes = ['Definitive', 'Predictive']
	ephem = ephemFileTypes[ephemeris]

	# rgb color codes
	# 0: green (definitive ephemeris), 1: blue (predictive ephemeris), 2: fuscia (guess)
	pathColors = [[124, 252, 0, 125], [0,191,255, 125], [255, 0, 255, 125]]
	pathColor = pathColors[ephemeris]

	#loading in the NC
	path = "/disks/icondata/Repository/Archive/Pre-Launch/LEVEL.0.PRIME/GROUND/" + ephemerisType
	print("%s/%s/ICON_L0P_Ephemeris_%s_%s-%s_%s.NC" % (path, year, ephem, year, num, version))
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
			datetimes = date + 'T' + str(datetime.time(hour[i], mins[i], sec[i])) + 'Z'
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
	formatting = """[{"version": "1.0", "id": "document"}, 
			{
				"label": {
					"text": "ICON", 
					"pixelOffset": {"cartesian2": [0.0, 16.0]}, 
					"scale": 0.5, 
					"show": true
			},
			"path": {
				"show": true, 
				"material": {
					"solidColor": {
						"color": {"rgba": %s}
					}
				}, 
				"width": 2, 
				"resolution": 4,
				"leadTime": 5000,
				"trailTime": 5000
			},   
			"model": {
				"gltf" : "../Models/icon.gltf", 
				"scale": 7500.0, 
				"minimumPixelSize": 64, 
				"show": true
			}, 
			"position": {
				"interpolationDegree": 3, 
	"cartographicDegrees": [""" % pathColor
	orient_format = '''], "interpolationAlgorithm": "LAGRANGE"},"orientation":{"interpolationAlgorithm":"LINEAR", "interpolationDegree":1, "unitQuaternion": ['''
	final_format = ''' ]},"id": "ICON"}]'''

	# add tag to identify ephemeris of different czml files
	ephemTags = ['-d', '-p', '-g']
	ephemTag = ephemTags[ephemeris]

	#writing to file   
	name = '%s-%s_%s' % (year, num, version)
	f = open('/home/lilyb/public_html/new-czml/' + name + ephemTag +'.czml', 'w')
	f.write(formatting)
	for i in range(len(coords)):
		f.write(coords[i])
	f.write(orient_format)
	for i in range(len(orient)):
		f.write(orient[i])
	f.write(final_format)
	print('Data saved in ' + name + '.czml')
	f.close()
