# FMKMF_F90 not set: using f90
# FMKMF_SFTAG not set: using f90
# FMKMF_SPATH not set: using . 
# FMKMF_LINKOPTS not set: using no link options 
# Using compile cmd ifort from cmd line
# Using openmp
# Using opt
# Using m64
# Main program is mkrndeuls.f90 
# process_fsource called with arg mkrndeuls.f90 
# mkrndeuls.f90 Uses Module simple_rnd
# Full list of modules in mkrndeuls.f90: simple_rnd 
# Uses simple_rnd which is in ../simple_rnd.f90
# process_fsource called with arg ../simple_rnd.f90 
# Full list of modules in ../simple_rnd.f90:  

# ------------------Macro-Defs---------------------
F90=ifort 

# -------------------End-macro-Defs---------------------------

# Here is the link step 
mkrndeuls:simple_rnd.o mkrndeuls.o 
	 $(F90) -o mkrndeuls simple_rnd.o mkrndeuls.o   -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

# Here are the compile steps
 
simple_rnd.o:../simple_rnd.f90  
	 $(F90) -c ../simple_rnd.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

mkrndeuls.o:mkrndeuls.f90 simple_rnd.o 
	 $(F90) -c mkrndeuls.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static
# This entry allows you to type " make clean " to get rid of
# all object and module files 
clean:
	rm -f -r f_{files,modd}* *~ *.g90 *.o *.mod *.M *.d V*.inc *.vo \
	V*.f *.dbg album F.err
  
