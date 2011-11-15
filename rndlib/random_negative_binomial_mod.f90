    MODULE random_negative_binomial_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_negative_binomial(n,p)
! .. Use Statements ..
        USE random_standard_gamma_mod
        USE random_poisson_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        INTEGER :: random_negative_binomial
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: p
        INTEGER, INTENT (IN) :: n
! ..
! .. Local Scalars ..
        REAL :: a, r, y
! ..
! .. Intrinsic Functions ..
        INTRINSIC REAL
! ..
! .. Executable Statements ..

!**********************************************************************
!     INTEGER FUNCTION IGNNBN( N, P )
!                GENerate Negative BiNomial random deviate
!                              Function
!     Generates a single random deviate from a negative binomial
!     distribution.
!                              Arguments
!     N  --> Required number of events.
!                              INTEGER N
!     JJV                      (N > 0)
!     P  --> The probability of an event during a Bernoulli trial.
!                              REAL P
!     JJV                      (0.0 < P < 1.0)
!                              Method
!     Algorithm from page 480 of
!     Devroye, Luc
!     Non-Uniform Random Variate Generation.  Springer-Verlag,
!     New York, 1986.
!**********************************************************************
!     JJV changed to call SGAMMA directly
!     REAL random_gamma
!      EXTERNAL random_gamma,random_poisson
!     Check Arguments
!     JJV changed argumnet checker to abort if N <= 0
        IF (n<=0) STOP 'N <= 0 in IGNNBN'
        IF (p<=0.0) STOP 'P <= 0.0 in IGNNBN'
        IF (p>=1.0) STOP 'P >= 1.0 in IGNNBN'

!     Generate Y, a random gamma (n,(1-p)/p) variable
!     JJV Note: the above parametrization is consistent with Devroye,
!     JJV       but gamma (p/(1-p),n) is the equivalent in our code
        r = REAL(n)
        a = p/(1.0-p)
!      y = random_gamma(a,r)
        y = random_standard_gamma(r)/a

!     Generate a random Poisson(y) variable
        random_negative_binomial = random_poisson(y)
        RETURN

      END FUNCTION random_negative_binomial

!*********************************************************************

    END MODULE random_negative_binomial_mod
