    MODULE random_gamma_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_gamma(scale,shape)
! .. Use Statements ..
        USE random_standard_gamma_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_gamma
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: scale
        REAL :: shape
! ..
! .. Executable Statements ..

!**********************************************************************
!     REAL FUNCTION RANDOM_GAMMA( scale, shape )
!           GENerates random deviates from GAMma distribution
!                              Function
!     Generates random deviates from the gamma distribution whose
!     density is
!          (scale**shape)/Gamma(shape) * X**(shape-1) * Exp(-scale*X)
!                              Arguments
!     JJV added the argument ranges supported
!     scale --> Location parameter of Gamma distribution
!                              REAL scale ( scale > 0 )
!     shape --> Shape parameter of Gamma distribution
!                              REAL shape ( shape > 0 )
!                              Method
!     Renames SGAMMA from TOMS as slightly modified by BWB to use RANF
!     instead of SUNIF.
!     For details see:
!               (Case shape >= 1.0)
!               Ahrens, J.H. and Dieter, U.
!               Generating Gamma Variates by scale
!               Modified Rejection Technique.
!               Comm. ACM, 25,1 (Jan. 1982), 47 - 54.
!     Algorithm GD
!     JJV altered the following to reflect random_standard_gamma argument ranges
!               (Case 0.0 < shape < 1.0)
!               Ahrens, J.H. and Dieter, U.
!               Computer Methods for Sampling from Gamma,
!               Beta, Poisson and Binomial Distributions.
!               Computing, 12 (1974), 223-246/
!     Adapted algorithm GS.
!**********************************************************************
!     JJV added argument value checker
        IF (scale<=0.0 .OR. shape<=0.0) THEN
          WRITE (*,*) 'In RANDOM_GAMMA - Either (1) Location &
            &param scale <= 0.0 or'
          WRITE (*,*) '(2) Shape param shape <= 0.0 - ABORT!'
          WRITE (*,*) 'scale value: ', scale, 'shape value: ', shape
          STOP 'Location or shape param out of range in RANDOM_GAMMA &
            &- ABORT!'
        END IF
!     JJV end addition

        random_gamma = random_standard_gamma(shape)/scale
!      random_gamma = random_gamma/scale
        RETURN

      END FUNCTION random_gamma

!*********************************************************************

    END MODULE random_gamma_mod
