!==Class simple_fvols_corr
!
! simple_fvols_corr correlates Fourier volumes. Use this singleton by (1) setting the volume pair targeted for 
! correlation (set_volpair) and (2) correlating the volumes with the target volume in orientation e1,e2,e3,x,y,z 
! (corr_fvols). The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution or modification is regulated by the GNU General Public License. 
! *Author:* Hans Elmlund, 2009-06-11.
! 
!==Changes are documented below
!
!*
!
module simple_fvols_corr
use simple_eulers
use simple_build
use simple_params
use simple_math
use simple_jiffys
use simple_fgridvol
implicit none
save

public :: make_fvols_corr, set_volpair, corr_fvols, cost_fvols
private

interface corr_fvols
    module procedure corr_fvols_1
    module procedure corr_fvols_2
    module procedure corr_fvols_3
end interface

type(build), pointer :: bp=>null()
type(eulers)         :: e_one
complex, allocatable :: vol(:,:,:)
real                 :: mat(3,3)
integer              :: volpair(2)

contains

    subroutine make_fvols_corr( b )
    ! associates pointer to builder, makes single Euler, and calculates sqsums
        type(build), intent(in), target :: b
        bp => b
        e_one = new_eulers(1)
    end subroutine make_fvols_corr

    subroutine set_volpair( ref, targ )
        integer, intent(in) :: ref, targ
        volpair(1) = ref
        volpair(2) = targ
    end subroutine set_volpair

    function corr_fvols_1( f1, f2, target_to ) result( corr )
        complex, intent(in) :: f1(-xdim:xdim,-xdim:xdim,-xdim:xdim)
        complex, intent(in) :: f2(-xdim:xdim,-xdim:xdim,-xdim:xdim)
        integer, intent(in) :: target_to
        real    :: sumasq, sumbsq
        real    :: corr, sqrtprod
        integer :: h, k, l
        ! correlate
        corr = 0.
        sumasq = 0.
        sumbsq = 0.
        !$omp parallel do default(shared) private(h,k,l) &
        !$omp reduction(+:corr,sumasq,sumbsq) schedule(static)
        do h=fromk,target_to
            do k=-target_to,target_to
                do l=-target_to,target_to
                    ! real part of the complex mult btw ref and targ*
                    corr = corr+real(f1(h,k,l))*real(f2(h,k,l))&
                    +aimag(f1(h,k,l))*aimag(f2(h,k,l))
                    sumasq = sumasq+csqsum( f2(h,k,l) )           
                    sumbsq = sumbsq+csqsum( f1(h,k,l) )
                end do
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
    end function corr_fvols_1

    function corr_fvols_2( e1, e2, e3 ) result( corr )
        real, intent(in) :: e1, e2, e3
        real :: corr
        integer :: target_to
        ! determine the dynamic low-pass Fourier index
        target_to = int(dstep/lp_dyn)
        if( target_to > tofny ) then
            target_to = tofny
        else if( target_to < 3 ) then
            target_to = 3
        endif
        call rot_fvol_lp( e1, e2, e3, volpair(2) )
        corr = corr_fvols_1( bp%s3d(volpair(1))%fvol, bp%s3d(volpair(2))%fvol_new, target_to )
    end function corr_fvols_2
            
    function corr_fvols_3( ) result( corr )
        real :: corr
        integer :: target_to
        ! determine the dynamic low-pass Fourier index
        target_to = int(dstep/lp_dyn)
        if( target_to > tofny ) then
            target_to = tofny
        else if( target_to < 3 ) then
            target_to = 3
        endif
        corr = corr_fvols_1( bp%s3d(volpair(1))%fvol, bp%s3d(volpair(2))%fvol_new, target_to )
    end function corr_fvols_3
    
    function cost_fvols( vec, D ) result( cost )
        integer, intent(in) :: D
        real, intent(in)    :: vec(D)
        real :: cost
        cost = -corr_fvols_2(vec(1), vec(2), vec(3))
    end function cost_fvols

end module simple_fvols_corr