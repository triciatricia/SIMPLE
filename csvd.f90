SUBROUTINE CSVD ( A, MMAX, NMAX, M, N, P, NU, NV, S, U, V )
! CSVD computes the singular value decomposition of a complex matrix.
!
!    The singular value decomposition of a complex M by N matrix A
!    has the form
!
!      A = U S V*
!
!    where 
!
!      U is an M by M unitary matrix,
!      S is an M by N diagonal matrix,
!      V is an N by N unitary matrix.
!
!    Moreover, the entries of S are nonnegative and occur on the diagonal
!    in descending order.
!
!    Several internal arrays are dimensioned under the assumption
!    that N <= 100.
!
!  Modified:
!
!    03 May 2007
!
!  Author:
!
!    Peter Businger, Gene Golub
!
!  Reference:
!
!    Peter Businger, Gene Golub,
!    Algorithm 358:
!    Singular Value Decomposition of a Complex Matrix,
!    Communications of the ACM,
!    Volume 12, Number 10, October 1969, pages 564-565.
!
!  Parameters:
!
!    Input/output, complex A(MMAX,*), the M by N matrix, which may be
!    augmented by P extra columns to which the transformation U*
!    is to be applied.  On output, A has been overwritten, and
!    if 0 < P, columns N+1 through N+P have been premultiplied by U*.
!
!    Input, integer MMAX, the leading dimension of the arrays A
!    and U.
!
!    Input, integer NMAX, the leading dimension of V, and perhaps
!    the second dimension of A and U.
!
!    Input, integer M, N, the number of rows and columns in A.
!    It must be the case that N <= M.  Several internal arrays are
!    dimensioned under the assumption that N <= NBIG, where NBIG
!    is an internal parameter, currently set to 100.
!
!    Input, integer P, the number of vectors, stored in A(*,N+1:N+P),
c    to which the transformation U* should be applied.
c
c    Input, integer NU, the number of columns of U to compute.
c
c    Input, integer NV, the number of columns of V to compute.
c
c    Output, real S(N), the computed singular values.
c
c    Output, complex U(MMAX,NU), the first NU columns of U.
c
c    Output, complex V(NMAX,NV), the first NV columns of V.
c
c  Local Parameters:
c
c    Local, real ETA, the relative machine precision.
c    The original text uses ETA = 1.5E-8.
c
c    Local, integer NBIG, is a parameter used to dimension work arrays.
c    The size of NBIG limits the maximum possible size of N that can
c    be handled.  If you want to work with values of N that are larger,
c    simply increase the value assigned to NBIG below.
c
c    Local, real TOL, the smallest normalized positive number, divided by ETA.
c    The original test uses TOL = 1.E-31.
c
      IMPLICIT NONE

      INTEGER MMAX
      INTEGER NMAX

      integer nbig
      parameter ( nbig = 100 )

      COMPLEX A(MMAX,*)
      REAL B(nbig)
      REAL C(nbig)
      REAL CS
      REAL EPS
      REAL ETA
      REAL F
      REAL G
      REAL H
      INTEGER I
      INTEGER J
      INTEGER K
      INTEGER KK
      INTEGER K1
      INTEGER L
      INTEGER L1
      INTEGER LL
      INTEGER M
      INTEGER N
      INTEGER N1
      INTEGER NP
      INTEGER NU
      INTEGER NV
      INTEGER P
      COMPLEX Q
      COMPLEX R
      REAL S(*)
      REAL SN
      REAL T(nbig)
      REAL TOL
      COMPLEX U(MMAX,*)
      COMPLEX V(NMAX,*)
      REAL W
      REAL X
      REAL Y
      REAL Z

      SAVE ETA
      SAVE TOL

      DATA ETA / 1.1920929E-07 /
      DATA TOL / 1.5E-31 /
c
c  Check N.
c
      if ( n < 1 ) then
        write ( *, '(a)' ) ' '
        write ( *, '(a)' ) 'CSVD - Fatal error!'
        write ( *, '(a)' ) '  Input N < 1.'
        stop
      else if ( nbig < n ) then
        write ( *, '(a)' ) ' '
        write ( *, '(a)' ) 'CSVD - Fatal error!'
        write ( *, '(a)' ) '  NBIG < N.'
        stop
      end if
c
c  Check M.
c
      if ( m < 1 ) then
        write ( *, '(a)' ) ' '
        write ( *, '(a)' ) 'CSVD - Fatal error!'
        write ( *, '(a)' ) '  Input M < 1.'
        stop
      else if ( m < n ) then
        write ( *, '(a)' ) ' '
        write ( *, '(a)' ) 'CSVD - Fatal error!'
        write ( *, '(a)' ) '  M < N.'
        stop
      end if

      NP = N + P
      N1 = N + 1
c
c  Householder reduction.
c
      C(1) = 0.0E+00
      K = 1

10    continue

      K1 = K + 1
c
c  Elimination of A(I,K), I = K+1, ..., M.
c
      Z = 0.0E+00
      do I = K, M
        Z = Z + real ( A(I,K) )**2 + aimag ( A(I,K) )**2
      end do

      B(K) = 0.0E+00

      if ( TOL .lt. Z ) then

        Z = sqrt ( Z )
        B(K) = Z
        W = cabs ( A(K,K) )

        if ( W .eq. 0.0E+00 ) then
          Q = cmplx ( 1.0E+00, 0.0E+00 )
        else
          Q = A(K,K) / W
        end if

        A(K,K) = Q * ( Z + W )

        if ( K .ne. NP ) then

          do J = K1, NP

            Q = cmplx ( 0.0E+00, 0.0E+00 )
            do I = K, M
              Q = Q + conjg ( A(I,K) ) * A(I,J)
            end do
            Q = Q / ( Z * ( Z + W ) )

            do I = K, M
              A(I,J) = A(I,J) - Q * A(I,K)
            end do

          end do
c
c  Phase transformation.
c
          Q = -conjg ( A(K,K) ) / cabs ( A(K,K) )

          do J = K1, NP
            A(K,J) = Q * A(K,J)
          end do

        end if

      end if
c
c  Elimination of A(K,J), J = K+2, ..., N
c
      if ( K .eq. N ) then
        go to 140
      end if

      Z = 0.0E+00
      do J = K1, N
        Z = Z + real ( A(K,J) )**2 + aimag ( A(K,J) )**2
      end do

      C(K1) = 0.0E+00

      if ( TOL .lt. Z ) then

        Z = sqrt ( Z )
        C(K1) = Z
        W = cabs ( A(K,K1) )

        if ( W .eq. 0.0E+00 ) then
          Q = cmplx ( 1.0E+00, 0.0E+00 )
        else
          Q = A(K,K1) / W
        end if

        A(K,K1) = Q * ( Z + W )

        do I = K1, M

          Q = cmplx ( 0.0E+00, 0.0E+00 )

          do J = K1, N
            Q = Q + conjg ( A(K,J) ) * A(I,J)
          end do

          Q = Q / ( Z * ( Z + W ) )

          do J = K1, N
            A(I,J) = A(I,J) - Q * A(K,J)
          end do

        end do
c
c  Phase transformation.
c
        Q = -conjg ( A(K,K1) ) / cabs ( A(K,K1) )
        do I = K1, M
          A(I,K1) = A(I,K1) * Q
        end do

      end if

      K = K1
      go to 10
c
c  Tolerance for negligible elements.
c
140   continue

      EPS = 0.0E+00
      do K = 1, N
        S(K) = B(K)
        T(K) = C(K)
        EPS = amax1 ( EPS, S(K) + T(K) )
      end do

      EPS = EPS * ETA
c
c  Initialization of U and V.
c
      if ( 0 .lt. NU ) then

        do J = 1, NU
          do I = 1, M
            U(I,J) = cmplx ( 0.0E+00, 0.0E+00 )
          end do
          U(J,J) = cmplx ( 1.0E+00, 0.0E+00 )
        end do

      end if

      if ( 0 .lt. NV ) then

        do J = 1, NV
          do I = 1, N
            V(I,J) = cmplx ( 0.0E+00, 0.0E+00 )
          end do
          V(J,J) = cmplx ( 1.0E+00, 0.0E+00 )
        end do

      end if
c
c  QR diagonalization.
c
      do KK = 1, N

        K = N1 - KK
c
c  Test for split.
c
220     continue

        do LL = 1, K

          L = K + 1 - LL

          if ( abs ( T(L) ) .le. EPS ) then
            go to 290
          end if

          if ( abs ( S(L-1) ) .le. EPS ) then
            go to 240
          end if

        end do
c
c  Cancellation of E(L).
c
240     continue

        CS = 0.0E+00
        SN = 1.0E+00
        L1 = L - 1

        do I = L, K

          F = SN * T(I)
          T(I) = CS * T(I)

          if ( abs ( F ) .le. EPS ) then
            go to 290
          end if

          H = S(I)
          W = sqrt ( F * F + H * H )
          S(I) = W
          CS = H / W
          SN = - F / W

          if ( 0 .lt. NU ) then

            do J = 1, N
              X = real ( U(J,L1) )
              Y = real ( U(J,I) )
              U(J,L1) = cmplx ( X * CS + Y * SN, 0.0E+00 )
              U(J,I)  = cmplx ( Y * CS - X * SN, 0.0E+00 )
            end do

          end if

          if ( NP .ne. N ) then

            do J = N1, NP
              Q = A(L1,J)
              R = A(I,J)
              A(L1,J) = Q * CS + R * SN
              A(I,J)  = R * CS - Q * SN
            end do

          end if

        end do
c
c  Test for convergence.
c
290     continue

        W = S(K)

        if ( L .eq. K ) then
          go to 360
        end if
c
c  Origin shift.
c
        X = S(L)
        Y = S(K-1)
        G = T(K-1)
        H = T(K)
        F = ( ( Y - W ) * ( Y + W ) + ( G - H ) * ( G + H ) ) 
     &    / ( 2.0E+00 * H * Y )
        G = sqrt ( F * F + 1.0E+00 )
        if ( F .lt. 0.0E+00 ) then
          G = -G
        end if
        F = ( ( X - W ) * ( X + W ) + ( Y / ( F + G ) - H ) * H ) / X
c
c  QR step.
c
        CS = 1.0E+00
        SN = 1.0E+00
        L1 = L + 1

        do I = L1, K

          G = T(I)
          Y = S(I)
          H = SN * G
          G = CS * G
          W = sqrt ( H * H + F * F )
          T(I-1) = W
          CS = F / W
          SN = H / W
          F = X * CS + G * SN
          G = G * CS - X * SN
          H = Y * SN
          Y = Y * CS

          if ( 0 .lt. NV ) then

            do J = 1, N
              X = real ( V(J,I-1) )
              W = real ( V(J,I) )
              V(J,I-1) = cmplx ( X * CS + W * SN, 0.0E+00 )
              V(J,I)   = cmplx ( W * CS - X * SN, 0.0E+00 )
            end do

          end if

          W = sqrt ( H * H + F * F )
          S(I-1) = W
          CS = F / W
          SN = H / W
          F = CS * G + SN * Y
          X = CS * Y - SN * G

          if ( 0 .lt. NU ) then

            do J = 1, N
              Y = real ( U(J,I-1) )
              W = real ( U(J,I) )
              U(J,I-1) = cmplx ( Y * CS + W * SN, 0.0E+00 )
              U(J,I)   = cmplx ( W * CS - Y * SN, 0.0E+00 )
            end do

          end if

          if ( N .ne. NP ) then

            do J = N1, NP
              Q = A(I-1,J)
              R = A(I,J)
              A(I-1,J) = Q * CS + R * SN
              A(I,J)   = R * CS - Q * SN
            end do

          end if

        end do

        T(L) = 0.0E+00
        T(K) = F
        S(K) = X
        go to 220
c
c  Convergence.
c
360     continue

        if ( W .lt. 0.0E+00 ) then

          S(K) = -W

          if ( 0 .lt. NV ) then

            do J = 1, N
              V(J,K) = -V(J,K)
            end do

          end if
 
        end if

      end do
c
c  Sort the singular values.
c
      do K = 1, N

        G = -1.0E+00
        J = K

        do I = K, N
          if ( G .lt. S(I) ) then
            G = S(I)
            J = I
          end if
        end do

        if ( J .ne. K ) then

          S(J) = S(K)
          S(K) = G
c
c  Interchange V(1:N,J) and V(1:N,K).
c
          if ( 0 .lt. NV ) then

            do I = 1, N
              Q      = V(I,J)
              V(I,J) = V(I,K)
              V(I,K) = Q
            end do

          end if
c
c  Interchange U(1:N,J) and U(1:N,K).
c
          if ( 0 .lt. NU ) then
  
            do I = 1, N
              Q      = U(I,J)
              U(I,J) = U(I,K)
              U(I,K) = Q
            end do

          end if
c
c  Interchange A(J,N1:NP) and A(K,N1:NP).
c
          if ( N .ne. NP ) then

            do I = N1, NP
              Q      = A(J,I)
              A(J,I) = A(K,I)
              A(K,I) = Q
            end do

          end if

        end if

      end do
c
c  Back transformation.
c
      if ( 0 .lt. NU ) then

        do KK = 1, N

          K = N1 - KK

          if ( B(K) .ne. 0.0E+00 ) then

            Q = -A(K,K) / cabs ( A(K,K) )

            do J = 1, NU
              U(K,J) = Q * U(K,J)
            end do

            do J = 1, NU

              Q = cmplx ( 0.0E+00, 0.0E+00 )

              do I = K, M
                Q = Q + conjg ( A(I,K) ) * U(I,J)
              end do

              Q = Q / ( cabs ( A(K,K) ) * B(K) )

              do I = K, M
                U(I,J) = U(I,J) - Q * A(I,K)
              end do

            end do

          end if

        end do

      end if

      if ( 0 .lt. NV ) then

        if ( 2 .lt. N ) then

          do KK = 2, N

            K = N1 - KK
            K1 = K + 1

            if ( C(K1) .ne. 0.0E+00 ) then

              Q = -conjg ( A(K,K1) ) / cabs ( A(K,K1) )

              do J = 1, NV
                V(K1,J) = Q * V(K1,J)
              end do

              do J = 1, NV

                Q = cmplx ( 0.0E+00, 0.0E+00 )

                do I = K1, N
                  Q = Q + A(K,I) * V(I,J)
                end do

                Q = Q / ( cabs ( A(K,K1) ) * C(K1) )

                do I = K1, N
                  V(I,J) = V(I,J) - Q * conjg ( A(K,I) )
                end do

              end do

            end if

          end do

        end if

      end if

      return
      end