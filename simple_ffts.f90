!==Module simple_ffts
!
! simple_ffts provides an interface for 2d and 3d Fourier transforms by the fftw library.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution or modification is regulated by the GNU General Public License. 
! *Author:* Hans Elmlund, 2011-08-29.
! 
!==Changes are documented below
!
module simple_ffts
use simple_fftw3
use simple_jiffys

private :: tmp3d
public

complex, allocatable :: tmp3d(:,:,:)

contains

    subroutine simple_2dfft( rmat, imdim, outft )
    ! is for FFT of 2D image
        integer, intent(in)  :: imdim
        real, intent(in)     :: rmat(imdim,imdim)
        complex, intent(out) :: outft(-imdim/2:imdim/2,-imdim/2:imdim/2)
        complex              :: tmp(imdim/2+1,imdim)      
        integer              :: h, k, kt
        integer*8            :: plan
        ! init
        tmp = (0.,0.)
        outft = (0.,0.)
        ! make FFT plan
        call sfftw_plan_dft_r2c_2d(plan, imdim,&
        imdim, rmat, tmp, FFTW_ESTIMATE)
        ! execute FFT
        call sfftw_execute_dft_r2c(plan, rmat, tmp)
        ! destroy plan
        call sfftw_destroy_plan(plan) 
        ! expand according to friedels law:
        do h=0,imdim/2
            kt = imdim/2+1
            do k=-imdim/2,imdim/2
                outft(h,k) = tmp(h+1,kt) 
                outft(-h,-k) = conjg(tmp(h+1,kt))
                kt = kt+1
                if( kt > imdim ) kt = 1
            end do
        end do       
    end subroutine simple_2dfft
    
    subroutine simple_2dfft_rev( cmat, imdim, outimg )
    ! is for reverse FFT of 2D image
        integer, intent(in) :: imdim
        complex, intent(in) :: cmat(-imdim/2:imdim/2,-imdim/2:imdim/2)
        real, intent(out)   :: outimg(imdim,imdim)
        complex             :: tmp(imdim/2+1,imdim)   
        integer             :: h, k, kt
        integer*8           :: plan
        ! init
        tmp = (0.,0.)
        outimg = 0.
        ! compress to compact representation
        do h=0,imdim/2
            kt = imdim/2+1
            do k=-imdim/2,imdim/2
                tmp(h+1,kt) = cmat(h,k)
                kt = kt+1
                if( kt > imdim ) kt = 1
            end do
        end do 
        ! make FFT plan
        call sfftw_plan_dft_c2r_2d(plan, imdim,&
        imdim, tmp, outimg, FFTW_ESTIMATE)
        ! execute FFT
        call sfftw_execute_dft_c2r(plan, tmp, outimg)
        ! destroy plan
        call sfftw_destroy_plan(plan)     
    end subroutine simple_2dfft_rev
    
    subroutine prep_3dfft( vdim )
        integer, intent(in) :: vdim
        integer             :: alloc_stat
        if( allocated(tmp3d) ) deallocate(tmp3d)
        allocate(tmp3d(vdim/2+1,vdim,vdim), stat=alloc_stat)
        call alloc_err('In: prep_3dfft, module: simple_ffts', alloc_stat)
    end subroutine prep_3dfft

    subroutine simple_3dfft( rmat, vdim, outft, xdim )
    ! is for FFT of 3D volume
        integer, intent(in) :: vdim, xdim
        real, intent(in), dimension(vdim,vdim,vdim) :: rmat
        complex,intent(out), dimension(-xdim:xdim,-xdim:xdim,-xdim:xdim) :: outft
        integer :: h, k, l, kt, lt
        integer*8 :: plan
        ! init
        outft = (0.,0.)
        tmp3d = (0.,0.)
        ! make FFT plan
        call sfftw_plan_dft_r2c_3d(plan, vdim, vdim,&
        vdim, rmat, tmp3d, FFTW_ESTIMATE)
        ! execute FFT
        call sfftw_execute_dft_r2c(plan, rmat, tmp3d)
        ! destroy plan
        call sfftw_destroy_plan(plan)
        ! expand according to friedels law:
        do h=0,xdim
            kt = xdim+1
            do k=-xdim,xdim
                lt = xdim+1
                do l=-xdim,xdim
                    outft(l,k,h) = tmp3d(h+1,lt,kt)
                    outft(-l,-k,-h) = conjg(tmp3d(h+1,lt,kt))
                    lt = lt+1
                    if( lt > vdim ) lt = 1
                end do    
                kt = kt+1
                if( kt > vdim ) kt = 1
            end do
        end do
    end subroutine simple_3dfft

    subroutine simple_3dfft_rev( cmat, xdim, outvol, vdim )
    ! is for reverse FFT of 3D volume
        integer, intent(in) :: vdim, xdim
        complex, intent(in), dimension(-xdim:xdim,-xdim:xdim,-xdim:xdim) :: cmat
        real, intent(out), dimension(vdim,vdim,vdim) :: outvol
        integer :: h, k, l, kt, lt
        integer*8 :: plan
        ! init
        outvol = 0.
        tmp3d = (0.,0.)   
        ! compress to compact representation
        do h=0,xdim
            kt = xdim+1
            do k=-xdim,xdim
                lt = xdim+1
                do l=-xdim,xdim
                    tmp3d(h+1,lt,kt) = cmat(l,k,h)
                    lt = lt+1
                    if( lt > vdim ) lt = 1
                end do    
                kt = kt+1
                if( kt > vdim ) kt = 1
            end do
        end do
        ! make FFT plan
        call sfftw_plan_dft_c2r_3d(plan, vdim, vdim,&
        vdim, tmp3d, outvol, FFTW_ESTIMATE)
        ! execute backtransform
        call sfftw_execute_dft_c2r(plan, tmp3d, outvol)
        ! destroy plan
        call sfftw_destroy_plan(plan) 
    end subroutine simple_3dfft_rev

end module simple_ffts