!==Program mkrndeuls
!
! _mkrndeuls_ is a SIMPLE program for making random Euler angles.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011-09-11.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-09-11
!
program mkrndeuls
use simple_rnd
implicit none
save
character(len=60) :: str 
integer :: neuls, i
if( command_argument_count() < 1 )then
    write(*,*) './mkrndeuls nr_of_eulers'
    stop
endif
call seed_rnd
call getarg(1,str)
read(str,'(I10)') neuls
do i=1,neuls
  write(*,*) ran3()*360., ran3()*180., ran3()*360.
end do
end program mkrndeuls
