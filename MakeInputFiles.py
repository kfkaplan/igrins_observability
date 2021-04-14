import sys


def OutputFile(outfilename, starname):
    outlines = ["#Input file for making finder and observability charts\n",
                "#--------------------Select Charts To Display---------------------------------------\n",
                "n                       #Show telescope Hour Angle observing limits\n",
                "y                       #Show altitude vs. Local Siderial Time plot with telescope observing limits\n",
                "y                       #Show finder chart for IGRINS Slit View Camera FOV\n",
                "#--------------------Target Info------------------------------------------\n",
                "90.0                    #Sky Position Angle (Start north and go east, N=0, E=90, S=180, W=270 degrees, Default = 90 deg slit oriented east-west)\n",
                "2                       #1=Input object as RA & Dec., 2=Input object name\n",
                "{0:s}            #Object Coordinates in RA & Dec [hh:mm:ss.ss<space>+/-hh:mm:ss.s], or Object Name\n".format(starname),
                "#--------------------Guide Star Info---------------------------------------\n",
                "0                       #Input guide star as... 0=no guide star, 1=dRA & dDec, 2=RA & Dec., 3=guide star name, #4=automatically find guide stars\n",
                "                        #Guide star offset in dRA & dDec [arseconds<space>arcseconds], coordinates in RA & Dec [hh:mm:ss.ss<space>+/-hh:mm:ss.s], or Name\n",
                "#--------------------User Supplied FITS File---------------------------------------\n",
                "                        #Fits file path for making finder chart, leave blank if you just want to use 2MASS K-band\n"]

    outfile = open(outfilename, "w")
    outfile.writelines(outlines)
    outfile.close()



if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("This script will create input files that are usable by observability.py")
        print("type 'python MakeInputFiles.py csvfile [options]', where csvfile is the")
        print("  filename of a comma-separated value table, and options are:")
        print("\n")
        print("-skip=n :  skip the n first lines of the table (contains header info or ")
        print("           something. Defaults to 1")
        print("-delim=c : set the delimiter to the character 'c' (can be whatever you want)")
        print("           Defaults to a comma")
        print("-col=i :   The name of the star is in the ith column, starting at 0. ")
        print("           Defaults to 1.")
    else:
        skip = 1
        delim = ","
        col = 1
        for arg in sys.argv[1:]:
            if "-skip" in arg:
                skip = int(arg.split("=")[-1])
            elif "-delim" in arg:
                delim = arg.split("=")[-1]
            elif "-col" in arg:
                col = int(arg.split("=")[-1])
            else:
                target_file = arg
        infile = open(target_file)
        lines = infile.readlines()
        infile.close()

        for line in lines[skip:]:
            segments = line.split(delim)
            starname = segments[col].strip('"').strip()
            print(starname)
            OutputFile("input/{:s}.inp".format(starname.replace(" ", "_")), starname)
