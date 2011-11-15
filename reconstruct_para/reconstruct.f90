!==Program reconstruct
!
! _reconstruct_ is the SIMPLE program used for calculating volumes from aligned particle images by Fourier gridding.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011-08-16.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-08-16
!
program reconstruct
use simple_build
use simple_params
use simple_fgridvol
use simple_jiffys
use simple_volspi
use simple_cmdline
implicit none
save
type(build), target, save :: b
logical :: cmderr(4)
integer :: s
if( command_argument_count() < 4 )then
    write(*,*) './reconstruct fstk=fprojs.fim vol1=recvol_1.spi [vol2=recvol_2.spi etc.] oritab=algndoc.dat nthr=<nr of openMP threads> [winsz=2] [wchoice=2] [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr(1) = .not. defined_cmd_carg('fstk')
cmderr(2) = .not. defined_cmd_carg('vol1')
cmderr(3) = .not. defined_cmd_carg('oritab')
cmderr(4) = .not. defined_cmd_rarg('nthr')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for reconstruct defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! Build all objects required for alignment
b = new_build(30)
! Reconstruct Fourier volumes
! Associate pointer in fgridvol
call make_fgridvol( b, 'old' )
! Grid
call fgrid
! Write
do s=1,nstates
    call fft_rev_fvol( b, s )
    call write_volspi( b%s3d(s)%vspi, vols(s) )
end do
call haloween( 0 )
write(0,'(a)') "**** RECONSTRUCT NORMAL STOP ****"
end program reconstruct