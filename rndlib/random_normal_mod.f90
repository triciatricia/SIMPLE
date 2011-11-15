    MODULE random_normal_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_normal(mean,sd)
! .. Use Statements ..
        USE random_standard_normal_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_normal
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: mean, sd
! ..
! .. Executable Statements ..

!**********************************************************************
!     REAL FUNCTION GENNOR( MEAN, SD )
!         GENerate random deviate from a NORmal distribution
!                              Function
!     Generates a single random deviate from a normal distribution
!     with mean, MEAN, and standard deviation, SD.
!                              Arguments
!     MEAN --> Mean of the normal distribution.
!                              REAL MEAN
!     SD --> Standard deviation of the normal distribution.
!                              REAL SD
!     JJV                      (SD >= 0)
!     GENNOR <-- Generated normal deviate.
!                              REAL GENNOR
!                              Method
!     Renames SNORM from TOMS as slightly modified by BWB to use RANF
!     instead of SUNIF.
!     For details see:
!               Ahrens, J.H. and Dieter, U.
!               Extensions of Forsythe's Method for Random
!               Sampling from the Normal Distribution.
!               Math. Comput., 27,124 (Oct. 1973), 927 - 937.
!**********************************************************************
!     JJV added check to ensure SD >= 0.0
        IF (sd<0.0) THEN
          WRITE (*,*) 'SD < 0.0 in GENNOR - ABORT'
          WRITE (*,*) 'Value of SD: ', sd
          STOP 'SD < 0.0 in GENNOR - ABORT'
        END IF

        random_normal = sd*random_standard_normal() + mean
        RETURN

      END FUNCTION random_normal

!*********************************************************************

    END MODULE random_normal_mod
