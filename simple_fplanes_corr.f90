module simple_fplanes_corr
use simple_eulers
use simple_build
use simple_params
use simple_math
use simple_jiffys
use simple_def_precision
implicit none
save

private :: bp, indices, mat, exists
public

interface corr_fplanes
    module procedure corr_fplanes_1
    module procedure corr_fplanes_2
    module procedure corr_fplanes_3
    module procedure corr_fplanes_4
    module procedure corr_fplanes_5
end interface

type(build), pointer :: bp=>null()
type(eulers)         :: e_one
integer, allocatable :: indices(:,:)
real                 :: mat(3,3)
logical              :: exists=.false.

contains

    subroutine make_fplanes_corr( b )
    ! associates pointer to builder, makes single Euler, and allocates
        type(build), intent(in), target :: b
        integer :: alloc_stat
        if( exists ) return
        bp => b
        e_one = new_eulers(1)
        allocate( indices(tok*2+1,2), stat=alloc_stat )
        call alloc_err('In: make_fplanes_corr, module: simple_fplanes_corr', alloc_stat )
        exists = .true.
    end subroutine make_fplanes_corr
    
    subroutine kill_fplanes_corr
        if( exists )then
            bp => null()
            deallocate( indices )
            exists = .false.
        endif
    end subroutine kill_fplanes_corr
    
    function calc_sqsum( f1, target_to ) result( sumasq )
        complex, intent(in) :: f1(-xdim:xdim,-xdim:xdim)
        integer, intent(in) :: target_to
        real    :: sumasq
        integer :: h, k
        sumasq = 0.
        !$omp parallel do default(shared) private(h,k) &
        !$omp reduction(+:sumasq) schedule(static)
        do h=fromk,target_to
            do k=fromk,target_to
                sumasq = sumasq+csqsum( f1(h,k) )
            end do
        end do
        !$omp end parallel do
    end function calc_sqsum
    
    function corr_fplanes_4( f1, f2, sumasq, sumbsq, target_to ) result( corr )
        complex, intent(in) :: f1(-xdim:xdim,-xdim:xdim), f2(-xdim:xdim,-xdim:xdim)
        real, intent(in)    :: sumasq, sumbsq
        integer, intent(in) :: target_to
        real    :: corr, sqrtprod
        integer :: h, k
        ! correlate
        corr   = 0.
        !$omp parallel do default(shared) private(h,k) &
        !$omp reduction(+:corr) schedule(static)     
        do h=fromk,target_to
            do k=fromk,target_to
                ! real part of the complex mult btw ref and targ*
                corr = corr+real(f1(h,k))*real(f2(h,k))&
                +aimag(f1(h,k))*aimag(f2(h,k))       
            end do
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
    end function corr_fplanes_4
    
    function corr_fplanes_3( f1, fref, sumasq, target_to ) result( corr )
        complex, intent(in) :: f1(-xdim:xdim,-xdim:xdim), fref(-xdim:xdim,-xdim:xdim)
        real, intent(in)    :: sumasq
        integer, intent(in) :: target_to
        real    :: corr, sqrtprod, sumbsq
        integer :: h, k
        ! correlate
        corr   = 0.
        sumbsq = 0.
        !$omp parallel do default(shared) private(h,k) &
        !$omp reduction(+:corr,sumbsq) schedule(static)     
        do h=fromk,target_to
            do k=fromk,target_to
                ! real part of the complex mult btw ref and targ*
                corr = corr+real(f1(h,k))*real(fref(h,k))&
                +aimag(f1(h,k))*aimag(fref(h,k))         
                sumbsq = sumbsq+csqsum( f1(h,k) )
            end do
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
    end function corr_fplanes_3
    
    function corr_fplanes_2( f1, f2, target_to ) result( corr )
        complex, intent(in) :: f1(-xdim:xdim,-xdim:xdim), f2(-xdim:xdim,-xdim:xdim)
        integer, intent(in) :: target_to
        real    :: corr, sqrtprod, sumasq, sumbsq
        integer :: h, k
        ! correlate
        corr   = 0.
        sumasq = 0.
        sumbsq = 0.
        !$omp parallel do default(shared) private(h,k) &
        !$omp reduction(+:corr,sumasq,sumbsq) schedule(static)     
        do h=fromk,target_to
            do k=fromk,target_to
                ! real part of the complex mult btw ref and targ*
                corr = corr+real(f1(h,k))*real(f2(h,k))&
                +aimag(f1(h,k))*aimag(f2(h,k))
                sumasq = sumasq+csqsum( f2(h,k) )           
                sumbsq = sumbsq+csqsum( f1(h,k) )
            end do
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
    end function corr_fplanes_2

    function corr_fplanes_1( e1, e2, e3, x, y ) result( corr )
        real, intent(in) :: e1, e2, e3, x, y
        real :: corr, sqrtprod, sumasq, sumbsq
        integer :: target_to, h, k
        ! determine the dynamic low-pass Fourier index
        target_to = int(dstep/lp_dyn)
        if( target_to > tofny ) then
            target_to = tofny
        else if( target_to < 3 ) then
            target_to = 3
        endif
        ! extract the section from the volume
        call extr_fplane( 1, e1, e2, e3, x, y, target_to )
        ! correlate
        corr   = 0.
        sumasq = 0.
        sumbsq = 0.
        !$omp parallel do default(shared) private(h,k) &
        !$omp reduction(+:corr,sumasq,sumbsq) schedule(static)     
        do h=fromk,target_to
            do k=fromk,target_to
                ! real part of the complex mult btw ref and targ*
                corr = corr+real(bp%frefs(1)%arr(h,k))*real(bp%f(ptcl)%arr(h,k))&
                +aimag(bp%frefs(1)%arr(h,k))*aimag(bp%f(ptcl)%arr(h,k))
                sumasq = sumasq+csqsum( bp%f(ptcl)%arr(h,k) )
                sumbsq = sumbsq+csqsum( bp%frefs(1)%arr(h,k) )
            end do
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
    end function corr_fplanes_1
    
    subroutine corr_fplanes_5( e1, e2, e3, x, y, corr1, corr2 )
        real, intent(in)  :: e1, e2, e3, x, y
        real, intent(out) :: corr1, corr2
        real :: sqrtprod1, sqrtprod2, sumasq1, sumbsq1, sumasq2, sumbsq2
        integer :: target_to, h, k, pivot
        ! determine the dynamic low-pass Fourier index
        target_to = int(dstep/lp_dyn)
        if( target_to > tofny ) then
            target_to = tofny
        else if( target_to < 3 ) then
            target_to = 3
        endif
        pivot = (target_to-fromk+1)/2+fromk
        ! extract the section from the volume
        call extr_fplane( 1, e1, e2, e3, x, y, target_to )
        ! correlate
        corr1   = 0.
        corr2   = 0.
        sumasq1 = 0.
        sumbsq1 = 0.
        sumasq2 = 0.
        sumbsq2 = 0.
        !$omp parallel default(shared) private(h,k)
        !$omp do reduction(+:corr1,sumasq1,sumbsq1) schedule(static)
        do h=fromk,pivot-1
            do k=fromk,pivot-1   
                ! real part of the complex mult btw ref and targ*
                corr1 = corr1+real(bp%frefs(1)%arr(h,k))*real(bp%f(ptcl)%arr(h,k))&
                +aimag(bp%frefs(1)%arr(h,k))*aimag(bp%f(ptcl)%arr(h,k))
                sumasq1 = sumasq1+csqsum( bp%f(ptcl)%arr(h,k) )          
                sumbsq1 = sumbsq1+csqsum( bp%frefs(1)%arr(h,k) )
            end do
        end do
        !$omp end do
        !$omp do reduction(+:corr2,sumasq2,sumbsq2) schedule(static)      
        do h=pivot,target_to
            do k=pivot,target_to   
                ! real part of the complex mult btw ref and targ*
                corr2 = corr2+real(bp%frefs(1)%arr(h,k))*real(bp%f(ptcl)%arr(h,k))&
                +aimag(bp%frefs(1)%arr(h,k))*aimag(bp%f(ptcl)%arr(h,k))
                sumasq2 = sumasq2+csqsum( bp%f(ptcl)%arr(h,k) )          
                sumbsq2 = sumbsq2+csqsum( bp%frefs(1)%arr(h,k) )
            end do
        end do
        !$omp end do
        !$omp end parallel
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
    end subroutine corr_fplanes_5
    
    subroutine corrspec_fplanes( e1, e2, e3, x, y, rescorr, corrspec, lowpass )
    ! estimates the integral over a strictly positive spectral 
    ! correlation interval, returns the estimate (_corrspec_), a low-pass limit value (_lowpass_),
    ! and the correlation as function of spatial frequency (_rescorr_)
        real, intent(in)  :: e1, e2, e3, x, y
        real, intent(out) :: rescorr(fromk:tok)
        real, intent(out) :: corrspec, lowpass
        integer           :: k, i
        real              :: sum_this, sum_previous, sqrtprod, sumasq, sumbsq, corr
        corrspec     = 0.
        lowpass      = dstep/real(fromk)
        sum_this     = 0.
        sum_previous = 0.
        rescorr      = 0.
        ! extract the section from the volume
        call extr_fplane( 1, e1, e2, e3, x, y, xdim )
        ! loop over Fourier indices (componentwise calculation)
        do k=fromk,tok
            ! get the indices
            call get_fourier_partshell( k, indices(:k*2+1,:) )
            ! correlate components along the ring
            sumasq = 0.
            sumbsq = 0.
            corr = 0.
            !$omp parallel do default(shared) private(i) &
            !$omp reduction(+:corr,sumasq,sumbsq) schedule(static)
            do i=1,k*2+1
                ! real part of the complex mult btw ref and targ*
                corr = corr+real(bp%frefs(1)%arr(indices(i,1),indices(i,2)))*&
                real(bp%f(ptcl)%arr(indices(i,1),indices(i,2)))&
                +aimag(bp%frefs(1)%arr(indices(i,1),indices(i,2)))*&
                aimag(bp%f(ptcl)%arr(indices(i,1),indices(i,2)))
                sumasq = sumasq+csqsum( bp%f(ptcl)%arr(indices(i,1),indices(i,2)) )           
                sumbsq = sumbsq+csqsum( bp%frefs(1)%arr(indices(i,1),indices(i,2)) )
            end do
            !$omp end parallel do
            sqrtprod = sqrt(sumasq*sumbsq)
            ! correct for corr=NaN
            if( corr == 0. .or. (corr > 0. .or. corr < 0.) )then
                if( sqrtprod == 0. )then
                    rescorr(k) = 0. 
                else
                    rescorr(k) = corr/sqrtprod ! Pearsons corr. coeff. in complex space
                endif
            else
                rescorr(k) = 0.
            endif
            ! Here comes the spectral analysis   
            sum_previous = sum_this
            sum_this     = sum_this+rescorr(k)
            if( rescorr(k) > 0.) then
                if( k /= tok ) then
                    cycle
                else
                    corrspec = sum_this
                    lowpass  = dstep/real(k)
                endif
            else
                if( k-1 <= fromk ) then
                    corrspec = 0.
                    lowpass  = dstep/real(fromk)
                    exit
                else
                    corrspec = sum_previous
                    lowpass  = dstep/real(k-1)
                    exit
                endif
            endif
        end do
    end subroutine corrspec_fplanes
    
    function cost_fplanes( vec, D ) result( cost )
        integer, intent(in) :: D
        real, intent(in)    :: vec(D)
        real                :: cost
        cost = -corr_fplanes_1( vec(1), vec(2), vec(3), vec(4), vec(5) )
    end function cost_fplanes
    
    function wcost_fplanes( vec, D ) result( cost )
        integer, intent(in) :: D
        real, intent(in)    :: vec(D)
        real                :: cost, corr1, corr2
        call corr_fplanes_5( vec(1), vec(2), vec(3), vec(4), vec(5), corr1, corr2 )
        cost = -(0.5*corr1+0.5*corr2)
    end function wcost_fplanes
    
    ! functionality for extracting the Fourier plane from the volume
    
    subroutine extr_fplane( ref, e1, e2, e3, x, y, target_to )
    ! is for extracting a Fourier plane from the volume
        integer, intent(in) :: ref
        real, intent(in)    :: e1, e2, e3, x, y
        integer, intent(in) :: target_to
        integer             :: h, k
        ! set the euler to make the rotation matrix
        call set_euler(e_one, 1, e1, e2, e3)
        ! get the matrix
        call get_euler_mat(e_one, 1, mat)
        !$omp parallel do default(shared) private(h,k) schedule(static)
        do h=fromk,target_to
            do k=fromk,target_to
                call extr_fvol_comp(h,k)
            end do
        end do
        !$omp end parallel do
        
        contains
        
            subroutine extr_fvol_comp( h, k )
            ! is for interpolating a Fourier component from the Fourier volume state,
            ! _h_ & _k_ are the reciprocal indices, _x_ & _y_ is the origin shift vec
            !* choice=1: sinc window
            !* choice=2 gauwindowed sinc
            !* choice=else bmanwindowed sinc
                integer, intent(in) :: h, k 
                integer :: i, j, l, istart, istop, jstart, jstop, lstart, lstop
                real    :: tmp1, tmp2, tmp3, btmp1, btmp2, btmp3, vec(3), loc(3), tmp, arg
                vec(1) = real(h)
                vec(2) = real(k)
                vec(3) = 0.
                loc = matmul(vec,mat)
                bp%frefs(ref)%arr(h,k) = cmplx(0.,0.)
                ! make window
                call recwin_3d(loc(1), loc(2), loc(3), xdim, winsz,&
                istart, istop, jstart, jstop, lstart, lstop)
                ! interpolate
                do i=istart,istop
                    do j=jstart,jstop
                        do l=lstart,lstop
                            if( wchoice == 1 )then
                                tmp1 = sinc(loc(1)-real(i))
                                tmp2 = sinc(loc(2)-real(j))
                                tmp3 = sinc(loc(3)-real(l))
                                tmp = tmp1*tmp2*tmp3
                            else if( wchoice == 2 )then
                                tmp1 = sinc(loc(1)-real(i))
                                tmp2 = sinc(loc(2)-real(j))
                                tmp3 = sinc(loc(3)-real(l))
                                btmp1 = gauwfun(loc(1)-real(i), winsz, 0.5)
                                btmp2 = gauwfun(loc(2)-real(j), winsz, 0.5)
                                btmp3 = gauwfun(loc(3)-real(l), winsz, 0.5)
                                tmp = tmp1*tmp2*tmp3*btmp1*btmp2*btmp3
                            else
                                tmp1 = sinc(loc(1)-real(i))
                                tmp2 = sinc(loc(2)-real(j))
                                tmp3 = sinc(loc(3)-real(l))
                                btmp1 = bmanwfun(loc(1)-real(i), winsz)
                                btmp2 = bmanwfun(loc(2)-real(j), winsz)
                                btmp3 = bmanwfun(loc(3)-real(l), winsz)
                                tmp = tmp1*tmp2*tmp3*btmp1*btmp2*btmp3
                            endif
                            bp%frefs(ref)%arr(h,k) = bp%frefs(ref)%arr(h,k)+&
                            cmplx(real(bp%s3d(state)%fvol(i,j,l))*tmp,&
                            aimag(bp%s3d(state)%fvol(i,j,l))*tmp)
                        end do
                    end do
                end do
                if( x /= 0. .and. y /= 0. )then
                    arg = (-twopi/real(box))*(x*real(h)+y*real(k))
                    bp%frefs(ref)%arr(h,k) = bp%frefs(ref)%arr(h,k)*cmplx(cos(arg),sin(arg))
                endif
            end subroutine extr_fvol_comp         
        
    end subroutine extr_fplane
      
end module simple_fplanes_corr