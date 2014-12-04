#This script will convert the alt,az 2.7 m telescope F9 west axis observing limits into HA
#and Dec. for use by observability.py

#Import pythong libraries
from scipy import *
import matplotlib.pyplot as plt #Import matplotlib's plotting routines

#Read in telescope options input
input_file = 'options.inp' #Path to options file
paths = open(input_file) #open options file
skip = paths.readline() #Skip first line of options list
rotator_zero_point = float(str.strip(paths.readline().split('\t')[0])) #Zero point for the rotator where PA=90 degrees
observatory_latitude =  float(str.strip(paths.readline().split('\t')[0])) #Latitude of the observatory (probably never need to change)
observatory_longitude = float(str.strip(paths.readline().split('\t')[0])) #Longitude of the observatory (probably never need to change)
img_size = float(str.strip(paths.readline().split('\t')[0])) #test setting image size to NxN arcminutes
band = str.strip(paths.readline().split('\t')[0]) #Test setting to a 2MASS band
plate_scale = float(str.strip(paths.readline().split('\t')[0])) #arcseconds per pixel on the Slit View Camera
gstar_mag_limit = float(str.strip(paths.readline().split('\t')[0])) #When searching for guide stars, msut be brighter than this K-band mag. limit
gstar_ra_limit = float(str.strip(paths.readline().split('\t')[0]))#arcmin limit in RA for searching for guide stars
gstar_dec_limit = float(str.strip(paths.readline().split('\t')[0])) #arcmin limit in RA for searching for guide stars
n_gstars = int(str.strip(paths.readline().split('\t')[0])) #Number of brightest guide stars to find when searching for guide stars
paths.close() #close options file


az, alt = loadtxt('mask_27y1999d106t1444.f9', unpack=True, skiprows=2) #Read in TCS telescope limit file in Alt, Az in degrees for tube east side of axis
#az, alt = loadtxt('mask_27y1999d108t1901.f9', unpack=True, skiprows=2) #Read in TCS telescope limit file in Alt, Az in degrees for tube west side of axis
rad_alt = radians(alt) #Save alt, az, and observatory latitude in radians for later easier calulations
rad_az = radians(az)
rad_lat = radians(observatory_latitude)

radplot =  plt.subplot(111, polar=True) #Set up view of radial alt/az plot
radplot.plot(rad_az,-alt)
#radplot.set_yticks(range(90,0,10))
radplot.set_ylim(-90,0) #Set radial units
radplot.set_yticks(arange(-90,0,10)) #Set tick marks for radial units
radplot.set_yticklabels(map(str, arange(90, 0, -10)))   #label radial units
radplot.set_theta_direction(-1) #Put east on right, west on left
radplot.set_theta_zero_location("N") #Set north to be top of plot
radplot.set_ylabel('Altitude')
radplot.set_xlabel('Azimuth')
plt.show() #Show alt, az radial plot

#Do the trig
cos_lat = cos(rad_lat)
sin_lat = sin(rad_lat)
cos_alt = cos(rad_alt)
sin_alt = sin(rad_alt)
cos_az = cos(rad_az)
sin_az = sin(rad_az)

#Calculate HA and Dec limits (see notebook for sources of equations)
#x=(-sin_az*cos_alt)/(cos_lat*sin_alt-sin_lat*cos_az*cos_alt)
#HA = arctan(x)
dec = arcsin(sin_lat*sin_alt+cos_lat*cos_alt*cos_az)
multiplier = ones(size(dec))
multiplier[dec > 0.] = -1.0
x = -multiplier*sin_az*cos_alt/cos(dec)
x = array(x)
dec = array(dec)
#blah = logical_and(x > 0., dec > 0.)
HA = arcsin(x)
HA[blah] = abs(HA[blah] - pi) #+ 2.0*pi
#x2 = (sin_alt - sin(dec)*sin_lat) / (cos(dec)*cos_lat)
#HA2 = arcsin(x2)
#x = -sin_az*cos_alt/cos(dec)
#HA = zeros(len(x))
#negative = x < -1.0
#positive = x >= -1,9
#HA[positive] = arcsin(x[positive]) 
#HA[negative] = arcsin(x[negative])


#ha_below_zero = HA < 0.0
#HA[ha_below_zero] = HA[ha_below_zero] + 2.0*pi #Make all hour angles positive
#HA = HA % 2.0*pi #Take modulus of Hour Angle so that it is always between 0 and 2pi radians

#print array(HA*24./(2.*pi)).round()
#print dec

#Show HA and dec limits plot
radplot = plt.subplot(111, polar=True) #set up object for making a radial plot
for i in arange(0, 2*pi, pi/12): #Loop to add in more radial lines for each hour
  radplot.plot([i]*19, arange(-120,70, 10), linewidth=1, linestyle=':', color='gray')
#radplot.plot((pi/2)+read_limits_HA_min*2*pi/24,-read_limits_dec, color='blue', linewidth=2) #plot observing limits
#radplot.plot((pi/2)+read_limits_HA_max*2*pi/24,-read_limits_dec, color='blue', linewidth=2)
radplot.plot(0.5*pi+HA,-degrees(dec), color='blue', linewidth=2)
#radplot.plot(0.5*pi+HA2,-degrees(dec), color='blue', linewidth=2)
#radplot.plot(arange(0,2*pi,2*pi/100), [-obj_coords.dec.deg()]*100, color='red', linewidth=3)
radplot.set_ylim(-120,60) #Set radial units
radplot.set_yticks(arange(-120,60,20)) #Set tick marks for radial units
radplot.set_yticklabels(map(str, arange(120, -60, -20)))   #label radial units
radplot.set_xticklabels(['-6 HA', '-3 HA', '0 HA','3 HA' ,'6 HA','9 HA' ,' ','-9 HA'])  # Label HA units
radplot.set_xlabel('Hour Angle')
radplot.set_ylabel('Declination')
radplot.set_title('107'' (2.7 m) Observing Limit Chart') #Title of plot
plt.show() #show plot


#plt.plot(degrees(dec), degrees(HA)/15.0)
#plt.show()
test = plt.subplot(111)
test.plot(degrees(dec), degrees(HA)/(15.0))
test.set_xlabel('Dec')
test.set_ylabel('HA')
plt.show()
#plt.plot(alt, degrees(dec))
#plt.show()

savetxt('testlimits.dat', transpose([(pi/2)+HA*2*pi/24, degrees(dec)]), fmt='%f5.1')

#  radplot = plt.subplot(111, polar=True) #set up object for making a radial plot

#      gra, gdec, gmag = loadtxt('tmp.dat', usecols=(0,1,9), delimiter='\t', unpack=True, skiprows=1) #Grab RA, Dec., and K-mag from catalog
