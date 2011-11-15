    MODULE random_binomial_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_binomial(n,pr)
!**********************************************************************
!     INTEGER FUNCTION IGNBIN( N, pr )
!                    GENerate BINomial random deviate
!                              Function
!     Generates a single random deviate from a binomial
!     distribution whose number of trials is N and whose
!     probability of an event in each trial is P.
!                              Arguments
!     N  --> The number of trials in the binomial distribution
!            from which a random deviate is to be generated.
!                              INTEGER N
!     JJV                      (N >= 0)
!     pr --> The probability of an event in each trial of the
!            binomial distribution from which a random deviate
!            is to be generated.
!                              REAL pr
!     JJV                      (0.0 <= pr <= 1.0)
!     IGNBIN <-- A random deviate yielding the number of events
!                from N independent trials, each of which has
!                a probability of event P.
!                              INTEGER IGNBIN
!                              Note
!     Uses RANF so the value of the seeds, ISEED1 and ISEED2 must be set
!     by a call similar to the following
!          DUM = RANSET( ISEED1, ISEED2 )
!                              Method
!     This is algorithm BTPE from:
!         Kachitvichyanukul, V. and Schmeiser, B. W.
!         Binomial Random Variate Generation.
!         Communications of the ACM, 31, 2
!         (February, 1988) 216.
!**********************************************************************
!     SUBROUTINE BTPEC(N,pr,ISEED,JX)
!     BINOMIAL RANDOM VARIATE GENERATOR
!     MEAN .LT. 30 -- INVERSE CDF
!       MEAN .GE. 30 -- ALGORITHM BTPE:  ACCEPTANCE-REJECTION VIA
!       FOUR REGION COMPOSITION.  THE FOUR REGIONS ARE A TRIANGLE
!       (SYMMETRIC IN THE CENTER), A PAIR OF PARALLELOGRAMS (ABOVE
!       THE TRIANGLE), AND EXPONENTIAL LEFT AND RIGHT TAILS.
!     BTPE REFERS TO BINOMIAL-TRIANGLE-PARALLELOGRAM-EXPONENTIAL.
!     BTPEC REFERS TO BTPE AND "COMBINED."  THUS BTPE IS THE
!       RESEARCH AND BTPEC IS THE IMPLEMENTATION OF A COMPLETE
!       USABLE ALGORITHM.
!     REFERENCE:  VORATAS KACHITVICHYANUKUL AND BRUCE SCHMEISER,
!       "BINOMIAL RANDOM VARIATE GENERATION,"
!       COMMUNICATIONS OF THE ACM, FORTHCOMING
!     WRITTEN:  SEPTEMBER 1980.
!       LAST REVISED:  MAY 1985, JULY 1987
!     REQUIRED SUBPROGRAM:  RAND() -- A UNIFORM (0,1) RANDOM NUMBER
!                           GENERATOR
!     ARGUMENTS
!       N : NUMBER OF BERNOULLI TRIALS            (INPUT)
!       pr : PROBABILITY OF SUCCESS IN EACH TRIAL (INPUT)
!       ISEED:  RANDOM NUMBER SEED                (INPUT AND OUTPUT)
!       JX:  RANDOMLY GENERATED OBSERVATION       (OUTPUT)
!     VARIABLES
!       PSAVE: VALUE OF pr FROM THE LAST CALL TO BTPEC
!       NSAVE: VALUE OF N FROM THE LAST CALL TO BTPEC
!       XNP:  VALUE OF THE MEAN FROM THE LAST CALL TO BTPEC
!       P: PROBABILITY USED IN THE GENERATION PHASE OF BTPEC
!       FFM: TEMPORARY VARIABLE EQUAL TO XNP + P
!       M:  INTEGER VALUE OF THE CURRENT MODE
!       FM:  FLOATING POINT VALUE OF THE CURRENT MODE
!       XNPQ: TEMPORARY VARIABLE USED IN SETUP AND SQUEEZING STEPS
!       P1:  AREA OF THE TRIANGLE
!       C:  HEIGHT OF THE PARALLELOGRAMS
!       XM:  CENTER OF THE TRIANGLE
!       XL:  LEFT END OF THE TRIANGLE
!       XR:  RIGHT END OF THE TRIANGLE
!       AL:  TEMPORARY VARIABLE
!       XLL:  RATE FOR THE LEFT EXPONENTIAL TAIL
!       XLR:  RATE FOR THE RIGHT EXPONENTIAL TAIL
!       P2:  AREA OF THE PARALLELOGRAMS
!       P3:  AREA OF THE LEFT EXPONENTIAL TAIL
!       P4:  AREA OF THE RIGHT EXPONENTIAL TAIL
!       U:  A U(0,P4) RANDOM VARIATE USED FIRST TO SELECT ONE OF THE
!           FOUR REGIONS AND THEN CONDITIONALLY TO GENERATE A VALUE
!           FROM THE REGION
!       V:  A U(0,1) RANDOM NUMBER USED TO GENERATE THE RANDOM VALUE
!           (REGION 1) OR TRANSFORMED INTO THE VARIATE TO ACCEPT OR
!           REJECT THE CANDIDATE VALUE
!       IX:  INTEGER CANDIDATE VALUE
!       X:  PRELIMINARY CONTINUOUS CANDIDATE VALUE IN REGION 2 LOGIC
!           AND A FLOATING POINT IX IN THE ACCEPT/REJECT LOGIC
!       K:  ABSOLUTE VALUE OF (IX-M)
!       F:  THE HEIGHT OF THE SCALED DENSITY FUNCTION USED IN THE
!           ACCEPT/REJECT DECISION WHEN BOTH M AND IX ARE SMALL
!           ALSO USED IN THE INVERSE TRANSFORMATION
!       R: THE RATIO P/Q
!       G: CONSTANT USED IN CALCULATION OF PROBABILITY
!       MP:  MODE PLUS ONE, THE LOWER INDEX FOR EXPLICIT CALCULATION
!            OF F WHEN IX IS GREATER THAN M
!       IX1:  CANDIDATE VALUE PLUS ONE, THE LOWER INDEX FOR EXPLICIT
!             CALCULATION OF F WHEN IX IS LESS THAN M
!       I:  INDEX FOR EXPLICIT CALCULATION OF F FOR BTPE
!       AMAXP: MAXIMUM ERROR OF THE LOGARITHM OF NORMAL BOUND
!       YNORM: LOGARITHM OF NORMAL BOUND
!       ALV:  NATURAL LOGARITHM OF THE ACCEPT/REJECT VARIATE V
!       X1,F1,Z,W,Z2,X2,F2, AND W2 ARE TEMPORARY VARIABLES TO BE
!       USED IN THE FINAL ACCEPT/REJECT TEST
!       QN: PROBABILITY OF NO SUCCESS IN N TRIALS
!     REMARK
!       IX AND JX COULD LOGICALLY BE THE SAME VARIABLE, WHICH WOULD
!       SAVE A MEMORY POSITION AND A LINE OF CODE.  HOWEVER, SOME
!       COMPILERS (E.G.,CDC MNF) OPTIMIZE BETTER WHEN THE ARGUMENTS
!       ARE NOT INVOLVED.
!     ISEED NEEDS TO BE DOUBLE PRECISION IF THE IMSL ROUTINE
!     GGUBFS IS USED TO GENERATE UNIFORM RANDOM NUMBER, OTHERWISE
!     TYPE OF ISEED SHOULD BE DICTATED BY THE UNIFORM GENERATOR
!**********************************************************************
!*****DETERMINE APPROPRIATE ALGORITHM AND WHETHER SETUP IS NECESSARY
!     JJV ..
!     JJV .. Save statement ..
!     JJV I am including the variables in data statements
!     JJV made these ridiculous starting values - the hope is that
!     JJV no one will call this the first time with them as args
! .. Use Statements ..
        USE random_standard_uniform_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        INTEGER :: random_binomial
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: pr
        INTEGER, INTENT (IN) :: n
! ..
! .. Local Scalars ..
        REAL :: al, alv, amaxp, f, f1, f2, ffm, u, v, w, w2, x, x1, x2, &
          ynorm, z, z2
        REAL, SAVE :: c, fm, g, p, p1, p2, p3, p4, psave, q, qn, r, xl, &
          xll, xlr, xm, xnp, xnpq, xr
        INTEGER :: i, ix, ix1, k, mp
        INTEGER, SAVE :: m, nsave
! ..
! .. Intrinsic Functions ..
        INTRINSIC ABS, ALOG, AMIN1, IABS, INT, SQRT
! ..
! .. Data Statements ..
        DATA psave, nsave/ -1.0E37, -214748365/
! ..
! .. Executable Statements ..

        IF (pr==psave) THEN
          IF (n/=nsave) GO TO 10
          IF (xnp-30.<0.) GO TO 50
          GO TO 20
        END IF

!*****SETUP, PERFORM ONLY WHEN PARAMETERS CHANGE


!     JJV added the argument checker - involved only renaming 10
!     JJV and 20 to the checkers and adding checkers
!     JJV Only remaining problem - if called initially with the
!     JJV initial values of psave and nsave, it will hang
        IF (pr<0.0) STOP 'pr < 0.0 in IGNBIN - ABORT!'
        IF (pr>1.0) STOP 'pr > 1.0 in IGNBIN - ABORT!'
        psave = pr
        p = AMIN1(psave,1.-psave)
        q = 1. - p
10      CONTINUE
        IF (n<0) STOP 'N < 0 in IGNBIN - ABORT!'
        xnp = n*p
        nsave = n
        IF (xnp<30.) GO TO 40
        ffm = xnp + p
        m = ffm
        fm = m
        xnpq = xnp*q
        p1 = INT(2.195*SQRT(xnpq)-4.6*q) + 0.5
        xm = fm + 0.5
        xl = xm - p1
        xr = xm + p1
        c = 0.134 + 20.5/(15.3+fm)
        al = (ffm-xl)/(ffm-xl*p)
        xll = al*(1.+0.5*al)
        al = (xr-ffm)/(xr*q)
        xlr = al*(1.+0.5*al)
        p2 = p1*(1.+c+c)
        p3 = p2 + c/xll
        p4 = p3 + c/xlr
!      WRITE(6,100) N,P,P1,P2,P3,P4,XL,XR,XM,FM
!  100 FORMAT(I15,4F18.7/5F18.7)

!*****GENERATE VARIATE

20      CONTINUE
        u = random_standard_uniform()*p4
        v = random_standard_uniform()

!     TRIANGULAR REGION

        IF (u<=p1) THEN
          ix = xm - p1*v + u
          GO TO 70
        END IF

!     PARALLELOGRAM REGION

        IF (u<=p2) THEN
          x = xl + (u-p1)/c
          v = v*c + 1. - ABS(xm-x)/p1
          IF (v>1. .OR. v<=0.) GO TO 20
          ix = x
        ELSE

!     LEFT TAIL

          IF (u<=p3) THEN
            ix = xl + ALOG(v)/xll
            IF (ix<0) GO TO 20
            v = v*(u-p2)*xll
          ELSE

!     RIGHT TAIL

            ix = xr - ALOG(v)/xlr
            IF (ix>n) GO TO 20
            v = v*(u-p3)*xlr

!*****DETERMINE APPROPRIATE WAY TO PERFORM ACCEPT/REJECT TEST

          END IF
        END IF
        k = IABS(ix-m)
        IF (k<=20 .OR. k>=xnpq/2-1) THEN

!     EXPLICIT EVALUATION

          f = 1.0
          r = p/q
          g = (n+1)*r
          IF (m-ix<=0) THEN
            IF (m-ix==0) GO TO 30
            mp = m + 1
            DO i = mp, ix
              f = f*(g/i-r)
            END DO
            GO TO 30
          END IF

          ix1 = ix + 1
          DO i = ix1, m
            f = f/(g/i-r)
          END DO
30        CONTINUE
          IF (v-f>0.) GO TO 20
          GO TO 70
        END IF

!     SQUEEZING USING UPPER AND LOWER BOUNDS ON ALOG(F(X))

        amaxp = (k/xnpq)*((k*(k/3.+0.625)+0.1666666666666)/xnpq+0.5)
        ynorm = -k*k/(2.*xnpq)
        alv = ALOG(v)
        IF (alv<ynorm-amaxp) GO TO 70
        IF (alv>ynorm+amaxp) GO TO 20

!     STIRLING'S FORMULA TO MACHINE ACCURACY FOR
!     THE FINAL ACCEPTANCE/REJECTION TEST

        x1 = ix + 1
        f1 = fm + 1.
        z = n + 1 - fm
        w = n - ix + 1.
        z2 = z*z
        x2 = x1*x1
        f2 = f1*f1
        w2 = w*w
        IF (alv-(xm*ALOG(f1/x1)+(n-m+0.5)*ALOG(z/w)+(ix-m)*ALOG(w*p/(x1*q &
          ))+(13860.-(462.-(132.-(99.-140./f2)/f2)/f2)/f2)/f1/166320.+( &
          13860.-(462.-(132.-(99.-140./z2)/z2)/z2)/z2)/z/166320.+(13860.- &
          (462.-(132.-(99.-140./x2)/x2)/x2)/x2)/x1/166320.+(13860.-(462.- &
          (132.-(99.-140./w2)/w2)/w2)/w2)/w/166320.)>0.) GO TO 20
        GO TO 70

!     INVERSE CDF LOGIC FOR MEAN LESS THAN 30

40      CONTINUE
        qn = q**n
        r = p/q
        g = r*(n+1)
50      CONTINUE
        ix = 0
        f = qn
        u = random_standard_uniform()
60      CONTINUE
        IF (u<f) GO TO 70
        IF (ix>110) GO TO 50
        u = u - f
        ix = ix + 1
        f = f*(g/ix-r)
        GO TO 60

70      CONTINUE
        IF (psave>0.5) ix = n - ix
        random_binomial = ix
        RETURN

      END FUNCTION random_binomial

!*********************************************************************

    END MODULE random_binomial_mod
