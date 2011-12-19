!==Module simple_math
!
! simple_math contains mathematical subroutines and functions divided into different categories. The code is !distributed with the hope
! that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund, 2009-05-12.
! 
!==Changes are documented below
!* merged with calc_linalg, replaced matrix routines with intrinsic routines to get rid of lapack, needs debugging, HE 2009-05-13
!* debugged, documented, restructured, HE 2009-05-26 
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!* added a few statistical routines for the cross-entropy optimization, HE 2009-07-06
!* added subroutine get_fourier_shell for getting the indices of all comps in a given shell
!
module simple_math
use simple_def_precision
use simple_syscalls
use simple_jiffys
use simple_rnd
implicit none

interface taperedge
    module procedure taperedge_1
    module procedure taperedge_2
    module procedure taperedge_3
end interface

interface cosedge
    module procedure cosedge_1
    module procedure cosedge_2
end interface

interface hardedge
    module procedure hardedge_1
    module procedure hardedge_2
end interface

interface sincwin
    module procedure sincwin_1
    module procedure sincwin_2
end interface

interface gauwin
    module procedure gauwin_1
    module procedure gauwin_2
    module procedure gauwin_3
end interface

interface bmanwin
    module procedure bmanwin_1
    module procedure bmanwin_2
end interface

interface find
    module procedure find_1
    module procedure find_2
    module procedure find_3
end interface

interface locate
    module procedure locate_1
    module procedure locate_2
    module procedure locate_3
end interface

interface selec
    module procedure selec_1
    module procedure selec_2
    module procedure selec_3
end interface

interface hpsort
    module procedure hpsort_1
    module procedure hpsort_2
    module procedure hpsort_3
    module procedure hpsort_4
end interface

type p_i
    integer, pointer :: p=>null()
end type p_i

contains

    ! jiffys
    
    function find_pixvol( smpd, MWkDa ) result( npix )
        real, intent(in)    :: smpd, MWkDa
        real(DP)            :: Da_per_mL, pix_per_mL, prot_d2
        integer             :: npix
        real(DP), parameter :: PROT_D = 1.43d0            ! g/mL
        real(DP), parameter :: ONE_DA = 1.66053892173e-27 ! kg
        Da_per_mL = (PROT_D*1e-3)/ONE_DA
        pix_per_mL = ((1e-2)**3)/((smpd*1e-10)**3)
        prot_d2 = Da_per_mL/pix_per_mL ! protein density in Da per pixel
        npix = nint(MWkDa*1000.d0/prot_d2)
    end function find_pixvol
    
    function dsum( vec, filter ) result( s )
        real(double), intent(in)      :: vec(:)
        logical, intent(in), optional :: filter(:)
        real(double) :: s
        integer      :: i
        s = 0.d0
        if(present(filter))then
            do i=1,size(vec)
                if(filter(i)) s = s+vec(i)
            end do
        else
            do i=1,size(vec)
                s = s+vec(i)
            end do
        endif
    end function dsum

    function deg2rad( deg ) result( rad )
    ! converts between radians and degrees
        real, intent(in) :: deg
        real             :: rad
        rad = (deg/180.)*pi
    end function deg2rad

    function rad2deg( rad ) result( deg )
    ! converts from radians to degrees
        real, intent(in) :: rad
        real             :: deg
        deg = (rad/pi)*180.
    end function rad2deg
    
    function even( val ) result( ev )
        real, intent(in) :: val
        integer :: ev, rounded, remainer
        rounded = nint(val)
        remainer = val-real(rounded)
        if( mod(rounded,2) == 0 )then
            ev = rounded
        else
            if( remainer > 0. )then
                ev = rounded+1
            else
                ev = rounded-1
            endif
        endif
    end function even
        
    function get_angres( res, diam ) result( ang )
    ! get the angular resultion in degrees, given diameter and resolution
        real, intent(in)  :: res, diam 
        real :: ang
        ang = rad2deg((2.*res)/diam)
    end function get_angres
    
     function is_a_number( number ) result( is )
    ! validity check of real number (so that it is not NaN)
        real, intent(in) :: number
        logical          :: is       
        if( number == 0. .or. (number > 0. .or. number < 0.) )then ! number is a number
            is = .true.
        else ! number is NaN
            is = .false.
        endif   
    end function is_a_number
    
    subroutine pgroup_to_lim(pgroup, p1, p2, t1, t2, csym )
    ! converts string descriptors of c and d pointgroups to Euler angle limits
        character(len=*), intent(in) :: pgroup
        integer, intent(out)         :: csym
        real, intent(out)            :: t1, t2, p1, p2
        if( pgroup(1:1) .eq. 'c' )then
            t1     = 0.
            t2     = 180.
        else if( pgroup(1:1) .eq. 'd' )then
            t1     = 0.
            t2     = 90.
        else
            write(*,*) 'ERROR, presently only c and d symmetries are supported!'
            write(*,*) 'In: pgroup_to_lim, module: simple_math.f90'
            stop
        endif
        read(pgroup(2:),'(I2)') csym
        p1 = 0.
        p2 = 359.9999/real(csym)
    end subroutine pgroup_to_lim
    
    function sgn( nr ) result( s )
        integer, intent(in) :: nr
        integer             :: s
        s = 0
        if( nr < 0 ) s = -1
        if( nr > 0 ) s = 1
    end function sgn

    ! useful mathematical functions
   
    function myacos( arg ) result( r )
    ! returns acos with the argument's absolute value limited to 1. 
    ! This seems to be necessary due to small numerical inaccuracies.
        real, intent(in) :: arg
        real             :: r, x, y
        x = min(1.,abs(arg))
        y = sign(x,arg)
        r = acos(y)
    end function myacos

    function easoms( vec, D )result( r )
    ! is a unimoidal test-function, where the global minimum has a small area 
    ! with respect to the search space. The global minimum is _f_(_pi_,_pi_) = _-1_ 
    ! and a suitable search range is [_-100_,_100_] for both dimensions.
        integer, intent(in) :: D ! D should be = 2
        real, intent(in)    :: vec(D)
        real :: r
        r = -1.*cos(vec(1))*cos(vec(2))*exp(-1.*((vec(1)-pi)**2+(vec(2)-pi)**2 ))
    end function easoms

    function goldstein_price( vec, D )result( r )
    ! is a global optimization test-function where the global minimum is f(0,-1) = 3
    ! and a suitable search range is [_-2_,_2_] for both dimensions
        integer, intent(in) :: D ! D should be = 2
        real, intent(in)    :: vec(D)
        real :: r
        r = (1.+(vec(1)+vec(2)+1)**2.*(19.-14.*vec(1)+&
        3.*vec(1)**2.-14.*vec(2)+6.*vec(1)*vec(2)+3.*vec(2)**2.))&
        *(30.+(2.*vec(1)-3.*vec(2))**2.*(18.-32.*vec(1)+12.*vec(1)**2.+&
        48*vec(2)-36.*vec(1)*vec(2)+27.*vec(2)**2.))
    end function goldstein_price

    function ce_testfun( vec, D ) result( r )
    ! is the test function used by Kroese et al "The Cross-Entropy Method for Continuous Multi-
    ! Extremal Optimization" Methodol Comput Appl Probab (2006) 8:383-407. The function has a local
    ! maximum at point -2.00 (approximately) and a global maximum at 2.00.
        integer, intent(in) :: D ! D should be = 1
        real, intent(in)    :: vec(D)
        real :: r
        r = exp(-1*(vec(1)-2)**2)+0.8*exp(-1*(vec(1)+2)**2)
    end function ce_testfun
    
    ! Complex stuff 
   
    function cdiv( a, b ) result( z )
    ! is for complex division, from numerical recepies
        complex, intent(in)  :: a, b
        complex :: z
        real    :: r, den
        if( abs(real(b)) >= abs(aimag(b)) ) then
            r   = aimag(b)/real(b)
            den = real(b)+r*aimag(b)
            z   = cmplx((real(a)+r*aimag(a))/den,(aimag(a)-r*real(a))/den)
        else
            r   = real(b)/aimag(b)
            den = aimag(b)+r*real(b)
            z   = cmplx((real(a)*r+aimag(a))/den,(aimag(a)*r-real(a))/den)
        endif
    end function cdiv
    
    function cmul( a, b ) result( z )
    ! is for complex multiplication, from numerical recepies
        complex, intent(in)  :: a, b
        complex :: z
        z = cmplx(real(a)*real(b)-aimag(a)*aimag(b),aimag(a)*real(b)+real(a)*aimag(b))
    end function cmul
    
    function csqsum( a ) result( sq )
    ! is for complex squaresum
        complex, intent(in) :: a
        real :: sq, x, y, frac
        x = abs(real(a))
        y = abs(aimag(a))
        if( x == 0. ) then
            sq = y*y
        else if( y == 0. ) then
            sq = x*x
        else if( x > y ) then
            frac = y/x
            sq = x*x*(1.+frac*frac)
        else
            frac = x/y
            sq = y*y*(1.+frac*frac)
        endif
    end function csqsum
    
    function mycabs( a ) result( myabs )
    ! is for calculating complex arg/abs/modulus, from numerical recepies
        complex, intent(in) :: a
        real                :: myabs, x, y, frac
        x = abs(real(a))
        y = abs(aimag(a))
        if( x == 0. ) then
            myabs = y
        else if( y == 0. ) then
            myabs = x
        else if( x > y ) then
            frac = y/x
            myabs = x*sqrt(1.+frac*frac)
        else
            frac = x/y
            myabs = y*sqrt(1.+frac*frac)
        endif
    end function mycabs
    
    ! interpolation windows
    
    subroutine recwin_1d( x, xdim, winsz, xstart, xstop )
        real, intent(in)     :: x             ! input point
        integer, intent(in)  :: xdim          ! Fourier dim
        integer, intent(in)  :: winsz       ! size of window
        integer, intent(out) :: xstart, xstop ! start, stop
        xstart = max(-xdim,floor(x-real(winsz)))
        xstop  = min(xdim,ceiling(x+real(winsz)))
    end subroutine recwin_1d
    
    subroutine recwin_2d( x, y, xdim, winsz, xstart, xstop, ystart, ystop )
        real, intent(in)     :: x, y                         ! input point
        integer, intent(in)  :: xdim                         ! Fourier dim
        integer, intent(in)  :: winsz                      ! size of window
        integer, intent(out) :: xstart, xstop, ystart, ystop ! starts & stops
        call recwin_1d( x, xdim, winsz, xstart, xstop )
        call recwin_1d( y, xdim,  winsz, ystart, ystop )
    end subroutine recwin_2d
    
    subroutine recwin_3d( x, y, z, xdim, winsz, xstart, xstop, ystart, ystop, zstart, zstop )
        real, intent(in)     :: x, y, z         ! input point
        integer, intent(in)  :: xdim            ! Fourier dim
        integer, intent(in)  :: winsz         ! size of window
        integer, intent(out) :: xstart, xstop, ystart, ystop, zstart, zstop ! starts & stops
        call recwin_1d( x, xdim, winsz, xstart, xstop )
        call recwin_1d( y, xdim, winsz, ystart, ystop )
        call recwin_1d( z, xdim, winsz, zstart, zstop )
    end subroutine recwin_3d

    function sinc( x ) result( r )
    ! sinc function
        real, intent(in) :: x
        real             :: r, arg
        if( abs(x) < 0.00000001 ) then
            r = 1.
        else
            arg = pi*x
            r = sin(arg)/(arg)
        endif
    end function sinc
    
    subroutine sincwin_1( winsz, w )
    ! sinc window, choice '1'
        integer, intent(in) :: winsz
        real, intent(out)   :: w(-winsz:winsz)
        integer             :: i
        do i=0,winsz
            w(i) = sinc(real(i))
            if( i /= 0) w(-i) = w(i)
        end do
    end subroutine sincwin_1
    
    subroutine sincwin_2( winsz, w2 )
    ! sinc window, choice '1'
        integer, intent(in) :: winsz
        real, intent(out)   :: w2(-winsz:winsz,-winsz:winsz)
        real                :: w(-winsz:winsz)
        integer             :: i, j
        ! Make a one dimensional window
        call sincwin_1(winsz, w)
        ! Extend to two dimensions
        do i=-winsz,winsz
            do j=-winsz,winsz
                w2(i,j) = w(i)*w(j)
            end do
        end do
    end subroutine sincwin_2
    
    function gauwfun( x, winsz, alpha ) result( w )
    ! Gaussian window function, choice '2'
    ! to compensate for the finite extent of the interpolation window
    ! slightly softer than the Blackman window (alpha=0.5)
        real, intent(in)    :: x
        integer, intent(in) :: winsz
        real, intent(in)    :: alpha
        real                :: var, w
        var = alpha*real(winsz)
        w = 2.**(-(real(x)/var)**2.)
    end function gauwfun

    subroutine gauwin_1( winsz, alpha, w )
    ! gauwin window, choice '2
        integer, intent(in) :: winsz
        real, intent(in)    :: alpha
        real, intent(out)   :: w(-winsz:winsz)
        integer             :: i
        do i=0,winsz
            w(i) = gauwfun( real(i), winsz, alpha )
            if( i /= 0) w(-i) = w(i)
        end do
    end subroutine gauwin_1
    
    subroutine gauwin_2( winsz, alpha, w2 )
    ! gauwin window, choice '2'
        integer, intent(in) :: winsz
        real, intent(in)    :: alpha
        real, intent(out)   :: w2(-winsz:winsz,-winsz:winsz)
        real                :: w(-winsz:winsz)
        integer             :: i, j
        ! Make a one dimensional window
        call gauwin_1(winsz, alpha, w)
        ! Extend to two dimensions
        do i=-winsz,winsz
            do j=-winsz,winsz
                w2(i,j) = w(i)*w(j)
            end do
        end do
    end subroutine gauwin_2

    subroutine gauwin_3( winsz, alpha, w3 )
    ! gauwin window, choice '2'
        integer, intent(in) :: winsz
        real, intent(in)    :: alpha
        real, intent(out)   :: w3(-winsz:winsz,-winsz:winsz,-winsz:winsz)
        real                :: w(-winsz:winsz)
        integer             :: i, j, k
        ! Make a one dimensional window
        call gauwin_1(winsz, alpha, w)
        ! Extend to three dimensions
        do i=-winsz,winsz
            do j=-winsz,winsz
                do k=-winsz,winsz
                    w3(i,j,k) = w(i)*w(j)*w(k)
                end do
            end do
        end do
    end subroutine gauwin_3
    
    function bmanwfun( x, winsz ) result( w )
    ! Blackman window function, choice '3'
    ! to compensate for the finite extent of the interpolation window
    ! slightly harder than the gaussian kernel
        real, intent(in)    :: x
        integer, intent(in) :: winsz
        real                :: arg, w
        arg = (pi*x)/real(winsz)
        w = 0.42+0.5*cos(arg)+0.08*cos(2.*arg)
    end function bmanwfun
    
    subroutine bmanwin_1( winsz, w )
    ! Blackman window, choice '3'
        integer, intent(in) :: winsz
        real, intent(out)   :: w(-winsz:winsz)
        integer             :: i
        do i=0,winsz
            w(i) = bmanwfun(real(i), winsz)
            if( i /= 0) w(-i) = w(i)
        end do
    end subroutine bmanwin_1
    
    subroutine bmanwin_2( winsz, w2 )
    ! gauwin window, choice '3'
        integer, intent(in) :: winsz
        real, intent(out)   :: w2(-winsz:winsz,-winsz:winsz)
        real                :: w(-winsz:winsz)
        integer             :: i, j
        ! Make a one dimensional window
        call bmanwin_1(winsz, w)
        ! Extend to two dimensions
        do i=-winsz,winsz
            do j=-winsz,winsz
                w2(i,j) = w(i)*w(j)
            end do
        end do
    end subroutine bmanwin_2

    ! Edge functions
    
    function hardedge_1( x, y, mskrad ) result( w )
        real,intent(in) :: x, y, mskrad
        real :: w
        if( sqrt(x**2.+y**2.) > mskrad )then
            w = 0.
        else
            w = 1.
        endif
    end function hardedge_1
    
    function hardedge_2( x, y, z, mskrad ) result( w )
        real,intent(in) :: x, y, z, mskrad
        real :: w
        if( sqrt(x**2.+y**2.+z**2.) > mskrad )then
            w = 0.
        else
            w = 1.
        endif
    end function hardedge_2
    
    function cosedge_1( x, y, mskrad, width ) result( w )
        real, intent(in) :: x, y, mskrad, width
        real :: w, arg, pos, halfwidth
        halfwidth = width/2
        pos = sqrt(x**2.+y**2.)
        if( pos > mskrad+halfwidth )then
            w = 0.
        else
            arg = max(0.,min(halfwidth,pos-mskrad))
            w = cos((pi/2)*(1./halfwidth)*arg)
        endif
    end function cosedge_1
    
    function cosedge_2( x, y, z, mskrad, width ) result( w )
        real, intent(in) :: x, y, z, mskrad, width
        real :: w, arg, pos, halfwidth
        halfwidth = width/2
        pos = sqrt(x**2.+y**2.+z**2.)
        if( pos > mskrad+halfwidth )then
            w = 0.
        else
            arg = max(0.,min(halfwidth,pos-mskrad))
            w = cos((pi/2)*(1./halfwidth)*arg)
        endif
    end function cosedge_2
    
    function taperedge_1( dstep, h, lplim, width ) result( w )
        real, intent(in) :: dstep, lplim, width
        integer, intent(in) :: h
        real :: w, dpix, arg, halfwidth
        halfwidth = width/2
        dpix = sqrt(real(h)**2)-dstep/lplim
        arg = max(0.,min(halfwidth,dpix))
        w = max(0.,cos((pi/2)*(1./halfwidth)*arg))
    end function taperedge_1
    
    function taperedge_2( dstep, h, k, lplim, width ) result( w )
        real, intent(in) :: dstep, lplim, width
        integer, intent(in) :: h, k
        real :: w, dpix, arg, halfwidth
        halfwidth = width/2
        dpix = sqrt(real(h)**2.+real(k)**2.)-dstep/lplim
        arg = max(0.,min(halfwidth,dpix))
        w = max(0.,cos((pi/2)*(1./halfwidth)*arg))
    end function taperedge_2
    
    function taperedge_3( dstep, h, k, l, lplim, width ) result( w )
        real, intent(in) :: dstep, lplim, width
        integer, intent(in) :: h, k, l
        real :: w, dpix, arg, halfwidth
        halfwidth = width/2
        dpix = sqrt(real(h)**2.+real(k)**2.+real(l)**2.)-dstep/lplim
        arg = max(0.,min(halfwidth,dpix))
        w = max(0.,cos((pi/2)*(1./halfwidth)*arg))
    end function taperedge_3
    
    ! Fourier stuff
    
    subroutine origshift( xdim, x, y, dx, dy, comp )
    ! returns the real and imaginary parts of the phase shift at point (_x_,_y_) in a Fourier
    ! transform caused by the origin shift (_dx_,_dy_), i.e. _exp_(_pi_/_xdim_*(_dx_*_x_+_dy_*_y_)
        integer, intent(in)  :: xdim
        real, intent(in)     :: x, y, dx, dy
        complex, intent(out) :: comp
        comp = cmplx(cos((pi/real(xdim))*(dx*x+dy*y)),sin((pi/real(xdim))*(dx*x+dy*y)))
    end subroutine origshift
    
    function extr_fcomp( cmat, xdim, winsz, wchoice, h, k, mat ) result( comp )
    ! is for interpolation of a Fourier component at arbitrary rotation (mat)
        integer, intent(in) :: xdim, winsz, wchoice
        complex, intent(in) :: cmat(-xdim:xdim,-xdim:xdim)
        integer, intent(in) :: h, k
        real, intent(in)    :: mat(2,2)
        complex             :: comp
        integer             :: i, j, istart, istop, jstart, jstop
        real                :: tmp, vec(2), loc(2)
        vec(1) = real(h)
        vec(2) = real(k)
        loc = matmul(vec,mat)
        comp = cmplx(0.,0.)
        ! make window
        call recwin_2d(loc(1), loc(2), xdim, winsz, istart, istop, jstart, jstop)
        ! interpolate
        do i=istart,istop
            do j=jstart,jstop
                if( wchoice == 1 )then
                    tmp = sinc(loc(1)-real(i))*sinc(loc(2)-real(j))
                else
                    tmp = sinc(loc(1)-real(i))*sinc(loc(2)-real(j))*&
                    gauwfun(loc(1)-real(i),winsz,0.5)*gauwfun(loc(2)-real(j),winsz,0.5)
                endif
                comp = comp+cmplx(real(cmat(i,j))*tmp,aimag(cmat(i,j))*tmp)
            end do
        end do
    end function extr_fcomp
    
    subroutine grid_fcomp( cmat_in, xdim, winsz, wchoice, h, k, mat, cmat_grid, kernel )
    ! grids a plane to the 2D reference
        integer, intent(in)    :: xdim, winsz, wchoice
        complex, intent(in)    :: cmat_in(-xdim:xdim,-xdim:xdim)
        integer, intent(in)    :: h, k
        real, intent(in)       :: mat(2,2)
        complex, intent(inout) :: cmat_grid(-xdim:xdim,-xdim:xdim)
        real, intent(inout)    :: kernel(-xdim:xdim,-xdim:xdim)
        integer                :: i, j, istart, istop, jstart, jstop
        real                   :: tmp, vec(2), loc(2)
        vec(1) = real(h)
        vec(2) = real(k)
        loc = matmul(vec,mat)
        ! make window
        call recwin_2d(loc(1), loc(2), xdim, winsz, istart, istop, jstart, jstop)
        ! interpolate
        do i=istart,istop
            do j=jstart,jstop
                 if( wchoice == 1 )then
                    tmp = sinc(real(i)-loc(1))*sinc(real(j)-loc(2))
                else
                    tmp = sinc(loc(1)-real(i))*sinc(loc(2)-real(j))*&
                    gauwfun(real(i)-loc(1),winsz,0.5)*gauwfun(real(j)-loc(2),winsz,0.5)
                endif
                ! grid the Fourier data
                cmat_grid(i,j) = cmat_grid(i,j)+cmplx(real(cmat_in(h,k))*tmp,aimag(cmat_in(h,k))*tmp)
                ! grid the kernel
                kernel(i,j) = kernel(i,j)+tmp
            end do
        end do
    end subroutine grid_fcomp
    
    subroutine get_fourier_shell( shell, indices )
    ! is for getting the indices of one fourier shell, shell 0 is the central spot
    ! and the total number of components in one shell is 8*shell
        integer, intent(in) :: shell
        integer, intent(out), dimension(shell*8,2) :: indices
        integer :: i, counter
        counter = 0
        if( shell == 0 )then
            indices = 0
        else     
            do i=-shell,shell
                counter = counter+1
                indices(counter,1) = -shell
                indices(counter,2) = i
                counter = counter+1
                indices(counter,1) = shell
                indices(counter,2) = i
            end do 
            do i=-shell+1,shell-1
                counter = counter+1
                indices(counter,1) = i
                indices(counter,2) = shell
                counter = counter+1
                indices(counter,1) = i
                indices(counter,2) = -shell
            end do
        endif
    end subroutine get_fourier_shell
    
    subroutine get_fourier_partshell( shell, indices )
    ! is for getting the indices of a quarter fourier shell, shell 0 is the central spot
    ! and the total number of components in one quarter shell is shell*2+1
        integer, intent(in) :: shell
        integer, intent(out), dimension(shell*2+1,2) :: indices ! (1)h (2)k
        integer :: h, k, counter
        counter = 0
        if( shell == 0 )then
            indices = 0
        else
            do k=0,shell
                counter = counter+1
                indices(counter,1) = shell
                indices(counter,2) = k
            end do
            do h=0,shell-1
                counter = counter+1
                indices(counter,2) = shell
                indices(counter,1) = h
            end do
        endif
    end subroutine get_fourier_partshell
    
    ! linear algebra routines
    
    SUBROUTINE matinv(matrix, inverse, n, errflg)
    ! Subroutine to find the inverse of a square matrix
    ! Author : Louisda16th a.k.a Ashwith J. Rego
    ! Reference : Algorithm explained at:
    ! http://math.uww.edu/~mcfarlat/inverse.htm           
    ! http://www.tutor.ms.unimelb.edu.au/matrix/matrix_inverse.html
        INTEGER, INTENT(IN) :: n
        INTEGER, INTENT(OUT) :: errflg  !Return error status. -1 for error, 0 for normal
        REAL, INTENT(IN), DIMENSION(n,n) :: matrix  !Input matrix
        REAL, INTENT(OUT), DIMENSION(n,n) :: inverse !Inverted matrix
        LOGICAL :: FLAG = .TRUE.
        INTEGER :: i, j, k
        REAL :: m
        REAL, DIMENSION(n,2*n) :: augmatrix !augmented matrix
        ! Augment input matrix with an identity matrix
        DO i=1,n
            DO j=1,2*n
                IF(j <= n )THEN
                    augmatrix(i,j) = matrix(i,j)
                ELSE IF((i+n) == j)THEN
                    augmatrix(i,j) = 1
                ELSE
                    augmatrix(i,j) = 0
                ENDIF
            END DO
        END DO   
        ! Reduce augmented matrix to upper traingular form
        DO k=1,n-1
            IF(augmatrix(k,k) == 0)THEN
                FLAG = .FALSE.
                DO i=k+1,n
                    IF(augmatrix(i,k) /= 0)THEN
                        DO j=1,2*n
                            augmatrix(k,j) = augmatrix(k,j)+augmatrix(i,j)
                        END DO
                        FLAG = .TRUE.
                        EXIT
                    ENDIF
                    IF(FLAG .EQV. .FALSE.)THEN
                        inverse = 0
                        errflg = -1
                        RETURN
                    ENDIF
                END DO
            ENDIF
            DO j=k+1, n                       
                m = augmatrix(j,k)/augmatrix(k,k)
                DO i=k,2*n
                    augmatrix(j,i) = augmatrix(j,i)-m*augmatrix(k,i)
                END DO
            END DO
        END DO
        !Test for invertibility
        DO i=1,n
            IF(augmatrix(i,i) == 0)THEN
                inverse = 0
                errflg = -1
                RETURN
            ENDIF
        END DO  
        !Make diagonal elements as 1
        DO i=1,n
            m = augmatrix(i,i)
            DO j=i,2*n                               
                augmatrix(i,j) = augmatrix(i,j)/m
            END DO
        END DO  
        !Reduced right side half of augmented matrix to identity matrix
        DO k=n-1,1,-1
            DO i=1,k
                m = augmatrix(i,k+1)
                DO j = k,2*n
                    augmatrix(i,j) = augmatrix(i,j)-augmatrix(k+1,j)*m
                END DO
            END DO
        END DO                                  
        ! Store answer
        DO i=1,n
            DO j=1,n
                inverse(i,j) = augmatrix(i,j+n)
            END DO
        END DO
        errflg = 0
    END SUBROUTINE matinv 
        
    function tr( matrix, n ) result( sum )
        integer, intent(in) :: n
        real, intent(in), dimension(n,n) :: matrix
        real :: sum
        integer :: i
        sum = 0.
        do i=1,n
            sum = sum+matrix(i,i)
        end do
    end function tr
    
    function det( matrix, n ) result( d )
        integer               :: n, j
        real, dimension(n,n)  :: matrix
        integer, dimension(n) :: indx(n)
        real                  :: d
        logical               :: err
        call ludcmp(matrix,n,n,indx,d,err)
        if( err )then
            d = 0.
            return
        endif
        do j=1,n
            d = d*matrix(j,j) ! this returns d as +-1
        end do
    end function det

    function diag( diagvals, n ) result( mat )
        integer, intent(in) :: n
        real, intent(in)    :: diagvals(n)
        real :: mat(n,n)
        integer :: i
        mat = 0.
        do i=1,n
            mat(i,i) = diagvals(i)
        end do
    end function diag 
    
    SUBROUTINE LUDCMP(A,N,NP,INDX,D,err)
    ! LU DECOMPOSITION, NR
        INTEGER :: N,NP,INDX(N),NMAX
        REAL    :: D,A(NP,NP), TINY
        PARAMETER (NMAX=100,TINY=1.0E-20)
        INTEGER :: I,IMAX,J,K
        REAL    :: AAMAX,DUM,SUM,VV(NMAX)
        logical :: err
        err = .false.
        D=1.
        DO I=1,N
          AAMAX=0.
          DO J=1,N
            IF (ABS(A(I,J)).GT.AAMAX) AAMAX=ABS(A(I,J))
          END DO
          IF (AAMAX.EQ.0.)then
              err = .true.
              return
          endif
          VV(I)=1./AAMAX
        END DO
        DO J=1,N
          IF (J.GT.1) THEN
            DO I=1,J-1
              SUM=A(I,J)
              IF (I.GT.1)THEN
                DO K=1,I-1
                  SUM=SUM-A(I,K)*A(K,J)
                END DO
                A(I,J)=SUM
              ENDIF
            END DO
          ENDIF
          AAMAX=0.
          DO I=J,N
            SUM=A(I,J)
            IF (J.GT.1)THEN
              DO K=1,J-1
                SUM=SUM-A(I,K)*A(K,J)
              END DO
              A(I,J)=SUM
            ENDIF
            DUM=VV(I)*ABS(SUM)
            IF (DUM.GE.AAMAX) THEN
              IMAX=I
              AAMAX=DUM
            ENDIF
          END DO
          IF (J.NE.IMAX)THEN
            DO K=1,N
              DUM=A(IMAX,K)
              A(IMAX,K)=A(J,K)
              A(J,K)=DUM
            END DO
            D=-D
            VV(IMAX)=VV(J)
          ENDIF
          INDX(J)=IMAX
          IF(J.NE.N)THEN
            IF(A(J,J).EQ.0.) A(J,J)=TINY
            DUM=1./A(J,J)
            DO I=J+1,N
              A(I,J)=A(I,J)*DUM
          END DO
          ENDIF
        END DO
        IF(A(N,N).EQ.0.)A(N,N)=TINY
    END SUBROUTINE LUDCMP

    subroutine spiral_2d( np, trs, vecs )
        integer, intent(in) :: np
        real, intent(in)    :: trs
        real, intent(out)   :: vecs(np,2)
        real                :: angstep, ang, normstep, norm
        integer             :: i
        angstep  = 360./(real(np)/trs)
        normstep = trs/real(np)
        ang      = 0.
        norm     = 0.
        do i=1,np
            call get_radial_line( ang, vecs(i,:) )
            vecs(i,:) = norm*vecs(i,:)
            norm = norm+normstep
            ang  = ang+angstep
        end do
    end subroutine spiral_2d

    subroutine gen_origsh_pop( opop )
        real, intent(inout) :: opop(98,2)
        real :: yvec(1,2), vec(1,2), rmat(2,2), dang, ang
        integer :: i, cnt, sh
        yvec(1,1) = 0.
        yvec(1,2) = 1.
        cnt = 0
        do sh=1,5
            if( sh == 1 )then
                dang = 360./6.
                ang = 0.
                do i=1,6
                    rmat = rotmat2d(ang)
                    vec = matmul(yvec,rmat)
                    cnt = cnt+1
                    opop(cnt,1) = real(sh)*vec(1,1)
                    opop(cnt,2) = real(sh)*vec(1,2)
                    ang = ang+dang
                end do
            endif
            if( sh == 2 )then
                dang = 360./13.
                ang = 0.
                do i=1,13
                    rmat = rotmat2d(ang)
                    vec = matmul(yvec,rmat)
                    cnt = cnt+1
                    opop(cnt,1) = real(sh)*vec(1,1)
                    opop(cnt,2) = real(sh)*vec(1,2)
                    ang = ang+dang
                end do
            endif
            if( sh == 3 )then
                dang = 360./19.
                ang = 0.
                do i=1,19
                    rmat = rotmat2d(ang)
                    vec = matmul(yvec,rmat)
                    cnt = cnt+1
                    opop(cnt,1) = real(sh)*vec(1,1)
                    opop(cnt,2) = real(sh)*vec(1,2)
                    ang = ang+dang
                end do
            endif
            if( sh == 4 )then
                dang = 360./25.
                ang = 0.
                do i=1,25
                    rmat = rotmat2d(ang)
                    vec = matmul(yvec,rmat)
                    cnt = cnt+1
                    opop(cnt,1) = real(sh)*vec(1,1)
                    opop(cnt,2) = real(sh)*vec(1,2)
                    ang = ang+dang
                end do
            endif
            if( sh == 5 )then
                dang = 360./31.
                ang = 0.
                do i=1,31
                    rmat = rotmat2d(ang)
                    vec = matmul(yvec,rmat)
                    cnt = cnt+1
                    opop(cnt,1) = real(sh)*vec(1,1)
                    opop(cnt,2) = real(sh)*vec(1,2)  
                    ang = ang+dang
                end do
            endif
        end do
        opop(95,1) = -4.99
        opop(95,2) = 4.99
        opop(96,1) = 4.99
        opop(96,2) = 4.99
        opop(97,1) = 4.99
        opop(97,2) = -4.99
        opop(98,1) = -4.99
        opop(98,2) = -4.99   
    end subroutine gen_origsh_pop

    function min_hamming_dist( x, y, Np, N, L ) result( d )
    ! returns a distance measure btw a set of solution vectors _x_ and a single solution vector _y_. 
    ! Defined in Laguna et al. Hybridizing the CE method: "An application to the max-cut problem", 
    ! Computers & Operations Research 36 (2009) 487-498
        integer, intent(in) :: Np, N, L
        integer, intent(in) :: x(Np,N,L), y(N,L) ! x is the solution set and y is the single solution
        integer :: dists(Np), d, i
        do i=1,Np
            dists(i) = sum(abs(x(i,:,:)-y(:,:)))
        end do
        d = minval(dists)
    end function min_hamming_dist

    function euclid( vec1, vec2 ) result( dist )
    ! calculates the euclidean distance between two vectors of dimension _N_
        real, intent(in)    :: vec1(:), vec2(:)
        real                :: dist     
        dist = sqrt(sum((vec1-vec2)**2.))
    end function euclid
    
    function arg( vec ) result( length )
        real, intent(in) :: vec(:)
        real :: length
        length = sqrt(sum(vec**2.))
    end function arg
    
    subroutine normvec( vec )
        real, intent(inout) :: vec(:)
        real :: length
        length = arg(vec)
        vec = vec/length
    end subroutine normvec
    
    subroutine projz( vec3, vec2 )
    ! projects a 3D vector in the _z_-direction
        real, intent(in)  :: vec3(3)
        real, intent(out) :: vec2(2)
        vec2(1) = vec3(1)
        vec2(2) = vec3(2)
    end subroutine projz

    subroutine calc_common_line( normal_target, normal_reference, rtot_target,&
    rtot_reference, line_target, line_reference, foundline )
    ! calculates the 3D intersection between two planes defined by their normals 
    ! and maps the 3D intersection to the coordinate systems of the respective planes
        real, intent(in), dimension(3)   :: normal_target, normal_reference
        real, intent(in), dimension(3,3) :: rtot_target, rtot_reference
        real, intent(out), dimension(2)  :: line_target, line_reference
        logical, intent(out)             :: foundline
        real, dimension(3)               :: intsct, tmp1, tmpb1
        integer                          :: errflg
        real                             :: scalprod
        scalprod = dot_product(normal_target, normal_reference)
        if( scalprod > 0.99 ) then
            foundline = .false.
            return
        endif
        call planintersect( normal_target, normal_reference, intsct, errflg )
        if( errflg == 1 ) then
            foundline = .false.
            return
        endif
        ! intsct is the intersection in 3D, map to the
        ! respective coordinate systems
        ! first map onto the target
        tmp1 = matmul( rtot_target, intsct )
        call projz( tmp1, line_target )
        ! then map onto the reference:
        tmpb1 = matmul( rtot_reference, intsct )
        call projz( tmpb1, line_reference )
        foundline = .true.
    end subroutine calc_common_line
                           
    subroutine planintersect( lin1, lin2, comlin, error )
    ! calculates the intersection between two planes by calculating the 
    ! cross product between their normals.
        real, intent(in), dimension( 3 ) :: lin1, lin2
        real, intent(out), dimension( 3 ) :: comlin
        integer, intent(out) :: error
        real :: abscom
        comlin(1) = lin1(2)*lin2(3)-lin1(3)*lin2(2)
        comlin(2) = lin1(3)*lin2(1)-lin1(1)*lin2(3)
        comlin(3) = lin1(1)*lin2(2)-lin1(2)*lin2(1)
        abscom = sqrt(comlin(1)**2+comlin(2)**2+comlin(3)**2)
        if( abscom >= 0.0001 ) then
            comlin(1) = comlin(1)/abscom
            comlin(2) = comlin(2)/abscom
            comlin(3) = comlin(3)/abscom
            error = 0
        else
            ! identical planes give error
            error = 1
        endif
    end subroutine planintersect

    subroutine get_radial_line( ang, lin )
    ! calculates a 2D vector in the _xy_ plane rotated _ang_ degrees.
        real, intent(in) :: ang
        real, intent(out), dimension( 2 ) :: lin
        real, dimension( 3,3 ) :: T
        real, dimension( 3 ) :: u, v
        T = rotmat( ang, 3 )
        u(1) = 0.
        u(2) = 1.
        u(3) = 0.
        v = matmul( u, T )
        lin(1) = v(1)
        lin(2) = v(2)    
    end subroutine get_radial_line

    function euler2m( e1, e2, e3 ) result( r )
    ! makes a rotation matrix from a Spider format Euler triplet
        real, intent(in) :: e1, e2, e3
        real, dimension(3,3) :: r1, r2, r3, r, tmp
        r1 = rotmat( e1, 3 ) ! rotation around z
        r2 = rotmat( e2, 2 ) ! tilt
        r3 = rotmat( e3, 3 ) ! rotation around z
        ! order of multiplication is r3r2r1
        tmp  = matmul( r3,r2 )
        r    = matmul( tmp,r1 )
    end function euler2m

    function euler2vec( phi, theta, psi ) result( normal )
    ! calculates the normal of a Fourier plane in orientation _phi_, _theta_, _psi_
        real, intent( in ) :: phi, theta, psi
        real :: normal(3), mat(3,3), zvec(3)
        zvec(1)=0.
        zvec(2)=0.
        zvec(3)=1.  
        mat = euler2m( phi, theta, psi )
        normal = matmul( zvec,mat )
    end function euler2vec

    subroutine m2euler( mat, ceul1, ceul2, ceul3 )
    ! returns a Spider format Euler triplet, given a rotation matrix 
        real, intent(in), dimension( 3,3 ) :: mat
        real, intent(out) :: ceul3, ceul2, ceul1
        real, dimension( 3,3 ):: tmp, anticomp1z, anticomp2y, get3eul
        real :: zvec(3), imagevec(3), absxy, mceul1deg, mceul2deg, phitmp
        zvec(1)=0.0
        zvec(2)=0.0
        zvec(3)=1.0  
        ! get image of (0,0,1)
        imagevec = matmul( zvec, mat )
        ! extract eul1 from imagevec:
        absxy = sqrt(imagevec(1)**2+imagevec(2)**2)
        if(absxy < 0.0000001) then
            ceul1 = 0.
            ! normal parallel to z, phi undefined
        else
            phitmp = myacos( imagevec(1)/absxy )
            if (imagevec(2) >= 0.) then
                ceul1 = phitmp
            else
                ceul1 = -phitmp
            endif
        endif
        ! extract the theta
        ceul2 = myacos( imagevec(3) )
        ! setup the rotation matrices to retrieve the resulting psi angle:
        mceul1deg = rad2deg( -ceul1 )
        mceul2deg = rad2deg( -ceul2 )
        anticomp1z = rotmat( mceul1deg,3 )
        anticomp2y = rotmat( mceul2deg,2 )
        tmp = matmul( anticomp1z,anticomp2y  )        
        get3eul = matmul( mat,tmp )                    
        ! get3eul is a rotation around z, 1st element is cosangle
        if( get3eul( 1,2 ) > 0. ) then
            ceul3 = myacos( get3eul( 1,1 ) )
        else
            ceul3 = -myacos( get3eul( 1,1 ) )
        endif
        ceul3=rad2deg( ceul3 )
        ceul2=rad2deg( ceul2 )
        ceul1=rad2deg( ceul1 )
        do while( ceul3 < 0. )
            ceul3=ceul3+360.
        end do
        do while( ceul1 < 0. )
            ceul1=ceul1+360.
        end do
    end subroutine m2euler
    
    function rotmat( ang, choice ) result( r )
    ! returns the rotation matrix for _ang_ degrees of rotation 
    ! around x,y or z for _choice_ = _1_,_2_ or _3_
        real, dimension(3,3) :: r
        real, intent(in) :: ang
        integer, intent(in) :: choice
        real :: ang_in_rad
        ang_in_rad = ang*pi/180.
        if ( choice == 1 ) then
            r( 1,1 ) = 1.
            r( 1,2 ) = 0.
            r( 1,3 ) = 0.
            r( 2,1 ) = 0.
            r( 2,2 ) = cos( ang_in_rad )
            r( 2,3 ) =-sin( ang_in_rad )
            r( 3,1 ) = 0.
            r( 3,2 ) = sin( ang_in_rad )
            r( 3,3 ) = cos( ang_in_rad )
        elseif ( choice == 2 ) then
            r( 1,1 ) = cos( ang_in_rad )
            r( 1,2 ) = 0.
            r( 1,3 ) = -sin( ang_in_rad )
            r( 2,1 ) = 0.
            r( 2,2 ) = 1.
            r( 2,3 ) = 0.
            r( 3,1 ) = sin( ang_in_rad )
            r( 3,2 ) = 0.
            r( 3,3 ) = cos( ang_in_rad )
        elseif ( choice == 3 ) then
            r( 1,1 ) = cos( ang_in_rad )
            r( 1,2 ) = sin( ang_in_rad )
            r( 1,3 ) = 0.
            r( 2,1 ) = -sin( ang_in_rad )
            r( 2,2 ) = cos( ang_in_rad )
            r( 2,3 ) = 0.
            r( 3,1 ) = 0.
            r( 3,2 ) = 0.
            r( 3,3 ) = 1.
            ! beware of the signs:z-rot is really negative
        endif
    end function rotmat
    
    function rotmat2d( ang ) result( mat )
        real, intent(in) :: ang
        real :: mat(2,2), ang_in_rad
        ang_in_rad = ang*pi/180.
        mat(1,1) = cos(ang_in_rad)
        mat(1,2) = sin(ang_in_rad)
        mat(2,1) = -mat(1,2)
        mat(2,2) = mat(1,1)
    end function rotmat2d
    
    ! sorting
    
    subroutine hpsort_1( N, rarr, iarr )
    ! heapsort subroutine, from numerical recepies
        integer, intent(in)    :: N
        real, intent(inout)    :: rarr(N)
        integer, intent(inout) :: iarr(N)
        integer                :: i, ir, j, l, ia
        real                   :: ra    
        if( N < 2) return
        l  = N/2+1
        ir = N
        do
            if(l > 1)then
                l  = l-1
                ra = rarr(l)
                ia = iarr(l)
            else
                ra = rarr(ir)
                ia = iarr(ir)
                rarr(ir) = rarr(1)
                iarr(ir) = iarr(1)
                ir = ir-1
                if(ir == 1)then
                    rarr(1) = ra
                    iarr(1) = ia
                    return
                endif
            endif
            i = l
            j = l+l
            do while(j <= ir)
                if(j < ir) then
                    if(rarr(j) < rarr(j+1)) j = j+1
                endif
                if(ra < rarr(j))then
                    rarr(i) = rarr(j)
                    iarr(i) = iarr(j)
                    i = j
                    j = j+j
                else
                    j = ir+1
                endif
                rarr(i) = ra
                iarr(i) = ia
            end do
        end do
    end subroutine hpsort_1
    
    subroutine hpsort_2( N, rarr )
    ! heapsort subroutine, from numerical recepies
        integer, intent(in)    :: N
        real, intent(inout)    :: rarr(N)
        integer                :: i, ir, j, l
        real(double)           :: ra
        if( N < 2) return
        l  = N/2+1
        ir = N
        do
            if(l > 1)then
                l  = l-1
                ra = rarr(l)
            else
                ra = rarr(ir)
                rarr(ir) = rarr(1)
                ir = ir-1
                if(ir == 1)then
                    rarr(1) = ra
                    return
                endif
            endif
            i = l
            j = l+l
            do while(j <= ir)
                if(j < ir) then
                    if(rarr(j) < rarr(j+1)) j = j+1
                endif
                if(ra < rarr(j))then
                    rarr(i) = rarr(j)
                    i = j
                    j = j+j
                else
                    j = ir+1
                endif
                rarr(i) = ra
            end do
        end do
    end subroutine hpsort_2
    
    subroutine hpsort_3( N, iarr )
    ! heapsort subroutine, from numerical recepies
        integer, intent(in)    :: N
        integer, intent(inout) :: iarr(N)
        integer                :: i, ir, j, l, ra
        if( N < 2) return
        l  = N/2+1
        ir = N
        do
            if(l > 1)then
                l  = l-1
                ra = iarr(l)
            else
                ra = iarr(ir)
                iarr(ir) = iarr(1)
                ir = ir-1
                if(ir == 1)then
                    iarr(1) = ra
                    return
                endif
            endif
            i = l
            j = l+l
            do while(j <= ir)
                if(j < ir) then
                    if(iarr(j) < iarr(j+1)) j = j+1
                endif
                if(ra < iarr(j))then
                    iarr(i) = iarr(j)
                    i = j
                    j = j+j
                else
                    j = ir+1
                endif
                iarr(i) = ra
            end do
        end do
    end subroutine hpsort_3
    
    subroutine hpsort_4( N, iarr, p1_lt_p2 )
    ! heapsort subroutine, from numerical recepies
        integer, intent(in)    :: N
        integer, intent(inout) :: iarr(N)
        interface
            function p1_lt_p2( p1, p2 ) result( val )
                integer, intent(in) :: p1, p2
                logical :: val
            end function p1_lt_p2
        end interface
        integer                :: i, ir, j, l, ra
        if( N < 2) return
        l  = N/2+1
        ir = N
        do
            if(l > 1)then
                l  = l-1
                ra = iarr(l)
            else
                ra = iarr(ir)
                iarr(ir) = iarr(1)
                ir = ir-1
                if(ir == 1)then
                    iarr(1) = ra
                    return
                endif
            endif
            i = l
            j = l+l
            do while(j <= ir)
                if(j < ir) then
                    if(p1_lt_p2(iarr(j),iarr(j+1))) j = j+1
                endif
                if(p1_lt_p2(ra,iarr(j)))then
                    iarr(i) = iarr(j)
                    i = j
                    j = j+j
                else
                    j = ir+1
                endif
                iarr(i) = ra
            end do
        end do
    end subroutine hpsort_4  
        
    ! searching
        
    function locate_1( arr, n, x ) result( j )
    ! From numerical recepies. Given an array arr(1:n), and given value x, locate returns a value j
    ! such that x is between arr(j) and arr(j+1). arr(1:n) must be monotonic, either increasing or decreasing.
    ! j=0 or j=n is returned to indicate that x is out of range.
        integer, intent(in) :: n
        real, intent(in)    :: arr(n), x
        integer             :: jl, jm, ju, j
        jl = 0                ! initialize lower
        ju = n+1              ! and upper limits
        do while( ju-jl > 1 ) ! if we are not yet done
            jm = (ju+jl)/2    ! compute a midpoint
            if((arr(n) >= arr(1)).eqv.(x >= arr(jm))) then
                jl = jm       ! and replace either the lower limit
            else
                ju = jm       ! or the upper limit, as appropriate
            endif
        end do
        if( x == arr(1) )then
            j = 1
        else if( x == arr(n) )then
            j = n-1
        else
            j = jl
        endif     
    end function locate_1
    
    function locate_2( arr, n, x ) result( j )
    ! From numerical recepies. Given an array arr(1:n), and given value x, locate returns a value j
    ! such that x is between arr(j) and arr(j+1). arr(1:n) must be monotonic, either increasing or decreasing.
    ! j=0 or j=n is returned to indicate that x is out of range.
        integer, intent(in)      :: n
        real(double), intent(in) :: arr(n), x
        integer                  :: jl, jm, ju, j
        jl = 0                ! initialize lower
        ju = n+1              ! and upper limits
        do while( ju-jl > 1 ) ! if we are not yet done
            jm = (ju+jl)/2    ! compute a midpoint
            if((arr(n) >= arr(1)).eqv.(x >= arr(jm))) then
                jl = jm       ! and replace either the lower limit
            else
                ju = jm       ! or the upper limit, as appropriate
            endif
        end do
        if( x == arr(1) )then
            j = 1
        else if( x == arr(n) )then
            j = n-1
        else
            j = jl
        endif     
    end function locate_2
    
    function locate_3( arr, n, x ) result( j )
    ! From numerical recepies. Given an array arr(1:n), and given value x, locate returns a value j
    ! such that x is between arr(j) and arr(j+1). arr(1:n) must be monotonic, either increasing or decreasing.
    ! j=0 or j=n is returned to indicate that x is out of range.
        integer, intent(in) :: n
        integer, intent(in) :: arr(n), x
        integer             :: jl, jm, ju, j
        jl = 0                ! initialize lower
        ju = n+1              ! and upper limits
        do while( ju-jl > 1 ) ! if we are not yet done
            jm = (ju+jl)/2    ! compute a midpoint
            if((arr(n) >= arr(1)).eqv.(x >= arr(jm))) then
                jl = jm       ! and replace either the lower limit
            else
                ju = jm       ! or the upper limit, as appropriate
            endif
        end do
        if( x == arr(1) )then
            j = 1
        else if( x == arr(n) )then
            j = n-1
        else
            j = jl
        endif     
    end function locate_3
    
    subroutine find_1( arr, n, x, j, dist1 )
        integer, intent(in)  :: n
        real, intent(in)     :: arr(n), x
        real, intent(out)    :: dist1      
        integer, intent(out) :: j  
        real                 :: dist2
        j = max(1,locate_1( arr, n, x ))
        dist1 = arr(j)-x
        if( j < n ) then
            dist2 = arr(j+1)-x
            if( abs(dist1) >= abs(dist2) )then
                j = j+1
                dist1 = dist2
            endif
        endif
    end subroutine find_1
    
    subroutine find_2( arr, n, x, j, dist1 )
        integer, intent(in)       :: n
        real(double), intent(in)  :: arr(n), x
        real(double), intent(out) :: dist1      
        integer, intent(out)      :: j  
        real(double)              :: dist2
        j = max(1,locate_2( arr, n, x ))
        dist1 = arr(j)-x
        if( j < n ) then
            dist2 = arr(j+1)-x
            if( dabs(dist1) >= dabs(dist2) )then
                j = j+1
                dist1 = dist2
            endif
        endif
    end subroutine find_2
    
    subroutine find_3( arr, n, x, j, dist1 )
        integer, intent(in)  :: n
        integer, intent(in)  :: arr(n), x
        integer, intent(out) :: dist1      
        integer, intent(out) :: j  
        integer              :: dist2
        j = max(1,locate_3( arr, n, x ))
        dist1 = arr(j)-x
        if( j < n ) then
            dist2 = arr(j+1)-x
            if( abs(dist1) >= abs(dist2) )then
                j = j+1
                dist1 = dist2
            endif
        endif
    end subroutine find_3
    
    real function selec_1(k,n,arr)
      integer k,n
      real arr(n)
      integer i,ir,j,l,mid
      real a,temp
      l = 1
      ir = n
 2    if (ir-l.le.1) then
         if (ir-1.eq.1) then
            if (arr(ir).lt.arr(l)) then
               temp = arr(l)
               arr(l) = arr(ir)
               arr(ir) = temp
            endif
         endif
         selec_1 = arr(k)
         return
      else
         mid = (l+ir)/2
         temp = arr(mid)
         arr(mid) = arr(l+1)
         arr(l+1) = temp
         if (arr(l).gt.arr(ir)) then
            temp = arr(l)
            arr(l) = arr(ir)
            arr(ir) = temp
         endif
         if (arr(l+1).gt.arr(ir)) then
            temp = arr(l+1)
            arr(l+1) = arr(ir)
            arr(ir) = temp
         endif
         if (arr(l).gt.arr(l+1)) then
            temp = arr(l)
            arr(l) = arr(l+1)
            arr(l+1) = temp
         endif
         i = l+1
         j = ir
         a = arr(l+1)
 3       continue
         i = i+1
         if (arr(i).lt.a) goto 3
 4       continue
         j = j-1
         if (arr(j).gt.a) goto 4
         if (j.lt.i) goto 5
         temp = arr(i)
         arr(i) = arr(j)
         arr(j) = temp
         goto 3
 5       arr(l+1) = arr(j)
         arr(j) = a
         if (j.ge.k) ir = j-1
         if (j.le.k) l = i
      endif
      goto 2
    end function selec_1
    
    real(double) function selec_2(k,n,arr)
      integer k,n
      real(double) arr(n)
      integer i,ir,j,l,mid
      real(double) a,temp
      l = 1
      ir = n
 2    if (ir-l.le.1) then
         if (ir-1.eq.1) then
            if (arr(ir).lt.arr(l)) then
               temp = arr(l)
               arr(l) = arr(ir)
               arr(ir) = temp
            endif
         endif
         selec_2 = arr(k)
         return
      else
         mid = (l+ir)/2
         temp = arr(mid)
         arr(mid) = arr(l+1)
         arr(l+1) = temp
         if (arr(l).gt.arr(ir)) then
            temp = arr(l)
            arr(l) = arr(ir)
            arr(ir) = temp
         endif
         if (arr(l+1).gt.arr(ir)) then
            temp = arr(l+1)
            arr(l+1) = arr(ir)
            arr(ir) = temp
         endif
         if (arr(l).gt.arr(l+1)) then
            temp = arr(l)
            arr(l) = arr(l+1)
            arr(l+1) = temp
         endif
         i = l+1
         j = ir
         a = arr(l+1)
 3       continue
         i = i+1
         if (arr(i).lt.a) goto 3
 4       continue
         j = j-1
         if (arr(j).gt.a) goto 4
         if (j.lt.i) goto 5
         temp = arr(i)
         arr(i) = arr(j)
         arr(j) = temp
         goto 3
 5       arr(l+1) = arr(j)
         arr(j) = a
         if (j.ge.k) ir = j-1
         if (j.le.k) l = i
      endif
      goto 2
    end function selec_2
    
    integer function selec_3(k,n,arr)
      integer :: k,n
      integer :: arr(n)
      integer :: i,ir,j,l,mid
      integer ::  a,temp
      l = 1
      ir = n
 2    if (ir-l.le.1) then
         if (ir-1.eq.1) then
            if (arr(ir).lt.arr(l)) then
               temp = arr(l)
               arr(l) = arr(ir)
               arr(ir) = temp
            endif
         endif
         selec_3 = arr(k)
         return
      else
         mid = (l+ir)/2
         temp = arr(mid)
         arr(mid) = arr(l+1)
         arr(l+1) = temp
         if (arr(l).gt.arr(ir)) then
            temp = arr(l)
            arr(l) = arr(ir)
            arr(ir) = temp
         endif
         if (arr(l+1).gt.arr(ir)) then
            temp = arr(l+1)
            arr(l+1) = arr(ir)
            arr(ir) = temp
         endif
         if (arr(l).gt.arr(l+1)) then
            temp = arr(l)
            arr(l) = arr(l+1)
            arr(l+1) = temp
         endif
         i = l+1
         j = ir
         a = arr(l+1)
 3       continue
         i = i+1
         if (arr(i).lt.a) goto 3
 4       continue
         j = j-1
         if (arr(j).gt.a) goto 4
         if (j.lt.i) goto 5
         temp = arr(i)
         arr(i) = arr(j)
         arr(j) = temp
         goto 3
 5       arr(l+1) = arr(j)
         arr(j) = a
         if (j.ge.k) ir = j-1
         if (j.le.k) l = i
      endif
      goto 2
    end function selec_3
    
    ! silly stuff

    subroutine reverse_iarr( iarr )
    !is for reversing an integer array
        integer, intent(inout) :: iarr(:)
        integer                :: i, j, iswap, sz, en
        sz = size(iarr,1)
        if( sz < 2 )then
            return
        endif
        if( mod(sz,2) == 0 )then
            en = sz/2+1
        else
            en = sz/2+2
        endif
        j = 0
        do i = sz,en,-1
            j = j+1
            iswap   = iarr(j)
            iarr(j) = iarr(i)
            iarr(i) = iswap 
        end do
    end subroutine reverse_iarr

    subroutine reverse_rarr( rarr )
    !is for reversing a real array
        real, intent(inout) :: rarr(:)
        integer             :: i, j, sz, en
        real                :: rswap
        sz = size(rarr,1)
        if( sz < 2 )then
            return
        endif
        if( mod(sz,2) == 0 )then
            en = sz/2+1
        else
            en = sz/2+2
        endif
        j = 0
        do i = sz,en,-1
            j = j+1
            rswap   = rarr(j)
            rarr(j) = rarr(i)
            rarr(i) = rswap 
        end do
    end subroutine reverse_rarr
    
    subroutine reverse_carr( carr )
    !is for reversing a complex array
        complex, intent(inout) :: carr(:)
        integer                :: i, j, sz, en
        complex                :: cswap
        sz = size(carr,1)
        if( sz < 2 )then
            return
        endif
        if( mod(sz,2) == 0 )then
            en = sz/2+1
        else
            en = sz/2+2
        endif
        j = 0
        do i = sz,en,-1
            j = j+1
            cswap   = carr(j)
            carr(j) = carr(i)
            carr(i) = cswap 
        end do
    end subroutine reverse_carr
    
    function cyci( NP, j ) result( i )
        integer, intent(in) :: j, NP
        integer :: i
        i = j
        if( j < 0 )  i = NP+j
        if( j == 0 ) i = NP
        if( j > NP)  i = j-NP
    end function cyci
    
    function cyci2( NP, j ) result( i )
        integer, intent(in) :: j, NP
        integer :: i
        i = j
        if( j < 0 )  i = NP+j+1
        if( j > NP)  i = j-NP-1
    end function cyci2
    
    pure function lowfact(n)
    ! returns the factorial of n. **Do not calclulate for big n.**
    ! ie: this function is bad for n > 12 (number is too big)
	integer, intent(in)		:: n
	integer				:: lowfact, i
	! if (n>12) then
	    ! write(*,*) 'Error: Lowfact does not calculate factorials for n > 12.'
	    ! write(*,*) 'In module: simple_math. Function: lowfact.'
	    ! stop
	! end if
	lowfact = 1
	do i=1,n
	    lowfact = lowfact * i
	end do
	return
    end function lowfact

end module simple_math