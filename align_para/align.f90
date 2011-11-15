!==Program align
!
! _Align_ is a program for reference-based orientation refinement. The algorithm is based on spectrally 
! self-adaptive differential evolution correlation search in Fourier space. The code is distributed with the hope 
! that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution and modification is regulated by the GNU 
! General Public License. *Author:* Hans Elmlund 2009-05-26.
!
!==References
!
!* Elmlund D. & Elmlund H. "High-resolution single- particle orientation refinement based on spectrally 
! self-adapting common lines" J. Struct. Biol. 2009 Jul;167(1):83-94
!
!==Changes are documented below
!
!* deugged and incorporated in the _SIMPLE_ library, HE 2009-06-26
!* modified for release 2 of _SIMPLE_, HE 2011-09-07
! 
program align
use simple_params
use simple_rnd
use simple_rbased_search
use simple_build
use simple_cmdline
use simple_syscalls
use simple_jiffys
implicit none
save
type(build), target, save :: b
integer                   :: i, file_stat
integer, parameter        :: fhandle=23
logical                   :: cmderr(7)
if( command_argument_count() < 4 )then
    write(*,*) './align mode=<mode nr> fstk=fstk.fim vol1=<refvol_1.spi> [vol2=<refvol_2.spi> etc.] lp=<low-pass limit (in A)> trs=<origin shift(in pixels){5}> outfile=algndoc_roundX.dat nthr=<nr of openMP threads> [oritab=<previous rounds alignment doc>] [fromp=<start ptcl> top=<stop ptcl>] [pgrp=<cn|dn>] [hp=<high-pass limit (in A)>] [debug=<yes|no>]'
    write(*,*) ''
    write(*,*) 'Available modes are:'
    write(*,*) '20: EvolAlign with fixed lowpass limit'
    write(*,*) '21: EvolAlign with spectral self-adaptation'
    write(*,*) '22: EvolAlign with spectral self-adaptation and orientation keeping'
    write(*,*) '23: EvolAlign validation mode'
    stop
endif
! parse command line
call parse_cmdline
! check so that trs is nonzero
if( get_cmd_rarg('trs') > 0. )then
else
    write(*,*) 'ERROR, trs argument must be > 0!'
    stop
endif
! check command line arguments
cmderr(1) = .not. defined_cmd_rarg('mode')
cmderr(2) = .not. defined_cmd_carg('fstk')
cmderr(3) = .not. defined_cmd_carg('vol1')
cmderr(4) = .not. defined_cmd_rarg('lp')
cmderr(5) = .not. defined_cmd_rarg('trs')
cmderr(6) = .not. defined_cmd_carg('outfile')
cmderr(7) = .not. defined_cmd_rarg('nthr')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for align defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! Seed the random number generator
call seed_rnd
! Build all objects required for alignment
b = new_build( )
if( mode < 20 .or. mode >= 30 )then
    write(*,*) 'ERROR, mode is not set or set incorrectly!'
    write(*,*) 'Execute align without command line arguments to get instructions'
    stop
endif
! Initialize the search class
call make_rbased_search( b )
if( spec > 0 )then ! Previous alignment data are available
    call calc_lowpass_lims
    if( mode == 23 )then ! only for finding filtering treshold or do spectral sorting
        stop             ! ...so it ends here
    endif   
endif
! Do the alignment
open(unit=23, file=outfile, status='replace', iostat=file_stat, action='write', form='formatted')
call fopen_err( 'In: align', file_stat )
do i=fromp,top
    write(*,'(A,I6,A)') '>>> ORIENTATION SEARCH FOR PARTICLE ', i, ' <<<'
    call read_fplane( b%f(ptcl)%arr, fstk, i )
    call rbased_evol_align( i, fhandle  )
end do
close(23)
call haloween( 0 )
write(0,'(a)') "**** ALIGN NORMAL STOP ****"
end program align