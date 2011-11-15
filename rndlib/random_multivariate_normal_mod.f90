    MODULE random_multivariate_normal_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
! .. Local Arrays ..
      REAL, ALLOCATABLE, SAVE :: param(:)
! ..
    CONTAINS

!*********************************************************************

      SUBROUTINE random_multivariate_normal(x)
! .. Use Statements ..
        USE random_standard_normal_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Array Arguments ..
        REAL, INTENT (OUT) :: x(:)
! ..
! .. Local Scalars ..
        REAL :: ae
        INTEGER :: i, icount, j, p
! ..
! .. Intrinsic Functions ..
        INTRINSIC ALLOCATED, INT, SIZE
! ..
! .. Local Arrays ..
        REAL, ALLOCATABLE :: work(:)
! ..
! .. Executable Statements ..

!----------------------------------------------------------------------
!     SUBROUTINE RANDOM_MULTIVARIATE_NORMAL(X)
!                              Arguments
!     X    <-- Vector deviate generated.
!                                             REAL X(P)
!                              Method
!     1) Generate P independent standard normal deviates - Ei ~ N(0,1)
!     2) Using Cholesky decomposition find A s.t. trans(A)*A = COVM
!     3) trans(A)E + MEANV ~ N(MEANV,COVM)
!______________________________________________________________________
        p = INT(param(1))

!    Allocate array work if necessary

        IF ( .NOT. ALLOCATED(work)) ALLOCATE (work(p))

        IF (SIZE(work)<p) THEN
          DEALLOCATE (work)
          ALLOCATE (work(p))
        END IF

!     Generate P independent normal deviates - WORK ~ N(0,1)

        DO i = 1, p
          work(i) = random_standard_normal()
        END DO
        DO i = 1, p

!     PARAM (P+2 : P*(P+3)/2 + 1) contains A, the Cholesky
!      decomposition of the desired covariance matrix.
!          trans(A)(1,1) = PARAM(P+2)
!          trans(A)(2,1) = PARAM(P+3)
!          trans(A)(2,2) = PARAM(P+2+P)
!          trans(A)(3,1) = PARAM(P+4)
!          trans(A)(3,2) = PARAM(P+3+P)
!          trans(A)(3,3) = PARAM(P+2-1+2P)  ...

!     trans(A)*WORK + MEANV ~ N(MEANV,COVM)

          icount = 0
          ae = 0.0
          DO j = 1, i
            icount = icount + j - 1
            ae = ae + param(i+(j-1)*p-icount+p+1)*work(j)
          END DO
          x(i) = ae + param(i+1)
        END DO
        RETURN

      END SUBROUTINE random_multivariate_normal

!*********************************************************************

      SUBROUTINE set_random_multivariate_normal(meanv,covm,p)
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Scalar Arguments ..
        INTEGER :: p
! ..
! .. Array Arguments ..
        REAL :: covm(:,:)
        REAL, INTENT (IN) :: meanv(p)
! ..
! .. Local Scalars ..
        INTEGER :: dim1_covm, dim2_covm, i, icount, info, size_meanv
! ..
! .. Intrinsic Functions ..
        INTRINSIC SIZE
! ..
! .. Executable Statements ..

!**********************************************************************
!      SUBROUTINE set_random_multivariate_normal(meanv,covm,p,param)
!     JJV changed this routine to take leading dimension of COVM
!     JJV argument and pass it to SPOFA, making it easier to use
!     JJV if the COVM which is used is contained in a larger matrix
!     JJV and to make the routine more consistent with LINPACK.
!     JJV Changes are in comments, declarations, and the call to SPOFA.
!**********************************************************************
!     SUBROUTINE SETGMN( MEANV, COVM, DIM1_COVM, P, PARAM)
!            SET Generate Multivariate Normal random deviate
!                              Function
!      Places P, MEANV, and the Cholesky factoriztion of COVM
!      in PARAM for GENMN.
!                              Arguments
!     MEANV --> Mean vector of multivariate normal distribution.
!                                        REAL MEANV(P)
!     COVM   <--> (Input) Covariance   matrix    of  the  multivariate
!                 normal distribution.  This routine uses only the
!                 (1:P,1:P) slice of COVM, but needs to know DIM1_COVM.
!                 (Output) Destroyed on output
!                                        REAL COVM(DIM1_COVM,P)
!     P     --> Dimension of the normal, or length of MEANV.
!                                        INTEGER P
!**********************************************************************
        IF (p<=0) THEN
          WRITE (*,*) 'P nonpositive in SET_RANDOM_MULTIVARIATE_NORMAL'
          WRITE (*,*) 'Value of P: ', p
          STOP 'P nonpositive in SET_RANDOM_MULTIVARIATE_NORMAL'
        END IF

        dim1_covm = SIZE(covm,dim=1)
        dim2_covm = SIZE(covm,dim=2)

        IF ((dim1_covm<p) .OR. (dim2_covm<p)) THEN
          WRITE (*,90000) p
90000     FORMAT (' Error in routine SET_RANDOM_MULTIVARIATE_NORMAL'/ &
            ' Dimension of multivariate normal input as: ',I4/)
          WRITE (*,90100) dim1_covm, dim2_covm, p
90100     FORMAT (' At least one dimension of argument covm too small:'/ &
            ' Dimensions are: ( ',I4,',',I4,' )'/ &
            ' Each dimension should be at least: ',I4)
        END IF


        size_meanv = SIZE(meanv)

        IF (size_meanv<p) THEN
          WRITE (*,90000) p
          WRITE (*,90200) size_meanv, p
90200     FORMAT (' Size of argument meanv is too small: '/ &
            ' The size is: ',I4/' It should be at least: ',I4)
        END IF

        param(1) = p

!     PUT P AND MEANV INTO PARAM

        param(2:p+1) = meanv(:p)

!      Cholesky decomposition to find A s.t. trans(A)*(A) = COVM

        CALL spofa(covm,dim1_covm,p,info)
        IF (info/=0) THEN
          WRITE (*,*) ' COVM not positive definite in SETGMN'
          STOP ' COVM not positive definite in SETGMN'
        END IF

        icount = p + 1

!     PUT UPPER HALF OF A, WHICH IS NOW THE CHOLESKY FACTOR, INTO PARAM
!          COVM(1,1) = PARAM(P+2)
!          COVM(1,2) = PARAM(P+3)
!                    :
!          COVM(1,P) = PARAM(2P+1)
!          COVM(2,2) = PARAM(2P+2)  ...

        DO i = 1, p
          IF (p-i+1>0) THEN
            param(icount+1:p-i+1+icount) = covm(i,i:p)
            icount = p - i + 1 + icount
          END IF
        END DO
        RETURN

      CONTAINS

!.....................................................................

        FUNCTION sdot(n,sx,incx,sy,incy)
! .. Implicit None Statement ..
          IMPLICIT NONE
! ..
! .. Function Return Value ..
          REAL :: sdot
! ..
! .. Scalar Arguments ..
          INTEGER, INTENT (IN) :: incx, incy, n
! ..
! .. Array Arguments ..
          REAL, INTENT (IN) :: sx(1), sy(1)
! ..
! .. Local Scalars ..
          REAL :: stemp
          INTEGER :: ix, iy, m, mp1
! ..
! .. Intrinsic Functions ..
          INTRINSIC DOT_PRODUCT, MOD
! ..
! .. Executable Statements ..

!-----------------------------------------------
          stemp = 0.0E0
          sdot = 0.0E0
          IF (n<=0) RETURN
          IF (incx/=1 .OR. incy/=1) THEN
            ix = 1
            iy = 1
            IF (incx<0) ix = ((-n)+1)*incx + 1
            IF (incy<0) iy = ((-n)+1)*incy + 1
            stemp = DOT_PRODUCT(sx(ix:(n-1)*incx+ix:incx),sy(iy:(n- &
              1)*incy+iy:incy))
            sdot = stemp
            RETURN
          END IF

          m = MOD(n,5)
          IF (m==0) GO TO 10
          stemp = DOT_PRODUCT(sx(:m),sy(:m))
          IF (n<5) GO TO 20
10        CONTINUE
          mp1 = m + 1
          stemp = stemp + DOT_PRODUCT(sx(mp1:((n-mp1+5)/5)*5-1+mp1),sy( &
            mp1:((n-mp1+5)/5)*5-1+mp1))
20        CONTINUE
          sdot = stemp
          RETURN

        END FUNCTION sdot

!.....................................................................

        SUBROUTINE spofa(a,lda,n,info)
! .. Implicit None Statement ..
          IMPLICIT NONE
! ..
! .. Scalar Arguments ..
          INTEGER, INTENT (OUT) :: info
          INTEGER, INTENT (IN) :: lda, n
! ..
! .. Array Arguments ..
          REAL :: a(lda,1)
! ..
! .. Local Scalars ..
          REAL :: s, t
          INTEGER :: j, jm1, k
! ..
! .. Intrinsic Functions ..
          INTRINSIC SQRT
! ..
! .. Executable Statements ..

!**********************************************************************
!     SPOFA FACTORS A REAL SYMMETRIC POSITIVE DEFINITE MATRIX.
!     SPOFA IS USUALLY CALLED BY SPOCO, BUT IT CAN BE CALLED
!     DIRECTLY WITH A SAVING IN TIME IF  RCOND  IS NOT NEEDED.
!     (TIME FOR SPOCO) = (1 + 18/N)*(TIME FOR SPOFA) .
!     ON ENTRY
!        A       REAL(LDA, N)
!                THE SYMMETRIC MATRIX TO BE FACTORED.  ONLY THE
!                DIAGONAL AND UPPER TRIANGLE ARE USED.
!        LDA     INTEGER
!                THE LEADING DIMENSION OF THE ARRAY  A .
!        N       INTEGER
!                THE ORDER OF THE MATRIX  A .
!     ON RETURN
!        A       AN UPPER TRIANGULAR MATRIX  R  SO THAT  A = TRANS(R)*R
!                WHERE  TRANS(R)  IS THE TRANSPOSE.
!                THE STRICT LOWER TRIANGLE IS UNALTERED.
!                IF  INFO .NE. 0 , THE FACTORIZATION IS NOT COMPLETE.
!        INFO    INTEGER
!                = 0  FOR NORMAL RETURN.
!                = K  SIGNALS AN ERROR CONDITION.  THE LEADING MINOR
!                     OF ORDER  K  IS NOT POSITIVE DEFINITE.
!     LINPACK.  THIS VERSION DATED 08/14/78 .
!     CLEVE MOLER, UNIVERSITY OF NEW MEXICO, ARGONNE NATIONAL LAB.
!     SUBROUTINES AND FUNCTIONS
!     BLAS SDOT
!     FORTRAN SQRT
!     INTERNAL VARIABLES
!     BEGIN BLOCK WITH ...EXITS TO 40
!**********************************************************************
          DO j = 1, n
            info = j
            s = 0.0E0
            jm1 = j - 1
            IF (jm1>=1) THEN
              DO k = 1, jm1
                t = a(k,j) - sdot(k-1,a(1,k),1,a(1,j),1)
                t = t/a(k,k)
                a(k,j) = t
                s = s + t*t
              END DO
            END IF
            s = a(j,j) - s
            IF (s<=0.0E0) GO TO 10
            a(j,j) = SQRT(s)
          END DO
          info = 0
10        CONTINUE
          RETURN

        END SUBROUTINE spofa

!.....................................................................

      END SUBROUTINE set_random_multivariate_normal

!*********************************************************************

    END MODULE random_multivariate_normal_mod
