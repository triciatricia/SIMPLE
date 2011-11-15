    MODULE random_standard_exponential_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_standard_exponential()
!**********************************************************************C
!                                                                      C
!                                                                      C
!     (STANDARD-)  E X P O N E N T I A L   DISTRIBUTION                C
!                                                                      C
!                                                                      C
!**********************************************************************C
!**********************************************************************C
!                                                                      C
!     FOR DETAILS SEE:                                                 C
!                                                                      C
!               AHRENS, J.H. AND DIETER, U.                            C
!               COMPUTER METHODS FOR SAMPLING FROM THE                 C
!               EXPONENTIAL AND NORMAL DISTRIBUTIONS.                  C
!               COMM. ACM, 15,10 (OCT. 1972), 873 - 882.               C
!                                                                      C
!     ALL STATEMENT NUMBERS CORRESPOND TO THE STEPS OF ALGORITHM       C
!     'SA' IN THE ABOVE PAPER (SLIGHTLY MODIFIED IMPLEMENTATION)       C
!                                                                      C
!     Modified by Barry W. Brown, Feb 3, 1988 to use RANF instead of   C
!     SUNIF.  The argument IR thus goes away.                          C
!                                                                      C
!**********************************************************************C
!     Q(N) = SUM(ALOG(2.0)**K/K!)    K=1,..,N ,      THE HIGHEST N
!     (HERE 8) IS DETERMINED BY Q(N)=1.0 WITHIN STANDARD PRECISION
!     JJV added a Save statement for q (in Data statement)
! .. Use Statements ..
        USE random_standard_uniform_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_standard_exponential
! ..
! .. Local Scalars ..
        REAL :: a, q1, u, umin, ustar
        INTEGER :: i
! ..
! .. Local Arrays ..
        REAL, SAVE :: q(8)
! ..
! .. Intrinsic Functions ..
        INTRINSIC AMIN1
! ..
! .. Equivalences ..
        EQUIVALENCE (q(1),q1)
! ..
! .. Data Statements ..
        DATA q/0.6931472, 0.9333737, 0.9888778, 0.9984959, 0.9998293, &
          0.9999833, 0.9999986, 0.9999999/
! ..
! .. Executable Statements ..

        a = 0.0
        u = random_standard_uniform()
        GO TO 20

10      CONTINUE
        a = a + q1
20      CONTINUE
        u = u + u
!     JJV changed the following to reflect the true algorithm and
!     JJV prevent unpredictable behavior if U is initially 0.5.
!      IF (u.LE.1.0) GO TO 20
        IF (u<1.0) GO TO 10
        u = u - 1.0
        IF (u<=q1) THEN
          random_standard_exponential = a + u
          RETURN
        END IF

        i = 1
        ustar = random_standard_uniform()
        umin = ustar
        ustar = random_standard_uniform()
        umin = AMIN1(ustar,umin)
        i = i + 1
        DO WHILE (u>q(i))
          ustar = random_standard_uniform()
          umin = AMIN1(ustar,umin)
          i = i + 1
        END DO
        random_standard_exponential = a + umin*q1
        RETURN

      END FUNCTION random_standard_exponential

!*********************************************************************

    END MODULE random_standard_exponential_mod
