!==Program cenvol
!
! _cenvol_ is a SIMPLE program for centering a spider volume volume according to the center of mass of the binary volume.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011
!
!==Changes are documented below
!
!* 
!
program cenvol
use simple_cmdline
use simple_build
use simple_params
use simple_volspi
use simple_jiffys
implicit none
save
! declaration section
type(build) :: b
logical     :: cmderr(5)
if( command_argument_count() < 5 )then
    write(*,*) './cenvol vol1=invol.spi box=100 smpd=2.33 lp=<low-pass limit(in A){15-30}> mw=<molecular weight(in kD)>  [debug=<yes|no>]'
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
    write(*,*) 'ERROR, not all input variables for cenvol defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! build objects
b = new_build(32) ! mode=32
call center_vspi(b,1)
! ouput volume
call write_volspi(b%s3d(1)%vspi, trim(adjustl(cwd))//'/cenvol.spi')
call haloween( 0 )
write(0,'(a,1xa)') "GENERATED CENTERED VOLUME:", trim(adjustl(cwd))//'/cenvol.spi'
write(0,'(a)') "**** CENVOL NORMAL STOP ****"
end program cenvol