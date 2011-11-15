#!/usr/bin/env python

# $Id: crossCommonLineSearch.py,v 1.29 2006/05/14 18:43:11 wjiang Exp $


import sys
import glob
import os
import copy
import time
import random
from math import *
import string
import re
try:
	from optparse import OptionParser
except:
	from optik import OptionParser
try:
	import mpi
except:
	mpi = None
import ConfigParser
		
import EMAN

def parse_command_line():
	usage="Usage: %prog <Raw image filename 1> ... <Raw image filename n> <reference filename> [options]"
	parser = OptionParser(usage=usage)

	parser.add_option("--createconfigFile",dest="createconfigFile",type="string",help="use to create a configure file under a given directory and file name (Default file name is [./ccmlConfigFile.ini])", default="./ccmlConfigFile.ini")
        parser.add_option("--configFile",dest="configFile",type="string",help="all/parts of the parameters can be read from this file. command line parameters have higher priority, but it will be enforced to use if an 'endforce' is followed by the corresponding values. (Default file name is [./ccmlConfigFile.ini])", default="./ccmlConfigFile.ini")
        parser.add_option("--saveParms",dest="saveParms",type="string",help="if a file name is given, the actually parameters will be saved to the file. (default is not save if no name)", default="")

	#options
	parser.add_option("--sym",dest="sym",type="string",help="set symmetry of the particle, (default is \"icos\")",default="icos")
	parser.add_option("--rMask",dest="rMask",type="int",help="Mask will be applied to image center. The radial size = rMask, [half image size]",default=0)
	parser.add_option("--rMask1",dest="rMask1",type="int",help="Mask will be applied to solved particle center. The radial size = rMask1, [rMask]",default=0)
	parser.add_option("--startNum",dest="startNumOfRawImages",type="int",help="The starting image number",default=0)
	parser.add_option("--endNum",dest="endNumOfRawImages",type="int",help="The ending image number, (0 is default, all images)",default=0)
	parser.add_option("--numOfRefImages",dest="numOfRefImages",type="int",help="Number of projection images to use for calculating orientation, (5 is default)",default=5)
	parser.add_option("--scatteringFactorFile",dest="sfFileName",type="string",help="File name for scattering factor of raw images",default="")
	parser.add_option("--phasecorrected",dest="phasecorrected",action="store_true",help="if the particle images already phase flipped. default to false", default=0)
	parser.add_option("--overSample",dest="FFTOverSampleScale",type="int",help="Scale of over sample FFT, (1 is default, NO over sample)",default=1)
	parser.add_option("--pftStepSize",dest="pftStepSize",type="float",help="Angular step size for creating pseudo PFT, (0.1 degree is default)",default=0.1)
	parser.add_option("--radialStepSize",dest="deltaR",type="float",help="Radial step size for collecting data on common line, (1.0 is default)",default=1.0)
	parser.add_option("--radialStartPoint",dest="RMin",type="int",help="Radial start point for collecting data on common line, (5 is default)",default=5)
	parser.add_option("--radialEndPoint",dest="RMax",type="int",help="Radial end point for collecting data on common line, (35 is default)",default=35)
	#parser.add_option("--maskRadius",dest="maskR",type="int",help="Mask radius to remove background pixels at large radius (default to half of image size)",default=0)
	parser.add_option("--orientationSearchRange",dest="orientationSearchRange",type="float",help="Maximum orientation deviation from a given one, (36.0 is default)",default=36.0)
	parser.add_option("--centerSearchRange",dest="centerSearchRange",type="float",help="Maximum center deviation from a given one, (15.0 is default)",default=15.0)
	parser.add_option("--maxIteration",dest="maxNumOfIteration",type="int",help="Maximum iteration, (1000 is default for coarse search, 150 for refinement)",default=150)
	parser.add_option("--numOfRandomJump",dest="numOfRandomJump",type="int",help="iteration of beginning random jump, (50 is default for coarse search, 20 for refinement)",default=20)
	parser.add_option("--numOfFastShrink",dest="numOfFastShrink",type="int",help="iteration of ending fast shrink, (150 is default for coarse search, 80 for refinement)",default=80)
	parser.add_option("--numOfStartConfigurations",dest="numOfStartConfigurations",type="int",help="starting configurations, (10 is default)",default=10)
	parser.add_option("--searchMode",dest="searchMode",type="int",help="Mode to handle a raw image, (0 is default)",default=0)
	parser.add_option("--scalingMode",dest="scalingMode",type="int",help="Mode to handle a raw image, (0 is default)",default=0)
	parser.add_option("--residualMode",dest="residualMode",type="int",help="Mode to calculate residual, (2 is default)",default=2)
	parser.add_option("--weightMode",dest="weightMode",type="int",help="Weighting function mode to calculate residual, default to 1",default=1)
	parser.add_option("--iniParameterFile",dest="rawImageIniParmFN",type="string",help="File name for initial orientation and center of raw images",default="")
	parser.add_option("--refEulerConvention",dest="refEulerConvention",type="choice",choices=["eman","mrc"],help='Spcify an euler convention of the refence orientation. choices are ["eman","mrc"]. default to "eman"',default="eman")
	parser.add_option("--iniCenterOrientationMode",dest="iniCenterOrientationMode",type="choice",choices=["random","headerfile","iniparmfile"],help='mode to initialize particle center and orientation. choices are  ["random","headerfile","iniparmfile"]. default to "random"',default="random")
	parser.add_option("--refCenterOrientationMode",dest="refCenterOrientationMode",type="string",help="mode to set reference center and orientation of the particle [copy from ini]",default="")
	parser.add_option("--zScoreCriterion",dest="zScoreCriterion",type="float",help="The criterion of stopping run, (6.0 is default)",default=6.0)
	parser.add_option("--residualCriterion",dest="residualCriterion",type="float",help="The criterion of stopping run, (default: no residual criterion)",default=-1.0)
	parser.add_option("--solutionCenterDiffCriterion",dest="solutionCenterDiffCriterion",type="float",help="The criterion of stopping run, (default: no solution center diff criterion)",default=-1.0)
	parser.add_option("--solutionOrientationDiffCriterion",dest="solutionOrientationDiffCriterion",type="float",help="The criterion of stopping run, (default: no solution orientation diff criterion)",default=-1.0)
	parser.add_option("--numConsistentRun",dest="numConsistentRun",type="int",help="number of runs with consistent orienttion/center to accept as success. default to 2", default=2)
	parser.add_option("--maxNumOfRun",dest="maxNumOfRun",type="int",help="Maximum number of re-search, (5 is default)",default=5)
	parser.add_option("--updateHeader", dest="updataHeader",type="int", help="Write the calculated result to the header file, (default is O, NO update)",default=0)
	parser.add_option("--solutionFile",dest="solutionFile",type="string",help="File name for outputing results, (default is Raw image filename + \"-OrientationCenter.dat\")",default="")
	parser.add_option("--mrcSolutionFile",dest="mrcSolutionFile",type="string",help="File name for outputing results in MRC format, (default is Raw image filename + \"-MRC-OrientationCenter.dat\") ",default="")
	parser.add_option("--listFile",dest="listFile",type="string",help="File name for listing good particles in EMAN LST format",default="")
	parser.add_option("--scoreFile",dest="scoreFile",type="string",help="File name for the defocus and residual values of good particles in EMAN LST format",default="")
	parser.add_option("--verbose", dest="verbose",type="int", help="verbose level [0-5], (default is O, no screen print out)",default=0)
	parser.add_option("--nolog",dest="nolog",action="store_true",help="don't log the command in .emanlog", default=0)

	if(len(sys.argv) > 1) : #for creating configure file
		configFileName = ""
		if (sys.argv[1] == "--createconfigFile" ) or (sys.argv[1] == "--createconfigFile=" ) : configFileName = "./ccmlConfigFile.ini" #default value
		elif re.match("--createconfigFile=",sys.argv[1]) : #if specified
			splitPosition = re.match("--createconfigFile=",sys.argv[1]).end()
			configFileName = sys.argv[1][splitPosition:]
		if configFileName != "" : createConfigureFile(configFileName) #create the configure file, then quite the program


	(options, args)=parser.parse_args() #this is first parse the command line inputs, later a pseudo command line option will be parsed

	allAdoptedOptions = {} #make a dictionary for saving the final adopted options which combines the command line options and the options form configure file
	for aArg in sys.argv[1:] : 
		if re.match('--.*.=', aArg) :
			splitPosition = re.match('--.*.=', aArg).end()
			allAdoptedOptions[aArg[2:(splitPosition-1)]] = aArg[splitPosition:]
		elif re.match('--.*.', aArg) :
			allAdoptedOptions[aArg[2:]] = ""


	if not os.path.exists(options.configFile) : #check if the default or given configure file is exist or not
		if options.configFile != "./ccmlConfigFile.ini" : 
			print "The configure file : %s does NOT exist, QUIT the program!!!" % (options.configFile)
			sys.exit(-1)
	else :

		config = ConfigParser.ConfigParser()
		config.optionxform = str #output case-sensitive options
		config.read(options.configFile)

	        tempListCommandParms = []
		tempListArgs = []
		tempRefImg = ""
                tempListOptions = []
		rawImgEnforced = False
		refImgEnforced = False
		tempListOptions.append("--%s=%s" % ("configFile",options.configFile)) #set value for configFile option
		for section in config.sections(): #parse the configure file
        		for option in config.options(section):
				#print option, " = ", config.get(section, option)
				values = config.get(section, option).replace(","," ").split()
				if len(values)==0 : continue  # if give nothing, it will be ignored
				if values[0][0] == ";" or values[0][0] == "#" : continue  #sometimes, no value given, the parse will take comments as its value
				enforced = False
				if len(values) > 1 and re.search('enforce', values[-1]) : enforced = True  #detect if this value will be enforced to replace the command line value
				if re.search('option',section.lower()) :
					if ((values[0].lower == 'yes') or (values[0].lower == 'true')) : values[0]='True' 
                                        if ((values[0].lower == 'no') or (values[0].lower == 'false')) : values[0]='False'
					if not allAdoptedOptions.has_key(option) : allAdoptedOptions[option] = values[0] #if not specified in command line, add this option
					elif enforced : allAdoptedOptions[option] = values[0]                             #if enforced, this option will replce the corresponding command line's value
				if re.search('require',section.lower()) : #for required arguments in configure file
                                        if  re.match('raw.*.image.*.file', string.join(option.split(), sep=" ").lower()) : #remove all unneccessary spaces and convert to lower cases
						if enforced : 
							rawImgEnforced = True 
							tempListArgs = values[:-1]
						else :  tempListArgs = values  #raw images could be in multiple files
					if  re.match('ref.*.image.*.file', string.join(option.split(), sep=" ").lower()) : 
                                                if enforced : refImgEnforced = True
						tempRefImg = values[0] #for reference image
		argsFinal = []
		if len(args) == 0 :
                        argsFinal = tempListArgs
			argsFinal.append(tempRefImg)
		if len(args) == 1 :
			if not rawImgEnforced: 
				argsFinal = args
				argsFinal.append(tempRefImg)
			else : 
				argsFinal = tempListArgs
                                argsFinal.append(tempRefImg)
                if len(args) >= 2 :
			if rawImgEnforced and refImgEnforced : 
				argsFinal = tempListArgs
				argsFinal.append(tempRefImg)
                        elif (not rawImgEnforced) and refImgEnforced :
                                argsFinal = args[:-1]
                                argsFinal.append(tempRefImg)
                        elif rawImgEnforced and (not refImgEnforced) :
                                argsFinal = tempListArgs
                                argsFinal.append(args[-1])
			else : argsFinal = args

		args = argsFinal #copy the final args to the args, the adopted options is already in list, allAdoptedOptions

        adoptedArguments = [] #all actually adopted paramemters
	#adoptedArguments = args #copy all the required argument to the list
	for i in range(len(args)) : adoptedArguments += glob.glob(args[i]) #check if the raw and ref images exist and extend the pattern file name to all real names
       	for anOption in allAdoptedOptions : #it combines the both comand line options and the options from configure file
		if allAdoptedOptions[anOption] == "False" : continue  #if it is False, does not space
		if allAdoptedOptions[anOption] == "True" or allAdoptedOptions[anOption] == "" : adoptedArguments.append("--" + anOption) #for the option take no value, just specifiy it as True
               	else : adoptedArguments.append("--" + anOption + "=" + str(allAdoptedOptions[anOption]))

	#print adoptedArguments

	(options, args)=parser.parse_args(adoptedArguments) # parse the adoptedArguments by command line parser
	
	if len(args) < 2:
		parser.print_help()
		sys.exit(-1)

	if options.saveParms != "" :
		commandtime = time
		t = commandtime.localtime()
		timeStr = "# Command start time    %s/%s/%s %s:%s:%s\n" % (t[1],t[2],t[0],t[3],t[4],t[5])
	        commandStr = sys.argv[0] #save all actually used paramemters
        	for aArg in args :  commandStr += (" " + aArg)
        	#for anOption in options.__dict__ : commandStr += (" --" + anOption + "=" + str(options.__dict__[anOption])) #output all internal used parameters
		for anOption in allAdoptedOptions : 
			if allAdoptedOptions[anOption] == "False" : continue  #if it is False, does not space
			if allAdoptedOptions[anOption] == "True" or allAdoptedOptions[anOption] == "" : commandStr += (" --" + anOption) #for the option take no value, just specifiy it as True
			else : commandStr += (" --" + anOption + "=" + str(allAdoptedOptions[anOption])) #output all input parameters
		commandStr += "\n" 

		f=open(options.saveParms, "a")
		f.write(timeStr)
		f.write(commandStr)
		f.close()


	for key in parser.option_list[1:]:  #this omits the -h/--help option
		eval_string = "options.%s" % (key.dest)
		value = eval(eval_string)
		if value == None:
			if (options.verbose > 0) :
				print "The option %s must be specified on the command line" % (key)
			sys.exit(-1)

	#remove the input string's spaces, some string may need to convert to lower cases
	options.sfFileName = options.sfFileName.replace(" ", "")
	options.rawImageIniParmFN = options.rawImageIniParmFN.replace(" ", "")
	options.solutionFile = options.solutionFile.replace(" ", "")
	options.mrcSolutionFile = options.mrcSolutionFile.replace(" ", "")
	options.iniCenterOrientationMode = options.iniCenterOrientationMode.lower().replace(" ", "")
	options.refCenterOrientationMode = options.refCenterOrientationMode.lower().replace(" ", "")
	options.refEulerConvention = options.refEulerConvention.lower().replace(" ", "")

	#if options.solutionFile == "":
	#	options.solutionFile = os.path.splitext(args[0])[0] + "-OrientationCenter.dat"

	#if options.mrcSolutionFile == "":
	#	options.mrcSolutionFile = os.path.splitext(args[0])[0] + "-MRC-OrientationCenter.dat"

	#numOfRawImages = EMAN.fileCount(args[0])[0]
	#if options.endNumOfRawImages < 1:
	#	options.endNumOfRawImages = numOfRawImages

	numOfRefImages = EMAN.fileCount(args[-1])[0]
	if options.numOfRefImages > numOfRefImages:
		options.numOfRefImages = numOfRefImages

	if options.startNumOfRawImages < 0:
		options.startNumOfRawImages = 0

	if (options.searchMode) == 0 : # coarse search
		# set default values
		if options.numOfRandomJump == 20 : options.numOfRandomJump = 1000
		if options.numOfFastShrink == 50 : options.numOfFastShrink = 300
		if options.maxNumOfIteration == 150 : options.maxNumOfIteration = 2500
		# check if the given values are less than mins
		if options.numOfRandomJump < 500 : options.numOfRandomJump = 500
		if options.numOfFastShrink <150 : options.numOfFastShrink = 150
		if options.maxNumOfIteration < (options.numOfRandomJump + options.numOfFastShrink + 500) :
			options.maxNumOfIteration = (options.numOfRandomJump + options.numOfFastShrink + 500)
		if options.maxNumOfIteration < 1500 : options.maxNumOfIteration = 1500
	elif (options.searchMode) == 1 : # refinement
		if options.rawImageIniParmFN == "" :
			if (options.verbose > 0) : print "\n\n\tFor refinement, you need to give a file name which specifies orientation and center of each image\n"
			#sys.exit(0)
		# check if the given values are less than mins
		if options.numOfRandomJump < 20 : options.numOfRandomJump = 20
		if options.numOfFastShrink < 50 : options.numOfFastShrink = 50
		if options.maxNumOfIteration < (options.numOfRandomJump + options.numOfFastShrink + 50) :
			options.maxNumOfIteration = (options.numOfRandomJump + options.numOfFastShrink + 50)
		if options.maxNumOfIteration < 120 : options.maxNumOfIteration = 120
	if options.orientationSearchRange > 36 : options.orientationSearchRange = 36
	if options.centerSearchRange > 100 : options.centerSearchRange = 100
	if options.zScoreCriterion < 0 : options.zScoreCriterion = 0
	
	allInputParameters   = "-------------------------------------------------------------------------\n"
	allInputParameters  += "--------------- All input parameters are listed as follows --------------\n"
	allInputParameters  += "-------------------------------------------------------------------------\n"
	allInputParameters  += "%40s :: %s \n" % ("Raw image file name",args[0:-1])
	allInputParameters  += "%40s :: %s \n" % ("Reference image file name",args[-1])
	if options.sfFileName != "" : allInputParameters  += "%40s :: %s \n" % ("Scattering factor file name",options.sfFileName)
	if options.searchMode == 1  : allInputParameters  += "%40s :: %s \n" % ("Raw image initial parameter file name",  options.rawImageIniParmFN)
	allInputParameters  += "%40s :: %s \n" % ("Starting number of raw images", options.startNumOfRawImages)
	allInputParameters  += "%40s :: %s \n" % ("Ending number of raw images", options.endNumOfRawImages)
	allInputParameters  += "%40s :: %s \n" % ("Number of reference images", options.numOfRefImages)
	allInputParameters  += "%40s :: %d \n" % ("Mask radius (pixels)", options.rMask)
	allInputParameters  += "%40s :: %s \n" % ("Scale of over sample FFT", options.FFTOverSampleScale)
	allInputParameters  += "%40s :: %s \n" % ("Maximum number of iteration", options.maxNumOfIteration)
	allInputParameters  += "%40s :: %s \n" % ("Iteration number of random jump", options.numOfRandomJump)
	allInputParameters  += "%40s :: %s \n" % ("Iteration number of fast shrink", options.numOfFastShrink)
	allInputParameters  += "%40s :: %s \n" % ("Center search range", options.centerSearchRange)
	allInputParameters  += "%40s :: %s \n" % ("Orientation search range", options.orientationSearchRange)
	allInputParameters  += "%40s :: %s \n" % ("Radial Step size of a common line", options.deltaR)
	allInputParameters  += "%40s :: %s \n" % ("Radial start point of a common line", options.RMin)
	allInputParameters  += "%40s :: %s \n" % ("Radial end point of a common line", options.RMax)
	allInputParameters  += "%40s :: %s \n" % ("Mode to handle a raw image", options.searchMode)
	allInputParameters  += "%40s :: %s \n" % ("Mode to calculate residual", options.residualMode)
	allInputParameters  += "%40s :: %s \n" % ("Weighting mode to calculate residual", options.weightMode)

	allInputParameters  += "%40s :: %s \n" % ("Maximum number of re-run", options.maxNumOfRun)
	allInputParameters  += "%40s :: %s%s \n" % ("The criteria of discriminating data", "z score = ", options.zScoreCriterion)
	if options.residualCriterion > 0 : allInputParameters  += "%40s :: %s%s \n" % ("", "residual threshold = ", options.residualCriterion)
	else : allInputParameters  += "%40s :: %s \n" % ("", "residual threshold = N/A")
	if options.solutionCenterDiffCriterion > 0 : allInputParameters  += "%40s :: %s%s \n" % ("", "center difference = ", options.solutionCenterDiffCriterion)
	else : allInputParameters  += "%40s :: %s \n" % ("", "center difference = N/A")
	if options.solutionOrientationDiffCriterion > 0 : allInputParameters  += "%40s :: %s%s \n" % ("", "orientation difference = ", options.solutionOrientationDiffCriterion)
	else : allInputParameters  += "%40s :: %s \n" % ("", "orientation difference = N/A")

	printOnScreen   = allInputParameters
	printOnScreen  += "-------------------------------------------------------------------------\n"
	printOnScreen  += "%40s :: %s \n" % ("Solution file name", options.solutionFile)
	printOnScreen  += "-------------------------------------------------------------------------\n"

	writeToSolutionFile  = allInputParameters
	writeToSolutionFile += "-------------------------------------------------------------------------\n\n"
	writeToSolutionFile += "%6s%8s%7s%7s%7s%7s%10s%34s%16s%24s%9s%12s\n" % ("######","X","Y","Alt","Az","Phi","residual","  sigma      Z  Z-crti Run# Status","ref center", "ref orientation", "XY diff","angle diff")
	writeToSolutionFile += "------------------------------------------------------------------------------------------------------------------------\n"
	if options.verbose > 0 and (not mpi or (mpi and mpi.rank==0)) : #print out the input parameters on screen
		print "%s " % (printOnScreen)

	if options.solutionFile and options.startNumOfRawImages == 0 : #write the input parameters to the solution file
		solutionFile = open(options.solutionFile, "w")
		solutionFile.write("%s" % (writeToSolutionFile))
		solutionFile.close()


	return (options,args)

def createConfigureFile(configFileName) :
	f=open(configFileName,"w")
	f.write(";the format of this configure file is as the follows\n")
        f.write(";[section]\n")
        f.write(";option = value1[, value2, ..., enforced] ;commentsi\n")
        f.write(";comments at end of a line has to start with space then pluse ;\n")
        f.write(";if no value to give, just leave a space there, but = can not be ignored, otherwise it will fail to parse it.\n")
        f.write(";you may give multiple values which sperated either by , or space.\n")
        f.write(";if you want to used the value given here in case it is already given in command line, you have to put enforce there.\n")
        f.write(";if no value, the enforce option won't be effective\n")
        f.write("\n")
        f.write("[required]\n")
        f.write("Raw image file names =   ;input raw images, could be multiple image files, list file\n")
        f.write("Reference image file name = ;reference image, one file name only\n")
        f.write("[options]\n")
	f.write("phasecorrected= ;if True, the particle's phase has been flipped, [False]\n")
        f.write("startNum=0 ;start from this number [0]\n")
        f.write("endNum=1   ;end with this number [total # of particles]\n")
        f.write("numOfRefImages=5 ;number of reference images [all reference images]\n")
        f.write("rMask=   ;give mask image a mask in pixel [no mask]\n")
        f.write("scatteringFactorFile   =      ;structure factor file name\n")
        f.write("refEulerConvention=eman ;reference euler angle : eman, mrc [eman]\n")
        f.write("iniCenterOrientationMode=iniparmfile ;raw particle's inintial orientation have 3 choice: random, headerfile, iniparmfile [random]\n")
        f.write("iniParameterFile= ;if iniCenterOrientationMode = iniparmfile, this one must be specified\n")
        f.write("overSample=1  ;oversample in FFT space\n")
        f.write("pftStepSize=0.1 ;for pseudo PFT, the angle step size in degree [0.1]\n")
        f.write("maxNumOfRun=12 ;how many times to re-run the search to check the consistency\n")
        f.write("maxIteration=2500 ;total # of iterations for each run\n")
        f.write("numOfStartConfigurations=12 ;number of path/configurations to start\n")
        f.write("numOfRandomJump=400 ;iterations for the first stage\n")
        f.write("numOfFastShrink=800 ;iterations for the third stage\n")
        f.write("orientationSearchRange=35 ;orientation search range in degree\n")
        f.write("centerSearchRange= ;center seach range in pixel\n")
        f.write("radialStepSize=1.0 ;step size to sample common line\n")
        f.write("radialStartPoint=5 ;start sample point of the common line\n")
        f.write("radialEndPoint= ;end sample point of the common line\n")
        f.write("searchMode=0 ;search mode: 0 --> coarse search, 1 --> refine [0]\n")
        f.write("scalingMode=0 ;scaling mode 0, 1. currently 0 only\n")
        f.write("residualMode=2 ;residual modes 0-->6\n")
        f.write("residualCriterion = ;in general, ;we do not use this criterion [-1 : not use]\n")
        f.write("zScoreCriterion=8.0 ;z score, will not use any more\n")
        f.write("solutionCenterDiffCriterion=0.7 ;tolerant error for orientation in degree\n")
        f.write("solutionOrientationDiffCriterion=0.7 ;tolerant error for center in pixel\n")
        f.write("verbose=3 ;control display 0-->5\n")
        f.write("updateHeader=0 ;update header if 1, [0]\n")
        f.write("solutionFile= ;output solution with all information\n")
        f.write("mrcSolutionFile= ;output orientation in mrc definition\n")
        f.write("listFile= ;output list file with center and orientation\n")
	f.write("nolog=True ;if True, no log file save to .emanlog, [False]\n")
        f.write("saveParms = savecommands.txt ;save the actually parameter used into a file\n")
	f.close()
	print "Configure file : [%s] has been created\n" % (configFileName)
	sys.exit(-1)

def CTFPeakZeroPosition(defocus,ampcontrast,voltage,Cs,order=1):
	"""Calculate the CTF peak, zero positions using analytic method. defocus should be negative for underfocus"""
	wl=12.2639/sqrt(voltage*1000.0+.97845*voltage*voltage)
	#gamma=2*pi*(2.5e6*Cs*wl*wl*wl*s*s*s*s+5000.*defocus*wl*s*s)
	Qphi = -asin(ampcontrast)
	
	# ctf = sin(gamma+Qphi) = sin(a*s^4+b*s^2+c)
	a = 2*pi*2.5e6*Cs*wl*wl*wl
	b = 2*pi*5000.*defocus*wl
	c = Qphi
	#
	# ctf=0 when a*s^4+b*s^2+c = -n*pi
	#	i.e. s = sqrt(((-b-sqrt(b*b-4*a*(c+n*pi)))/(2*a)))
	# ctf=peak when a*s^4+b*s^2+c = -n*pi-pi/2
	#	i.e. s = sqrt(((-b-sqrt(b*b-4*a*(c+n*pi+pi/2)))/(2*a)))
	#
	try:
		szero = sqrt(((-b-sqrt(b*b-4*a*(c+order*pi)))/(2*a)))
		speak = sqrt(((-b-sqrt(b*b-4*a*(c+(order-1)*pi+pi/2)))/(2*a)))
	except ValueError:
		szero = 0
		speak = 0
	return (szero, speak)


def main():
	if sys.argv[-1].startswith("usefs="): sys.argv = sys.argv[:-1]	# remove the runpar fileserver info

	(options,args) =  parse_command_line()
	
	if not options.nolog and (not mpi or (mpi and mpi.rank==0)): EMAN.appinit(sys.argv)

	inputParm = EMAN.ccmlInputParm()
	sf = EMAN.XYData()
	if options.sfFileName != "" :
		readsf = sf.readFile(options.sfFileName)
		if ((readsf == -1) and (options.verbose > 0)) :
			print "The file of scattering factor does NOT exist"
	inputParm.scateringFactor = sf

	startNumOfRawImages = options.startNumOfRawImages
	#endNumOfRawImages = options.endNumOfRawImages

	refImageFileName = args[-1]
	numOfRefImages = options.numOfRefImages
	solutionFile = options.solutionFile

	# write log info to .emanlog file so that eman program can browse the history
	if not options.nolog and (not mpi or (mpi and mpi.rank==0)): 
		pid = EMAN.LOGbegin(sys.argv)
		for f in args[0:-1]: EMAN.LOGInfile(pid,f)
		EMAN.LOGReffile(pid,args[-1])
		if options.solutionFile: EMAN.LOGOutfile(pid,options.solutionFile)
		if options.listFile: EMAN.LOGOutfile(pid,options.listFile)
		if options.mrcSolutionFile: EMAN.LOGOutfile(pid,options.mrcSolutionFile)

	inputParm.sym = options.sym
	inputParm.FFTOverSampleScale = options.FFTOverSampleScale
	inputParm.pftStepSize = options.pftStepSize
	inputParm.deltaR = options.deltaR
	inputParm.RMin = options.RMin
	inputParm.RMax = options.RMax
	inputParm.searchMode = options.searchMode
	inputParm.scalingMode = options.scalingMode
	inputParm.residualMode = options.residualMode
	inputParm.weightMode = options.weightMode
	# inputParm.rawImageFN will be set later
	inputParm.refImagesFN = refImageFileName
	inputParm.rawImageIniParmFN = options.rawImageIniParmFN
	inputParm.rawImagePhaseCorrected = options.phasecorrected

	inputParm.maxNumOfRun = options.maxNumOfRun
	inputParm.zScoreCriterion = options.zScoreCriterion
	inputParm.residualCriterion = options.residualCriterion
	inputParm.solutionCenterDiffCriterion = options.solutionCenterDiffCriterion
	inputParm.solutionOrientationDiffCriterion = options.solutionOrientationDiffCriterion/180.0*pi
	inputParm.maxNumOfIteration = options.maxNumOfIteration
	inputParm.numOfRandomJump = options.numOfRandomJump
	inputParm.numOfFastShrink = options.numOfFastShrink
	inputParm.numOfStartConfigurations = options.numOfStartConfigurations
	inputParm.orientationSearchRange = options.orientationSearchRange/180.0*pi
	inputParm.centerSearchRange = options.centerSearchRange

	inputParm.numOfRefImages = options.numOfRefImages
	inputParm.refEulerConvention = options.refEulerConvention
	#maskR = options.maskR
	#if (maskR<=0): maskR = refImageSizeY/2

	inputParm.verbose = options.verbose
	verbose = options.verbose
	#verboseSolution = options.verboseSolution

	updataHeader = options.updataHeader
	solutionFile = options.solutionFile
	mrcSolutionFile = options.mrcSolutionFile
	iniCenterOrientationMode = options.iniCenterOrientationMode
	refCenterOrientationMode = options.refCenterOrientationMode

	rawImages = []
	if not mpi or (mpi and mpi.rank==0):
		for imgfile in args[0:-1]:
			imgnum = EMAN.fileCount(imgfile)[0]
			for i in range(imgnum): rawImages.append((imgfile, i))
	if mpi: rawImages = mpi.bcast(rawImages)
	
	endNumOfRawImages = options.endNumOfRawImages
	if endNumOfRawImages <=0  or endNumOfRawImages > len(rawImages):
		endNumOfRawImages = len(rawImages)

	numRawImages = endNumOfRawImages - startNumOfRawImages

	if mpi:
		ptclset = range(startNumOfRawImages + mpi.rank, endNumOfRawImages, mpi.size)
	else:
		ptclset = range(startNumOfRawImages, endNumOfRawImages)
	
	solutions = []

	rMask = options.rMask        #mask size is given
	if options.rMask <= 0 : rMask = refImageSizeY/2   #mask size = half image size
	
	rMask1 = options.rMask1             #output tnf mask size is given
	if options.rMask1 <= 0 : rMask1 = rMask    #output tnf mask size = half image size

	inputParm.rMask = rMask
	inputParm.rMask1 = rMask1

	rawImage = EMAN.EMData()
	rawImage.getEuler().setSym(inputParm.sym) #set the symmetry of the raw partile
	inputParm.rawImageFN = rawImages[0][0] #give the initial raw particle filename
	print "start to prepare------"
	rawImage.crossCommonLineSearchPrepare(inputParm) #prepare, create pseudo PFT of ref images
	print "end to prepare------"
	inputParm.rawImage = rawImage
	#for rawImgSN in ptclset:
	for index in range(len(ptclset)):
		rawImgSN = ptclset[index]
		inputParm.rawImageFN = rawImages[rawImgSN][0]
		inputParm.thisRawImageSN = rawImages[rawImgSN][1]
		if mpi: print "rank %d: %d in %d-%d (%d in %d-%d)" % (mpi.rank, rawImgSN, startNumOfRawImages, endNumOfRawImages, index, 0, len(ptclset))
		#rawImage.readImage(rawImages[rawImgSN][0], rawImages[rawImgSN][1])

		#rawImage.applyMask(rMask, 6) #apply mask type 6 [edge mean value] to raw image, center will be image center
		#rawImage.getEuler().setSym("icos")
		#if rawImage.hasCTF() == 1:
			#ctfParm = rawImage.getCTF()
			#inputParm.zScoreCriterion = options.zScoreCriterion + atan(abs(ctfParm[0])-1.5)/(pi/4) +0.59 #adjust zScore criterion -0.6 --> +1.2, 1.5, 2.0
			#inputParm.numOfRefImages = int(min(numOfRefImages, max(numOfRefImages*exp(-(abs(ctfParm[0])/2.0-0.15))+0.5, 5.0))) # adjust maxNumOfRun, the min is 2

		inputParm.thisRawImageSN = rawImgSN

		solutionCenterDiffCriterion = inputParm.solutionCenterDiffCriterion
		solutionOrientationDiffCriterion = inputParm.solutionOrientationDiffCriterion

		#initialize Center And Orientation by ont of the following modes

		if iniCenterOrientationMode == "iniparmfile" :
			inputParm.initializeCenterAndOrientationFromIniParmFile() # need to set "refEulerConvention"
		elif iniCenterOrientationMode == "headerfile" :
			inputParm.initializeCenterAndOrientationFromParticle() # need to set "refEulerConvention"
		else :
			inputParm.initializeCenterAndOrientationFromRandom()  # default is random orientation and physical center

		#set the refence Center And Orientation by ont of the following modes

		if refCenterOrientationMode == "iniparmfile" : inputParm.setRefCenterAndOrientationFromIniParmFile() # need to set "refEulerConvention"
		elif refCenterOrientationMode == "headerfile" : inputParm.setRefCenterAndOrientationFromParticle() # need to set "refEulerConvention"
		else : inputParm.setRefCenterAndOrientationFromInitializedParms() # default is copy the initial center and orientation

		rawImage.crossCommonLineSearchReadRawParticle(inputParm) #create pseudo PFT of raw image

		maxNumOfRun = inputParm.maxNumOfRun
		outputParmList = []
		numOfRun = 0
		passAllConsistencyCriteria = 0
		while (numOfRun < maxNumOfRun) or (len(outputParmList) < 2):

			if (iniCenterOrientationMode != "iniparmfile") and (iniCenterOrientationMode != "headerfile") :
				inputParm.initializeCenterAndOrientationFromRandom()  # default is random orientation and physical center
			if (refCenterOrientationMode != "iniparmfile") and (refCenterOrientationMode != "headerfile") :
				inputParm.setRefCenterAndOrientationFromInitializedParms() # default is copy the initial center and orientation

			numOfRun = numOfRun + 1
			print "numOfRun = ", numOfRun

			############################################################################
			############ execute cross common line search for reference ################
			############################################################################
			outputParm  = rawImage.crossCommonLineSearch(inputParm)
			############################################################################
			# pass criteria check
			outputParmList.append(outputParm) #if passed criteria, e.g. zscore, residualThreshold, etc
			############################################################################

			outputParmList.sort(lambda x, y: cmp(x.residual, y.residual))

			############################################################################
			########################## consistency check ###############################
			############################################################################
			#passConsistencyCriteria = 0
			finalOutputParmList = []
			lowestResidualList = []
			lengthOfList = len(outputParmList)
			if lengthOfList < 2 : continue
			for i in range(lengthOfList-1):
				thisOutputParm = outputParmList[i]
				numOfPairsPassConsistencyCheck = 0
				for j in range(i+1,lengthOfList):
					refOutputParm = outputParmList[j]
					tmpOutputParm = EMAN.ccmlOutputParm() #create a new output parm object
					tmpOutputParm.rawImageSN = thisOutputParm.rawImageSN #copy all paramenters
					tmpOutputParm.residual = thisOutputParm.residual
					tmpOutputParm.sigma = thisOutputParm.sigma
					tmpOutputParm.verbose = thisOutputParm.verbose
					tmpOutputParm.zScore = thisOutputParm.zScore
					tmpOutputParm.zScoreCriterion = thisOutputParm.zScoreCriterion

					tmpOutputParm.passAllCriteria = 0
					tmpOutputParm.setCalculatedCenterAndOrientation(thisOutputParm.cx,thisOutputParm.cy,thisOutputParm.q)
					tmpOutputParm.setRefCenterAndOrientation(refOutputParm.cx, refOutputParm.cy, refOutputParm.q)
					tmpOutputParm.calculateDifferenceWithRefParm() #calculated the difference

					centerDiff = tmpOutputParm.centerDiff
					orientationDiff = tmpOutputParm.orientationDiff
					
					#####  FLIP CASE :  if no consistency found, try flip this orientation
					if ((centerDiff > solutionCenterDiffCriterion) or (orientationDiff > solutionOrientationDiffCriterion)) :
						quatFlip = EMAN.Quaternion(refOutputParm.q.getEuler().alt(), refOutputParm.q.getEuler().az(), refOutputParm.q.getEuler().phi()+pi)
						tmpOutputParm.setRefCenterAndOrientation(refOutputParm.cx, refOutputParm.cy, quatFlip)
						tmpOutputParm.calculateDifferenceWithRefParm() #calculated the difference
						centerDiff = tmpOutputParm.centerDiff
						orientationDiff = tmpOutputParm.orientationDiff
						tmpOutputParm.setRefCenterAndOrientation(refOutputParm.cx, refOutputParm.cy, refOutputParm.q) #set back the exact orientation of reference 

					#Save the configurations with lowest residuals
					if (i<3) and (j==i+1) : lowestResidualList.append(tmpOutputParm)
					
					#make the good/answers list
					if ((centerDiff < solutionCenterDiffCriterion) and (orientationDiff < solutionOrientationDiffCriterion)) :
						numOfPairsPassConsistencyCheck += 1
						if numOfPairsPassConsistencyCheck == 1 : #save to the final list
							tmpOutputParm.passAllCriteria = 1
							finalOutputParmList.append(tmpOutputParm)
						if i==0 and numOfPairsPassConsistencyCheck >= options.numConsistentRun: #if the first one, check whether it has 3 pair of consistencies
							passAllConsistencyCriteria = 1
							break
						if i>0 : break #if not the first one, find one pair of consistency, then break
				
				#no break here, just for saving all possible solutions

			if passAllConsistencyCriteria and len(finalOutputParmList) >= options.numConsistentRun: break #if 3 consistent pair orientations were found, then stop


		rawImage.crossCommonLineSearchReleaseParticle(inputParm) # release the memory related to this raw particle

		# if no consistency found, keep the lowest ones as output
		if len(finalOutputParmList) == 0 : finalOutputParmList = lowestResidualList
		for i in range(len(finalOutputParmList)) : 
			if passAllConsistencyCriteria : finalOutputParmList[i].passAllCriteria = 1
			else : finalOutputParmList[i].passAllCriteria = 0

		if options.solutionFile:
			for i in range(len(finalOutputParmList)) : finalOutputParmList[i].outputResult(solutionFile)

		outputParm = finalOutputParmList[0] #just use the lowest residual as regular output
		if outputParm.passAllCriteria: 	passfail = "pass"
		else: passfail = "fail"

		print "Final result: euler=%g\t%g\t%g\tcenter=%g\t%g\tresidue=%g\t%s" % (outputParm.alt*180/pi, outputParm.az*180/pi, outputParm.phi*180/pi, outputParm.cx, outputParm.cy, outputParm.residual, passfail)
		
		if options.scoreFile:
			rawImage.readImage(rawImages[rawImgSN][0], rawImages[rawImgSN][1], 1) # read header only
			if rawImage.hasCTF(): 
				defocus = rawImage.getCTF()[0]
		else:
			defocus = 0

		solution = (rawImages[rawImgSN][0], rawImages[rawImgSN][1], outputParm.alt, outputParm.az, outputParm.phi, \
					   outputParm.cx, outputParm.cy, defocus, outputParm.residual, outputParm.passAllCriteria)
		solutions.append( solution )

		sys.stdout.flush()

	rawImage.crossCommonLineSearchFinalize(inputParm) #finalize, i.e. delete memories

	if mpi:
		if options.verbose: 
			print "rank %d: done and ready to output" % (mpi.rank)
			sys.stdout.flush()
		mpi.barrier()
		#print "rank %d: %s" % (mpi.rank, solutions)
		if mpi.rank==0:
			for r in range(1,mpi.size):
				msg, status = mpi.recv(source = r, tag = r)
				solutions += msg
			def ptcl_cmp(x, y):
				eq = cmp(x[0], y[0])
				if not eq: return cmp(x[1],y[1])
				else: return eq
			solutions.sort(ptcl_cmp)
		else:
			mpi.send(solutions, 0, tag = mpi.rank)

	if not mpi or (mpi and mpi.rank==0):
		if options.scoreFile:
			sFile = open(options.scoreFile, "w")
			sFile.write("#LST\n")
			for i in solutions:
				if i[-1]: 
					sFile.write("%d\t%s\tdefocus=%g\tresidual=%g\n" % (i[1], i[0], i[7], i[8]))
			sFile.close()
			
		if options.listFile:
			lFile = open(options.listFile, "w")
			lFile.write("#LST\n")
			for i in solutions:
				if i[-1]: 
					lFile.write("%d\t%s\t%g\t%g\t%g\t%g\t%g\n" % (i[1], i[0], i[2]*180.0/pi, i[3]*180.0/pi, i[4]*180.0/pi, i[5], i[6]))
			lFile.close()
		if options.mrcSolutionFile:
			outFile = open(options.mrcSolutionFile, "w")
			for i in solutions:
				if i[-1]:
					#rawImage.readImage(i[0], i[1], 1)
					rawImage.readImage(i[0], i[1])
					thisEu = EMAN.Euler(i[2], i[3], i[4])
					thisEu.convertToMRCAngle()
					alt = thisEu.alt_MRC()*180.0/pi
					az  = thisEu.az_MRC()*180.0/pi
					phi = thisEu.phi_MRC()*180.0/pi
		
					cx  = i[5]
					cy  = i[6]
					dx = cx - rawImage.xSize()/2
					dy = cy - rawImage.ySize()/2
					rawImage.applyMask(rMask1,6,dx,dy,0) #apply mask type 4 [outside=0] to raw image, center will be the solved center
					#tnfFileName = "%s-%d.tnf" % (os.path.basename(os.path.splitext(rawImages[rawImgSN][0])[0]), rawImages[rawImgSN][1])
					prefix = os.path.dirname(options.mrcSolutionFile).replace(" ", "")
					if prefix != "" : prefix = prefix + "/"
					tnfFileName = "%s%s-%d.tnf" % (prefix,os.path.basename(os.path.splitext(i[0])[0]), i[1])
					rawFFT = rawImage.doFFT()
					rawFFT.writeImage(tnfFileName,0)  #tnf file no header information, it is a pure FFT of raw image file
		
					outFile.write("%s\n" % (os.path.abspath(tnfFileName)))
					outFile.write(" %d, %.4f, %.4f, %.4f, %.4f, %.4f, 0.0\n" % (0, alt, az, phi, cy, cx))
			outFile.close()
		if updataHeader:
			for i in solutions:
				rawImage.readImage(i[0], i[1], 1)
				if options.verbose:
					cx  = rawImage.get_center_x()
					cy  = rawImage.get_center_y()
					alt = rawImage.alt()
					az  = rawImage.az()
					phi = rawImage.phi()
					print "Update header: %s %d\t%7.5f  %7.5f  %7.2f  %7.2f  %7.2f => %7.5f  %7.5f  %7.2f  %7.2f  %7.2f" % \
						(i[0], i[1], alt*180.0/pi, az*180.0/pi, phi*180.0/pi, cx, cy, i[2]*180.0/pi, i[3]*180.0/pi, i[4]*180.0/pi, i[5], i[6])
				rawImage.setRAlign(i[2], i[3], i[4])
				rawImage.set_center_x(i[5])
				rawImage.set_center_y(i[6])
				imgtype = EMAN.EMData.ANY
				rawImage.writeImage(i[0], i[1], imgtype, 1)
	if not options.nolog and (not mpi or (mpi and mpi.rank==0)): EMAN.LOGend()

if __name__== "__main__":
	main()



