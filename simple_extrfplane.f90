module simple_extrfplane
use simple_eulers
use simple_params
use simple_math
use simple_build
use simple_def_precision
implicit none
save
! THIS SHOULD BE A SUBMODULE OF FPLANES CORR
public :: make_extrfplane, extr_fplane
private

type(build), pointer :: bp=>null()
type(eulers)         :: e_one
real                 :: mat(3,3)

contains

    subroutine make_extrfplane( b )
    ! associates pointer to builder, makes single Euler, and allocates data
        type(build), intent(in), target :: b
        bp => b
        e_one = new_eulers(1)
    end subroutine make_extrfplane
    
    subroutine extr_fvol_comp( h, k, x, y )
    ! is for interpolating a Fourier component from the Fourier volume state,
    ! _h_ & _k_ are the reciprocal indices, _x_ & _y_ is the origin shift vec
    !* choice=1: sinc window
    !* choice=2 gauwindowed sinc
    !* choice=else bmanwindowed sinc  
        integer, intent(in) :: h, k
        real, intent(in)    :: x, y
        integer             :: i, j, l, istart, istop, jstart, jstop, lstart, lstop
        real                :: tmp1, tmp2, tmp3, btmp1, btmp2, btmp3, vec(3), loc(3), tmp, arg
        vec(1) = real(h)
        vec(2) = real(k)
        vec(3) = 0.
        loc = matmul(vec,mat)
        bp%frefs(1)%arr(h,k) = cmplx(0.,0.)
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
                    bp%frefs(1)%arr(h,k) = bp%frefs(1)%arr(h,k)+cmplx(real(bp%s3d(state)%fvol(i,j,l))*tmp,aimag(bp%s3d(state)%fvol(i,j,l))*tmp)
                end do
            end do
        end do
        if( x /= 0. .and. y /= 0. )then
            arg = (-twopi/real(box))*(x*real(h)+y*real(k))
            bp%frefs(1)%arr(h,k) = bp%frefs(1)%arr(h,k)*cmplx(cos(arg),sin(arg))
        endif
    end subroutine extr_fvol_comp
    
    subroutine extr_fplane( e1, e2, e3, x, y, target_to )
    ! is for extracting a Fourier plane from the volume
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
                call extr_fvol_comp( h, k, x, y )
            end do
        end do
        !$omp end parallel do
    end subroutine extr_fplane

end module simple_extrfplane