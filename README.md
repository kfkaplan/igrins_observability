# IGRINS Observability Version 1.7
Written by Kyle Kaplan (@kfkaplan)
Email: kfkaplan@email.arizona.edu

This python program's main purpose is to create finder charts matching what
an observer sees in the FOV of the IGRINS Slit View Camera at the Discovery 
Channel Telescope at Lowell Observtoary or the Harlen J. Smith 2.7 meter telescope at McDonald 
Observatory.

This program creates the following charts:
* Telescope observing limits chart showing RA and Dec.
* Altitude chart for target vs. LST showing the telescope observing limits
* Finder chart for IGRINS Slit View Camera

## Compatible Operating Systems
Should be compatible with any OS that can run python and DS9 from a
command line.

Successfully tested on Mac OS 10.6.8, 10.9.4, 10.11.5, 10.12.1, and 10.12.6.
Works on Linux, tested successfully on Ubuntu.
I have seen it work on Windows but am not exactly sure how to set it up (e-mail me if you have done this)

## Requirements
* DS9, callable from the command line.  The best version to currently use is the DS9 Version 7.6 http://ds9.si.edu/ (also works fine for some versions of DS9 7.2-7.4,
 but I have seen 7.4 this cause issues for some people, this is solved by using the 7.6)
* XPA for allowing commands to be given to DS9 from the command line
* Python 2.7 (untested on other versions)
* pyds9 (http://hea-www.harvard.edu/RD/pyds9/)
* Scipy
* Matplotlib

## Version Notes

### (May 2018) Changes for V1.7
* Switched from custom DS9 XPA commands to using pyds9 (http://hea-www.harvard.edu/RD/pyds9/).  For the code to run now, you need to install pyds9 on your system.  Switching to pyds9 increases compatibility with newer operating systems to ensure observabilty.py .
* Fixed issues with using 2MASS image mosaics for the finder charts.  They should work properly now if you were having issues.

### (October 2016) Changes for V1.6
* Updated to allow for use on multiple telescopes.  This primarily is set by the IGRINS SVC plate scale.  Current default is set for the DCT.  To change telescopes to 2.7m at McDonald or DCT, copy the text from options_mcd.inp or options_dct.inp to options.inp.  You can also modify options.inp to match any future telescope that IGRINS might be installed on.
* Increased resolution of mosaiced 2MASS images downloaded for finder charts.  Should make it easier to see things.


### (June 2016) Changes for V1.5
* 2MASS images are finally mosaiced! No more finder charts where only half of the field is shown.  This takes advantages of new features in the lastest version of DS9 so please make sure your DS9 is up to date.
* Updated rotation encoder at PA=90 deg. from 636 to 633 to now report the correct new encoder setting when IGRINS is mounted on the McDonald Observatory 2.7m telescope.
* Various other minor imporvements and bug fixes over the past year and a half.

### (Dec 2014) Changes since V1.4
* NEW FEATURE! Load input files from the command line! Thank you
Kevin Guillikson for adding this feature
* Coordinate grid is now displayed in DS9
* DS9 regions files are now movable by the user (previously this was
turned off)
* Bug fix: Declinations of -00 deg used to be read in as +00, now
should work fine

### (Sept. 2014) Changes since V1.3:
* NEW FEATURE! Automatically find guide stars by setting the input
 for guide star to 4 and displays them in DS9 and command line with
 K- mag, SL, SW
* NEW FEATURE! When automatically searching for guide stars, you can
 double click them to see some extra info (ie. K-mag, SL, SW, &
 coordinates)
* Change: Background regions (ie. SVC FOV, slit, & compass) do not
 move anymore.  You can still double click them and turn movement
 back on if you wish.
* Change: Streamlined and reordered a bunch of the code, commented it
 up so it is easier to understand what is going on.
* Bug fix: Set XPA to load immediately after opening DS9, eliminating
 the errors of XPA communicating with DS9 when program is first run,
 and speeding up code
* Bug fix: Fixed bug preventing user from specifying a guide star in
 arcsec. From target in RA and Dec.
* Bug fix: Fixed some minor typos
* Bug fix: Fixed a bug where program fails if RA seconds has a
 decimal < .1.

### (July 24, 2014) Changes since V1.2:
* Astropy is no longer required to run the code
* Added text output in ds9 showing slit view camera coordinates if
 using an off slit guide star
* Created library coordfuncs.py to take over the coordinate functions
 from astropy, it probably will prove useful in the future as a
 general spherical astronomy library
* Updated input file format to be less cluttered and more readable, if
 you have old input files you will need to change them to the new
 format
* Fixed a bug involving placement in RA of the guide star pointer in
 DS9 (this did not affect the printed out offsets on the command
 line)
* Fixed a bug where the slit was sometimes not placed exactly over the
 target coordinates
* Simplified some of the DS9 scripting
* Updated the DS9 region template text and colors to be a little
 easier on the eyes
* Corrected rotating the view in DS9 when loading user specified fits
 files



## How To Run
To run type:
"python observability.py"

You will be prompted to enter an input file
"Enter name of input file:"
so you will type in the name of the input file you would like to
    use...
"Enter name of intput file: input/star.inp"


## Making/Modifying Input Files

All the input files are stored in the "input" directory.
All user inputs must end with at leat one tab.
I will summarize the different parts of each input file below

The first set of options in the input file denote which charts the
    program will make.
If you are only interested in the finder charts, set the first two
    options to 'n' while leaving the third option set to 'y'.
### Select Charts To Display

  Value        |Description                                  
  :-----------:| -------------------------------------------- 
   y           | Show telescope Hour Angle observing limits.  
   y           | Show altitude vs. Local Siderial Time plot with telescope <br>  observing limits. 
   y           | Show finder chart for IGRINS Slit View Camera FOV. 

Here the sky PA is the rotation of the slit counterclockwise from
    the North.
Below that is the target object where the slit is placed can be
    inputted by name '2' where the coordinates are grabbed online
    via seasme, or in RA and Dec. '1'.
The final line is where you input the name or coordinates of the
    target object.

### Information on Target

  Value                     |Description                                  
  :------------------------:| -------------------------------------------- 
   155.0                    | Sky Position Angle (Start north and go east, N = 0, E = 90, S = 180, <br> W = 270 degrees, Default = 90 deg slit oriented east-west
   1                        | 1 = Input object as RA & Dec, 2 = Input object name 
   22:29:33.18 -20:47:58.4  | Object Coordinates in RA & Dec [hh:mm:ss.ss +/- hh:mm:ss.s], or Object Name

Here you specifiy if you don't want a guide star '0', want to input
    a guide star based on the distance in RA and Dec. in arcseconds
    from the target '1', inputting the RA and Dec. of the guidestar
    '2', or specifying a name for the guide star '3'.
To automatically find guide stars set this to '4'.  DS9 and the
    command line will then display the brightest possible nearby
    stars from the 2MASS point source catalog, along with the
    K-magnitude, distance from the target (SL and SW) and
    coordinates (command line only).
Below that you put in the name or coordinates for a guide star, if
    you are specifying one with option '1' or '2'.

### Information on Guide Star

  Value                     |Description                                  
  :--------------------------:| -------------------------------------------- 
   155.0                      | Sky Position Angle (Start north and go east, N = 0, E = 90, S = 180, <br> W = 270 degrees, Default = 90 deg slit oriented east-west
   2                          | Guide star input; 0 = no guide star, 1 = dRA & dDec, 2 = RA & Dec.,          <br> 3 = guide star name, 4 = automatically find guide stars 
   22:29:38.016 -20:52:16.36  | Guide star offset in dRA & dDec [arcseconds arcseonds], coordinates <br> in RA & Dec [hh:mm:ss.ss +/- hh:mm:ss.s], or Name

If you want to use your own fits file for the finder charts in ds9,
    put the path here to the fits file, leave blank to default to
    the 2MASS K-band images

### User-Supplied FITS File
/path/to/image.fits will fits file path for making finder chart, leave blank if you just want to use 2MASS K-band




## Setting which telescope to use and other  options
All telescope settings are stored in the "options.inp" file.
By default, the telescope used is the Discovery Channel Telescope (DCT). 

To set which telescope to use:
* Copy 'options_mcd.inp' to 'options.inp' to use the settings for the 2.7m telescope at McDonald Observatory.
* Copy 'options_dct.inp' to 'options.inp' to use the settings for the Discovery Channel Telescope.

The 'options.inp' file allows you change the following settings:

  Value                     |Description                                  
  :--------------------------:| -------------------------------------------- 
	333.0					  | Instrument rotator zero point (Default East-West setting has PA = 90 deg.)
	34.7444					  | Latitude of observatory (degrees north)
	-111.4222				  | Longitude of observatory  (degrees west)
	5.0						  | Set 2MASS image size to NxN arcmin
	k						  | Set 2MASS near-infrared band ('h','j','k'), default is K-band to match SVC filter
	0.0783					  | Slit View Camera plate-scale, arcsec per pixel, this will change the IGRINS SVC FOV and slit size
	14.0					  | Dimmest K-band mag. to search for guide stars, brighter stars are typically better for guiding
	2.0						  | Guide star search limit in RA in arcminutes from target, generally kept near the FOV limit
	2.0						  | Guide star search limit in Dec. in arcminutes from target, generally kept near the FOV limit
	20						  | Limit on number of brightest guide stars found near target (ie. 10 means find 10 the brightest stars)



## Troubleshooting
* If the DS9 regions (the slit, FOV, and directional compass) do not show up correctly, you are likely using version 7.4 (or older) of DS9.  If that is the case, I highly reccomend you update DS9 to the beta Version 7.5rc2 (or later) which should solve the problem.
* If you get an error on the function `name_query` or when trying to download a 2MASS image in DS9 you might need to connect to the internet.
 IGRINS Observability looks up names of objects and grabs 2MASS images from the web.  If you provide coordinates for your target, and your own
 FITS file, you can run IGRINS Observability offline.


Post an issue here on github or email me at kfkaplan@astro.as.utexas.edu if you have any issues or find a bug.

##Future Plans
* Integrate with the IGRINS Finder Chart Package (FCP) and/or Slit-View Camera Package (SCP)
    * It should probably be something simple like clicking a button and haveing a finder chart load up in DS9.
* Automated batch processing of a list of multiple targets, saving finder charts as image files.
