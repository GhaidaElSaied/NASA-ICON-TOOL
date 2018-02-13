from astropy.coordinates import GCRS, ITRS, EarthLocation, CartesianRepresentation
from astropy import units as u
from astropy.time import Time
from datetime import datetime

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
    tt=Time(datetime(yyyy, mm, dd, h, m, s), scale='utc')

    # Read the coordinates in the Geocentric Celestial Reference System
    gcrs = GCRS(CartesianRepresentation(x=x*u.m, y=y*u.m,z=z*u.m), obstime=tt)
    
    # Convert it to an Earth-fixed frame
    itrs = gcrs.transform_to(ITRS(obstime=tt))

    el = EarthLocation.from_geocentric(itrs.x, itrs.y, itrs.z) 

    # conversion to geodetic
    lon, lat, alt = el.to_geodetic() 

    return lon, lat, alt



def future_czml_writer(yyyy,mm,dd):
	tt=datetime(yyyy, mm, dd, 0, 0, 0)
	day_of_year = tt.timetuple().tm_yday
	UTC = str(yyyy) + '/' + str(day_of_year)
	return UTC


print(future_czml_writer(2018,2,9))
	


