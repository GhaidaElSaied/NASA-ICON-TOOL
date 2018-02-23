import datetime

from astropy import units as u
from astropy.coordinates import GCRS, ITRS, EarthLocation, CartesianRepresentation
from astropy.time import Time


def eci2lla(x, y, z, yyyy, mm, dd, h, m, s):
    """
    Convert Earth-Centered Inertial (ECI) cartesian coordinates to latitude, longitude, and altitude, using astropy.

    Inputs :
    x = ECI X-coordinate (m)
    y = ECI Y-coordinate (m)
    z = ECI Z-coordinate (m)
    dt = UTC time (datetime object)
    Outputs :
    lon = longitude (radians)
    lat = geodetic latitude (radians)
    alt = height above WGS84 ellipsoid (m)
    """
    # convert datetime object to astropy time object
    tt = Time(datetime.datetime(yyyy, mm, dd, h, m, s), scale='utc')

    # Read the coordinates in the Geocentric Celestial Reference System
    gcrs = GCRS(CartesianRepresentation(x=x * u.m, y=y * u.m, z=z * u.m), obstime=tt)

    # Convert it to an Earth-fixed frame
    itrs = gcrs.transform_to(ITRS(obstime=tt))

    el = EarthLocation.from_geocentric(itrs.x, itrs.y, itrs.z)

    # conversion to geodetic
    lon, lat, alt = el.to_geodetic()

    return lon, lat, alt


def convert_time_to_string(year_date, time):
    """
    Convert yyyy/ddd,hh:mm:ss.ssss to yyyy-mm-ddThh:mm:ss+ss:ss
    """
    yyyy = year_date.split("/")[0]
    ddd = year_date.split("/")[1]
    time_stamp = time.split(":")
    hours = time_stamp[0]
    minutes = time_stamp[1]
    seconds = time_stamp[2].split(".")[0]
    UTC = datetime.datetime(int(yyyy), 1, 1) + datetime.timedelta(int(ddd) - 1, seconds=int(seconds),
                                                                  minutes=int(minutes), hours=int(hours))
    UTC = UTC.strftime("%Y-%m-%dT%H:%M:%S")
    return UTC + "+00:00"


def convert_time_to_list(year_date, time):
    """
    Convert time string in format of yyyy/dd hh:mm:ss.sss to a list containing [yyyy,mm,dd,h,m,s]

    """

    yyyy = year_date.split("/")[0]
    ddd = year_date.split("/")[1]
    time_stamp = time.split(":")
    hours = time_stamp[0]
    minutes = time_stamp[1]
    seconds = time_stamp[2].split(".")[0]
    UTC = datetime.datetime(int(yyyy), 1, 1) + datetime.timedelta(int(ddd) - 1, seconds=int(seconds),
                                                                  minutes=int(minutes), hours=int(hours))
    timetuple = UTC.timetuple()
    lst = []
    for i in timetuple:
        lst += [i]
    return lst[0:6]


def convert_time_and_position(lst):
    """
    Convert line of file into goal format "yyyy-mm-ddThh:mm:ss+ss:ss", lat , long, alt,
    """
    time_string = convert_time_to_string(lst[0], lst[1])
    time_list = convert_time_to_list(lst[0], lst[1])
    yyyy = int(time_list[0])
    mm = int(time_list[1])
    dd = int(time_list[2])
    h = int(time_list[3])
    m = int(time_list[4])
    s = int(time_list[5])
    x = float(lst[2])
    y = float(lst[3])
    z = float(lst[4])
    tuple1 = eci2lla(x, y, z, yyyy, mm, dd, h, m, s)
    longitude = tuple1[0].value
    latitude = tuple1[1].value
    altitude = abs(tuple1[2].value)
    # sketchy that this returns something negative!
    return time_string + ", " + str(latitude) + ", " + str(longitude) + ", " + str(altitude)


def czml_writer():
    # opens file with 10 years worth of data
    f = open("ICON_EPHPRE120_18037_000000_28034_235800.txt", "r")
    start_file = '[{"version": "1.0", "id": "document"}, {"label": {"text": "ICON", "pixelOffset": {"cartesian2": [0.0, 16.0]}, "scale": 0.5, "show": true}, "path": {"show": true, "material": {"solidColor": {"color": {"rgba": [255, 165, 0, 1]}}}, "width": 2, "trailTime": 0, "resolution": 120, "leadTime": 0, "trailTime": 10000}, "model": {"gltf" : "../../SampleData/models/CesiumAir/Cesium_Air.glb", "scale" : 2.0, "minimumPixelSize": 64, "show": true}, "position": {"interpolationDegree": 5, "referenceFrame": "INTERTIAL", "cartographicDegrees": '
    end_file = ', "interpolationAlgorithm": "LAGRANGE"}, "id": "ICON"}]'
    lines = f.readlines()
    lines = lines[1:]
    all_data = []
    # iterates through each data and gets the relevant data - converts each measurement into a list with the time and the x,y,z position vectors -
    # stores all of these lists into all_data
    for individual_line in lines:
        thisline = [individual_line.split()[:5]]
        all_data += thisline
    all_converted_data = []
    #sets starting date to first date of data in the file
    date = all_data[0][0][5:]
    count = 0

    # iterates through one day of data, once you get through the first day- writes a file, and then moves on to the next day
    while ((all_data[count][0][5:] == date or ('0' + str(int(all_data[count][0][5:]) - 1)) == date)
           and count < len(all_data)):
        if ('0' + str(int(all_data[count][0][5:]) - 1) == date):
            file_complete = start_file + str(all_converted_data) + end_file
            f = open(string_position[0:10]+".txt", "w+")
            f.write(file_complete);
            f.close();
            print('Data for: ' + string_position[0:10] + ' written to file ' + string_position[0:10] + ".czml")
            date = all_data[count][0][5:]
            all_converted_data = []
            string_position = convert_time_and_position(all_data[count])
            all_converted_data += [string_position]
            count = count + 1
        else:
            #print((str(int(all_data[count][0][5:]) - 1)))
            #print(count)
            string_position = convert_time_and_position(all_data[count])
            all_converted_data += [string_position]
            count = count + 1



czml_writer()
