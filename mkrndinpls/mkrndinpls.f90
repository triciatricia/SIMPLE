!==Program mkrndinpls
!
! _mkrndinpls_ is a SIMPLE program for making random in-plane degrees of freedom.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011-09-11.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-09-11
!
program mkrndinpls
use simple_rnd
implicit none
save
character(len=60) :: str
integer          :: n, i
real              :: trs
if( command_argument_count() < 2 )then
    write(*,*) './mkrndinpls nr_of_inpls shift'
    stop
endif
call seed_rnd
call getarg(1,str)
read(str,'(I10)') n
call getarg(2,str)
read(str,'(F3.0)') trs
do i=1,n
    write(*,*) 360.*ran3(), 2.*trs*ran3()-trs, 2.*trs*ran3()-trs 
end do
end program mkrndinpls
