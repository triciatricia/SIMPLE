    MODULE random_standard_normal_mod
! .. Implicit None Statement ..
      IMPLICIT NONE
! ..
    CONTAINS

!*********************************************************************

      FUNCTION random_standard_normal()
!**********************************************************************C
!                                                                      C
!                                                                      C
!     (STANDARD-)  N O R M A L  DISTRIBUTION                           C
!                                                                      C
!                                                                      C
!**********************************************************************C
!**********************************************************************C
!                                                                      C
!     FOR DETAILS SEE:                                                 C
!                                                                      C
!               AHRENS, J.H. AND DIETER, U.                            C
!               EXTENSIONS OF FORSYTHE'S METHOD FOR RANDOM             C
!               SAMPLING FROM THE NORMAL DISTRIBUTION.                 C
!               MATH. COMPUT., 27,124 (OCT. 1973), 927 - 937.          C
!                                                                      C
!     ALL STATEMENT NUMBERS CORRESPOND TO THE STEPS OF ALGORITHM 'FL'  C
!     (M=5) IN THE ABOVE PAPER     (SLIGHTLY MODIFIED IMPLEMENTATION)  C
!                                                                      C
!     Modified by Barry W. Brown, Feb 3, 1988 to use                   C
!     RANDOM_STANDARD_UNIFORM instead of                               C
!     SUNIF.  The argument IR thus goes away.                          C
!                                                                      C
!**********************************************************************C
!     THE DEFINITIONS OF THE CONSTANTS A(K), D(K), T(K) AND
!     H(K) ARE ACCORDING TO THE ABOVEMENTIONED ARTICLE
! .. Use Statements ..
        USE random_standard_uniform_mod
! ..
! .. Implicit None Statement ..
        IMPLICIT NONE
! ..
! .. Local Scalars ..
        REAL :: aa, s, tt, u, ustar, w, y
        INTEGER :: i
! ..
! .. Intrinsic Functions ..
        INTRINSIC FLOAT, INT, MIN
! ..
! .. Function Return Value ..
        REAL :: random_standard_normal
! ..
! .. Parameters ..
        REAL, PARAMETER :: a(32) = (/ 0.0, 0.3917609E-1, 0.7841241E-1, &
          0.1177699, 0.1573107, 0.1970991, 0.2372021, 0.2776904, &
          0.3186394, 0.3601299, 0.4022501, 0.4450965, 0.4887764, &
          0.5334097, 0.5791322, 0.6260990, 0.6744898, 0.7245144, &
          0.7764218, 0.8305109, 0.8871466, 0.9467818, 1.009990, 1.077516, &
          1.150349, 1.229859, 1.318011, 1.417797, 1.534121, 1.675940, &
          1.862732, 2.153875/)
        REAL, PARAMETER :: d(31) = (/ 0.0, 0.0, 0.0, 0.0, 0.0, 0.2636843, &
          0.2425085, 0.2255674, 0.2116342, 0.1999243, 0.1899108, &
          0.1812252, 0.1736014, 0.1668419, 0.1607967, 0.1553497, &
          0.1504094, 0.1459026, 0.1417700, 0.1379632, 0.1344418, &
          0.1311722, 0.1281260, 0.1252791, 0.1226109, 0.1201036, &
          0.1177417, 0.1155119, 0.1134023, 0.1114027, 0.1095039/)
        REAL, PARAMETER :: h(31) = (/ 0.3920617E-1, 0.3932705E-1, &
          0.3950999E-1, 0.3975703E-1, 0.4007093E-1, 0.4045533E-1, &
          0.4091481E-1, 0.4145507E-1, 0.4208311E-1, 0.4280748E-1, &
          0.4363863E-1, 0.4458932E-1, 0.4567523E-1, 0.4691571E-1, &
          0.4833487E-1, 0.4996298E-1, 0.5183859E-1, 0.5401138E-1, &
          0.5654656E-1, 0.5953130E-1, 0.6308489E-1, 0.6737503E-1, &
          0.7264544E-1, 0.7926471E-1, 0.8781922E-1, 0.9930398E-1, &
          0.1155599, 0.1404344, 0.1836142, 0.2790016, 0.7010474/)
        REAL, PARAMETER :: t(31) = (/ 0.7673828E-3, 0.2306870E-2, &
          0.3860618E-2, 0.5438454E-2, 0.7050699E-2, 0.8708396E-2, &
          0.1042357E-1, 0.1220953E-1, 0.1408125E-1, 0.1605579E-1, &
          0.1815290E-1, 0.2039573E-1, 0.2281177E-1, 0.2543407E-1, &
          0.2830296E-1, 0.3146822E-1, 0.3499233E-1, 0.3895483E-1, &
          0.4345878E-1, 0.4864035E-1, 0.5468334E-1, 0.6184222E-1, &
          0.7047983E-1, 0.8113195E-1, 0.9462444E-1, 0.1123001, 0.1364980, &
          0.1716886, 0.2276241, 0.3304980, 0.5847031/)
! ..
! .. Executable Statements ..

        u = random_standard_uniform()
        s = 0.0
        IF (u>0.5) s = 1.0
        u = u + u - s
        u = 32.0*u
        i = MIN(INT(u),31)
        IF (i==0) GO TO 50

!                                START CENTER

        ustar = u - FLOAT(i)
        aa = a(i)
10      IF (ustar<=t(i)) GO TO 20
        w = (ustar-t(i))*h(i)
        CALL set_value
        RETURN

!                                CENTER CONTINUED

20      u = random_standard_uniform()
        w = u*(a(i+1)-aa)
        tt = (0.5*w+aa)*w
        GO TO 40

30      tt = u
        ustar = random_standard_uniform()
40      IF (ustar>tt) THEN
          CALL set_value
          RETURN
        END IF
        u = random_standard_uniform()
        IF (ustar>=u) GO TO 30
        ustar = random_standard_uniform()
        GO TO 10

!                                START TAIL

50      i = 6
        aa = a(32)
        GO TO 70

60      aa = aa + d(i)
        i = i + 1
70      u = u + u
        IF (u<1.0) GO TO 60
        u = u - 1.0
80      w = u*d(i)
        tt = (0.5*w+aa)*w
        GO TO 100

90      tt = u
100     ustar = random_standard_uniform()
        IF (ustar>tt) THEN
          CALL set_value
          RETURN
        END IF
        u = random_standard_uniform()
        IF (ustar>=u) GO TO 90
        u = random_standard_uniform()
        GO TO 80

      CONTAINS

!.....................................................................

        SUBROUTINE set_value
! .. Implicit None Statement ..
          IMPLICIT NONE
! ..
! .. Executable Statements ..

!                                EXIT   (BOTH CASES)
          y = aa + w
          random_standard_normal = y
          IF (s==1.0) random_standard_normal = -y
          RETURN

        END SUBROUTINE set_value

!.....................................................................

      END FUNCTION random_standard_normal

!*********************************************************************

    END MODULE random_standard_normal_mod
