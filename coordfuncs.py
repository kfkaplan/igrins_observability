#This library is for handling astronomical positions, RA, Dec, longitude, latitude, etc.

#Import python libraries
from pdb import set_trace as stop #Use stop() for debugging
#from scipy import *
from numpy import * #Import numpy
import urllib
from six import string_types


try:
    from astroquery.simbad import Simbad
    astroquery_import = True
except ImportError:
    astroquery_import = False
    print('\n\nWARNING! astroquery not found! Falling back to urllib! ')
    print('This is less reliable for parsing object name --> ra/dec!\n\n')

#Grab RA and Dec of object by looking up it's name
#This function is a modified copy of https://gist.github.com/juandesant/5163782#file-sesame-py-L18
def name_query(target_name):
    # target_name is a variable containing a source name, such as M31, Alpha Centauri, Sag A*, etc
    if astroquery_import:
        data = Simbad.query_object(target_name)
        ra = data['RA'].item()
        dec = data['DEC'].item()
        return coords(ra, dec)

    else:
        # Just use urllib if astroquery is not available
        # This is the string with the URL to query the Sesame service,
        # using a 'name' parameter.
        # sesameQueryUrl = 'http://cdsws.u-strasbg.fr/axis/services/Sesame?'  +\
        #                  'method=sesame&resultType=p&all=true&service=NSVA' +\
        #                  '&name=%(name)s'
        # use the updated CDS REST endpoint
        sesameQueryUrl = 'http://cdsweb.u-strasbg.fr/cgi-bin/nph-sesame/-op/NSV?%(name)s'
        # Build the query from the sesameQueryUrl and the dictionary
        # We have to use urllib.quote to make it safe to include in a URL
        sesameQuery = sesameQueryUrl % {
            'name': urllib.quote(target_name)
        }
        # Read the lines of the response from the final URL
        sesameResponse = urllib.urlopen(sesameQuery).readlines()
        # Parse the sesameResponse to get RA, Dec
        # oneliner: ra, dec = filter(lambda x: x.find('%J') == 0, sesameResponse)[0].split(' ')[1:3]
        # The coordinates are in the lines starting with %J
        coordinateList = filter(lambda x: x.find('%J') == 0, sesameResponse)
        # As filter returns a list, get the first line
        print(target_name)
        print(coordinateList)
        coordinates = coordinateList[0]
        # Split the coordinates between the spaces, and drop de first item (%J) (so, start from the second on)
        coordinates = coordinates.split(' ')[1:]
        ra = float(coordinates[0])
        dec = float(coordinates[1])
        print(ra, dec)
        print(target_name)
        return coords(ra, dec)  #Return a coordinate object

#Input coordinates as a sexigasimal string and turn into a coords object
def coord_query(input_coords):
  if input_coords.count(' ') == 1 :#format for something like XX:XX:XX.XXX +XX:XX:XX.XX
    [ra,dec] = input_coords.split(' ')  #Just split at the space between RA and Dec.
  elif input_coords.count(' ') == 5: #format for something like XX XX XX.XX +XX XX XX.X
    s = input_coords.split(' ')
    ra = s[0]+':'+s[1]+':'+s[2]
    dec = s[3]+':'+s[4]+':'+s[5]
  else:
    ra = ValueError
    dec = ValueError
    print('ERROR: Coordinate format entered incorrect.')
  return coords(ra, dec)

#Convert sexigasimal units to decimal degrees, need to speficy units as hours 'hms' or degrees 'dms'
#Accepts the following formats "xx:xx:xx.x" "xx xx xx.x"  "xxhxxmxx.xs" "xxHxxMxx.xS"
def sex2deg(input, units='dms'):
  input = input.lower()
  input = input.replace('+','') #get rid of plus signs if they are there
  input = input.replace('h',':') #Set all delimiters to : for later splitting up the input string
  input = input.replace('d',':')
  input = input.replace('m',':')
  input = input.replace('s','')
  input = input.replace(' ',':')
  [x,m,s] = input.split(':')  #Split up degrees/hours, minutes, seconds into x,m,s
  if s == '':
    s=0.0 #Set seconds to zero if user does not input seconds
  if float(x) >= 0: #Check if number is positive
    deg = float(x) + (float(m)/60.0) + (float(s)/3600.0) #Convert sexigasimal units to degrees
    if x == '-00': #Fix bug where dec of -00 gets read in as positive 
      deg = -deg
  else: #If number is not positive we want to subtract the minutes and seconds
    deg = float(x) - (float(m)/60.0) - (float(s)/3600.0) #Convert sexigasimal units to degrees
  units = units.lower() #Change units to lower case to 
  if units == 'hms' or units == 'h' or units == 'hour' or units == 'hr' or units == 'hours': #If units in hours, multipy by 15 to convert to degrees
    deg = deg * 15.0
  return deg

#Convert decimal degrees (or hours) to sexagesimal units
def deg2sex(input, precision=1, sign='', units='dms'):
  x = input #Degrees or hours
  if x < 0.0: #if 
     sign = '-'
     x = abs(x) #Make everything positive, but show sign as negative
  m = (x % 1.0)*60.0 #Minutes
  s = (m % 1.0)*60.0 #Seconds
  fractional_s = (s % 1.0)*10.0**precision #fraction of seconds in precision number to decimal places
  if round(fractional_s) >= 10**precision: #catch rounding issues and correct them
    fractional_s = 0.0
    s = s + 1.0
    if s >= 60.0: #in the incredibly rare event that xx:xx:59.99 rounds up
      s = 0.0
      m = m + 1.0
      if m >=60.0: #in the super dooper incredibly rare event that xx:59:59.99 rounds up
        m = 0.0
        x = x+1.0
  if units == 'dms' or units == 'hms': #return everything in format "xx:xx:xx.xx"
    fmt = "%02d:%02d:%02d.%0"+str(int(precision))+"d" #Set up formatting for string that will hold the sexagesimal output
    sexagesimal = fmt % (int(x), int(m), int(s), round(fractional_s)) #Save sexagesimal output string
  if units == 'dm' or units == 'hm': #return everything in format "xx:xx"
    fmt = "%02d:%02d" #Set up formatting for string that will hold the sexagesimal output
    sexagesimal = fmt % (int(x), round(m)) #Save sexagesimal output string
  return sign + sexagesimal #Return sign (+/-) plus sexagesimal output s tring

#Reads in two instances of the coordinate class storing RA and Dec., for two objects,
#and calculates the angular seperation between the two
#Formula can be seen at http://www.astronomycafe.net/qadir/q1890.html
def angular_seperation(obj1, obj2, units='deg'):
  ddeg = degrees(arccos( obj1.dec.sin()*obj2.dec.sin() + obj1.dec.cos()*obj2.dec.cos()*cos(obj1.ra.rad()-obj2.ra.rad()) ) )
  if units=='deg' or units=='d' or units=='degree' or units=='degrees':
    return ddeg
  elif units=='arcmin' or units=='arminute' or units=='arcminutes':
    return ddeg*60.0
  elif units=='arcsec' or units=='arcsecond' or units=='arcseconds':
    return ddeg*3600.0

#Calculate angular seperation in RA between two objects
def ra_seperation(obj1, obj2, units='deg'):
  #The line below is (RA2-RA1)*cos(dec) where cos(dec) is the average declination taken using the integral defintion of averages
  dra = (obj2.ra.deg()-obj1.ra.deg()) * ( (obj2.dec.sin()-obj1.dec.sin())/(obj2.dec.rad()-obj1.dec.rad()) )
  if units=='deg' or units=='d' or units=='degree' or units=='degrees':
    return dra
  elif units=='arcmin' or units=='arminute' or units=='arcminutes':
    return dra*60.0
  elif units=='arcsec' or units=='arcsecond' or units=='arcseconds':
    return dra*3600.0
  elif units=='h' or units=='hr' or units=='hour' or units=='hours':
    return dra/15.0
  elif units=='m' or units=='min' or units=='minute' or units=='minutes':
    return dra*60.0/15.0
  elif units=='s' or units=='sec' or units=='second' or units=='seconds':
    return dra*3600.0/15.0
    

#Calculate angular seperation in Dec. between two objects
def dec_seperation(obj1, obj2, units='deg'):
  ddec = obj2.dec.deg() - obj1.dec.deg()
  if units=='deg' or units=='d' or units=='degree' or units=='degrees':
    return ddec
  elif units=='arcmin' or units=='arminute' or units=='arcminutes':
    return ddec*60.0
  elif units=='arcsec' or units=='arcsecond' or units=='arcseconds':
    return ddec*3600.0

	

#Calculate altitude of target in the sky given target coords, observer location, and Local Siderial Time (LST)
def alt(tar, loc, LST):
  if isinstance(LST, string_types):
    LST_deg = sex2deg(LST) #Convert local siderial time into degrees
  else:
    LST_deg = LST * 15.0
  sin_lat = loc.lat.sin()
  sin_dec = tar.dec.sin()
  cos_lat = loc.lat.cos()
  cos_dec = tar.dec.cos()
  cos_HA = cos(radians(LST_deg - tar.ra.deg()))
  return degrees(arcsin(sin_lat*sin_dec + cos_lat*cos_dec*cos_HA)) #Equation from http://koti.mbnet.fi/jukaukor/Star_altitude_azimuth.pdf

#Calculate azimuth of target in the sky given target coords, observer location, and Local Siderial Time (LST)
def az(tar, loc, LST):
  sin_lat = loc.lat.sin()
  sin_dec = tar.dec.sin()
  cos_lat = loc.lat.cos()
  alt = alt(tar,loc,LST) #grab altiude in degrees
  sin_alt = sin(radians(alt))
  cos_alt = cos(radians(alt))
  return degrees(arccos((sin_dec-sin_lat*sin_alt)/(cos_lat*cos_alt))) #Equation from http://koti.mbnet.fi/jukaukor/Star_altitude_azimuth.pdf  

#Basic class for angles that will be used, parent class of latitude and longitude
class angle:
  def __init__(self, input_angle):
    self.theta = float(input_angle) #read in and store latitude
    self.precision = 2
  def check_angle_limit(self):
    print('ERROR: You are running the dummy check angle limit method.  Check overloading of methods.')
  def deg(self): #Return latitude in decimal degrees
    self.check_angle_limit()
    return self.theta 
  def rad(self): #Returns angle in radians
    self.check_angle_limit()
    return radians(self.theta)
  def arcmin(self):
    self.check_angle_limit()
    return self.theta * 60.0
  def arcsec(self):
    self.check_angle_limit()
    return self.theta * 3600.0
  def hour(self):
    self.check_angle_limit()
    return self.theta / 15.0
  def dms(self):
    self.check_angle_limit()
    return deg2sex(self.theta, units='dms', precision=self.precision)
  def hms(self):
    self.check_angle_limit()
    return deg2sex(self.hour(), precision=self.precision, units='hms')
  def dm(self):
    self.check_angle_limit()
    return deg2sex(self.theta, units='dm')
  def hm(self):
    return deg2sex(self.hour(), units='hm')
  def cos(self):
    self.check_angle_limit()
    return cos(radians(self.theta))
  def sin(self):
    self.check_angle_limit()
    return sin(radians(self.theta))
  def tan(self):
    self.check_angle_limit()
    return tan(radians(self.theta))

#class that stores an angle between +/- 90 degrees
class latitude(angle):
  def __init__(self, input_angle, precision=2):
    self.theta = float(input_angle) #read in and store latitude
    self.precision=precision
    self.check_angle_limit()
  def check_angle_limit(self):
    if self.theta > 90.0:
      print('ERROR: Latitude angle > 90 degrees')
      self.theta = ValueError
    if self.theta < -90.0:
      print('ERROR: Latitude angle < 90 degrees')
      self.theta = ValueError
  
#Class stores an angle betwseen 0 -> 360 degrees    
class longitude(angle):
  def __init__(self, input_angle, units='deg',precision=2):
    self.theta = float(input_angle) #read in and store latitude
    self.precision = precision
    if units == 'hms' or units == 'h' or units == 'hour' or units == 'hr' or units == 'hours': #If units in hours, multipy by 15 to convert to degrees
      self.theta = self.theta * 15.0
    self.check_angle_limit() #check latitude to make sure it's within the range of +/- 90 degrees adn
  def check_angle_limit(self):
    if self.theta > 360.0 or self.theta < 0.0:
      self.theta = self.theta % 360.0
      
##Class stores the RA and Dec. of an object
#Accessed like coords.ra.hour(), coords.dec.deg(), coords.ra.hms(), coords.dec.dms()
class coords():
  def __init__(self, input_ra=0.0, input_dec=0.0):
    if isinstance(input_ra, string_types): #If units sexigasimal, convert to decimal degrees
      [input_ra, input_dec] = [sex2deg(input_ra, units='hms'), sex2deg(input_dec, units='dms')]
    self.ra = longitude(input_ra, precision=3) #Create RA object
    self.dec = latitude(input_dec, precision=2) #Create Dec. object
  def showcoords(self): #Print coordinates in sexigasimal units as a string
    if self.dec.deg() < 0: #Set sign to +/- for the declination
      sign = ''
    else:
      sign = '+'
    return self.ra.hms() + ' ' + sign + self.dec.dms()
  
##Same as coords class but uses "lon" and "lat" to store location longitude and latitude
class location():
  def __init__(self, input_lon=0.0, input_lat=0.0):
    if isinstance(input_lon, string_types): #If units sexigasimal, convert to decimal degrees
      [input_lon, input_lat] = [sex2deg(input_lon, units='hms'), sex2deg(input_lat, units='dms')]
    self.lon = longitude(input_lon, precision=3) #Create RA object
    self.lat = latitude(input_lat, precision=2) #Create Dec. object
  def showcoords(self): #Print coordinates in sexigasimal units as a string
    if self.lon.deg() < 0: #Set sign to +/- for the declination
      sign = ''
    else:
      sign = '+'
    return self.lon.hms() + ' ' + sign + self.lat.dms()
