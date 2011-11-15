    MODULE random_poisson_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_poisson(lambda)
!**********************************************************************
!     INTEGER FUNCTION IGNPOI( LAMBDA )
!                    GENerate POIsson random deviate
!                              Function
!     Generates a single random deviate from a Poisson
!     distribution with mean LAMBDA.
!                              Arguments
!     LAMBDA --> The mean of the Poisson distribution from which
!            a random deviate is to be generated.
!                              REAL LAMBDA
!     JJV                    (LAMBDA >= 0.0)
!     IGNPOI <-- The random deviate.
!                              INTEGER IGNPOI (non-negative)
!                              Method
!     Renames KPOIS from TOMS as slightly modified by BWB to use RANF
!     instead of SUNIF.
!     For details see:
!               Ahrens, J.H. and Dieter, U.
!               Computer Generation of Poisson Deviates
!               From Modified Normal Distributions.
!               ACM Trans. Math. Software, 8, 2
!               (June 1982),163-179
!**********************************************************************
!**********************************************************************C
!**********************************************************************C
!                                                                      C
!                                                                      C
!     P O I S S O N  DISTRIBUTION                                      C
!                                                                      C
!                                                                      C
!**********************************************************************C
!**********************************************************************C
!                                                                      C
!     FOR DETAILS SEE:                                                 C
!                                                                      C
!               AHRENS, J.H. AND DIETER, U.                            C
!               COMPUTER GENERATION OF POISSON DEVIATES                C
!               FROM MODIFIED NORMAL DISTRIBUTIONS.                    C
!               ACM TRANS. MATH. SOFTWARE, 8,2 (JUNE 1982), 163 - 179. C
!                                                                      C
!     (SLIGHTLY MODIFIED VERSION OF THE PROGRAM IN THE ABOVE ARTICLE)  C
!                                                                      C
!**********************************************************************C
!      INTEGER FUNCTION IGNPOI(IR,LAMBDA)
!     INPUT:  IR=CURRENT STATE OF BASIC RANDOM NUMBER GENERATOR
!             LAMBDA=MEAN LAMBDA OF THE POISSON DISTRIBUTION
!     OUTPUT: IGNPOI=SAMPLE FROM THE POISSON-(LAMBDA)-DISTRIBUTION
!     MUPREV=PREVIOUS LAMBDA, MUOLD=LAMBDA AT LAST EXECUTION OF STEP P OR CASE B
!     TABLES: COEFFICIENTS A0-A7 FOR STEP F. FACTORIALS FACT
!     COEFFICIENTS A(K) - FOR PX = FK*V*V*SUM(A(K)*V**K)-DEL
!     SEPARATION OF CASES A AND B
!     JJV I added a variable 'll' here - it is the 'l' for CASE A
!     JJV added this for case: lambda unchanged
!     JJV end addition - I am including vars in Data statements
!     JJV changed initial values of MUPREV and MUOLD to -1.0E37
!     JJV if no one calls IGNPOI with LAMBDA = -1.0E37 the first time,
!     JJV the code shouldn't break
! .. Use Statements ..
        USE random_standard_uniform_mod
        USE random_standard_exponential_mod
        USE random_standard_normal_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        INTEGER :: random_poisson
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: lambda
! ..
! .. Local Scalars ..
        REAL, SAVE :: a0, a1, a2, a3, a4, a5, a6, a7, c, c0, c1, c2, c3, &
          d, muold, muprev, omega, p, p0, q, s
        REAL :: b1, b2, del, difmuk, e, fk, fx, fy, g, px, py, t, u, v, &
          x, xx
        INTEGER :: j, k, kflag
        INTEGER, SAVE :: l, ll, m
! ..
! .. Local Arrays ..
        REAL, SAVE :: fact(10)
        REAL :: pp(35)
! ..
! .. Intrinsic Functions ..
        INTRINSIC ABS, ALOG, EXP, FLOAT, IFIX, MAX0, MIN0, SIGN, SQRT
! ..
! .. Data Statements ..
        DATA muprev, muold/ -1.0E37, -1.0E37/
        DATA a0, a1, a2, a3, a4, a5, a6, a7/ -.5, 0.3333333, -.2500068, &
          0.2000118, -.1661269, 0.1421878, -.1384794, 0.1250060/
        DATA fact/1., 1., 2., 6., 24., 120., 720., 5040., 40320., &
          362880./
! ..
! .. Executable Statements ..

        IF (lambda/=muprev) THEN
          IF (lambda<10.0) GO TO 50

!     C A S E  A. (RECALCULATION OF S,D,LL IF LAMBDA HAS CHANGED)

!     JJV This is the case where I changed 'l' to 'll'
!     JJV Here 'll' is set once and used in a comparison once

          muprev = lambda
          s = SQRT(lambda)
          d = 6.0*lambda*lambda

!             THE POISSON PROBABILITIES PK EXCEED THE DISCRETE NORMAL
!             PROBABILITIES FK WHENEVER K >= M(LAMBDA). LL=IFIX(LAMBDA-1.1484)
!             IS AN UPPER BOUND TO M(LAMBDA) FOR ALL LAMBDA >= 10 .

          ll = IFIX(lambda-1.1484)
        END IF

!     STEP N. NORMAL SAMPLE - SNORM(IR) FOR STANDARD NORMAL DEVIATE

        g = lambda + s*random_standard_normal()
        IF (g>=0.0) THEN
          random_poisson = IFIX(g)

!     STEP I. IMMEDIATE ACCEPTANCE IF IGNPOI IS LARGE ENOUGH

          IF (random_poisson>=ll) RETURN

!     STEP S. SQUEEZE ACCEPTANCE - SUNIF(IR) FOR (0,1)-SAMPLE U

          fk = FLOAT(random_poisson)
          difmuk = lambda - fk
          u = random_standard_uniform()
          IF (d*u>=difmuk*difmuk*difmuk) RETURN
        END IF

!     STEP P. PREPARATIONS FOR STEPS Q AND H.
!             (RECALCULATIONS OF PARAMETERS IF NECESSARY)
!             .3989423=(2*PI)**(-.5)  .416667E-1=1./24.  .1428571=1./7.
!             THE QUANTITIES B1, B2, C3, C2, C1, C0 ARE FOR THE HERMITE
!             APPROXIMATIONS TO THE DISCRETE NORMAL PROBABILITIES FK.
!             C=.1069/LAMBDA GUARANTEES MAJORIZATION BY THE 'HAT'-FUNCTION.

        IF (lambda/=muold) THEN
          muold = lambda
          omega = 0.3989423/s
          b1 = 0.4166667E-1/lambda
          b2 = 0.3*b1*b1
          c3 = 0.1428571*b1*b2
          c2 = b2 - 15.*c3
          c1 = b1 - 6.*b2 + 45.*c3
          c0 = 1. - b1 + 3.*b2 - 15.*c3
          c = 0.1069/lambda
        END IF
        IF (g<0.0) GO TO 20

!             'SUBROUTINE' F IS CALLED (KFLAG=0 FOR CORRECT RETURN)

        kflag = 0
        GO TO 40

!     STEP Q. QUOTIENT ACCEPTANCE (RARE CASE)

10      CONTINUE
        IF (fy-u*fy<=py*EXP(px-fx)) RETURN

!     STEP E. EXPONENTIAL SAMPLE - SEXPO(IR) FOR STANDARD EXPONENTIAL
!             DEVIATE E AND SAMPLE T FROM THE LAPLACE 'HAT'
!             (IF T <= -.6744 THEN PK < FK FOR ALL LAMBDA >= 10.)

20      CONTINUE
        e = random_standard_exponential()
        u = random_standard_uniform()
        u = u + u - 1.0
        t = 1.8 + SIGN(e,u)
        DO WHILE (t<=(-.6744))
          e = random_standard_exponential()
          u = random_standard_uniform()
          u = u + u - 1.0
          t = 1.8 + SIGN(e,u)
        END DO
        random_poisson = IFIX(lambda+s*t)
        fk = FLOAT(random_poisson)
        difmuk = lambda - fk

!             'SUBROUTINE' F IS CALLED (KFLAG=1 FOR CORRECT RETURN)

        kflag = 1
        GO TO 40

!     STEP H. HAT ACCEPTANCE (E IS REPEATED ON REJECTION)

30      CONTINUE
        IF (c*ABS(u)>py*EXP(px+e)-fy*EXP(fx+e)) GO TO 20
        RETURN

!     STEP F. 'SUBROUTINE' F. CALCULATION OF PX,PY,FX,FY.
!             CASE IGNPOI .LT. 10 USES FACTORIALS FROM TABLE FACT

40      CONTINUE
        IF (random_poisson<10) THEN
          px = -lambda
          py = lambda**random_poisson/fact(random_poisson+1)
        ELSE

!             CASE IGNPOI .GE. 10 USES POLYNOMIAL APPROXIMATION
!             A0-A7 FOR ACCURACY WHEN ADVISABLE
!             .8333333E-1=1./12.  .3989423=(2*PI)**(-.5)

          del = 0.8333333E-1/fk
          del = del - 4.8*del*del*del
          v = difmuk/fk
          IF (ABS(v)>0.25) THEN
            px = fk*ALOG(1.0+v) - difmuk - del
          ELSE

            px = fk*v*v*(((((((a7*v+a6)*v+a5)*v+a4)*v+a3)*v+ &
              a2)*v+a1)*v+a0) - del
          END IF
          py = 0.3989423/SQRT(fk)
        END IF
        x = (0.5-difmuk)/s
        xx = x*x
        fx = -0.5*xx
        fy = omega*(((c3*xx+c2)*xx+c1)*xx+c0)
        IF (kflag>0) GO TO 30
        GO TO 10

!     C A S E  B. (START NEW TABLE AND CALCULATE P0 IF NECESSARY)

!     JJV changed MUPREV assignment from 0.0 to initial value
50      CONTINUE
        muprev = -1.0E37
        IF (lambda/=muold) THEN
!     JJV added argument checker here
          IF (lambda<0.0) THEN
            WRITE (*,*) 'LAMBDA < 0 in IGNPOI - ABORT'
            WRITE (*,*) 'Value of LAMBDA: ', lambda
            STOP 'LAMBDA < 0 in IGNPOI - ABORT'
          END IF
!     JJV added line label here
          muold = lambda
          m = MAX0(1,IFIX(lambda))
          l = 0
          p = EXP((-lambda))
          q = p
          p0 = p

!     STEP U. UNIFORM SAMPLE FOR INVERSION METHOD

        END IF
60      CONTINUE
        u = random_standard_uniform()
        random_poisson = 0
        IF (u<=p0) RETURN

!     STEP T. TABLE COMPARISON UNTIL THE END PP(L) OF THE
!             PP-TABLE OF CUMULATIVE POISSON PROBABILITIES
!             (0.458=PP(9) FOR LAMBDA=10)

        IF (l==0) GO TO 70
        j = 1
        IF (u>0.458) j = MIN0(l,m)
        DO k = j, l
          IF (u<=pp(k)) GO TO 90
        END DO
        IF (l==35) GO TO 60

!     STEP C. CREATION OF NEW POISSON PROBABILITIES P
!             AND THEIR CUMULATIVES Q=PP(K)

70      CONTINUE
        l = l + 1
        DO k = l, 35
          p = p*lambda/FLOAT(k)
          q = q + p
          pp(k) = q
          IF (u<=q) GO TO 80
        END DO
        l = 35
        GO TO 60

80      CONTINUE
        l = k
90      CONTINUE
        random_poisson = k
        RETURN

      END FUNCTION random_poisson

!*********************************************************************

    END MODULE random_poisson_mod
