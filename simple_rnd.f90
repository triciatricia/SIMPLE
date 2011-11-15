!==Module simple_rnd
!
! simple_rnd contains routines for generation of random numbers. The code is distributed 
! with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution
! or modification is regulated by the GNU General Public License. *Author:* Hans Elmlund, 2009-05-12.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
! 
module simple_rnd
implicit none

private :: idum, r8po_fa
public

integer, save :: idum

contains

    subroutine seed_rnd
    ! Set idum to any negative value to initialize or reinitialize the sequence
        real :: rrnd
        call random_seed
        call random_number(rrnd)
        idum = -nint(rrnd*(real(3000000)))
    end subroutine seed_rnd

    function ran3( ) result( harvest )
    ! returns a random deviate between 0.0 and 1.0. The algorithm is developed by Donald Knuth, fetched from numerical 
    ! recepies. If suspecting that the randomness is not sufficient using this routine, implement ran4 from NR or
    ! go back to the standard generator
        integer, parameter     :: mbig=1000000000, mseed=161803398, mz=0
        real, parameter        :: fac=1.e-9
        integer, save          :: ma(55),inext,inextp,iff=0
        integer                :: mj,mk,i,ii,k
        real                   :: harvest
        if( idum < 0 .or. iff == 0 )then ! Initialization
            iff    = 1
            mj     = mseed-iabs(idum) ! Initialize ma(55) using the seed idum and the large number mseed
            mj     = mod(mj,mbig)
            ma(55) = mj
            mk     = 1
            do i=1,54                 ! Now, initialize the rest of the table
                ii     = mod(21*i,55) ! in a slightly random order
                ma(ii) = mk           ! with numbers that are not especially random    
                mk     = mj-mk
                if( mk < mz ) mk = mk+mbig
                mj     = ma(ii)   
            end do
            do k=1,4          ! randomize by "warming up the generator"
                do i=1,55
                      ma(i) = ma(i)-ma(1+mod(i+30,55))
                      if( ma(i) < mz ) ma(i) = ma(i)+mbig
                end do
            end do    
            inext  = 0  ! prepare indices for our first generated number
            inextp = 31 ! constant 31 is special, see Knuth
            idum   = 1
        endif
        ! Here is were it starts, except on initialization
        inext  = inext+1
        if( inext == 56 ) inext = 1
        inextp = inextp+1
        if( inextp == 56 ) inextp = 1
        mj = ma(inext)-ma(inextp)
        if( mj < mz ) mj = mj+mbig
        ma(inext) = mj
        harvest = real(mj)*fac
    end function ran3

    function bran( p ) result( b )
    ! is for generating a Bernoulli random number _b_, which is a random number that is 1.0 with probablility _p_ and
    ! 0.0 otherwise. Therefore, for a uniform random number _u_ drawn between zero and one, we take _b_ = _1_._0_ when
    ! _u_ <= _p_ and _b_ = _0_._0_ otherwise
        real, intent(in)       :: p
        real                   :: b, u
        ! check so that the given probability is btw 0. and 1.
        if( p < 0. )then
            write(*,*) 'ERROR: probability less than zero!'
            write(*,*) 'In: bran, module: simple_rnd.f95'
            stop
        else if( p > 1. )then
            write(*,*) 'ERROR: probability larger than one!'
            write(*,*) 'In: bran, module: simple_rnd.f95'
            stop
        endif
        ! generate uniform random number
        u = ran3( )
        ! generate the Bernoulli random number
        if( u <= p ) then
            b = 1. ! success
        else
            b = 0. ! failure
        endif
    end function bran

    function gasdev_lim( mean, stdev, limits ) result( harvest )
    ! random number generator yielding normal distribution with given mean and stdev (from NR).
    ! Added acceptance-rejection according to limits (for constrained CE optimization)
        real, intent(in) :: mean, stdev
        real, intent(in) :: limits(2)
        real             :: harvest
        harvest = limits(2)+99.
        do while( harvest < limits(1) .or. harvest > limits(2) )
            harvest = gasdev( mean, stdev )
        end do 
    end function gasdev_lim

    function gasdev( mean, stdev ) result( harvest )
    ! random number generator yielding normal distribution with given _mean_ and _stdev_ (from NR).
    ! standard _mean_ and _stdev_ values are 0 and 1, respectively
        real, intent(in) :: mean, stdev
        real             :: harvest
        harvest = stdev*gasdev3( )+mean
    end function gasdev

    function gasdev3( ) result( harvest )
    ! random number generator yielding normal distribution with zero mean and unit variance (from NR)
        real                   :: v1=0., v2=0., r, fac, harvest
        real,save              :: gset
        integer,save           :: iset=0
        if( idum < 0 ) iset = 0
        if( iset == 0 )then ! reinitialize
            r = 99.
            do while( r >= 1. .or. r == 0. )
                v1 = 2.*ran3( )-1.
                v2 = 2.*ran3( )-1.
                r  = v1**2.+v2**2.
            end do
            fac = sqrt(-2.*log(r)/r)
            ! Now make Box-Muller transformation to get the two normal deviates.
            ! Return one and save the other for the next call.
            gset    = v1*fac
            iset    = 1
            harvest = v2*fac
        else
            iset    = 0
            harvest = gset
        endif
    end function gasdev3

    function irnd_uni( NP )result( irnd )
    ! generates a uniformly distributed random integer [_1_,_NP_]
        integer, intent(in) :: NP
        integer             :: irnd
        irnd = 1
        if( NP == 0 )then
            write(*,*) 'Uniform random integer must be generated from a non-empty set!'
            write(*,*) 'In: irnd_uni, module: simple_rnd.f95'
            stop
        else if( NP == 1 )then
            irnd = 1
        else
            irnd = max(1,ceiling(ran3()*(real(NP))))
        endif
    end function irnd_uni
    
    function irnd_uni_not( NP, no )result( irnd )
        integer, intent(in) :: NP, no
        integer             :: irnd
        irnd = irnd_uni( NP )
        do while( irnd == no )
            irnd = irnd_uni( NP )
        end do
    end function irnd_uni_not

    function irnd_uni_lim( llim, hlim )result( irnd )
        integer, intent(in) :: llim, hlim
        integer             :: irnd
        irnd = irnd_uni( hlim )
        do while( irnd < llim .or. irnd >= hlim )
            irnd = irnd_uni( hlim )
        end do
    end function irnd_uni_lim

    subroutine irnd_uni_pair( NP, irnd, jrnd )
    ! generates a random disjoint pair
        integer, intent(in)  :: NP
        integer, intent(out) :: irnd, jrnd
        irnd = irnd_uni( NP )
        jrnd = irnd
        do while( irnd == jrnd ) 
            jrnd = irnd_uni( NP )
        end do
    end subroutine irnd_uni_pair

    function irnd_gasdev( mean, stdev, NP )result( irnd )
    ! generates a normally distributed random integer [_1_,_NP_]
        real, intent(in)    :: mean, stdev
        integer, intent(in) :: NP
        integer             :: irnd
        real                :: limits(2)
        irnd = 1
        if( NP == 0 )then
            write(*,*) 'Gaussian random integer must be generated from a non-empty (.ne. 0) set!'
            write(*,*) 'In: irnd_gasdev, module: simple_rnd.f95'
            stop
        else if( NP == 1 )then
            irnd = 1
        else
            limits(1) = 1.
            limits(2) = real(NP)
            irnd      = max(1,nint(gasdev_lim( mean, stdev, limits )))
        endif       
    end function irnd_gasdev

    subroutine ran_iarr( iarr, NP )
    ! generates an array of random integers [_1_,_NP_]
        integer, intent(in)  :: NP
        integer, intent(out) :: iarr(:)
        integer :: i
        do i=1,size( iarr )
            iarr(i) = irnd_uni(NP)
        end do
    end subroutine ran_iarr
    
    function mnorm_smp( cov, m, means ) result( x )
    ! mnorm_smp samples a multivariate normal distribution.
    !
    !  Discussion:
    !
    !    The multivariate normal distribution for the M dimensional vector X
    !    has the form:
    !
    !      pdf(X) = (2*pi*det(A))**(-M/2) * exp(-0.5*(X-MU)'*inverse(A)*(X-MU))
    !
    !    where MU is the mean vector, and A is a positive definite symmetric
    !    matrix called the variance-covariance matrix.
    !
    !  Licensing:
    !
    !    This code is distributed under the GNU LGPL license. 
    !
    !  Modified:
    !
    !    07 December 2009
    !
    !  Author:
    !
    !    John Burkardt
    !
    !  Parameters:
    !
    !    Input, integer M, the dimension of the space.
    !
    !    Input, integer N, the number of points.
    !
    !    Input, real A(M,M), the variance-covariance 
    !    matrix.  A must be positive definite symmetric.
    !
    !    Input, real MU(M), the mean vector.
    !
    !    Input/output, integer SEED, the random number seed.
    !
    !    Output, real X(M), the points.
    !
        integer, intent(in) :: m
        real, intent(in)    :: cov(m,m), means(m)
        integer             :: info, i
        real                :: r(m,m), x(m), xtmp(1,m)
        ! Compute the upper triangular Cholesky factor R of the variance-covariance matrix.
        r = cov
        call r8po_fa ( m, r, info )
        if ( info /= 0 ) then
            write ( *, '(a)' ) ' '
            write ( *, '(a)' ) 'mnorm_smp - Fatal error!'
            write ( *, '(a)' ) 'The variance-covariance matrix is not positive definite symmetric'
            stop
        end if
        ! Samples of the 1D normal distribution with mean 0 and variance 1.
        do i=1,m
            x(i) = gasdev3()
        end do  
        ! Compute R' * X.
        xtmp(1,:) = x
        xtmp = matmul(xtmp,r)
        x = xtmp(1,:)+means
    end function mnorm_smp
    
    subroutine r8po_fa( n, a, info )
    ! R8PO_FA factors an R8PO matrix.
    !
    !  Discussion:
    !
    !    The R8PO storage format is used for a symmetric positive definite 
    !    matrix and its inverse.  (The Cholesky factor of an R8PO matrix is an
    !    upper triangular matrix, so it will be in R8GE storage format.)
    !
    !    Only the diagonal and upper triangle of the square array are used.
    !    This same storage scheme is used when the matrix is factored by
    !    R8PO_FA, or inverted by R8PO_INVERSE.  For clarity, the lower triangle
    !    is set to zero.
    !
    !    R8PO storage is used by LINPACK and LAPACK.
    !
    !    The positive definite symmetric matrix A has a Cholesky factorization
    !    of the form:
    !
    !      A = R' * R
    !
    !    where R is an upper triangular matrix with positive elements on
    !    its diagonal.  This routine overwrites the matrix A with its
    !    factor R.
    !
    !  Licensing:
    !
    !    This code is distributed under the GNU LGPL license. 
    !
    !  Modified:
    !
    !    22 March 2003
    !
    !  Author:
    !
    !    Original FORTRAN77 version by Dongarra, Bunch, Moler, Stewart.
    !    FORTRAN90 version by John Burkardt.
    !
    !  Reference:
    !
    !    Jack Dongarra, Jim Bunch, Cleve Moler, Pete Stewart,
    !    LINPACK User's Guide,
    !    SIAM, 1979,
    !    ISBN13: 978-0-898711-72-1,
    !    LC: QA214.L56.
    !
    !  Parameters:
    !
    !    Input, integer ( kind = 4 ) N, the order of the matrix.
    !
    !    Input/output, real ( kind = 8 ) A(N,N).
    !    On input, the matrix in R8PO storage.
    !    On output, the Cholesky factor R in R8GE storage.
    !
    !    Output, integer ( kind = 4 ) INFO, error flag.
    !    0, normal return.
    !    K, error condition.  The principal minor of order K is not
    !    positive definite, and the factorization was not completed.
    !
        integer, intent(in)  :: n
        real, intent(inout)  :: a(n,n)
        integer, intent(out) :: info
        integer :: i, j, k
        real :: s
        do j = 1, n
            do k = 1, j - 1
                a(k,j) = ( a(k,j) - sum ( a(1:k-1,k) * a(1:k-1,j) ) ) / a(k,k)
            end do
            s = a(j,j) - sum ( a(1:j-1,j)**2 )
            if ( s <= 0.0D+00 ) then
                info = j
                return
            end if
            a(j,j) = sqrt(s)
        end do
        info = 0
        ! Since the Cholesky factor is stored in R8GE format, be sure to
        ! zero out the lower triangle
        do i = 1, n
            do j = 1, i-1
                a(i,j) = 0.0D+00
            end do
        end do
    end subroutine r8po_fa

end module simple_rnd