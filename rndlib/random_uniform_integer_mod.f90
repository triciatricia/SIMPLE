    MODULE random_uniform_integer_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_uniform_integer(low,high)
! .. Use Statements ..
        USE ecuyer_cote_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Function Return Value ..
        INTEGER :: random_uniform_integer
! ..
! .. Parameters ..
        INTEGER, PARAMETER :: maxnum = 2147483561
        CHARACTER (20), PARAMETER :: err1 = 'LOW > HIGH in IGNUIN'
        CHARACTER (41), PARAMETER :: err2 = &
          ' ( HIGH - LOW ) > 2,147,483,561 in IGNUIN'
! ..
! .. Scalar Arguments ..
        INTEGER, INTENT (IN) :: high, low
! ..
! .. Local Scalars ..
        INTEGER :: err, ign, maxnow, range, ranp1
! ..
! .. Intrinsic Functions ..
        INTRINSIC MOD
! ..
! .. Executable Statements ..

!**********************************************************************
!     INTEGER FUNCTION IGNUIN( LOW, HIGH )
!               GeNerate Uniform INteger
!                              Function
!     Generates an integer uniformly distributed between LOW and HIGH.
!                              Arguments
!     LOW --> Low bound (inclusive) on integer value to be generated
!                         INTEGER LOW
!     HIGH --> High bound (inclusive) on integer value to be generated
!                         INTEGER HIGH
!                              Note
!     If (HIGH-LOW) > 2,147,483,561 prints error message on * unit and
!     stops the program.
!**********************************************************************
!     random_large_integer generates integers between 1 and 2147483562
!     MAXNUM is 1 less than maximum generable value
        IF (low>high) THEN
          err = 1
!      ABORT-PROGRAM
        ELSE

          range = high - low
          IF (range>maxnum) THEN
            err = 2
!      ABORT-PROGRAM
          ELSE

            IF (low==high) THEN
              random_uniform_integer = low
              RETURN
            END IF

!     Number to be generated should be in range 0..RANGE
!     Set MAXNOW so that the number of integers in 0..MAXNOW is an
!     integral multiple of the number in 0..RANGE

            ranp1 = range + 1
            maxnow = (maxnum/ranp1)*ranp1
            ign = random_large_integer() - 1
            DO WHILE ( .NOT. ign<=maxnow)
              ign = random_large_integer() - 1
            END DO
            random_uniform_integer = low + MOD(ign,ranp1)
            RETURN

          END IF
        END IF
        IF (err==1) THEN
          WRITE (*,*) err1
        ELSE

!     TO ABORT-PROGRAM
          WRITE (*,*) err2
        END IF
        WRITE (*,*) ' LOW: ', low, ' HIGH: ', high
        WRITE (*,*) ' Abort on Fatal ERROR'
        IF (err==1) STOP 'LOW > HIGH in IGNUIN'

        STOP ' ( HIGH - LOW ) > 2,147,483,561 in IGNUIN'
      END FUNCTION random_uniform_integer

!*********************************************************************

    END MODULE random_uniform_integer_mod
