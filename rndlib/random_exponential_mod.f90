    MODULE random_exponential_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_exponential(av)
! .. Use Statements ..
        USE random_standard_exponential_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_exponential
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: av
! ..
! .. Executable Statements ..

!**********************************************************************
!     REAL FUNCTION GENEXP( AV )
!                    GENerate EXPonential random deviate
!                              Function
!     Generates a single random deviate from an exponential
!     distribution with mean AV.
!                              Arguments
!     AV --> The mean of the exponential distribution from which
!            a random deviate is to be generated.
!                              REAL AV
!     JJV                      (AV >= 0)
!     GENEXP <-- The random deviate.
!                              REAL GENEXP
!                              Method
!     Renames SEXPO from TOMS as slightly modified by BWB to use RANF
!     instead of SUNIF.
!     For details see:
!               Ahrens, J.H. and Dieter, U.
!               Computer Methods for Sampling From the
!               Exponential and Normal Distributions.
!               Comm. ACM, 15,10 (Oct. 1972), 873 - 882.
!**********************************************************************
!     JJV added check to ensure AV >= 0.0
        IF (av<0.0) THEN
          WRITE (*,*) 'AV < 0.0 in GENEXP - ABORT'
          WRITE (*,*) 'Value of AV: ', av
          STOP 'AV < 0.0 in GENEXP - ABORT'
        END IF

        random_exponential = random_standard_exponential()*av
        RETURN

      END FUNCTION random_exponential

!*********************************************************************

    END MODULE random_exponential_mod
