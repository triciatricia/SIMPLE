module simple_fgridvol
use simple_eulers
use simple_params
use simple_math
use simple_build
use simple_fplane
implicit none
save

private :: e_one, bp, mat, grid_fplane_comp_1, grid_fplane_comp_2, that, prep_new_fvols, calc_weight
public

interface grid_fplane
    module procedure grid_fplane_1
    module procedure grid_fplane_2
end interface

type(eulers)         :: e_one
type(build), pointer :: bp
real                 :: mat(3,3)
character(len=3)     :: that

contains

    subroutine make_fgridvol( b, which )
    ! associates pointer to builder, makes single Euler, and allocates data
        type(build), intent(in), target :: b
        character(len=*), intent(in) :: which
        bp => b
        call set_fgridvol( which )
        e_one = new_eulers(1)
    end subroutine make_fgridvol
    
    subroutine set_fgridvol( which )
        character(len=*), intent(in) :: which
        if( which == 'new' )then
            that = 'new'
        else
            that = 'old'
        endif
    end subroutine set_fgridvol

    subroutine grid_fvol_comp_1( h, k, l, s )
    ! grids a Fourier volume component to the new Fourier volume
        integer, intent(in) :: h, k, l, s
        integer             :: i, j, m, istart, istop, jstart, jstop, mstart, mstop
        real                :: tmp, vec(3), loc(3)
        vec(1) = real(h)
        vec(2) = real(k)
        vec(3) = real(l)
        loc = matmul(vec,mat)
        ! make window
        call recwin_3d( loc(1), loc(2), loc(3), xdim, winsz,&
        istart, istop, jstart, jstop, mstart, mstop )
        ! interpolate
        do i=istart,istop
            do j=jstart,jstop
                do m=mstart,mstop
                    ! calculate weight (Gaussian windowed sinc)
                    tmp = calc_weight( i, j, m, loc )
                    ! grid the Fourier data
                    bp%s3d(s)%fvol_new(i,j,m) = bp%s3d(s)%fvol_new(i,j,m)+&
                    cmplx(real(bp%s3d(s)%fvol(h,k,l))*tmp,aimag(bp%s3d(s)%fvol(h,k,l))*tmp)
                end do
            end do
        end do
    end subroutine grid_fvol_comp_1

    subroutine grid_fplane_comp_1( h, k, s )
    ! grids a plane component to the Fourier volume
        integer, intent(in) :: h, k, s
        integer             :: i, j, m, istart, istop, jstart, jstop, mstart, mstop
        real                :: tmp, vec(3), loc(3)
        vec(1) = real(h)
        vec(2) = real(k)
        vec(3) = 0.
        loc = matmul(vec,mat)
        ! make window
        call recwin_3d( loc(1), loc(2), loc(3), xdim, winsz,&
        istart, istop, jstart, jstop, mstart, mstop )
        ! interpolate
        do i=istart,istop
            do j=jstart,jstop
                do m=mstart,mstop
                    ! calculate weight (Gaussian windowed sinc)
                    tmp = calc_weight( i, j, m, loc )
                    ! grid the Fourier data
                    if( that == 'old' )then
                        bp%s3d(s)%fvol(i,j,m) = bp%s3d(s)%fvol(i,j,m)+&
                        cmplx(real(bp%f(ptcl)%arr(h,k))*tmp,aimag(bp%f(ptcl)%arr(h,k))*tmp)
                    else
                        bp%s3d(s)%fvol_new(i,j,m) = bp%s3d(s)%fvol_new(i,j,m)+&
                        cmplx(real(bp%f(ptcl)%arr(h,k))*tmp,aimag(bp%f(ptcl)%arr(h,k))*tmp)
                    endif
                    ! grid the kernel
                    bp%s3d(s)%kernel(i,j,m) = bp%s3d(s)%kernel(i,j,m)+tmp
                end do
            end do
        end do
    end subroutine grid_fplane_comp_1
    
    subroutine grid_fplane_comp_2( h, k, s, w )
    ! grids a plane component to the Fourier volume with input weight 
        integer, intent(in) :: h, k, s
        real, intent(in)    :: w
        integer             :: i, j, m, istart, istop, jstart, jstop, mstart, mstop
        real                :: tmp, vec(3), loc(3)
        vec(1) = real(h)
        vec(2) = real(k)
        vec(3) = 0.
        loc = matmul(vec,mat)
        ! make window
        call recwin_3d( loc(1), loc(2), loc(3), xdim, winsz,&
        istart, istop, jstart, jstop, mstart, mstop )
        ! interpolate
        do i=istart,istop
            do j=jstart,jstop
                do m=mstart,mstop  
                    ! calculate weight (Gaussian windowed sinc)
                    tmp = calc_weight( i, j, m, loc )*w
                    ! grid the Fourier data
                    if( that == 'old' )then
                        bp%s3d(s)%fvol(i,j,m) = bp%s3d(s)%fvol(i,j,m)+&
                        cmplx(real(bp%f(ptcl)%arr(h,k))*tmp,aimag(bp%f(ptcl)%arr(h,k))*tmp)
                    else
                        bp%s3d(s)%fvol_new(i,j,m) = bp%s3d(s)%fvol_new(i,j,m)+&
                        cmplx(real(bp%f(ptcl)%arr(h,k))*tmp,aimag(bp%f(ptcl)%arr(h,k))*tmp)
                    endif
                    ! grid the kernel
                    bp%s3d(s)%kernel(i,j,m) = bp%s3d(s)%kernel(i,j,m)+tmp
                end do
            end do
        end do
    end subroutine grid_fplane_comp_2

    function calc_weight( i, j, m, loc ) result( w )
        integer, intent(in) :: i, j, m
        real, intent(in)    :: loc(3)
        real :: tmp1, tmp2, tmp3, btmp1, btmp2, btmp3, w
        tmp1 = sinc(real(i)-loc(1))
        tmp2 = sinc(real(j)-loc(2))
        tmp3 = sinc(real(m)-loc(3))
        btmp1 = gauwfun(real(i)-loc(1), winsz, 0.5)
        btmp2 = gauwfun(real(j)-loc(2), winsz, 0.5)
        btmp3 = gauwfun(real(m)-loc(3), winsz, 0.5)
        w = tmp1*tmp2*tmp3*btmp1*btmp2*btmp3
    end function calc_weight
    
    subroutine grid_fplane_1( e1, e2, e3, x, y, s )
        real, intent(in) :: e1, e2, e3, x, y
        integer, intent(in) :: s
        integer :: h, k
        ! set the euler to make the rotation matrix
        call set_euler(e_one, 1, e1, e2, e3)
        ! get the matrix
        call get_euler_mat(e_one, 1, mat)
        ! shift the fplane
        call shift_fplane(bp%f(ptcl)%arr, x, y)
        ! grid it onto the Fourier volume
        !$omp parallel do default(shared) private(h,k) schedule(static)
        do h=-xdim,xdim
            do k=-xdim,xdim
                call grid_fplane_comp_1( h, k, s )
            end do
        end do
        !$omp end parallel do
    end subroutine grid_fplane_1
    
    subroutine grid_fplane_2( e1, e2, e3, x, y, s, w )
        real, intent(in)    :: e1, e2, e3, x, y
        integer, intent(in) :: s
        real, intent(in)    :: w
        integer             :: h, k
        ! set the euler to make the rotation matrix
        call set_euler(e_one, 1, e1, e2, e3)
        ! get the matrix
        call get_euler_mat(e_one, 1, mat)
        ! shift the fplane
        call shift_fplane(bp%f(ptcl)%arr, x, y)
        ! grid it onto the Fourier volume
        !$omp parallel do default(shared) private(h,k) schedule(static)
        do h=-xdim,xdim
            do k=-xdim,xdim
                call grid_fplane_comp_2( h, k, s, w )
            end do
        end do
        !$omp end parallel do
    end subroutine grid_fplane_2
    
    subroutine kernel_div
        real :: fwght
        integer :: h, k, l, s
        write(*,'(A)') '>>> DIVIDING WITH THE GRIDDED KERNEL & ANTIALIASING'
        do s=1,nstates
            do h=-xdim,xdim
                do k=-xdim,xdim
                    do l=-xdim,xdim
                        if( bp%s3d(s)%kernel(h,k,l) /= 0. )then
                            fwght = taperedge( dstep, h, k, l, fny, 1.5 )
                            if( that == 'old' )then
                                bp%s3d(s)%fvol(h,k,l) = cmplx(fwght*real(bp%s3d(s)%fvol(h,k,l))/bp%s3d(s)%kernel(h,k,l),&
                                fwght*aimag(bp%s3d(s)%fvol(h,k,l))/bp%s3d(s)%kernel(h,k,l))
                            else
                                bp%s3d(s)%fvol_new(h,k,l) = cmplx(fwght*real(bp%s3d(s)%fvol_new(h,k,l))/bp%s3d(s)%kernel(h,k,l),&
                                fwght*aimag(bp%s3d(s)%fvol_new(h,k,l))/bp%s3d(s)%kernel(h,k,l))
                            endif
                        else
                            bp%s3d(s)%fvol(h,k,l) = cmplx(0,0)
                        endif
                    end do
                end do
            end do
        end do
    end subroutine kernel_div
    
    subroutine prep_new_fvols( e1, e2, e3 )
        real, intent(in) :: e1, e2, e3
        integer          :: s
        do s=1,nstates
            ! zero the target Fourier volumes
            bp%s3d(s)%fvol_new = cmplx(0.,0.)
            ! zero the kernels
            bp%s3d(s)%kernel = 0.
        end do
        ! set the euler to make the rotation matrix
        call set_euler(e_one, 1, e1, e2, e3)
        ! get the matrix
        call get_euler_mat(e_one, 1, mat)
    end subroutine prep_new_fvols
    
    subroutine rot_fvol_lp( e1, e2, e3, s )
    ! is for rotating the Fourier volumes according to input orientation
        real, intent(in)    :: e1, e2, e3
        integer, intent(in) :: s
        integer             :: h, k, l, target_to
        call prep_new_fvols( e1, e2, e3 )
        ! determine the dynamic low-pass Fourier index
        target_to = int(dstep/lp_dyn)
        if( target_to > tofny ) then
            target_to = tofny
        else if( target_to < 3 ) then
            target_to = 3
        endif
        !$omp parallel do default(shared) private(h,k,l) schedule(static)
        do h=-target_to,target_to
            do k=-target_to,target_to
                do l=-target_to,target_to
                    call grid_fvol_comp_1( h, k, l, s )
                end do
            end do
        end do
        !$omp end parallel do
    end subroutine rot_fvol_lp

    subroutine rot_fvol( e1, e2, e3, s )
    ! is for rotating the Fourier volumes according to input orientation
        real, intent(in)    :: e1, e2, e3
        integer, intent(in) :: s
        integer             :: h, k, l
        call prep_new_fvols( e1, e2, e3 )
        !$omp parallel do default(shared) private(h,k,l) schedule(static)
        do h=-xdim,xdim
            do k=-xdim,xdim
                do l=-xdim,xdim
                    call grid_fvol_comp_1( h, k, l, s )
                end do
            end do
        end do
        !$omp end parallel do
    end subroutine rot_fvol
        
    subroutine fgrid
    ! for gridding Fourier volumes according to the orientations and states in oris
        integer :: i, s
        do s=1,nstates
            ! zero the Fourier volumes
            bp%s3d(s)%fvol = cmplx(0.,0.)
            ! zero the kernels
            bp%s3d(s)%kernel = 0.
        end do
        ! loop over particles
        write(*,'(A)') '>>> GRIDDING FOURIER PLANES'
        do i=1,nptcls
            call print_bar(i, nptcls, '=')
            ! read the Fourier plane from stack
            call read_fplane(bp%f(ptcl)%arr, fstk, i)
            ! grid it
            call grid_fplane(oris(i,1), oris(i,2), oris(i,3), oris(i,4), oris(i,5), int(oris(i,6)))
        end do
        call kernel_div
    end subroutine fgrid

end module simple_fgridvol