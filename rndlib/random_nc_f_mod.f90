    MODULE random_nc_f_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_nc_f(dfn,dfd,xnonc)
! .. Use Statements ..
        USE random_standard_gamma_mod
        USE random_standard_normal_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_nc_f
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: dfd, dfn, xnonc
! ..
! .. Local Scalars ..
        REAL :: xden, xnum
        LOGICAL :: qcond
! ..
! .. Intrinsic Functions ..
        INTRINSIC SQRT
! ..
! .. Executable Statements ..

!**********************************************************************
!     REAL FUNCTION GENNF( DFN, DFD, XNONC )
!           GENerate random deviate from the Noncentral F distribution
!                              Function
!     Generates a random deviate from the  noncentral F (variance ratio)
!     distribution with DFN degrees of freedom in the numerator, and DFD
!     degrees of freedom in the denominator, and noncentrality parameter
!     XNONC.
!                              Arguments
!     DFN --> Numerator degrees of freedom
!             (Must be >= 1.0)
!                              REAL DFN
!      DFD --> Denominator degrees of freedom
!             (Must be positive)
!                              REAL DFD
!     XNONC --> Noncentrality parameter
!               (Must be nonnegative)
!                              REAL XNONC
!                              Method
!     Directly generates ratio of noncentral numerator chisquare variate
!     to central denominator chisquare variate.
!**********************************************************************
!     JJV changed the code to call SGAMMA and SNORM directly
!      REAL random_chisq,random_nc_chisq
!      EXTERNAL random_chisq,random_nc_chisq
!     JJV changed the argument checker to allow DFN = 1.0
!     JJV in the same way as GENNCH was changed.
        qcond = dfn < 1.0 .OR. dfd <= 0.0 .OR. xnonc < 0.0
        IF (qcond) THEN
          WRITE (*,*) 'In GENNF - Either (1) Numerator DF < 1.0 or'
          WRITE (*,*) '(2) Denominator DF <= 0.0 or '
          WRITE (*,*) '(3) Noncentrality parameter < 0.0'
          WRITE (*,*) 'DFN value: ', dfn, 'DFD value: ', dfd, &
            'XNONC value: ', xnonc
          STOP &
            'Degrees of freedom or noncent param out of range in GENNF'
        END IF

!      GENNF = ( GENNCH( DFN, XNONC ) / DFN ) / ( GENCHI( DFD ) / DFD )
!     JJV changed this to call SGAMMA and SNORM directly
!     xnum = random_nc_chisq(dfn,xnonc)/dfn
        IF (dfn<1.000001) THEN
!     JJV case dfn = 1.0 - here I am treating dfn as exactly 1.0
          xnum = (random_standard_normal()+SQRT(xnonc))**2
        ELSE

!     JJV case dfn > 1.0
          xnum = (2.0*random_standard_gamma((dfn- &
            1.0)/2.0)+(random_standard_normal()+SQRT(xnonc))**2)/dfn
        END IF

!     xden = random_chisq(dfd)/dfd
        xden = 2.0*random_standard_gamma(dfd/2.0)/dfd

!     JJV changed constant so that it will not underflow at compile time
!     JJV while not slowing generator by using double precision or logs.
!      IF (.NOT. (xden.LE. (1.0E-38*xnum))) GO TO 40
        IF (xden<=1.0E-37*xnum) THEN
          WRITE (*,*) ' GENNF - generated numbers would cause overflow'
          WRITE (*,*) ' Numerator ', xnum, ' Denominator ', xden
!     JJV next 2 lines changed to maintain truncation of large deviates.
!      WRITE (*,*) ' GENNF returning 1.0E38'
!      random_nc_f = 1.0E38
          WRITE (*,*) ' GENNF returning 1.0E37'
          random_nc_f = 1.0E37
        ELSE

          random_nc_f = xnum/xden
        END IF
        RETURN

      END FUNCTION random_nc_f

!*********************************************************************

    END MODULE random_nc_f_mod
