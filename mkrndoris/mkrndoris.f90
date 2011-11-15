!==Program mkrndoris
!
! _mkrndoris_ is a SIMPLE program for making random orinetations.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011-09-11.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-09-11
!
program mkrndoris
use simple_rnd
implicit none
save
character(len=60) :: str 
integer :: noris, i
real :: trs
if( command_argument_count() < 2 )then
    write(*,*) './mkrndoris nr_of_oris shift'
    stop
endif
call seed_rnd
call getarg(1,str)
read(str,'(I10)') noris
call getarg(2,str)
read(str,'(F3.0)') trs
do i=1,noris
  write(*,*) ran3()*360., ran3()*180., ran3()*360., 2.*trs*ran3()-trs, 2.*trs*ran3()-trs 
end do
end program mkrndoris
