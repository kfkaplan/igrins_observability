''' Finder chart making program for IGRINS at the 2.7 m telescope at McDonald 
Observatory.
Created by Kyle F. Kaplan July 2014.
Program makes the following
    -telescope limitation HA chart
    -Altitude chart vs. LST showing telescope observing limits
    -Finder chart for IGRINS Slit View Camera'''

'''This function creates the region file for the IGRINS Slit View Camera (SVC) FOV
Rotation in Position Angle is accounted for via rotation matrix for the 
polygon used to represent the SVC FOV'''
def create_region_template(rotation, guidestar_dra, guidestar_ddec, guidestar_sl, guidestar_sw):
    default_slit_angle = 359.98672  #Default angle of the slit (East to west)
    x, y, poly_x, poly_y = loadtxt('scam-outline.txt', unpack=True) #Outline of SVC FOV, thanks to Henry Roe (private communication)
    poly_x = poly_x / 3600.0 #Convert arcseconds to degrees
    poly_y = poly_y / 3600.0
    # poly_x = [0.02714, 0.02712, 0.02593, 0.02462, 0.02412, 0.02422, 0.02429,  #Old polygon, now using new one from Henry Roe
    #           #Default x values for points in FOV polygon
    #           -0.00265, -0.02095, -0.02338, -0.02403, -0.02681, -0.02677, -0.02518,
    #           -0.02256, -0.01865, -0.01333, 0.0158, 0.0236]
    # poly_y = [-0.00825096, -0.00809768, -0.00462737, -0.00309165, 0.00030273, 0.00061059, 0.00618683,
    #           #Default y values for points in FOV polygon
    #           0.00582677, 0.00541191, 0.00319962, 0.00332299, -0.00340406, -0.00778661, -0.01318707,
    #           -0.01728969, -0.02215466, -0.02662075, -0.0258552, -0.01869832]
    rad_rot = radians(rotation)  #Convert degrees to radians for angle of rotation
    rotMatrix = array(
        [[cos(rad_rot), -sin(rad_rot)], [sin(rad_rot), cos(rad_rot)]])  #Set up rotation matrix for polygon
    [poly_x, poly_y] = rotMatrix.dot([poly_x, poly_y])  #Apply rotation matrix to the FOV polygon
    poly_xy = '('  #Make string to output for polygon points
    n = size(poly_x)  #Find number of points in polygon
    for i in range(n - 1):  #Loop through points 0 -> n-2
        poly_xy = poly_xy + str(poly_x[i]) + ', ' + str(poly_y[i]) + ', '
    poly_xy = poly_xy + str(poly_x[n - 1]) + ', ' + str(
        poly_y[n - 1]) + ')'  #Give final point the special format it needs
    total_slit_angle = longitude(default_slit_angle - rotation)  #Calculate angle to rotate slit box
    slit_angle = str(total_slit_angle.deg())  #Convert slit angle after applying rotation of IGRINS to a string
    output = []  #Set up array to output lines of text to region tmeplate file, as strings appended to the array
    output.append('# Region file format: DS9 version 4.1')  #Output top line to region file
    output.append(
        'global color=green dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1')  #Set up color, fonts, and stuff
    output.append('wcs0;fk5')  #Set coordinate system
    output.append(
        '# compass(0,0,72") compass=fk5 {N} {E} 1 1 font="helvetica 12 bold roman" color=blue fixed=0')  #Set compass (North and East arrows)
    output.append('box(0,0,15",1",' + slit_angle + ') # color=green width=2')  #Display slit
    if abs(guidestar_dra) > 0. or abs(guidestar_ddec) > 0.:  #show guidestar if it exists
        output.append('point(' + str(guidestar_dra) + ',' + str(
            guidestar_ddec) + ') # point=circle font="helvetica 12 bold roman" color=yellow text={Offslit guide star [sl: ' + "%5.2f" % gstar_sl + ', sw:' + "%5.2f" % gstar_sw + ']}')
    output.append('polygon' + poly_xy)  #Save SVC FOV polygon
    savetxt('IGRINS_svc_generated.tpl', output, fmt="%s")  #Save region template file for reading into ds9


#Import Python Libraries
from pdb import set_trace as stop  #Use stop() for debugging
from scipy import *  #Import scipy
import matplotlib.pyplot as plt  #Import matplotlib's plotting routines
from scipy.interpolate import \
    InterpolatedUnivariateSpline  #Import interpolation for interpolating telescope HA & Dec. observing limits
from coordfuncs import *  #Import coordfuncs for handing spherical astronomy and coordinates
import ds9  #Import wrapper for allowing python script DS9 with XPA
import sys

#Read in telescope options input
input_file = 'options.inp'  #Path to options file
paths = open(input_file)  #open options file
skip = paths.readline()  #Skip first line of options list
rotator_zero_point = float(str.strip(paths.readline().split('\t')[0]))  #Zero point for the rotator where PA=90 degrees
observatory_latitude = float(
    str.strip(paths.readline().split('\t')[0]))  #Latitude of the observatory (probably never need to change)
observatory_longitude = float(
    str.strip(paths.readline().split('\t')[0]))  #Longitude of the observatory (probably never need to change)
img_size = float(str.strip(paths.readline().split('\t')[0]))  #test setting image size to NxN arcminutes
band = str.strip(paths.readline().split('\t')[0])  #Test setting to a 2MASS band
plate_scale = float(str.strip(paths.readline().split('\t')[0]))  #arcseconds per pixel on the Slit View Camera
gstar_mag_limit = float(str.strip(
    paths.readline().split('\t')[0]))  #When searching for guide stars, msut be brighter than this K-band mag. limit
gstar_ra_limit = float(str.strip(paths.readline().split('\t')[0]))  #arcmin limit in RA for searching for guide stars
gstar_dec_limit = float(str.strip(paths.readline().split('\t')[0]))  #arcmin limit in RA for searching for guide stars
n_gstars = int(
    str.strip(paths.readline().split('\t')[0]))  #Number of brightest guide stars to find when searching for guide stars
paths.close()  #close options file

#Read in stuff from input file, see input file comments for more info
if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    while True:
        try:
            input_file = raw_input('Enter input file name: ')
            break
        except IOError: 
            print('Error: could not find file.')



paths = open(input_file)  #Open input file
skip = paths.readline()  #skip line
skip = paths.readline()  #skip line
show_telescope_limits = str.strip(paths.readline().split('#')[0])  #y/n display telescope HA & Dec. limits
show_altiutde_chart = str.strip(paths.readline().split('#')[0])  #y/n display telescope altitude chart
show_finder_chart = str.strip(paths.readline().split('#')[0])  #y/n display SVC FOV finder chart in DS9
skip = paths.readline()  #skip line
PA = float(str.strip(paths.readline().split('#')[0]))  #PA of slit on sky
obj_choice = str.strip(paths.readline().split('#')[0])  #number for type of object input
obj_input = str.strip(paths.readline().split('#')[0])  #object input (ie. name or coordinates)
skip = paths.readline()  #skip line
gstar_choice = str.strip(paths.readline().split('#')[0])  #number for type of input for offslit guidestar(s)
gstar_input = str.strip(paths.readline().split('#')[0])  #Offslit guide star input (ie. name or coords)
skip = paths.readline()  #skip line
finder_chart_fits = str.strip(paths.readline().split('#')[0])  #path to user supplied fits file
paths.close()  #Close input file

#Set rotator variables
delta_PA = 90.0 - PA  #Default instrument East-west setting is 90 degrees in PA
rotator_setting = rotator_zero_point - delta_PA  #Calculate setting to put the rotator at for a given PA
if rotator_setting > rotator_zero_point + 180.0: rotator_setting = rotator_setting - 360.0  #Force rotator to be +/- 180 deg from the default PA
gstar_dra_arcsec = 0.0  #Initialize these variables, if no guide star is used, just keep them zero
gstar_ddec_arcsec = 0.0
gstar_dra_deg = 0.0
gstar_ddec_deg = 0.0
gstar_sl = 0.0
gstar_sw = 0.0
command_line_output = []  #Set up a list to hold strings for later command line output


#Set up location of observatory from user inputted longitude and latitude
observatory_location = location(observatory_longitude, observatory_latitude)

#Grab object RA and Dec. from either user inputted name or user inputted coordinates
if obj_choice == '1':  #If user inputs object coordinates, set object class with RA and Ddec.
    obj_coords = coord_query(obj_input)
else:  #If user inputs object name, set object class by looking up the name of the object on the internet
    obj_coords = name_query(obj_input)
gstar_coords = obj_coords  #put something in variable to just get through silly errors


#Read in table of telescope limits
#User inputs RA & Dec., program outputs range in LST observable
#    HA=hour angle, RA = right ascention, LST = local siderial time
#      LST = HA + RA
read_limits_dec, read_limits_HA_min, read_limits_HA_max = loadtxt('observing_limit_table.txt', dtype='f4,f4,f4',
                                                                  unpack=True)  #Read in text file giving HA limits to the 2.7m scope
splinefit = InterpolatedUnivariateSpline(read_limits_dec, read_limits_HA_min)  #Do spline fit for HA min.
HA_min = splinefit(obj_coords.dec.deg())  #Find value of HA min for object's given dec from spline interopolation
splinefit = InterpolatedUnivariateSpline(read_limits_dec, read_limits_HA_max)  #Do spline fit for HA max.
HA_max = splinefit(obj_coords.dec.deg())  #Find value of Ha max for object's given dec from spline interopolation
LST_min = longitude(obj_coords.ra.hour() + HA_min,
                    units='hour')  #Calculate min and max Local Siderial time: LST = RA - HA
LST_max = longitude(obj_coords.ra.hour() + HA_max, units='hour')

#Plot radial plot of telescope hour angle limits
if show_telescope_limits == 'y':  #if user says yes to plotting telescope hour angle limits
    radplot = plt.subplot(111, polar=True)  #set up object for making a radial plot
    for i in arange(0, 2 * pi, pi / 12):  #Loop to add in more radial lines for each hour
        radplot.plot([i] * 19, arange(-120, 70, 10), linewidth=1, linestyle=':', color='gray')
    radplot.plot((pi / 2) + read_limits_HA_min * 2 * pi / 24, -read_limits_dec, color='blue',
                 linewidth=2)  #plot observing limits
    radplot.plot((pi / 2) + read_limits_HA_max * 2 * pi / 24, -read_limits_dec, color='blue', linewidth=2)
    radplot.plot(arange(0, 2 * pi, 2 * pi / 100), [-obj_coords.dec.deg()] * 100, color='red', linewidth=3)
    radplot.set_ylim(-120, 60)  #Set radial units
    radplot.set_yticks(arange(-120, 60, 20))  #Set tick marks for radial units
    radplot.set_yticklabels(map(str, arange(120, -60, -20)))  #label radial units
    radplot.set_xticklabels(['-6 HA', '-3 HA', '0 HA', '3 HA', '6 HA', '9 HA', ' ', '-9 HA'])  # Label HA units
    radplot.set_title('107'' (2.7 m) Observing Limit Chart')  #Title of plot
    plt.show()  #show plot

#Plot a simple altitude vs. LST map, also showing telescope observing limits (in LST)
if show_altiutde_chart == 'y':
    LST = arange(0, 23.9, 0.0166666667)  #Make an array for the LST with a point for every minute
    alt = alt(obj_coords, observatory_location, LST)  #Grab altitude of object in the sky
    airmass = 1.0 / cos(radians(90.0 - alt))  #Calculate airmass
    #alt_arr = arange(0,90,10)
    #airmass_arr = 1.0/cos(radians(90.0 - alt_arr))
    plt.plot(LST, alt)  #Plot altitude vs. LST
    plt.plot([LST_min.hour(), LST_min.hour()], [0, 90], color='red')  #Overplot LST limits telescope can observe object
    plt.plot([LST_max.hour(), LST_max.hour()], [0, 90], color='red')
    #plt.xlim(LST_min.hour-2.0,LST_max.hour+2.0)
    #plt.yticks(alt_arr, "%.2f" % airmass_arr) #set ticks to be airmass instead of altitude
    plt.ylim(0, 90)  #Set y axis to be limited to altiude of 0-90 degrees
    plt.xlabel('LST', fontsize=18)  #X-axis label
    plt.ylabel('Altitude', fontsize=18)  #Y-axis label
    plt.grid(color='gray')  #Set up gray background grid to help you use your eye to find things
    plt.title('Object visible between LST:  ' + LST_min.hm() + ' ---> ' + LST_max.hm())  #plot title
    plt.show()  #show plot

#Load up DS9 and create a finder chart
if show_finder_chart == 'y':
    ds9.open()  #Open DS9
    #ds9.wait(2.0) #Used to be needed, commented out for now because I think I fixed this bug and can now speed things up
    ds9.set('single')  #set single display mode
    if finder_chart_fits == '':  #Use 2MASS K-band if no user specified fits file is found
        ds9.set('2mass survey ' + band)  #Load 2MASS survey
        ds9.set('2mass size ' + str(img_size) + ' ' + str(
            img_size) + ' arcmin')  #Set size of image (weird issues here, only strips extracted)
        if obj_choice == '2':  #If user specifies object name
            ds9.set('2mass name ' + obj_input.replace(" ", "_"))  #Retrieve 2MASS image
        else:  #If user specifies object coordiantes
            ds9.set('2mass coord ' + str(obj_coords.ra.deg()) + ' ' + str(
                obj_coords.dec.deg()) + ' degrees')  #Retrieve 2MASS image
        ds9.set('2mass close')  #Close 2MASS window
    else:  #If user does specify their own fits file, use it
        ds9.set('fits ' + finder_chart_fits)  #Load fits fits file
    ds9.set('scale log')  #Set view to log scale
    ds9.set('scale Zmax')  #Set scale limits to Zmax, looks okay

    #Grab guide star RA and Dec. from user input if specified
    if gstar_choice == '1':  #Grab guide star coordinates from dRA & dDec input in arcseconds (distance guide star is from target in arcseconds)
        dra, ddec = gstar_input.split(' ')  #Sepearte delta RA and Dec. by a space entered by the user
        dra = float(dra) / 3600.0  #Convert arcseconds to degrees
        ddec = float(ddec) / 3600.0  #convert arcseconds to degrees
        gstar_coords = coords(obj_coords.ra.deg() + dra / obj_coords.dec.cos(), obj_coords.dec.deg() + ddec)
    elif gstar_choice == '2':  #Grab guide star coordinates from RA & Dec input
        gstar_coords = coord_query(gstar_input)
    elif gstar_choice == '3':  #Grab guide star coordinates from name lookup on internet
        gstar_coords = name_query(gstar_input)

    if gstar_choice != '0' and gstar_choice != '4':  #If single guide star actually put in by user calculate the following parameters...
        gstar_dra_arcsec = ra_seperation(obj_coords, gstar_coords,
                                         units='arcsec')  #position of guide star from object in arcseconds
        gstar_ddec_arcsec = dec_seperation(obj_coords, gstar_coords,
                                           units='arcsec')  #position of guide star from object in arcseconds
        gstar_dra_deg = gstar_dra_arcsec / 3600.0  #position of guide star from object in degrees
        gstar_ddec_deg = gstar_ddec_arcsec / 3600.0  #position of guide star from object in degrees
        gstar_dx = (-gstar_dra_arcsec * cos(radians(PA - 45.0)) + gstar_ddec_arcsec * sin(
            radians(PA - 45.0)) ) / plate_scale  #guide star position in pixels in the SVC display
        gstar_dy = (gstar_dra_arcsec * sin(radians(PA - 45.0)) + gstar_ddec_arcsec * cos(
            radians(PA - 45.0)) ) / plate_scale  #guide star position in pixels in the SVC display
        gstar_sl = -gstar_dra_arcsec * cos(radians(PA - 90.0)) + gstar_ddec_arcsec * sin(
            radians(PA - 90.0))  #guide star position relative to slit in arcseconds
        gstar_sw = gstar_dra_arcsec * sin(radians(PA - 90.0)) + gstar_ddec_arcsec * cos(
            radians(PA - 90.0))  #guide star position relative to slit in arcseconds

    create_region_template(delta_PA, gstar_dra_deg, gstar_ddec_deg, gstar_sl,
                           gstar_sw)  #Make region template file rotated and the specified PA
    ds9.set(
        'regions template IGRINS_svc_generated.tpl at ' + obj_coords.showcoords() + ' fk5')  #Read in regions template file
    ds9.set('regions select all')
    ds9.set('regions group FOV new')
    ds9.set('regions select none')  #Deslect regions when finished
    ds9.set(
        'align yes')  #Set north to be up and east to be left, before rotating, for weird fits files that open at odd angles
    ds9.rotto(-45 + delta_PA)  #Set orientation to match IGRINS guider
    ds9.set('pan to ' + obj_coords.showcoords() + ' wcs fk5')  #Center frame on target object
    ds9.set('zoom 0.8')  #Try to set the zoom to easily see the IGRINS FOV
    ds9.set('mode pointer')  #Go to this standard editing mode in DS9

    if gstar_choice == '4':  #If user specifies code to find guide stars automatically
        gstar_dec_limit = gstar_dec_limit / (2.0 * 60.0)  #Convert limit in Dec. to degrees
        gstar_ra_limit = gstar_ra_limit / (2.0 * 60.0 * obj_coords.dec.cos())  #Convert limit in RA to degrees
        ds9.set('catalog 2mass')  #Initialize catalog
        ds9.set("catalog filter '$RAJ2000>=" + str(obj_coords.ra.deg() - gstar_ra_limit) + "&&$RAJ2000<=" + str(
            obj_coords.ra.deg() + gstar_ra_limit) \
                + "&&$DEJ2000>=" + str(obj_coords.dec.deg() - gstar_dec_limit) + "&&$DEJ2000<=" + str(
            obj_coords.dec.deg() + gstar_dec_limit) \
                + "&&$Kmag<=" + str(gstar_mag_limit) + "'")  #Load catalog
        ds9.set(
            "catalog sort 'Kmag' incr")  #Sort list by starting from brightest K-band mag. and getting dimmer as you go down
        ds9.set("catalog export tsv tmp.dat")  #Save catalog list as a tab seperated value file for later trimming
        lines = open('tmp.dat').readlines()  #Open catalog list tsv file into memory
        if len(lines) > 1:
            open('tmp.dat', 'w').writelines(
                lines[0:n_gstars + 1])  #Truncate by maximum number of guide stars and save catalog list
            ds9.set('catalog clear')  #Clear 2MASS catalog
            ds9.set('catalog close')  #Close 2MASS catalog window
            ds9.set('catalog import tsv tmp.dat')  #Load only brightest stars to be potential guide stars
            ds9.set(
                'mode catalog')  #Set mode to catalog so user can click on possible guide stars and look at their stats
            gra, gdec, gmag = loadtxt('tmp.dat', usecols=(0, 1, 9), delimiter='\t', unpack=True,
                                      skiprows=1)  #Grab RA, Dec., and K-mag from catalog
            n_gstars = len(gra)  #reset n_gstars to the actual number of guide stars found
            command_line_output.append('Guide stars found:')  #Output for command line
            command_line_output.append('K-mag:\t sl: \t sw: \t\t Coordinates (J2000):')  #Output for command line
            for i in range(n_gstars):  #Loop through each guide star found and
                gstar_coords = coords(gra[i], gdec[i])
                found_gstar_dra_arcsec = ra_seperation(obj_coords, gstar_coords,
                                                       units='arcsec')  #position of guide star from object in arcseconds
                found_gstar_ddec_arcsec = dec_seperation(obj_coords, gstar_coords,
                                                         units='arcsec')  #position of guide star from object in arcseconds
                gstar_dx = (-found_gstar_dra_arcsec * cos(radians(PA - 45.0)) + found_gstar_ddec_arcsec * sin(
                    radians(PA - 45.0)) ) / plate_scale  #guide star position in pixels in the SVC display
                gstar_dy = (found_gstar_dra_arcsec * sin(radians(PA - 45.0)) + found_gstar_ddec_arcsec * cos(
                    radians(PA - 45.0)) ) / plate_scale  #guide star position in pixels in the SVC display
                gstar_sl = -found_gstar_dra_arcsec * cos(radians(PA - 90.0)) + found_gstar_ddec_arcsec * sin(
                    radians(PA - 90.0))  #guide star position relative to slit in arcseconds
                gstar_sw = found_gstar_dra_arcsec * sin(radians(PA - 90.0)) + found_gstar_ddec_arcsec * cos(
                    radians(PA - 90.0))  #guide star position relative to slit in arcseconds
                command_line_output.append("%7.2f" % gmag[
                    i] + '\t' + "%7.2f" % gstar_sl + '\t' + "%7.2f" % gstar_sw + '\t\t' + gstar_coords.showcoords())  #Save info on found guide stars to the command line
                ds9.draw('fk5; point(' + str(gra[i]) + ',' + str(
                    gdec[i]) + ') # point=cross font={helvetica 9 bold roman} color=yellow text={[K: ' \
                         + str(gmag[
                    i]) + '; SL: ' + "%5.2f" % gstar_sl + '; SW: ' + "%5.2f" % gstar_sw + ']}')  #Put pointer regions to guide stars in DS9
        else:
            ds9.set('catalog clear')  #Clear 2MASS catalog
            ds9.set('catalog close')  #Close 2MASS catalog window
            print 'ERROR: No possible guide stars found. Check target position and then the mangitude, RA, & Dec limits in options.inp and retry.'



#Print results to command line
print ''
print 'Object coordiantes (J2000):'
print '	' + obj_coords.showcoords()
#Display HH:MM for LST mins and maxes this object can be observed at
print 'Object between the following Local Siderial Times:  '
print '	', LST_min.hm() + ' ---> ' + LST_max.hm()
print 'Rotator setting should be: '
print '	', rotator_setting
if gstar_choice != '0' and gstar_choice != '4' and show_finder_chart == 'y':  #If guide star actually put in
    print 'Guide star:'
    print '	ddra: ', "%7.2f" % gstar_dra_arcsec, ', ddec:', "%7.2f" % gstar_ddec_arcsec
    print '	  dx: ', "%7.2f" % gstar_dx, ',   dy: ', "%7.2f" % gstar_dy
    print '	  sl: ', "%7.2f" % gstar_sl, ',   sw: ', "%7.2f" % gstar_sw
if gstar_choice == '4' and show_finder_chart == 'y':
    print '\n\t'.join(command_line_output)  #Output list of guide stars

#ds9.set('regions group FOV property move no') #Make FOV unmoveable, might change this later if this causes issues with folks
ds9.set('regions group FOV moveback') #move regions such as the FOV, slit, compass, etc. to the back so the user can select guide star points
ds9.set('mode pointer') #Go back to pointer mode when finished with everything

#Load coordinate grid and save finder chart as .eps file, EXPERIMENTAL FEATURE
ds9.set('colorbar no')
ds9.set('grid on')
#ds9.set('grid type publication')
ds9.set('grid sky fk5')
#ds9.set('grid color red')
ds9.set('grid grid color red')
#ds9.set('grid title def no')
#ds9.set('grid title text {'+object+'}')
#ds9.set('grid numerics type exterior')
ds9.set('grid numerics color red')
#ds9.set('grid axes type exterior')
ds9.set('zoom 0.7')
#ds9.set('saveimage eps finderchart.eps')
output_image = '{:s}.eps'.format(obj_input.replace(' ', '_'))
ds9.set('saveimage eps {:s}'.format(output_image))

