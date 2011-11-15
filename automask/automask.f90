!==Program automask
!
! _automask_ is a SIMPLE program for solvent flattening of a spider volume volume.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011
!
!==Changes are documented below
!
!*
!
program automask
use simple_cmdline
use simple_build
use simple_params
use simple_volspi
use simple_jiffys
implicit none
save
! declaration section
type(build), target :: b
logical :: cmderr(5)
if( command_argument_count() < 5 )then
    write(*,*) './automask vol1=invol.spi box=100 smpd=2.33 lp=<low-pass limit(in A){20-40}> mw=<molecular weight(in kD)> [msk=40] [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr(1) = .not. defined_cmd_carg('vol1')
cmderr(2) = .not. defined_cmd_rarg('box')
cmderr(3) = .not. defined_cmd_rarg('smpd')
cmderr(4) = .not. defined_cmd_rarg('lp')
cmderr(5) = .not. defined_cmd_rarg('mw')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for binarize defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! build all objects required for alignment
b = new_build(31) ! mode=31
! auto mask
call automask_vspi(b,1)
call haloween( 0 )
write(0,'(a,10xa)') "GENERATED MASK:", trim(masks(1))
write(0,'(a,1xa)') "GENERATED MASKED VOLUME:", trim(vols_msk(1))
write(0,'(a)') "**** AUTOMASK NORMAL STOP ****"
end program automask