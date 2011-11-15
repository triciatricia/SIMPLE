    MODULE random_uniform_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_uniform(low,high)
! .. Use Statements ..
        USE random_standard_uniform_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_uniform
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: high, low
! ..
! .. Executable Statements ..

!**********************************************************************
!     REAL FUNCTION GENUNF( LOW, HIGH )
!               GeNerate Uniform Real between LOW and HIGH
!                              Function
!     Generates a real uniformly distributed between LOW and HIGH.
!                              Arguments
!     LOW --> Low bound (exclusive) on real value to be generated
!                         REAL LOW
!     HIGH --> High bound (exclusive) on real value to be generated
!                         REAL HIGH
!**********************************************************************
        IF (low>high) THEN
          WRITE (*,*) 'LOW > HIGH in GENUNF: LOW ', low, ' HIGH: ', high
          WRITE (*,*) 'Abort'
          STOP 'LOW > High in GENUNF - Abort'
        END IF

        random_uniform = low + (high-low)*random_standard_uniform()

        RETURN

      END FUNCTION random_uniform

!*********************************************************************

    END MODULE random_uniform_mod
