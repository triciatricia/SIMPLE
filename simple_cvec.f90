!==Class simple_cvec
!
! simple_cvec handles complex vector arithmetics and calculation of correlations for the alignment methods in _SIMPLE_. 
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or 
! modification is regulated by the GNU General Public License. *Author:* Hans Elmlund, 2009-05-18.
! 
!==Changes are documented below
!
!* restructured, documented, HE 2009-05-26
!* added abstract class simple_abstr_vec to aviod assignment hangup, HE 2009-06-16
!* deugged and incorporated in the _SIMPLE_ library, HE 2009-06-25
!* removed deallocation of exiting cvec in the primary assignment method, HE 2009-07-02
!* added assignment method for assignment of a real scalar to cvec (here and in abstr_vec), HE 2009-07-02
!* optimized loops and parallelized amplitude correlation fcts , HE 2010-01-10
!* corr_cvec_arrays parallelized, needs debugging, HE 2010-01-25
!* double_corr_cvec_arrays parallelized, needs debugging, HE 2011-08-29
!* changed to single precision for porting to graphics cards, needs debugging, HE 2011-08-29
!
module simple_cvec
use simple_def_precision
use simple_math
use simple_stat
use simple_jiffys
implicit none

interface set_cvec_comp
    module procedure set_cvec_comp_1
    module procedure set_cvec_comp_2
end interface

type :: cvec
! complex vector type
    private
    real, allocatable :: r(:), im(:)
    integer :: from = 0, to = 0
    logical :: exists = .false.
end type cvec

contains

    function new_cvec( from, to ) result( num )
    ! allocates a complex vector (_from_,_to_)
        type(cvec)         :: num
        integer,intent(in) :: from, to ! cvec range
        integer            :: alloc_stat
        allocate( num%r(from:to), num%im(from:to), stat=alloc_stat )
        call alloc_err('In: new_cvec, module: simple_cvec.f90', alloc_stat)
        num%from   = from
        num%to     = to
        num%r      = 0.
        num%im     = 0.
        num%exists = .true.
    end function new_cvec
    
    subroutine assign_rvec_to_cvec( num, rin )
    ! transforms a real vector into a complex one, overloaded as '=' in simple_abstr_vec
        type(cvec), intent(inout) :: num
        real, intent(in)          :: rin(:)
        integer                   :: ru
        ru   = size(rin,1)
        if( num%exists ) then
            call kill_cvec( num )
        endif
        num    = new_cvec( 1, ru )
        num%r  = rin
        num%im = 0.
    end subroutine assign_rvec_to_cvec

    subroutine assign_rscalar_to_cvec( num, rin )
    ! transforms a real scalar into a complex vector, overloaded as '=' in simple_abstr_vec
        type(cvec), intent(inout) :: num
        real, intent(in)          :: rin
        if( num%exists ) then
            num%r  = rin
            num%im = rin
        else
            write( *,* ) 'Attempting to assign rscalar to a non-existing cvec!'
            write( *,* ) 'In: assign_rscalar_to_cvec, module: simple_cvec!'
            stop
        endif
    end subroutine assign_rscalar_to_cvec
      
    subroutine assign_cvec_to_cvec( num, cin )
    ! is the primary cvec assignment operator, overloaded as '=' in simple_abstr_vec
        type(cvec), intent(inout) :: num
        type(cvec), intent(in)  :: cin
        if( cin%exists )then
            if( num%exists ) then
                call kill_cvec( num )
            endif
            num    = new_cvec( cin%from, cin%to )
            num%r  = cin%r
            num%im = cin%im
        else
            write( *,* ) 'Attempting to use non-existing vector for assignment!'
            write( *,* ) 'In: assign_cvec_to_cvec, module: simple_cvec!'
            stop
        endif
    end subroutine assign_cvec_to_cvec

    subroutine assign_cvec_arr_to_cvec_arr( num, cin )
    ! is the cvec array assignment operator, overloaded as '=' in simple_abstr_vec
        type(cvec), intent(inout) :: num(:)
        type(cvec), intent(in)    :: cin(:)
        integer                   :: i,sn
        sn = size(num,1)
        if( sn /= size(cin(:)) )then
            write(*,*) 'Cannot assign cvec arrays of different size!'
            write(*,*) 'In: assign_cvec_arr_to_cvec_arr, module: simple_cvec!'
            stop
        else
            do i=1,sn
                call assign_cvec_to_cvec( num(i), cin(i) )
            end do
        endif
    end subroutine assign_cvec_arr_to_cvec_arr
    
    subroutine get_cvec_limits( num, from, to )
    ! is for getting the Fourier index limits of a cvec
        type(cvec), intent(in) :: num
        integer, intent(out)   :: from, to
        from = num%from
        to   = num%to
    end subroutine get_cvec_limits
      
    subroutine kill_cvec( num )
    ! is a destructor
        type(cvec), intent(inout) :: num
        if( num%exists ) then
            deallocate( num%r, num%im )
            num%from   = 0
            num%to     = 0
            num%exists = .false.
        endif
    end subroutine kill_cvec
    
    subroutine set_cvec_comp_1( num, i, amp, phase )
    ! is setting the phase and amplitude of complex component _i_
        type(cvec), intent(inout) :: num
        integer, intent(in)       :: i
        real, intent(in)          :: amp, phase
        num%r(i)  = amp
        num%im(i) = phase
    end subroutine set_cvec_comp_1
    
    subroutine set_cvec_comp_2( num, i, comp )
    ! is setting the phase and amplitude of complex component _i_
        type(cvec), intent(inout) :: num
        integer, intent(in)       :: i
        complex, intent(in)       :: comp
        num%r(i)  = real(comp)
        num%im(i) = aimag(comp)
    end subroutine set_cvec_comp_2
    
    subroutine add_to_cvec( num, i, amp, phase )
    ! is adding phase and amplitude to complex component _i_
        type(cvec), intent(inout) :: num
        integer, intent(in)       :: i
        real, intent(in)          :: amp, phase
        num%r(i)  = num%r(i)+amp
        num%im(i) = num%im(i)+phase
    end subroutine add_to_cvec
    
    subroutine add_cvec_to_cvec( to_add, to )
    ! is adding to_add to to
        type(cvec), intent(inout) :: to_add
        type(cvec), intent(inout) :: to
        to%r(:)  = to%r(:)+to_add%r(:)
        to%im(:) = to%im(:)+to_add%im(:)
    end subroutine add_cvec_to_cvec
        
    subroutine sub_cvec_from_cvec( to_sub, from )
    ! is subtracting to_sub from from
        type(cvec), intent(inout) :: to_sub
        type(cvec), intent(inout) :: from
        from%r(:)  = from%r(:)-to_sub%r(:)
        from%im(:) = from%im(:)-to_sub%im(:)
    end subroutine sub_cvec_from_cvec

    subroutine get_cvec_comp( num, i, amp, phase )
    ! is getting the phase and amplitude of complex component _i_
        type(cvec), intent(in) :: num
        integer, intent(in)    :: i
        real, intent(out)      :: amp, phase
        amp   = num%r(i)
        phase = num%im(i)
    end subroutine get_cvec_comp
    
    subroutine get_complex_part( num, vec )
    ! is returning the complex part of the complex vector
        type(cvec), intent(in)    :: num
        real(double), intent(out) :: vec(:)
        vec = num%im
    end subroutine get_complex_part
    
    subroutine set_complex_part( num, vec )
    ! is setting the complex part of the complex vector
        type(cvec), intent(inout) :: num
        real(double), intent(in)  :: vec(:)
        num%im = vec
    end subroutine set_complex_part
      
    subroutine get_real_part( num, vec )
    ! is returning the real part of the complex vector
        type(cvec), intent(in)    :: num
        real(double), intent(out) :: vec(:)
        vec = num%r
    end subroutine get_real_part
    
    subroutine set_real_part( num, vec )
    ! is returning the real part of the complex vector
        type(cvec), intent(inout) :: num
        real(double), intent(in)  :: vec(:)
        num%r = vec
    end subroutine set_real_part

    subroutine print_cvec( num )
    ! is for prettier printing
        type(cvec), intent(in) :: num
        write(*,*) "Re: [",num%r(num%from:num%to),"] Im: [",num%im(num%from:num%to),"]"
    end subroutine print_cvec
    
    function add_cvecs( a, b ) result( num )
    ! is for adding complex vectors overloaded as '+' in simple_abstr_vec
        type(cvec)              :: num
        type(cvec), intent(in)  :: a, b
        num    = new_cvec( b%from, b%to )
        num%r  = a%r+b%r      ! vector addition of the real part
        num%im = a%im+b%im    ! vector subtraction of the real part
    end function add_cvecs
        
    function sum_cvecs( z ) result( num )
    ! is summing all cvecs in the input array and returns the resulting cvec
        type(cvec)              :: num
        type(cvec), intent(in)  :: z(:) ! assumed to be indexed from 1
        integer                 :: i
        num    = new_cvec( z(1)%from, z(1)%to ) 
        num%r  = 0.
        num%im = 0.
        do i=1,size(z,1)
            num%r   = num%r+z(i)%r
            num%im  = num%im+z(i)%im
        end do
    end function sum_cvecs
    
    function avg_cvecs( z ) result( num )
    ! is returning the centroid of all cvecs in the input array
        type(cvec)             :: num
        type(cvec), intent(in) :: z(:) ! assumed to be indexed from 1
        real                   :: div
        div  = real(size(z,1))
        num  = rcdiv( sum_cvecs(z), div, div )
    end function avg_cvecs
    
    function sub_cvecs( a, b ) result( num )
    ! is for subtracting complex vectors, overloaded as '-' in simple_abstr_vec
        type(cvec)              :: num
        type(cvec), intent(in)  :: a, b
        if( (a%from /= b%from) .or. (a%to /= b%to) ) then
            write( *,* ) 'Cannot subtract cvecs of different shape in sub_cvecs, module: simple_cvec!'
            stop
        endif
        num    = new_cvec( b%from, b%to )
        num%r  = a%r-b%r            ! vector subtraction of the real part
        num%im = a%im-b%im          ! vector subtraction of the complex part
    end function sub_cvecs
    
    function mul_cvecs( a, b ) result( num )
    ! is for multiplying complex vectors, overloaded as '*' in simple_abstr_vec
        type(cvec)              :: num
        type(cvec), intent(in)  :: a, b
        if( (a%from /= b%from) .or. (a%to /= b%to) ) then
            write( *,* ) 'Cannot multiply cvecs of different shape in mul_cvecs, module: simple_cvec!'
            stop
        endif
        num    = new_cvec( a%from, a%to ) 
        num%r  = a%r*b%r-a%im*b%im           ! note that this is vector multiplication
        num%im = a%im*b%r+a%r*b%im           ! note also that multiplication with a real array gives                 
    end function mul_cvecs                   ! Re: a%r*b%r and Im: a%im*b%r (phase flipping)
    
    function rcmul( z, r, c ) result( num )
    ! is multiplying the real and complex parts of _z_ with _r_ and _c_, respectively, and returns the resulting cvec
        type( cvec )             :: num
        type( cvec ), intent(in) :: z 
        real, intent(in)         :: r, c
        num = new_cvec( z%from, z%to )
        num%r   = r*z%r   ! note that this is vector multiplication
        num%im  = c*z%im  ! note that this is vector multiplication
    end function rcmul
    
    function rcdiv( z, r, c ) result( num )
    ! is dividing the real and complex parts of _z_ with _r_ and _c_, respectively, and returns the resulting cvec
        type( cvec )             :: num
        type( cvec ), intent(in) :: z 
        real, intent(in)         :: r, c
        num = new_cvec( z%from, z%to )
        num%r   = z%r/r   ! note that this is vector division
        num%im  = z%im/c  ! note that this is vector division
    end function rcdiv
    
    function conjg_cvec( z ) result( num )
    ! returns the complex conjugate of the input cvec, overloaded as _conjg_ in simple_abstr_vec
        type( cvec )             :: num
        type( cvec ), intent(in) :: z
        num    = new_cvec( z%from, z%to )
        num%r  = z%r      ! note that this is vector assignment
        num%im = -1.*z%im ! note that this is vector multiplication
    end function conjg_cvec
    
    function dot_cvecs( a, b ) result( num )
    ! is the complex dot product, overloaded as _dot_product_ in simple_abstr_vec
        type(cvec)              :: num
        type(cvec), intent(in)  :: a, b
        type(cvec)              :: b_conjg, c
        if( (a%from /= b%from) .or. (a%to /= b%to) ) then
            write( *,* ) 'Cannot dot cvecs of different shape in dot_cvecs, module: simple_cvec!'
            stop
        endif
        b_conjg   = conjg_cvec(b)
        c         = mul_cvecs(a,b_conjg)
        num = new_cvec( 1, 1 )
        num%r(1)  = sum(c%r)
        num%im(1) = sum(c%im)
        call kill_cvec( b_conjg )
        call kill_cvec( c )
    end function dot_cvecs
    
    function div_cvecs( a, b ) result( num )
    ! is for dividing complex vectors, overloaded as '/' in simple_abstr_vec
        type( cvec ), intent(in)  :: a, b
        type( cvec )              :: num
        integer                   :: i
        complex                   :: ac, bc, dc
        if( (a%from /= b%from) .or. (a%to /= b%to) ) then
            write( *,* ) 'Cannot divide cvecs of different shape in div_cvecs, module: simple_cvec!'
            stop
        endif
        num = new_cvec( a%from, a%to ) 
        do i=num%from,num%to ! divide, component by componenet
            ac = cmplx(a%r(i),a%im(i))
            bc = cmplx(b%r(i), b%im(i))
            dc = cdiv(ac, bc)
            num%r(i)  = real(dc)
            num%im(i) = aimag(dc)
        end do
    end function div_cvecs

    function corr_cvec_arrays( a, b, target_to, freek, filter ) result( corr )
    ! calculates the 'classical' correlation coefficient between two equally sized arrays
    ! of complex vectors _a_ and _b_ with the lowpass limit _target_to_   
        type(cvec), intent(in) :: a(:), b(:)
        logical, intent(in)    :: filter(:) ! to select cvecs in the a & b arrays
        integer, intent(in)    :: target_to ! lowpass filtering in the Fourier domain
        integer, intent(in)    :: freek     ! free resolution shell
        real                   :: corr, sumasq, sumbsq, asq, bsq, sqrtprod
        integer                :: k, i
        complex                :: ac, bc
        corr   = 0.
        sumasq = 0.
        sumbsq = 0.
        !$omp parallel do default(shared) private(i,k,ac,bc,asq,bsq) &
        !$omp reduction(+:corr,sumasq, sumbsq) schedule(static)
        do i=1,size(a,1)
            if( filter(i) )then
                do k=a(i)%from,target_to
                    if( k /= freek )then
                        ! real part of the complex mult btw a and b*
                        corr = corr+a(i)%r(k)*b(i)%r(k)+a(i)%im(k)*b(i)%im(k)
                        ! if the resolution level is fixed and the number of vecs matched is always the same
                        ! the below terms can be precalculated for each transform
                        ac = cmplx(a(i)%r(k), a(i)%im(k))
                        bc = cmplx(b(i)%r(k), b(i)%im(k))
                        asq = csqsum( ac )
                        bsq = csqsum( bc )
                        sumasq = sumasq+asq           
                        sumbsq = sumbsq+bsq
                    endif
                end do        
            endif
        end do
        !$omp end parallel do
        sqrtprod = sqrt(sumasq*sumbsq)
        ! correct for corr=NaN
        if( corr == 0. .or. (corr > 0. .or. corr < 0.) )then
            if( sqrtprod == 0. )then
                corr = -1. 
            else
                corr = corr/sqrtprod ! Pearsons corr. coeff. in complex space
            endif
        else
            corr = -1.
        endif   
    end function corr_cvec_arrays
    
    subroutine double_corr_cvec_arrays( a, b, target_to, freek, filter, corr1, corr2 )
    ! calculates low and high-resolution correlation coefficients between
    ! two equally sized arrays of complex vectors _a_ and _b_ 
        type(cvec), intent(in) :: a(:), b(:)
        logical, intent(in)    :: filter(:) ! to select cvecs in the a & b arrays
        integer, intent(in)    :: target_to ! lowpass filtering in the Fourier domain
        integer, intent(in)    :: freek     ! free resolution shell
        real, intent(out)      :: corr1, corr2
        real                   :: sumasq1, sumbsq1, sqrtprod1, sqrtprod2, sumasq2, sumbsq2, asq, bsq
        integer                :: k, i, pivot
        complex                :: ac, bc
        pivot = (target_to-a(1)%from+1)/2+a(1)%from
        corr1 = 0.
        corr2 = 0.
        sumasq1 = 0.
        sumbsq1 = 0.
        sumasq2 = 0.
        sumbsq2 = 0.
        !$omp parallel do default(shared) private(i,k,ac,bc,asq,bsq) &
        !$omp reduction(+:corr1,corr2,sumasq1,sumasq2,sumbsq1,sumbsq2) schedule(static)
        do i=1,size(a,1)
            if( filter(i) )then
                do k=a(i)%from,target_to
                    if( k /= freek )then
                        if( k < pivot )then
                            ! real part of the complex mult btw a and b*
                            corr1 = corr1+a(i)%r(k)*b(i)%r(k)+a(i)%im(k)*b(i)%im(k)
                            ac = cmplx(a(i)%r(k), a(i)%im(k))
                            bc = cmplx(b(i)%r(k), b(i)%im(k))
                            asq = csqsum( ac )
                            bsq = csqsum( bc )
                            sumasq1 = sumasq1+asq           
                            sumbsq1 = sumbsq1+bsq
                        else
                            ! real part of the complex mult btw a and b*
                            corr2 = corr2+a(i)%r(k)*b(i)%r(k)+a(i)%im(k)*b(i)%im(k)
                            ac = cmplx(a(i)%r(k), a(i)%im(k))
                            bc = cmplx(b(i)%r(k), b(i)%im(k))
                            asq = csqsum( ac )
                            bsq = csqsum( bc )
                            sumasq2 = sumasq2+asq           
                            sumbsq2 = sumbsq2+bsq
                        endif
                    endif
                end do        
            endif
        end do
        !$omp end parallel do
        sqrtprod1 = sqrt(sumasq1*sumbsq1)   
        sqrtprod2 = sqrt(sumasq2*sumbsq2)
        ! correct for corr=NaN
        if( corr2 == 0. .or. (corr2 > 0. .or. corr2 < 0.) )then
            if( sqrtprod2 == 0. )then
                corr2 = -1. 
            else
                corr2 = corr2/sqrtprod2 ! Pearsons corr. coeff. in complex space
            endif
        else
            corr2 = -1.
        endif
        ! correct for corr=NaN
        if( corr1 == 0. .or. (corr1 > 0. .or. corr1 < 0.) )then
            if( sqrtprod1 == 0. )then
                corr1 = -1. 
            else
                corr1 = corr1/sqrtprod1 ! Pearsons corr. coeff. in complex space
            endif
        else
            corr1 = -1.
        endif  
    end subroutine double_corr_cvec_arrays
    
    function pcorr_cvec_arrays( a, b, k, filter ) result( pcorr )
    ! calculates the point normalized correlation between two equally sized arrays
    ! of complex vectors _a_ and _b_ at position _k_
        type(cvec), intent(in) :: a(:), b(:)
        integer, intent(in)    :: k         ! resolution shell
        logical, intent(in)    :: filter(:) ! to select cvecs in the _a_ & _b_ arrays  
        real                   :: pcorr, sumasq, sumbsq, asq, bsq, sqrtprod
        integer                :: i
        complex                :: ac, bc
        pcorr  = 0.
        sumasq = 0.
        sumbsq = 0.
        do i=1,size(a,1)
            if( filter(i) )then
                ! real part of the complex mult btw a and b*
                pcorr = pcorr+a(i)%r(k)*b(i)%r(k)+a(i)%im(k)*b(i)%im(k)
                ac = cmplx(a(i)%r(k), a(i)%im(k))
                bc = cmplx(b(i)%r(k), b(i)%im(k))
                asq = csqsum( ac )
                bsq = csqsum( bc )
                sumasq  = sumasq+asq           
                sumbsq  = sumbsq+bsq
            endif
        end do
        sqrtprod = sqrt(sumasq*sumbsq)
        ! correct for corr=NaN
        if( pcorr == 0. .or. (pcorr > 0. .or. pcorr < 0.) )then
            if( sqrtprod == 0. )then
                pcorr = -1. 
            else
                pcorr = pcorr/sqrtprod ! Pearsons corr. coeff. in complex space
            endif
        else
            pcorr = -1. 
        endif   
    end function pcorr_cvec_arrays
    
end module simple_cvec