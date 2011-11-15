    MODULE random_permutation_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      SUBROUTINE random_permutation(iarray,larray)
! .. Use Statements ..
        USE random_uniform_integer_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Scalar Arguments ..
        INTEGER :: larray
! ..
! .. Array Arguments ..
        INTEGER, INTENT (INOUT) :: iarray(larray)
! ..
! .. Local Scalars ..
        INTEGER :: i, itmp, iwhich
! ..
! .. Executable Statements ..

!**********************************************************************
!    SUBROUTINE GENPRM( IARRAY, LARRAY )
!               GENerate random PeRMutation of iarray
!                              Arguments
!     IARRAY <--> On output IARRAY is a random permutation of its
!                 value on input
!                         INTEGER IARRAY( LARRAY )
!     LARRAY <--> Length of IARRAY
!                         INTEGER LARRAY
!**********************************************************************
        DO i = 1, larray
          iwhich = random_uniform_integer(i,larray)
          itmp = iarray(iwhich)
          iarray(iwhich) = iarray(i)
          iarray(i) = itmp
        END DO
        RETURN

      END SUBROUTINE random_permutation

!*********************************************************************

    END MODULE random_permutation_mod
