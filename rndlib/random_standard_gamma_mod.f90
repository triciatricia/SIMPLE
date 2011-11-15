    MODULE random_standard_gamma_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_standard_gamma(a)
!**********************************************************************C
!                                                                      C
!                                                                      C
!     (STANDARD-)  G A M M A  DISTRIBUTION                             C
!                                                                      C
!                                                                      C
!**********************************************************************C
!**********************************************************************C
!                                                                      C
!               PARAMETER  A >= 1.0  !                                 C
!                                                                      C
!**********************************************************************C
!                                                                      C
!     FOR DETAILS SEE:                                                 C
!                                                                      C
!               AHRENS, J.H. AND DIETER, U.                            C
!               GENERATING GAMMA VARIATES BY A                         C
!               MODIFIED REJECTION TECHNIQUE.                          C
!               COMM. ACM, 25,1 (JAN. 1982), 47 - 54.                  C
!                                                                      C
!     STEP NUMBERS CORRESPOND TO ALGORITHM 'GD' IN THE ABOVE PAPER     C
!                                 (STRAIGHTFORWARD IMPLEMENTATION)     C
!                                                                      C
!     Modified by Barry W. Brown, Feb 3, 1988 to use RANF instead of   C
!     SUNIF.  The argument IR thus goes away.                          C
!                                                                      C
!**********************************************************************C
!                                                                      C
!               PARAMETER  0.0 < A < 1.0  !                            C
!                                                                      C
!**********************************************************************C
!                                                                      C
!     FOR DETAILS SEE:                                                 C
!                                                                      C
!               AHRENS, J.H. AND DIETER, U.                            C
!               COMPUTER METHODS FOR SAMPLING FROM GAMMA,              C
!               BETA, POISSON AND BINOMIAL DISTRIBUTIONS.              C
!               COMPUTING, 12 (1974), 223 - 246.                       C
!                                                                      C
!     (ADAPTED IMPLEMENTATION OF ALGORITHM 'GS' IN THE ABOVE PAPER)    C
!                                                                      C
!**********************************************************************C
!     INPUT: A =PARAMETER (MEAN) OF THE STANDARD GAMMA DISTRIBUTION
!     OUTPUT: SGAMMA = SAMPLE FROM THE GAMMA-(A)-DISTRIBUTION
!     COEFFICIENTS Q(K) - FOR Q0 = SUM(Q(K)*A**(-K))
!     COEFFICIENTS A(K) - FOR Q = Q0+(T*T/2)*SUM(A(K)*V**K)
!     COEFFICIENTS E(K) - FOR EXP(Q)-1 = SUM(E(K)*Q**K)
!     JJV added Save statement for vars in Data satatements
!     PREVIOUS A PRE-SET TO ZERO - AA IS A', AAA IS A"
!     SQRT32 IS THE SQUAREROOT OF 32 = 5.656854249492380
! .. Use Statements ..
        USE random_standard_uniform_mod
        USE random_standard_exponential_mod
        USE random_standard_normal_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_standard_gamma
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: a
! ..
! .. Local Scalars ..
        REAL, SAVE :: a1, a2, a3, a4, a5, a6, a7, aa, aaa, b, c, d, e1, &
          e2, e3, e4, e5, q0, q1, q2, q3, q4, q5, q6, q7, s, s2, si, &
          sqrt32
        REAL :: b0, e, p, q, r, t, u, v, w, x
! ..
! .. Intrinsic Functions ..
        INTRINSIC ABS, ALOG, EXP, SIGN, SQRT
! ..
! .. Data Statements ..
        DATA q1, q2, q3, q4, q5, q6, q7/0.04166669, 0.02083148, &
          0.00801191, 0.00144121, -.00007388, 0.00024511, 0.00024240/
        DATA a1, a2, a3, a4, a5, a6, a7/0.3333333, -.2500030, 0.2000062, &
          -.1662921, 0.1423657, -.1367177, 0.1233795/
        DATA e1, e2, e3, e4, e5/1., 0.4999897, 0.1668290, 0.0407753, &
          0.0102930/
        DATA aa/0.0/
        DATA aaa/0.0/
        DATA sqrt32/5.656854/
! ..
! .. Executable Statements ..

        IF (a/=aa) THEN
          IF (a<1.0) GO TO 40

!     STEP  1:  RECALCULATIONS OF S2,S,D IF A HAS CHANGED

          aa = a
          s2 = a - 0.5
          s = SQRT(s2)
          d = sqrt32 - 12.0*s
        END IF

!     STEP  2:  T=STANDARD NORMAL DEVIATE,
!               X=(S,1/2)-NORMAL DEVIATE.
!               IMMEDIATE ACCEPTANCE (I)

        t = random_standard_normal()
        x = s + 0.5*t
        random_standard_gamma = x*x
        IF (t>=0.0) RETURN

!     STEP  3:  U= 0,1 -UNIFORM SAMPLE. SQUEEZE ACCEPTANCE (S)

        u = random_standard_uniform()
        IF (d*u<=t*t*t) RETURN

!     STEP  4:  RECALCULATIONS OF Q0,B,SI,C IF NECESSARY

        IF (a/=aaa) THEN
          aaa = a
          r = 1.0/a
          q0 = ((((((q7*r+q6)*r+q5)*r+q4)*r+q3)*r+q2)*r+q1)*r

!               APPROXIMATION DEPENDING ON SIZE OF PARAMETER A
!               THE CONSTANTS IN THE EXPRESSIONS FOR B, SI AND
!               C WERE ESTABLISHED BY NUMERICAL EXPERIMENTS

          IF (a>3.686) THEN
            IF (a>13.022) THEN

!               CASE 3:  A .GT. 13.022

              b = 1.77
              si = 0.75
              c = 0.1515/s
              GO TO 10
            END IF

!               CASE 2:  3.686 .LT. A .LE. 13.022

            b = 1.654 + 0.0076*s2
            si = 1.68/s + 0.275
            c = 0.062/s + 0.024
            GO TO 10

!               CASE 1:  A .LE. 3.686

          END IF
          b = 0.463 + s + 0.178*s2
          si = 1.235
          c = 0.195/s - 0.079 + 0.16*s

!     STEP  5:  NO QUOTIENT TEST IF X NOT POSITIVE

        END IF
10      CONTINUE
        IF (x>0.0) THEN

!     STEP  6:  CALCULATION OF V AND QUOTIENT Q

          v = t/(s+s)
          IF (ABS(v)>0.25) THEN
            q = q0 - s*t + 0.25*t*t + (s2+s2)*ALOG(1.0+v)
          ELSE

            q = q0 + 0.5*t*t*((((((a7*v+a6)*v+a5)*v+a4)*v+ &
              a3)*v+a2)*v+a1)*v
          END IF

!     STEP  7:  QUOTIENT ACCEPTANCE (Q)

          IF (ALOG(1.0-u)<=q) RETURN

!     STEP  8:  E=STANDARD EXPONENTIAL DEVIATE
!               U= 0,1 -UNIFORM DEVIATE
!               T=(B,SI)-DOUBLE EXPONENTIAL (LAPLACE) SAMPLE

        END IF
20      CONTINUE
        e = random_standard_exponential()
        u = random_standard_uniform()
        u = u + u - 1.0
        t = b + SIGN(si*e,u)
        DO WHILE (t<(-.7187449))
          e = random_standard_exponential()
          u = random_standard_uniform()
          u = u + u - 1.0
          t = b + SIGN(si*e,u)

!     STEP  9:  REJECTION IF T .LT. TAU(1) = -.71874483771719

        END DO

!     STEP 10:  CALCULATION OF V AND QUOTIENT Q

        v = t/(s+s)
        IF (ABS(v)>0.25) THEN
          q = q0 - s*t + 0.25*t*t + (s2+s2)*ALOG(1.0+v)
        ELSE

          q = q0 + 0.5*t*t*((((((a7*v+a6)*v+a5)*v+a4)*v+a3)*v+a2)*v+a1)*v
        END IF

!     STEP 11:  HAT ACCEPTANCE (H) (IF Q NOT POSITIVE GO TO STEP 8)

        IF (q<=0.0) GO TO 20
        IF (q>0.5) THEN

!     JJV modified the code through line 125 to handle large Q case

          IF (q>=15.0) THEN

!     JJV Here Q is large enough that Q = log(exp(Q) - 1.0) (for real Q)
!     JJV so reformulate test at 120 in terms of one EXP, if not too big
!     JJV 87.49823 is close to the largest real which can be
!     JJV exponentiated (87.49823 = log(1.0E38))

            IF (q+e-0.5*t*t>87.49823) GO TO 30
            IF (c*ABS(u)>EXP(q+e-0.5*t*t)) GO TO 20
            GO TO 30
          END IF

          w = EXP(q) - 1.0
        ELSE

          w = ((((e5*q+e4)*q+e3)*q+e2)*q+e1)*q
        END IF

!               IF T IS REJECTED, SAMPLE AGAIN AT STEP 8

        IF (c*ABS(u)>w*EXP(e-0.5*t*t)) GO TO 20
30      CONTINUE
        x = s + 0.5*t
        random_standard_gamma = x*x
        RETURN

!     ALTERNATE METHOD FOR PARAMETERS A BELOW 1  (.3678794=EXP(-1.))

!     JJV changed B to B0 (which was added to declarations for this)
!     JJV in 130 to END to fix rare and subtle bug.
!     JJV Line: '130 aa = 0.0' was removed (unnecessary, wasteful).
!     JJV Reasons: the state of AA only serves to tell the A .GE. 1.0
!     JJV case if certain A-dependant constants need to be recalculated.
!     JJV The A .LT. 1.0 case (here) no longer changes any of these, and
!     JJV the recalculation of B (which used to change with an
!     JJV A .LT. 1.0 call) is governed by the state of AAA anyway.

40      CONTINUE
        b0 = 1.0 + 0.3678794*a
50      CONTINUE
        p = b0*random_standard_uniform()
        IF (p<1.0) THEN
          random_standard_gamma = EXP(ALOG(p)/a)
          IF (random_standard_exponential()<random_standard_gamma) &
            GO TO 50
          RETURN
        END IF

        random_standard_gamma = -ALOG((b0-p)/a)
        IF (random_standard_exponential()<(1.0-a)*ALOG( &
          random_standard_gamma)) GO TO 50
        RETURN

      END FUNCTION random_standard_gamma

!*********************************************************************

    END MODULE random_standard_gamma_mod
