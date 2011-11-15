    MODULE random_f_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_f(dfn,dfd)
! .. Use Statements ..
        USE random_standard_gamma_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_f
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: dfd, dfn
! ..
! .. Local Scalars ..
        REAL :: xden, xnum
! ..
! .. Executable Statements ..

!**********************************************************************
!     REAL FUNCTION RANDOM_F( DFN, DFD )
!                GENerate random deviate from the F distribution
!                              Function
!     Generates a random deviate from the F (variance ratio)
!     distribution with DFN degrees of freedom in the numerator
!     and DFD degrees of freedom in the denominator.
!                              Arguments
!     DFN --> Numerator degrees of freedom
!             (Must be positive)
!                              REAL DFN
!      DFD --> Denominator degrees of freedom
!             (Must be positive)
!                              REAL DFD
!                              Method
!     Directly generates ratio of chisquare variates
!**********************************************************************
!     JJV changed this code to call random_standard_gamma directly
!      REAL random_chisq
!      EXTERNAL random_chisq
        IF (dfn<=0.0 .OR. dfd<=0.0) THEN
          WRITE (*,*) 'Degrees of freedom nonpositive in GENF - abort!'
          WRITE (*,*) 'DFN value: ', dfn, 'DFD value: ', dfd
          STOP 'Degrees of freedom nonpositive in GENF - abort!'
        END IF

        xnum = 2.0*random_standard_gamma(dfn/2.0)/dfn

!      GENF = ( GENCHI( DFN ) / DFN ) / ( GENCHI( DFD ) / DFD )
        xden = 2.0*random_standard_gamma(dfd/2.0)/dfd
!     JJV changed constant so that it will not underflow at compile time
!     JJV while not slowing generator by using double precision or logs.
!      IF (.NOT. (xden.LE. (1.0E-38*xnum))) GO TO 20
        IF (xden<=1.0E-37*xnum) THEN
          WRITE (*,*) ' GENF - generated numbers would cause overflow'
          WRITE (*,*) ' Numerator ', xnum, ' Denominator ', xden
!     JJV next 2 lines changed to maintain truncation of large deviates.
!      WRITE (*,*) ' GENF returning 1.0E38'
!      random_f = 1.0E38
          WRITE (*,*) ' GENF returning 1.0E37'
          random_f = 1.0E37
        ELSE

          random_f = xnum/xden
        END IF
        RETURN

      END FUNCTION random_f

!*********************************************************************

    END MODULE random_f_mod
