#!/usr/bin/perl  -w
# Copyright (c) The University of Edinburgh
# This is a utility to generate make files 
# for Fortran 90. It was originally in shell script and was re-written
# in perl for greater speed and (hopefully) portability.
# Initial tests suggest speed is 10x better than the sh version.

# A basic makefile entry for bork.f90 would be
# bork.o:bork.f90
# <-tab->$(F90) -c bork.f90
#
# however if bork.f90 contains the line "use gunge" then 
# (A)
# the entry has to be 
# bork.o:bork.f90 garple.o <-- Forces bork to be recompiled if a module it 
# <-tab->$(F90) -c bork.f90                               uses is changed
# where garple.f90 is the program containing the line "module gunge
# (B)  
# The same type of entry has to be done for garple.f90
#
# We also need to generate an entry for the link step. If the main program
# was in baz.f90 then this should be 
# baz:baz.o bork.o.........
# <-tab->$(F90) -o baz baz.o bork.o .....
# The list of object files to be linked should have foo.o in it once 
# and only once for each foo.f90 that was compiled 

#-------------------------------------------------
# First check if the luser has any relevent environment vars set
#--------------------------------------------
if ( $ENV{FMKMF_F90} ) {
  print "\# FMKMF_F90 set to $ENV{FMKMF_F90}\n";
  $f90=$ENV{FMKMF_F90};
} 
else {
  print "\# FMKMF_F90 not set: using f90\n";
  $f90="f90";
}

if ( $ENV{FMKMF_SFTAG} ) {
  print "\# FMKMF_SFTAG set to $ENV{FMKMF_SFTAG}\n";
  $sftag=$ENV{FMKMF_SFTAG};
} 
else {
  print "\# FMKMF_SFTAG not set: using f90\n";
  $sftag="f90";
}

if ( $ENV{FMKMF_SPATH} ) {
  print "\# FMKMF_SPATH set to $ENV{FMKMF_SPATH}\n";
  $spath=$ENV{FMKMF_SPATH};
} 
else {
  print "\# FMKMF_SPATH not set: using . \n";
  $spath=".";
}

if ( $ENV{FMKMF_LINKOPTS} ) {
  print "\# FMKMF_LINKOPTS set to $ENV{FMKMF_LINKOPTS}\n";
  $linkopts=$ENV{FMKMF_LINKOPTS};
} 
else {
  print "\# FMKMF_LINKOPTS not set: using no link options \n";
  $linkopts=" ";
}

#------------------------------
# Done with environment variables. Now we need to process commandline args
# These supersede anything supplied via environment variables.
#------------------------------

while (@ARGV){

  $arg=shift;
  if ($arg =~ /^-f90$/){
    $f90=shift; 
    if( $f90 eq 'ifort' ){
        $ifort   = 1;
        $openf95 = 0;
    } else {
        $ifort   = 0;
        $openf95 = 1;
        $f90     = 'openf95';   
    }
    print "# Using compile cmd $f90 from cmd line\n";
  }
  if ($arg =~ /^-openmp$/){
    $openmp = shift;
    print "# Using openmp\n";
  }
  if ($arg =~ /^-opt$/){
    $opt = shift;
    print "# Using opt\n";
  }
  if ($arg =~ /^-mac$/){
    $mac = shift;
    print "# Using m64\n";
  }

}

# FFTW static library location
my $FFTWLIBDIR_MAC = "../fftw/fftw3-osx-64/lib/";
my $FFTWLIBDIR_LINUX = "../fftw/fftw3-3.3/";

# Static Link with FFTW libraries with threads and with static Intel compiler library
my $LINKLIBS_MAC  = "-L$FFTWLIBDIR_MAC -lfftw3f -lfftw3f_threads -i-static";
my $LINKLIBS_LINUX  = "-L$FFTWLIBDIR_LINUX -lfftw3f -lfftw3f_threads -i-static";

$spath = ".:..";

#-------------------------------------------
# Setting compiler directives
#-------------------------------------------

if( $opt == 1 ){
        if( $openmp ){
            if( $mac == 1 ){
                $comp_directives = "-implicitnone -openmp -m64 $LINKLIBS_MAC"; # optimized code mac
            } else {
                $comp_directives = "-implicitnone -static -openmp $LINKLIBS_LINUX"; # optimized code  
            }
        } else {
            if( $mac == 1 ){
                $comp_directives = "-implicitnone -m64 $LINKLIBS_MAC"; # optimized code mac
            } else {
                $comp_directives = "-implicitnone -static $LINKLIBS_LINUX"; # optimized code  
            }
        }
} else {
    if( $openmp ){
        if( $mac == 1 ){
            $comp_directives = "-CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -openmp $LINKLIBS_MAC"; # ifort debug openmp mac
        } else {
            $comp_directives = "-CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -static -openmp $LINKLIBS_LINUX"; # ifort debug openmp
        }
    } else {
        if( $mac == 1 ){
            $comp_directives = "-CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback $LINKLIBS_MAC"; # ifort debug mac
        } else {
            $comp_directives = "-CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -static $LINKLIBS_LINUX"; # ifort debug  
        }
    }  
}

@spath=split(/:/,$spath);
@global_outlines=();
@global_objlist=();
@global_modfiles=();

$mainprogfile=$arg;

print "# Main program is $mainprogfile \n" ;



# this subroutine (def below) does most of the work.
process_fsource($mainprogfile); 

# set some makefile . 

print "\n# ------------------Macro-Defs---------------------\n";

print "F90=$f90 \n";

print "\n# -------------------End-macro-Defs---------------------------\n";

# Generate a name for the executable file
$execfile=$mainprogfile;
$execfile=~s/\.${sftag}//;
$execfile=~s|.*/||;

# Generate makefile entry for the Link step
print "\n# Here is the link step \n";

print "$execfile:@global_objlist \n";
print "\t \$(F90) -o $execfile @global_objlist $linkopts $comp_directives\n";

print "\n# Here are the compile steps\n ";
print STDOUT @global_outlines;

# Add an entry for make clean at the end of the make file.  this
# removes most of the gubbage left around by most of the Unix Fortran
# 90 compilers I have tried. 

print "# This entry allows you to type \" make clean \" to get rid of\n";
print "# all object and module files \n";

print "clean:\n";
print "\trm -f -r f_{files,modd}* *~ *.g90 *.o *.mod *.M *.d V*.inc *.vo \\\n";
print "\tV*.f *.dbg album F.err";
print "\n  \n";

# End of main program 

##############################################
# Here is the subroutine that generates the compile entries in the makefile
# These end up in the global array @global_outlines. The magic part is 
# that this subroutine calls itself recursively.
##############################################
sub process_fsource {
  
  my $mainprogfile=$_[0];
  print"# process_fsource called with arg $mainprogfile \n";
  open( MAINPROG, $mainprogfile) or 
    die "Can't find main program file $mainprogfile: $! \n";
  
  # Read through Fortran source looking for USE statements
  # There should be nothing but whitespace before the USE. Sloppily, 
  # we allow tabs, although the standard (IIRC) does not
  my @modulelist=();
  while ($line=<MAINPROG>) { 
    if ($line =~ /^[ \t]*use[ \t]+(\w+)/i ) { # line matches regexp between / /
      print "# $mainprogfile Uses Module $1\n";
      @modulelist=(@modulelist,$1);
    }
  }
  
  close(MAINPROG);
  
  #print "# Full list of modules in $mainprogfile: @modulelist \n";
  
  print "# Full list of modules in $mainprogfile: @modulelist \n";
  # Find which file each module is in.
  
  
  
 my @modfiles=();
 MODLOOP:foreach $module (@modulelist){
    foreach $directory (@spath){
      # print "# Looking in directory $directory\n";
      opendir( DIRHANDLE, $directory) or die 
	"Can't open directory $directory : $! \n";
      @sourcefiles=grep /\.${sftag}\Z/, sort(readdir(DIRHANDLE));
    foreach $sourcefile (@sourcefiles){
      $pathsourcefile="$directory/$sourcefile";
      #print "\# Checking $pathsourcefile\n";
      open( SOURCEFILE, "$pathsourcefile") or 
	die "Can't find source file $pathsourcefile: $! \n";
      while ($line=<SOURCEFILE>){
	if ($line =~ /^[ \t]*module[ \t]+(\w+)/i ){
	  if($1 =~ /^$module$/i){
	    print "# Uses $module which is in $pathsourcefile\n";
	    @modfiles=(@modfiles,$pathsourcefile);
	    
	    if (grep (/$pathsourcefile/,@global_modfiles )){
	      print "# $pathsourcefile already in list\n";
	    } 
	    else {
	      @global_modfiles=(@global_modfiles,$pathsourcefile);
	      process_fsource($pathsourcefile);

	    }
	    # We found this module -- go on to the next one
	    close (SOURCEFILE);
	    next MODLOOP;	    
	  }
	}
      }
      close( SOURCEFILE );
    }
  }
  # exhausted source files
  print STDERR "Couldn't find source file for module $module\n";
}

# name of file we want to make
$objfile=$mainprogfile;
# replace source file name with .o
$objfile=~s/\.${sftag}/\.o/;
# strip path so object files go in current dir
$objfile=~s|.*/||;
@global_objlist=(@global_objlist,$objfile);
# list of dependencies
@objlist=();
foreach  $mf (@modfiles) { 
  $obj=$mf;
  # replace source file name with .o
  $obj=~s/\.${sftag}/\.o/;
  # strip path so object files go in current dir
  $obj=~s|.*/||;
  @objlist=(@objlist,$obj);
}

@global_outlines=(@global_outlines,"\n$objfile:$mainprogfile @objlist \n");
@global_outlines=(@global_outlines,"\t \$(F90) -c $mainprogfile $comp_directives\n");

}
