!==Class simple_fplane
!
! simple_fplane handles Fourier planes. Functionality includes reading, writing files to to stack,
! lowpass filtering, rotating, shifting. The code is distributed with the hope that it will be useful,
! but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund, 2011-06-05.
!
module simple_fplane
use simple_math
use simple_jiffys
use simple_params
use simple_stat
use simple_imgspi
use simple_ffts
implicit none

contains

    subroutine read_fplane( fplane, fstk, stkind )
    ! is for reading a single FT from stack
        complex, intent(inout) :: fplane(-xdim:xdim,-xdim:xdim)
        character(len=*)       :: fstk
        integer, intent(in)    :: stkind
        integer                :: file_stat
        open( unit=20, file=fstk, status='old', iostat=file_stat,&
        access='direct', action='read', form='unformatted', recl=ftsz )
        call fopen_err('In: read_fplane, module: simple_fplane.f90', file_stat)
        read( unit=20, rec=stkind ) fplane
        close(20)
    end subroutine read_fplane
    
    subroutine read_pcaplane( pcaplane, pcastk, stkind )
    ! is for reading a single FT from stack
        real, intent(inout) :: pcaplane(ncomps)
        character(len=*)    :: pcastk
        integer, intent(in) :: stkind
        integer             :: file_stat
        open( unit=20, file=pcastk, status='old', iostat=file_stat,&
        access='direct', action='read', form='unformatted', recl=pcasz )
        call fopen_err('In: read_pcaplane, module: simple_fplane.f90', file_stat)
        read( unit=20, rec=stkind ) pcaplane
        close(20)
    end subroutine read_pcaplane
    
    subroutine write_fplane( fplane, fstk, stkind )
    ! is for reading a single FT from stack
        complex, intent(inout) :: fplane(-xdim:xdim,-xdim:xdim)
        character(len=*)       :: fstk
        integer, intent(in)    :: stkind
        integer                :: file_stat
        open( unit=20, file=fstk, status='old', iostat=file_stat,&
        access='direct', action='write', form='unformatted', recl=ftsz )
        call fopen_err('In: write_fplane, module: simple_build.f90', file_stat)
        write( unit=20, rec=stkind ) fplane
        close(20)
    end subroutine write_fplane
    
    subroutine shift_fplane( fplane, x, y )
    ! is for origin shifting the Fourier plane
        complex, intent(inout) :: fplane(-xdim:xdim,-xdim:xdim)
        real, intent(in)       :: x, y
        integer                :: h, k
        real                   :: arg
        if( x /= 0. .and. y /= 0. )then
            !$omp parallel do default(shared) private(h,k,arg) schedule(static)
            do h=-xdim,xdim
                do k=-xdim,xdim
                    arg = (twopi/real(box))*(x*real(h)+y*real(k))
                    fplane(h,k) = fplane(h,k)*cmplx(cos(arg),sin(arg))
                end do
            end do
            !$omp end parallel do
        endif
    end subroutine shift_fplane
    
    subroutine rot_fplane( fplane, theta )
    ! is for rotating the Fourier plane
        complex, intent(inout) :: fplane(-xdim:xdim,-xdim:xdim)
        real, intent(in)       :: theta
        complex                :: fcopy(-xdim:xdim,-xdim:xdim)
        integer                :: h, k
        real                   :: mat(2,2)
        ! copy ptcl plane
        fcopy = fplane
        ! make 2D rotmat
        mat = rotmat2d(theta)
        !$omp parallel do default(shared) private(h,k) schedule(static)
        do h=-xdim,xdim
            do k=-xdim,xdim
                fplane(h,k) = extr_fcomp(fcopy, xdim, 2, 2, h, k, mat)
            end do
        end do
        !$omp end parallel do
    end subroutine rot_fplane
 
    subroutine shiftrot_fplane( fplane, theta, x, y )
    ! is for rotating the Fourier plane
        complex, intent(inout) :: fplane(-xdim:xdim,-xdim:xdim)
        real, intent(in)       :: theta, x, y
        complex                :: fcopy(-xdim:xdim,-xdim:xdim)
        integer                :: h, k
        real                   :: mat(2,2)
        if( x /= 0. .and. y /= 0. ) call shift_fplane( fplane, x, y )
        ! copy ptcl plane
        fcopy = fplane
        ! make 2D rotmat
        mat = rotmat2d(theta)
        !$omp parallel do default(shared) private(h,k) schedule(static)
        do h=-xdim,xdim
            do k=-xdim,xdim
                fplane(h,k) = extr_fcomp(fcopy, xdim, 2, 2, h, k, mat)
            end do
        end do
        !$omp end parallel do
    end subroutine shiftrot_fplane
    
    subroutine lp_fplane( fplane, lplim )
    ! is for low-pass filtering the Fourier plane
        complex, intent(inout) :: fplane(-xdim:xdim,-xdim:xdim)
        real, intent(in)       :: lplim
        integer                :: h, k
        real                   :: fwght
        !$omp parallel do default(shared) private(h,k,fwght) schedule(static)
        do h=-xdim,xdim
            do k=-xdim,xdim
                fwght = taperedge( dstep, h, k, lplim, 3.5 )
                fplane(h,k) = cmplx(fwght*real(fplane(h,k)),&
                fwght*aimag(fplane(h,k)))
            end do
        end do
        !$omp end parallel do
    end subroutine lp_fplane
    
    subroutine fft_rev_fplane( fplane, img )
        complex, intent(inout) :: fplane(-xdim:xdim,-xdim:xdim)
        type(imgspi)           :: img
        real, pointer          :: ip(:,:) 
        call get_imgspi_ptr( img, ip ) 
        call simple_2dfft_rev( fplane, 2*xdim, ip )
        call shift_imgspi( img )
    end subroutine fft_rev_fplane

end module simple_fplane