!==Program mkrndints
!
! _mkrndints_ is a SIMPLE program for making random integers.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011-09-11.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-09-11
!
program mkrndints
use simple_rnd
implicit none
save
character(len=60) :: str
integer           :: n, np, i
if( command_argument_count() < 2 )then
    write(*,*) './mkrndints nr_of_nrs_to_gen nr_of_nrs'
    stop
endif
call seed_rnd
call getarg(1,str)
read(str,'(I10)') n
call getarg(2,str)
read(str,'(I10)') np
do i=1,n
    write(*,*) irnd_uni(np)
end do
end program mkrndints