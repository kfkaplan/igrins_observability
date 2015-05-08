#IGRINS Observability Version 1.4
Written by Kyle Kaplan (@kfkaplan)
Email: kfkaplan@astro.as.utexas.edu

This python program's main purpose is to create finder charts matching what
an observer at the Harlen J. Smith 2.7 meter telescope at McDonald 
Observatory sees in the FOV of the IGRINS Slit View Camera.

This program creates the following charts:
* Telescope observing limits chart showing RA and Dec.
* Altitude chart for target vs. LST showing the telescope observing limits
* Finder chart for IGRINS Slit View Camera

##Compatible Operating Systems
Should be compatible with any OS that can run python and DS9 from a
command line.

Successfully tested on Mac OS 10.6.8, 10.9.4
Unable to get to run on Windows (e-mail me if you can get it to work)
Probably will work on Linux machines, but untested.

##Requirements
* DS9 7.2 callable from the command line (might work on earlier
versions)
* XPA for allowing commands to be given to DS9 from the command line
* Python 2.6 or 2.7 (untested on other versions)
* Scipy
* Matplotlib

##Version Notes
###(Dec 2014) Changes since V1.4
* NEW FEATURE! Load input files from the command line! Thank you
Kevin Guillikson for adding this feature
* Coordinate grid is now displayed in DS9
* DS9 regions files are now movable by the user (previously this was
turned off)
* Bug fix: Declinations of -00 deg used to be read in as +00, now
should work fine

###(Sept. 2014) Changes since V1.3:
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

###(July 24, 2014) Changes since V1.2:
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

##How To Run
To run type:
"python observability.py"

You will be prompted to enter an input file
"Enter name of input file:"
so you will type in the name of the input file you would like to
    use...
"Enter name of intput file: input/star.inp"

##Making/Modifying Input Files

All the input files are stored in the "input" directory.
All user inputs must end with at leat one tab.
I will summarize the different parts of each input file below

The first set of options in the input file denote which charts the
    program will make.
If you are only interested in the finder charts, set the first two
    options to 'n' while leaving the third option set to 'y'.
###Select Charts To Display
  |Variable     |Description                                 |
  |:-----------:|--------------------------------------------|
  | y           |Show telescope Hour Angle observing limits. |
  | y           |Show altitude vs. Local Siderial Time plot <br> with telescope observing limits. <br>|
  | y           |Show finder chart for IGRINS Slit View <br> Camera FOV. |

Here the sky PA is the rotation of the slit counterclockwise from
    the North.
Below that is the target object where the slit is placed can be
    inputted by name '2' where the coordinates are grabbed online
    via seasme, or in RA and Dec. '1'.
The final line is where you input the name or coordinates of the
    target object.

###Information on Target

  155.0                 #Sky Position Angle (Start north and go east, N=0, E=90, S=180, W=270 degrees, Default = 90 deg slit oriented east-west)
  1                     #1=Input object as RA & Dec., 2=Input object name
  22:29:33.18 -20:47:58.4               #Object Coordinates in RA & Dec [hh:mm:ss.ss<space>+/-hh:mm:ss.s], or Object Name

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

###Information on Guide Star

  2 ~~~~~~~~~~~~~~~~~~~~~~~~~ #Input guide star as... 0=no guide
                               star, 1=dRA & dDec, 2=RA & Dec.,
                               3=guide star name, #4=automatically
                               find guide stars
  22:29:38.016 -20:52:16.36 ~ #Guide star offset in dRA & dDec
                               [arseconds<space>arcseconds],
                               coordinates in RA & Dec
                               [hh:mm:ss.ss<space>+/-hh:mm:ss.s],
                               or Name

If you want to use your own fits file for the finder charts in ds9,
    put the path here to the fits file, leave blank to default to
    the 2MASS K-band images

###User-Supplied FITS File
/path/to/image.fits    #Fits file path for making finder chart, leave blank if you just want to use 2MASS K-band

##Troubleshooting
* If you get an error on the function `name_query` or when trying to download a 2MASS image in DS9 you might need to connect to the internet.
 IGRINS Observability looks up names of objects and grabs 2MASS images from the web.  If you provide coordinates for your target, and your own
 FITS file, you can run IGRINS Observability offline.
* Sometimes 2MASS images don't fully cover the field of view.  This is a problem with how the 2MASS images
 are served over the internet to DS9, and cannot be easily fixed on our end.  If this is a major issue for you, you can create your own
 image mosiac (http://hachi.ipac.caltech.edu:8080/montage/), save it to your drive, and set it as the user supplied fits file.
 This is something I plan on fixing some point in the future.  If you know how to create 2MASS mosaics in python or DS9, please let me know.

Email me at kfkaplan@astro.as.utexas.edu if you have any issues or find a bug.

##Future Plans
* Integrate with the IGRINS Finder Chart Package (FCP) and/or Slit-View Camera Package (SCP)
    * It should probably be something simple like clicking a button and haveing a finder chart load up in DS9.
* Automatically load 2MASS mosiacs instead of the 2MASS strips currently used in DS9, to ensure full coverage of the FOV.
* Automated batch processing of a list of multiple targets, saving finder charts as image files.
