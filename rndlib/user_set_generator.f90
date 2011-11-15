    MODULE user_set_generator
! .. Use Statements ..
      USE ecuyer_cote_mod
! ..
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
! .. Default Accessibility ..
      PRIVATE
! ..
! .. Local Scalars ..
      INTEGER :: seed1, seed2
      CHARACTER (500) :: message_format
      CHARACTER (80) :: phrase
! ..
! .. Public Statements ..
      PUBLIC :: set_seeds
! ..
    CONTAINS

!*********************************************************************

      SUBROUTINE inter_phrase_set_seeds
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Executable Statements ..

        message_format = '(/5X,''Enter a  phrase that will &
          & be used to initialize  the random''/5X,''number &
          & generator.    Different  phrases  provide  different''/5X,''in&
          &itialization values.''/)'

        WRITE (*,message_format)

        READ (*,'(A)') phrase

        CALL phrase_to_seed(phrase,seed1,seed2)

        RETURN

      END SUBROUTINE inter_phrase_set_seeds

!*********************************************************************

      SUBROUTINE phrase_set_seeds(phrase)
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Scalar Arguments ..
        CHARACTER (*), INTENT (IN) :: phrase
! ..
! .. Local Scalars ..
        INTEGER :: seed1, seed2
! ..
! .. Executable Statements ..

        CALL phrase_to_seed(phrase,seed1,seed2)

        CALL set_all_seeds(seed1,seed2)

        CALL set_current_generator(1)

      END SUBROUTINE phrase_set_seeds

!*********************************************************************

      SUBROUTINE phrase_to_seed(phrase,seed1,seed2)
!----------------------------------------------------------------------
!     SUBROUTINE PHRTSD( PHRASE, SEED1, SEED2 )
!               PHRase To SeeDs
!                              Function
!     Uses a phrase (character string) to generate two seeds for the RGN
!     random number generator.
!                              Arguments
!     PHRASE --> Phrase to be used for random number generation
!                         CHARACTER*(*) PHRASE
!     SEED1 <-- First seed for RGN generator
!                         INTEGER SEED1
!     SEED2 <-- Second seed for RGN generator
!                         INTEGER SEED2
!                              Note
!     Trailing blanks are eliminated before the seeds are generated.
!     Generated seed values will fall in the range 1..2^30
!     (1..1,073,741,824)
!----------------------------------------------------------------------
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Parameters ..
        INTEGER, PARAMETER :: twop30 = 1073741824
        CHARACTER (86), PARAMETER :: table = 'abcdefghijklmnopqrstuvwxyz' &
          // 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' // '0123456789' // &
          '!@#$%^&*()_+[];:''"<>?,./'
! ..
! .. Scalar Arguments ..
        INTEGER, INTENT (OUT) :: seed1, seed2
        CHARACTER (*) :: phrase
! ..
! .. Local Scalars ..
        INTEGER :: i, ichr, j, lphr
! ..
! .. Local Arrays ..
        INTEGER, SAVE :: shift(0:4)
        INTEGER :: values(5)
! ..
! .. Intrinsic Functions ..
        INTRINSIC INDEX, LEN_TRIM, MOD
! ..
! .. Data Statements ..
        DATA shift/1, 64, 4096, 262144, 16777216/
! ..
! .. Executable Statements ..

        seed1 = 1234567890
        seed2 = 123456789
        lphr = LEN_TRIM(phrase)
        IF (lphr<1) RETURN
        DO i = 1, lphr
          ichr = MOD(INDEX(table,phrase(i:i)),64)
          IF (ichr==0) ichr = 63
          DO j = 1, 5
            values(j) = ichr - j
            IF (values(j)>=1) CYCLE
            values(j) = values(j) + 63
          END DO
          DO j = 1, 5
            seed1 = MOD(seed1+shift(j-1)*values(j),twop30)
            seed2 = MOD(seed2+shift(j-1)*values(6-j),twop30)
          END DO
        END DO
        RETURN

      END SUBROUTINE phrase_to_seed

!*********************************************************************

      SUBROUTINE set_seeds(which)
!!! Set random number seeds from time (if which == 1) else from
!!! user entered phrase (if which /=1)
!!! If which is ommitted, ask user what to do
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Scalar Arguments ..
        INTEGER, OPTIONAL, INTENT (IN) :: which
! ..
! .. Local Scalars ..
        INTEGER :: local_which
! ..
! .. Intrinsic Functions ..
        INTRINSIC PRESENT
! ..
! .. Executable Statements ..

        IF (PRESENT(which)) THEN

          local_which = which

        ELSE

          DO

            message_format = '(/5X,''Enter (1) to set random &
              &number seeds from the time of day''/5X,''   &
              &       (Computer runs so set cannot be replicated &
              &exactly)''//5X,''      (2) to set seeds from &
              &a phrase (character string) entered''/5X,'' &
              &         by you''/5X,''          (Computer runs &
              &so set can be replicated exactly)''/)'

            WRITE (*,message_format)
            READ (*,*) local_which

            IF (local_which<1 .OR. local_which>2) THEN
               CYCLE
            ELSE
               EXIT
            END IF

          END DO

        END IF

        IF (local_which==1) THEN
          CALL time_set_seeds
        ELSE
          CALL inter_phrase_set_seeds
        END IF

        RETURN

      END SUBROUTINE set_seeds

!*********************************************************************

      SUBROUTINE time_set_seeds
!!! Sets random number generator randomly from the clock
!!! Assumes that there is a clock.
!!! Warns if there is apparently no clock
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Local Scalars ..
        CHARACTER (10) :: time
! ..
! .. Intrinsic Functions ..
        INTRINSIC DATE_AND_TIME
! ..
! .. Executable Statements ..

        CALL DATE_AND_TIME(time=time)

        IF (time==' ') THEN

!!! Apparently no clock

          message_format = '(/5X,''There appears to  be no &
            &accessible clock on  this computer, hence''/5X,''the &
            &random  number generator seed cannot be  initialized &
            &from the''/5X,''time.  You must thus enter a phrase &
            &(character string) to set the''/5X,''seed.''/)'

          WRITE (*,message_format)

          CALL inter_phrase_set_seeds

          RETURN

        ELSE

          CALL phrase_to_seed(time,seed1,seed2)

          CALL set_all_seeds(seed1,seed2)

        END IF

        RETURN

      END SUBROUTINE time_set_seeds

!*********************************************************************

      SUBROUTINE user_set_all(seed1,seed2,generator)
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Scalar Arguments ..
        INTEGER, OPTIONAL, INTENT (IN) :: generator
        INTEGER, INTENT (IN) :: seed1, seed2
! ..
! .. Intrinsic Functions ..
        INTRINSIC PRESENT
! ..
! .. Executable Statements ..

        CALL set_all_seeds(seed1,seed2)

        IF (PRESENT(generator)) THEN
          CALL set_current_generator(generator)

        ELSE
          CALL set_current_generator(1)

        END IF

      END SUBROUTINE user_set_all

!*********************************************************************

    END MODULE user_set_generator
