!==Program dock
!
! _dock_ is a SIMPLE program for docking two spider volumes. vol1 is reference and vol2 target.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011
!
!==Changes are documented below
!
!* 
!
program dock
use simple_cmdline
use simple_build
use simple_params
use simple_volspi
use simple_jiffys
use simple_fgridvol
use simple_dock
use simple_fvols_corr
use simple_rnd
implicit none
save
! declaration section
type(build)        :: b
logical            :: cmderr(7)
real               :: e1, e2, e3, corr
integer            :: i
character(len=120) :: dig
character(len=256) :: fnam
if( command_argument_count() < 9 )then
    write(*,*) './dock vol1=invol1.spi vol2=invol2.spi box=100 smpd=2.33 lp=<low-pass limit(in A){15-30}> mw=<molecular weight(in kD)> msk=<mask radius(in pixels)> nthr=<nr of openMP threads> nrnds=<nr of rounds> [nspace=<nr of projection directions>] [angres=<angular resolution in the plane>] [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr(1) = .not. defined_cmd_carg('vol1')
cmderr(2) = .not. defined_cmd_carg('vol2')
cmderr(3) = .not. defined_cmd_rarg('box')
cmderr(4) = .not. defined_cmd_rarg('smpd')
cmderr(5) = .not. defined_cmd_rarg('lp')
cmderr(6) = .not. defined_cmd_rarg('mw')
cmderr(7) = .not. defined_cmd_rarg('msk')
cmderr(8) = .not. defined_cmd_rarg('nthr')
cmderr(9) = .not. defined_cmd_rarg('nrnds')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for dock defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! seed random number generator
call seed_rnd
! build objects
b = new_build(34) ! mode=34
! center volumes
write(*,'(A)') '>>> CENTERING VOLUMES'
do i=1,nstates 
    call center_vspi( b, i )
end do
! make docking functionality
call make_dock( b )
winsz = 2
wchoice = 2
do i=1,nrnds
    write(*,'(A)') '***************************'
    write(*,'(A)') '>>> DOCKING VOLUMES'
    call dock_fvols( 1, 2, i )
    write(*,'(A)') '>>> ROTATING TARGET VOLUME ACCORDING TO DOCKING SOLUTION'
    call get_aligndata( b%a, i, e1=e1, e2=e2, e3=e3 )
    call rot_fvol( e1, e2, e3, 2 )
    call fft_rev_fvol_new(b,2)
    ! ouput volume
    write(dig,*) i
    fnam = trim(adjustl(cwd))//'/docked'//trim(adjustl(dig))//'.spi'
    call write_volspi(b%s3d(2)%vspi, fnam)
    write(0,'(1Xa,1xa)') "GENERATED DOCKED VOLUME:", trim(fnam)
end do
! write de solutions to file
call write_aligndata( b%a, trim(adjustl(cwd))//'dock_de_align.dat' )
call haloween( 0 )
write(0,'(a)') "WROTE SOLUTIONS TO FILE dock_de_align.dat"
write(0,'(a)') "**** DOCK NORMAL STOP ****"
end program dock