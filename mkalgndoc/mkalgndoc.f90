!==Program mkalgndoc
!
! _mkalgndoc_ is a SIMPLE program for making an alignment document with even Eulers.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011-09-11.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-09-11
!
program mkalgndoc
use simple_eulers
use simple_aligndata
use simple_params
implicit none
save
type(eulers)    :: e
type(aligndata) :: a
integer         :: i
real            :: e1, e2, e3
if( command_argument_count() < 1 )then
    write(*,*) './mkalgndoc nspace=2000 [pgrp=d2]'
    stop
endif
! parse command line
call make_params
! make eulers
e = new_eulers(nspace)
call spiral_eulers( e, pgrp )
! make aligndata
a = new_aligndata(1, 1)
! print
do i=1,nspace
    call get_euler( e, i, e1, e2, e3 )
    call set_aligndata( a, 1, e1=e1, e2=e2, e3=e3, x=0., y=0., corr=0., state=1 )
    call print_aligndata( a, 1, corr='CORR:', free_corr='FREE_CORR',&
    modelq='MODELQ:', alignq='ALIGNQ', lowpass='HRES:', state='STATE:' )
end do
end program mkalgndoc