    MODULE random_nc_chisq_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_nc_chisq(df,pnonc)
! .. Use Statements ..
        USE random_standard_gamma_mod
        USE random_standard_normal_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_nc_chisq
! ..
! .. Scalar Arguments ..
        REAL, INTENT (IN) :: df, pnonc
! ..
! .. Intrinsic Functions ..
        INTRINSIC SQRT
! ..
! .. Executable Statements ..

!**********************************************************************
!     REAL FUNCTION GENNCH( DF, PNONC )
!           Generate random value of Noncentral CHIsquare variable
!                              Function
!     Generates random deviate  from the  distribution  of a  noncentral
!     chisquare with DF degrees  of freedom and noncentrality  parameter
!     PNONC.
!                              Arguments
!     DF --> Degrees of freedom of the chisquare
!            (Must be >= 1.0)
!                         REAL DF
!     PNONC --> Noncentrality parameter of the chisquare
!               (Must be >= 0.0)
!                         REAL PNONC
!                              Method
!     Uses fact that  noncentral chisquare  is  the  sum of a  chisquare
!     deviate with DF-1  degrees of freedom plus the  square of a normal
!     deviate with mean sqrt(PNONC) and standard deviation 1.
!**********************************************************************
!     JJV changed these to call SGAMMA and SNORM directly
!      REAL random_chisq,random_normal
!      EXTERNAL random_chisq,random_normal
!     JJV changed abort to df < 1, and added case: df = 1
        IF (df<1.0 .OR. pnonc<0.0) THEN
          WRITE (*,*) 'DF < 1 or PNONC < 0 in GENNCH - ABORT'
          WRITE (*,*) 'Value of DF: ', df, ' Value of PNONC', pnonc
          STOP 'DF < 1 or PNONC < 0 in GENNCH - ABORT'
        END IF

!     JJV changed this to call SGAMMA and SNORM directly
!      random_nc_chisq = random_chisq(df-1.0) + random_normal(sqrt(pnonc),1.0)**2

        IF (df<1.000001) THEN
!     JJV case DF = 1.0
          random_nc_chisq = (random_standard_normal()+SQRT(pnonc))**2
        ELSE

!     JJV case DF > 1.0
          random_nc_chisq = 2.0*random_standard_gamma((df-1.0)/2.0) + &
            (random_standard_normal()+SQRT(pnonc))**2
        END IF
        RETURN

      END FUNCTION random_nc_chisq

!*********************************************************************

    END MODULE random_nc_chisq_mod
