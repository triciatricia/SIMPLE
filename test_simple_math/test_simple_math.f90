! -------------------------------------------------------------------------------------
! The purpose is to test functions and subroutines added to simple_math. 
! -------------------------------------------------------------------------------------
program test_simple_math
use simple_math
use tester_mod
implicit none

logical                         :: result(1000)

! Initialize
result = .TRUE.

! -------------------------------------------------------------------------------------
! lowfact
! (1:9)
! -------------------------------------------------------------------------------------
result(1) = fuzzy_compare(lowfact(1), 1, 0)
result(2) = fuzzy_compare(lowfact(12), 479001600, 0)
! This should error:
! write(*,*) lowfact(13)

! -------------------------------------------------------------------------------------
! Report results of tests
! -------------------------------------------------------------------------------------
call report(result, size(result))

end program test_simple_math