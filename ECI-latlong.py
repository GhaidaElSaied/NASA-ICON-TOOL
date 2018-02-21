from astropy.coordinates import GCRS, ITRS, EarthLocation, CartesianRepresentation
from astropy import units as u
from astropy.time import Time
import datetime 

def eci2lla(x,y,z,yyyy,mm,dd,h,m,s):
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
    tt=Time(datetime.datetime(yyyy, mm, dd, h, m, s), scale='utc')

    # Read the coordinates in the Geocentric Celestial Reference System
    gcrs = GCRS(CartesianRepresentation(x=x*u.m, y=y*u.m,z=z*u.m), obstime=tt)
    
    # Convert it to an Earth-fixed frame
    itrs = gcrs.transform_to(ITRS(obstime=tt))

    el = EarthLocation.from_geocentric(itrs.x, itrs.y, itrs.z) 

    # conversion to geodetic
    lon, lat, alt = el.to_geodetic() 

    return lon, lat, alt


def convert_time_to_string(time):
    """
    Convert time string in format of yyyy/dd hh:mm:ss.sss to yyyy-mm-ddThh:mm:ss+ss:ss
    """
    time = time.split(" ")
    date = time[1].split("/")
    yyyy = date[0]
    ddd = date[1]
    time_stamp = time[2].split(":")
    hours = time_stamp[0]
    minutes = time_stamp[1]
    seconds = time_stamp[2].split(".")[0]
    UTC = datetime.datetime(int(yyyy), 1, 1) + datetime.timedelta(int(ddd) - 1, seconds = int(seconds),minutes = int(minutes), hours =int(hours)) 
    UTC = UTC.strftime("%Y-%m-%dT%H:%M:%S")
    return UTC + "+00:00"

def convert_time_to_list(time):
    """
    Convert time string in format of yyyy/dd hh:mm:ss.sss to a list containing [yyyy,mm,dd,h,m,s]

    """
    time = time.split(" ")
    date = time[1].split("/")
    yyyy = date[0]
    ddd = date[1]
    time_stamp = time[2].split(":")
    hours = time_stamp[0]
    minutes = time_stamp[1]
    seconds = time_stamp[2].split(".")[0]
    UTC = datetime.datetime(int(yyyy), 1, 1) + datetime.timedelta(int(ddd) - 1, seconds = int(seconds),minutes = int(minutes), hours =int(hours)) 
    timetuple = UTC.timetuple()
    lst = []
    for i in timetuple:
        lst += [i]
    return lst[0:6]


def convert_time_and_position(lst):
    """
    Convert line of file into goal format "2017-08-13T00:00:00+00:00", 112.811759218, -22.1268950621, 571398.6700,
    """
    time_string = convert_time_to_string(lst[0])
    time_list = convert_time_to_list(lst[0])
    yyyy = int(time_list[0])
    mm = int(time_list[1])
    dd = int(time_list[2])
    h = int(time_list[3])
    m = int(time_list[4])
    s = int(time_list[5])
    x = float(lst[1])
    y = float(lst[2])
    z = float(lst[3])
    tuple1 = eci2lla(x,y,z,yyyy,mm,dd,h,m,s)
    longitude = tuple1[0].value
    latitude = tuple1[1].value
    altitude = abs(tuple1[2].value)
    #sketchy that this returns something negative!
    return time_string + ", " + str(latitude) +  ", " + str(longitude) +  ", " + str(altitude)



def czml_writer():
    f = open("ICON_EPHPRE120_18037_000000_28034_235800.txt","r");
    lines = f.readlines();
    all_data = []
    for individual_line in lines:
        thisline = individual_line.split(",");
        thisline = [thisline[0].split("  ")[:4]]
        all_data += thisline
    
    #convert_time_and_position(all_data[2])


# goal "2017-08-13T00:00:00+00:00", 112.811759218, -22.1268950621, 571398.6700,





	


