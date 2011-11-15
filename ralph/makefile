# FMKMF_F90 not set: using f90
# FMKMF_SFTAG not set: using f90
# FMKMF_SPATH not set: using . 
# FMKMF_LINKOPTS not set: using no link options 
# Using compile cmd ifort from cmd line
# Using openmp
# Using opt
# Using m64
# Main program is ralph.f90 
# process_fsource called with arg ralph.f90 
# ralph.f90 Uses Module simple_ralph
# Full list of modules in ralph.f90: simple_ralph 
# Uses simple_ralph which is in ./simple_ralph.f90
# process_fsource called with arg ./simple_ralph.f90 
# ./simple_ralph.f90 Uses Module simple_jiffys
# ./simple_ralph.f90 Uses Module simple_random_nrs
# Full list of modules in ./simple_ralph.f90: simple_jiffys simple_random_nrs 
# Uses simple_jiffys which is in ../simple_jiffys.f90
# process_fsource called with arg ../simple_jiffys.f90 
# Full list of modules in ../simple_jiffys.f90:  
# Uses simple_random_nrs which is in ../simple_random_nrs.f90
# process_fsource called with arg ../simple_random_nrs.f90 
# Full list of modules in ../simple_random_nrs.f90:  

# ------------------Macro-Defs---------------------
F90=ifort 

# -------------------End-macro-Defs---------------------------

# Here is the link step 
ralph:simple_jiffys.o simple_random_nrs.o simple_ralph.o ralph.o 
	 $(F90) -o ralph simple_jiffys.o simple_random_nrs.o simple_ralph.o ralph.o   -CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

# Here are the compile steps
 
simple_jiffys.o:../simple_jiffys.f90  
	 $(F90) -c ../simple_jiffys.f90 -CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

simple_random_nrs.o:../simple_random_nrs.f90  
	 $(F90) -c ../simple_random_nrs.f90 -CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

simple_ralph.o:./simple_ralph.f90 simple_jiffys.o simple_random_nrs.o 
	 $(F90) -c ./simple_ralph.f90 -CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

ralph.o:ralph.f90 simple_ralph.o 
	 $(F90) -c ralph.f90 -CB -CU -g -debug all -check all -implicitnone -warn unused -fp-stack-check -ftrapuv -check pointers -check bounds -traceback -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static
# This entry allows you to type " make clean " to get rid of
# all object and module files 
clean:
	rm -f -r f_{files,modd}* *~ *.g90 *.o *.mod *.M *.d V*.inc *.vo \
	V*.f *.dbg album F.err
  
