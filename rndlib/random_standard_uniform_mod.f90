    MODULE random_standard_uniform_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_standard_uniform()
! .. Use Statements ..
        USE ecuyer_cote_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_standard_uniform
! ..
! .. Executable Statements ..

!----------------------------------------------------------------------
!     REAL FUNCTION random_standard_uniform()
!     Returns a random floating point number from a uniform distribution
!     over 0 - 1 (endpoints of this interval are not returned) using the
!     current generator
!     This is a transcription from Pascal to Fortran of routine
!     Uniform_01 from the paper
!     L'Ecuyer, P. and Cote, S. "Implementing a Random Number Package
!     with Splitting Facilities." ACM Transactions on Mathematical
!     Software, 17:98-111 (1991)
!----------------------------------------------------------------------
!     4.656613057E-10 is 1/M1  M1 is set in a data statement in
!     random_large_integer
!      and is currently 2147483563. If M1 changes, change this also.
        random_standard_uniform = random_large_integer()*4.656613057E-10
        RETURN

      END FUNCTION random_standard_uniform

!*********************************************************************

    END MODULE random_standard_uniform_mod
