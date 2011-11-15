!==Program auto_mask
!
! _auto_mask_ is a SIMPLE program for solvent flattening of a spider volume volume.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011-09-11.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-09-11
!
program auto_mask
use simple_build
use simple_jiffys
implicit none
save
type(build), target, save :: b
if( command_argument_count() < 5 )then
    write(*,*) './auto_mask vol1=invol.spi amsklp=40 box=100 smpd=2.33 voltyp=<spider|simple> [msk=40] [debug=<yes|no>]'
    stop
endif
! build all objects required for alignment
b = new_build( 31 )
! auto mask
call auto_mask_ref( b,1 )
call haloween( 0 )
write(0,'(a)') "**** AUTO_MASK NORMAL STOP ****"
end program auto_mask