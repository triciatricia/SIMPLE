    MODULE random_beta_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_beta(a,b)
!**********************************************************************
!     REAL FUNCTION GENBET( A, B )
!               GeNerate BETa random deviate
!                              Function
!     Returns A_LOCAL single random deviate from the beta distribution with
!     parameters A_LOCAL and B_LOCAL.  The density of the beta is
!               x^(A_LOCAL-1) * (1-x)^(B_LOCAL-1) / B_LOCAL(A_LOCAL,B_LOCAL) for 0 < x < 1
!                              Arguments
!     A --> First parameter of the beta distribution
!                         REAL A_LOCAL
!     JJV                 (A_LOCAL > 1.0E-37)
!     B --> Second parameter of the beta distribution
!                         REAL B_LOCAL
!     JJV                 (B_LOCAL > 1.0E-37)
!                              Method
!     R. C. H. Cheng
!     Generating Beta Variates with Nonintegral Shape Parameters
!     Communications of the ACM, 21:317-322  (1978)
!     (Algorithms B and BC)
!**********************************************************************
!     JJV changed these to ridiculous values
! .. Use Statements ..
        USE random_standard_uniform_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_beta
! ..
! .. Parameters ..
        REAL, PARAMETER :: expmax = 87.49823, infnty = 1.0E38, &
          minlog = 1.0E-37
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: a, b
! ..
! .. Local Scalars ..
        REAL, SAVE :: alpha, a_local, beta, b_local, gamma, k1, k2, olda, &
          oldb
        REAL :: delta, r, s, t, u1, u2, v, w, y, z
        LOGICAL :: qsame
! ..
! .. Intrinsic Functions ..
        INTRINSIC EXP, LOG, MAX, MIN, SQRT
! ..
! .. Data Statements ..
        DATA olda, oldb/ -1.0E37, -1.0E37/
! ..
! .. Executable Statements ..

        qsame = olda == a .AND. oldb == b
        IF ( .NOT. qsame) THEN
!     JJV added small minimum for small log problem in calc of W
          IF (a<minlog .OR. b<minlog) THEN
            WRITE (*,*) ' A or B < ', minlog, ' in GENBET - Abort!'
            WRITE (*,*) ' A: ', a, ' B ', b
            STOP ' A or B too small in GENBET - Abort!'
          END IF

          olda = a
          oldb = b
        END IF
        IF (MIN(a,b)>1.0) THEN


!     Algorithm B


!     Initialize

          IF ( .NOT. qsame) THEN
            a_local = MIN(a,b)
            b_local = MAX(a,b)
            alpha = a_local + b_local
            beta = SQRT((alpha-2.0)/(2.0*a_local*b_local-alpha))
            gamma = a_local + 1.0/beta
          END IF
10        CONTINUE
          u1 = random_standard_uniform()

!     Step 1

          u2 = random_standard_uniform()
          v = beta*LOG(u1/(1.0-u1))
!     JJV altered this
          IF (v>expmax) GO TO 20
!     JJV added checker to see if A_LOCAL*exp(v) will overflow
!     JJV 50 _was_ w = A_LOCAL*exp(v); also note here A_LOCAL > 1.0
          w = EXP(v)
          IF (w>infnty/a_local) GO TO 20
          w = a_local*w
          GO TO 30
20        CONTINUE
          w = infnty

30        CONTINUE
          z = u1**2*u2
          r = gamma*v - 1.3862944
          s = a_local + r - w

!     Step 2

          IF (s+2.609438>=5.0*z) GO TO 40

!     Step 3

          t = LOG(z)
          IF (s>t) GO TO 40

!     Step 4

!     JJV added checker to see if log(alpha/(B_LOCAL+w)) will
!     JJV overflow.  If so, we count the log as -INF, and
!     JJV consequently evaluate conditional as true, i.e.
!     JJV the algorithm rejects the trial and starts over
!     JJV May not need this here since ALPHA > 2.0
          IF (alpha/(b_local+w)<minlog) GO TO 10

          IF (r+alpha*LOG(alpha/(b_local+w))<t) GO TO 10

!     Step 5

40        CONTINUE
          IF (a==a_local) THEN
            random_beta = w/(b_local+w)
          ELSE

            random_beta = b_local/(b_local+w)
          END IF
        ELSE


!     Algorithm BC


!     Initialize

          IF ( .NOT. qsame) THEN
            a_local = MAX(a,b)
            b_local = MIN(a,b)
            alpha = a_local + b_local
            beta = 1.0/b_local
            delta = 1.0 + a_local - b_local
            k1 = delta*(0.0138889+0.0416667*b_local)/ &
              (a_local*beta-0.777778)
            k2 = 0.25 + (0.5+0.25/delta)*b_local
          END IF
50        CONTINUE
          u1 = random_standard_uniform()

!     Step 1

          u2 = random_standard_uniform()
          IF (u1<0.5) THEN

!     Step 2

            y = u1*u2
            z = u1*y
            IF (0.25*u2+z-y>=k1) GO TO 50
          ELSE

!     Step 3

            z = u1**2*u2
            IF (z<=0.25) THEN
              v = beta*LOG(u1/(1.0-u1))

!     JJV instead of checking v > expmax at top, I will check
!     JJV if A_LOCAL < 1, then check the appropriate values

              IF (a_local<=1.0) THEN
!     JJV A_LOCAL < 1 so it can help out if EXP(V) would overflow
                IF (v<=expmax) THEN
                  w = a_local*EXP(v)
                  GO TO 90
                END IF
                w = v + LOG(a_local)
                IF (w>expmax) GO TO 60
                w = EXP(w)
                GO TO 90
              END IF

!     JJV in this case A_LOCAL > 1
              IF (v>expmax) GO TO 60
              w = EXP(v)
              IF (w>infnty/a_local) GO TO 60
              w = a_local*w
              GO TO 90
60            CONTINUE
              w = infnty
              GO TO 90
            END IF

            IF (z>=k2) GO TO 50
          END IF

!     Step 4


!     Step 5

          v = beta*LOG(u1/(1.0-u1))

!     JJV same kind of checking as above
          IF (a_local<=1.0) THEN
!     JJV A_LOCAL < 1 so it can help out if EXP(V) would overflow
            IF (v<=expmax) THEN
              w = a_local*EXP(v)
              GO TO 80
            END IF
            w = v + LOG(a_local)
            IF (w>expmax) GO TO 70
            w = EXP(w)
            GO TO 80
          END IF

!     JJV in this case A_LOCAL > 1
          IF (v>expmax) GO TO 70
          w = EXP(v)
          IF (w>infnty/a_local) GO TO 70
          w = a_local*w
          GO TO 80

70        CONTINUE
          w = infnty

!     JJV here we also check to see if log overlows; if so, we treat it
!     JJV as -INF, which means condition is true, i.e. restart
80        CONTINUE
          IF (alpha/(b_local+w)<minlog) GO TO 50
          IF (alpha*(LOG(alpha/(b_local+w))+v)-1.3862944<LOG(z)) GO TO 50

!     Step 6

90        CONTINUE
          IF (a_local==a) THEN
            random_beta = w/(b_local+w)
          ELSE

            random_beta = b_local/(b_local+w)
          END IF
        END IF
        RETURN

      END FUNCTION random_beta

!*********************************************************************

    END MODULE random_beta_mod
