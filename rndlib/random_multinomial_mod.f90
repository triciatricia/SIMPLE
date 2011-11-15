    MODULE random_multinomial_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      SUBROUTINE random_multinomial(n,p,ncat,ix)
! .. Use Statements ..
        USE random_binomial_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Scalar Arguments ..
        INTEGER, INTENT (IN) :: n, ncat
! ..
! .. Array Arguments ..
        REAL, INTENT (IN) :: p(*)
        INTEGER, INTENT (INOUT) :: ix(*)
! ..
! .. Local Scalars ..
        REAL :: prob, ptot, sum
        INTEGER :: i, icat, ntot
! ..
! .. Executable Statements ..

!**********************************************************************
!            SUBROUTINE GENMUL( N, P, NCAT, IX )
!     GENerate an observation from the MULtinomial distribution
!                              Arguments
!     N --> Number of events that will be classified into one of
!           the categories 1..NCAT
!                         INTEGER N
!     P --> Vector of probabilities.  P(i) is the probability that
!           an event will be classified into category i.  Thus, P(i)
!           must be [0,1]. Only the first NCAT-1 P(i) must be defined
!           since P(NCAT) is 1.0 minus the sum of the first
!           NCAT-1 P(i).
!                         REAL P(NCAT-1)
!     NCAT --> Number of categories.  Length of P and IX.
!                         INTEGER NCAT
!     IX <-- Observation from multinomial distribution.  All IX(i)
!            will be nonnegative and their sum will be N.
!                         INTEGER IX(NCAT)
!                              Method
!     Algorithm from page 559 of
!     Devroye, Luc
!     Non-Uniform Random Variate Generation.  Springer-Verlag,
!     New York, 1986.
!**********************************************************************
!     Check Arguments
        IF (n<0) STOP 'N < 0 in random_multinomial'
        IF (ncat<=1) STOP 'NCAT <= 1 in random_multinomial'
        ptot = 0.0
        DO i = 1, ncat - 1
          IF (p(i)<0.0) STOP 'Some P(i) < 0 in GENMUL'
          IF (p(i)>1.0) STOP 'Some P(i) > 1 in GENMUL'
          ptot = ptot + p(i)
        END DO
        IF (ptot>0.99999) STOP 'Sum of P(i) > 1 in GENMUL'

!     Initialize variables
        ntot = n
        sum = 1.0
        ix(:ncat) = 0

!     Generate the observation
        DO icat = 1, ncat - 1
          prob = p(icat)/sum
          ix(icat) = random_binomial(ntot,prob)
          ntot = ntot - ix(icat)
          IF (ntot<=0) RETURN
          sum = sum - p(icat)
        END DO
        ix(ncat) = ntot

!     Finished
        RETURN

      END SUBROUTINE random_multinomial

!*********************************************************************

    END MODULE random_multinomial_mod
