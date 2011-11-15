!==Program rotvol
!
! _rotvol_ is a SIMPLE program for rotating a spider volume spider volume volume.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011
!
!==Changes are documented below
!
!* 
!
program rotvol
use simple_cmdline
use simple_build
use simple_params
use simple_volspi
use simple_jiffys
use simple_fgridvol
implicit none
save
! declaration section
type(build) :: b
logical     :: cmderr(3)
if( command_argument_count() < 3 )then
    write(*,*) './rotvol vol1=invol.spi box=100 smpd=2.33 [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr(1) = .not. defined_cmd_carg('vol1')
cmderr(2) = .not. defined_cmd_rarg('box')
cmderr(3) = .not. defined_cmd_rarg('smpd')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for rotvol defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! build objects
b = new_build(32) ! mode=32
winsz = 2
wchoice = 2
call make_fgridvol( b, 'old' )
call rot_fvol( 92.08,  17.44, 259.3, 1 )
! let the rotated volume override the old one
b%s3d(1)%fvol = b%s3d(1)%fvol_new
call fft_rev_fvol(b,1)
! ouput volume
call write_volspi(b%s3d(1)%vspi, trim(adjustl(cwd))//'/rotvol.spi')
call haloween( 0 )
write(0,'(a,1xa)') "GENERATED ROTATED VOLUME:", trim(adjustl(cwd))//'/rotvol.spi'
write(0,'(a)') "**** ROTVOL NORMAL STOP ****"
end program rotvol