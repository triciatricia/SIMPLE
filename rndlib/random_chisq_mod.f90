    MODULE random_chisq_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_chisq(df)
!**********************************************************************
!     REAL FUNCTION GENCHI( DF )
!                Generate random value of CHIsquare variable
!                              Function
!     Generates random deviate from the distribution of a chisquare
!     with DF degrees of freedom random variable.
!                              Arguments
!     DF --> Degrees of freedom of the chisquare
!            (Must be positive)
!                         REAL DF
!                              Method
!     Uses relation between chisquare and gamma.
!**********************************************************************
! .. Use Statements ..
        USE random_standard_gamma_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        REAL :: random_chisq
! ..
! .. Scalar Arguments ..
        REAL :: df
! ..
! .. Executable Statements ..

        IF (df<=0.0) THEN
          WRITE (*,*) 'DF <= 0 in GENCHI - ABORT'
          WRITE (*,*) 'Value of DF: ', df
          STOP 'DF <= 0 in GENCHI - ABORT'
        END IF

!     JJV changed this to call random_standard_gamma directly
!   10 random_chisq = 2.0*random_gamma(1.0,df/2.0)
        random_chisq = 2.0*random_standard_gamma(df/2.0)
        RETURN

      END FUNCTION random_chisq

!*********************************************************************

    END MODULE random_chisq_mod
