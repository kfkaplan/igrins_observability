#Program to test finding best guide stars in a finder chart
import ds9
from coordfuncs import *

object_name = 'M3'
band = 'k'
size = 15
n_gstars = 10 #Number of brightest guide stars to find
gstar_mag_limit = 12.0
gstar_ra_limit = 10.0#arcmin
gstar_dec_limit = 10 #arcmin
PA = 90.0

#Read in telescope options input
input_file = 'options.inp'
paths = open(input_file)
skip = paths.readline()
rotator_zero_point = float(str.strip(paths.readline().split('\t')[0]))
observatory_latitude =  float(str.strip(paths.readline().split('\t')[0]))
observatory_longitude = float(str.strip(paths.readline().split('\t')[0]))
img_size = float(str.strip(paths.readline().split('\t')[0])) #test setting image size to NxN arcminutes
band = str.strip(paths.readline().split('\t')[0]) #Test setting to a 2MASS band
plate_scale = float(str.strip(paths.readline().split('\t')[0])) #arcseconds per pixel on the Slit View Camera
paths.close()

obj = name_query(object_name) #Read in object


ds9.open()
ds9.set('2mass survey '+band)
ds9.set('2mass coord '+str(obj.ra.deg())+' '+str(obj.dec.deg())+' degrees')
ds9.set('2mass close')
ds9.set('scale log') #Set to log scale
ds9.set('scale Zmax') #Set scale limits t`o Zmax, looks okay
ds9.set('pan to '+obj.showcoords()+' wcs fk5') #Center frame on target object

gstar_dec_limit = gstar_dec_limit/(2.0*60.0) #Convert to degrees
gstar_ra_limit = gstar_ra_limit/(2.0*60.0*obj.dec.cos()) #Convert to degrees
ds9.set('catalog 2mass') #Initialize catalog
ds9.set("catalog filter '$RAJ2000>="+str(obj.ra.deg()-gstar_ra_limit)+"&&$RAJ2000<="+str(obj.ra.deg()+gstar_ra_limit) \ #Load catalog
  +"&&$DEJ2000>="+str(obj.dec.deg()-gstar_dec_limit) + "&&$DEJ2000<=" + str(obj.dec.deg()+gstar_dec_limit) \
    +"&&$Kmag<=" + str(gstar_mag_limit) + "'")
ds9.set("catalog sort 'Kmag' incr") #Sort list by starting from brightest K-band mag. and getting dimmer as you go down
ds9.set("catalog export tsv tmp.dat") #Save catalog list as a tab seperated value file for later trimming
lines = open('tmp.dat').readlines() #Open catalog list tsv file into memory
if len(lines) > 1:
  open('tmp.dat', 'w').writelines(lines[0:n_gstars+1]) #Truncate and save catalog list
  ds9.set('catalog clear') #Clear 2MASS catalog
  ds9.set('catalog close') #Close 2MASS catalog window
  ds9.set('catalog import tsv tmp.dat') #Load only brightest stars to be potential guide stars
  ds9.set('mode catalog') #Set mode to catalog so user can click on possible guide stars and look at their stats
  gra, gdec, gmag = loadtxt('tmp.dat', usecols=(0,1,9), delimiter='\t', unpack=True, skiprows=1) #Grab RA, Dec., and K-mag from catalog
  n_gstars = len(gra)
  command_line_output = [] #Set up a list to hold strings for later command line output
  command_line_output.append('Guide stars found:')
  command_line_output.append('K-mag:\t sl: \t sw:')
  for i in range(n_gstars):
    print 'point('+str(gra[i])+','+str(gdec[i])+') # point=cross' 
    gstar_coords = coords(gra[i], gdec[i])
    gstar_dra_arcsec = ra_seperation(obj, gstar_coords, units='arcsec')
    gstar_ddec_arcsec = dec_seperation(obj, gstar_coords, units='arcsec')
    gstar_dx = ( -gstar_dra_arcsec*cos(radians(PA-45.0)) + gstar_ddec_arcsec*sin(radians(PA-45.0)) ) / plate_scale
    gstar_dy = ( gstar_dra_arcsec*sin(radians(PA-45.0)) + gstar_ddec_arcsec*cos(radians(PA-45.0)) ) / plate_scale
    gstar_sl =  -gstar_dra_arcsec*cos(radians(PA-90.0)) + gstar_ddec_arcsec*sin(radians(PA-90.0))
    gstar_sw =   gstar_dra_arcsec*sin(radians(PA-90.0)) + gstar_ddec_arcsec*cos(radians(PA-90.0))
    command_line_output.append("%7.2f" % gmag[i] +'\t'+ "%7.2f" % gstar_sl +'\t'+  "%7.2f" % gstar_sw)
    ds9.draw('fk5; point('+str(gra[i])+','+str(gdec[i])+') # point=cross font={helvetica 9 bold roman} color=yellow text={[K: '+str(gmag[i])+'; SL: '+"%5.2f" % gstar_sl+'; SW: '+"%5.2f" % gstar_sw+']}')
  print '\n\t'.join(command_line_output) #Output list of guide stars
else:
  ds9.set('catalog clear') #Clear 2MASS catalog
  ds9.set('catalog close') #Close 2MASS catalog window
  print 'ERROR: No possible guide stars found. Check mangitude, RA, & Dec limits and retry.'