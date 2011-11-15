# FMKMF_F90 not set: using f90
# FMKMF_SFTAG not set: using f90
# FMKMF_SPATH not set: using . 
# FMKMF_LINKOPTS not set: using no link options 
# Using compile cmd ifort from cmd line
# Using openmp
# Using opt
# Using m64
# Main program is test_origsh_pop.f90 
# process_fsource called with arg test_origsh_pop.f90 
# test_origsh_pop.f90 Uses Module simple_math
# Full list of modules in test_origsh_pop.f90: simple_math 
# Uses simple_math which is in ../simple_math.f90
# process_fsource called with arg ../simple_math.f90 
# ../simple_math.f90 Uses Module simple_def_precision
# ../simple_math.f90 Uses Module simple_syscalls
# ../simple_math.f90 Uses Module simple_jiffys
# ../simple_math.f90 Uses Module simple_rnd
# Full list of modules in ../simple_math.f90: simple_def_precision simple_syscalls simple_jiffys simple_rnd 
# Uses simple_def_precision which is in ../simple_def_precision.f90
# process_fsource called with arg ../simple_def_precision.f90 
# Full list of modules in ../simple_def_precision.f90:  
# Uses simple_syscalls which is in ../simple_syscalls.f90
# process_fsource called with arg ../simple_syscalls.f90 
# Full list of modules in ../simple_syscalls.f90:  
# Uses simple_jiffys which is in ../simple_jiffys.f90
# process_fsource called with arg ../simple_jiffys.f90 
# Full list of modules in ../simple_jiffys.f90:  
# Uses simple_rnd which is in ../simple_rnd.f90
# process_fsource called with arg ../simple_rnd.f90 
# Full list of modules in ../simple_rnd.f90:  

# ------------------Macro-Defs---------------------
F90=ifort 

# -------------------End-macro-Defs---------------------------

# Here is the link step 
test_origsh_pop:simple_def_precision.o simple_syscalls.o simple_jiffys.o simple_rnd.o simple_math.o test_origsh_pop.o 
	 $(F90) -o test_origsh_pop simple_def_precision.o simple_syscalls.o simple_jiffys.o simple_rnd.o simple_math.o test_origsh_pop.o   -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

# Here are the compile steps
 
simple_def_precision.o:../simple_def_precision.f90  
	 $(F90) -c ../simple_def_precision.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

simple_syscalls.o:../simple_syscalls.f90  
	 $(F90) -c ../simple_syscalls.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

simple_jiffys.o:../simple_jiffys.f90  
	 $(F90) -c ../simple_jiffys.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

simple_rnd.o:../simple_rnd.f90  
	 $(F90) -c ../simple_rnd.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

simple_math.o:../simple_math.f90 simple_def_precision.o simple_syscalls.o simple_jiffys.o simple_rnd.o 
	 $(F90) -c ../simple_math.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static

test_origsh_pop.o:test_origsh_pop.f90 simple_math.o 
	 $(F90) -c test_origsh_pop.f90 -implicitnone -m64 -L../fftw/fftw3-osx-64/lib/ -lfftw3f -lfftw3f_threads -i-static
# This entry allows you to type " make clean " to get rid of
# all object and module files 
clean:
	rm -f -r f_{files,modd}* *~ *.g90 *.o *.mod *.M *.d V*.inc *.vo \
	V*.f *.dbg album F.err
  
