!==Class simple_comlin
!
! simple_comlin is the central class for all common lines based alignment methods in _SIMPLE_. It contains 
! all reference and target common lines, takes care of the common lines algebra, interpolation, and provides
! basic functionality for calculation of common line correlations. Euler angle arithmetics is delegated 
! to simple_eulers, other mathemathical operations are provided by simple_math. The code is distributed with
! the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated
! by the GNU General Public License. *Author:* Hans Elmlund, 2009-06-11.
! 
!==Changes are documented below
!
!* deugged and incorporated in the _SIMPLE_ library, HE 2009-06-25
!* parallelized, needs parallel debugging, done
!* free correlation value introduced, HE March 28 2011
!* restructured according to the new regime, needs debugging, HE Aug 29 2011
!
module simple_comlin
use simple_eulers
use simple_math
use simple_jiffys
use simple_params
implicit none
save

public :: make_comlin, fix_comlins, corr_lines, kill_comlin, set_comlin_target_to
private

type line
! contains the complex vector and the extra variables _found_ (which is set true
! if a common line is found and false otherwise) and _lin_ (which holds the parametrized line found)
    complex, allocatable :: vec(:)
    logical              :: found=.false.
    real                 :: lin(2)=0.
end type line

type(line), allocatable :: ref_lines(:)
type(line), allocatable :: target_lines(:)
logical, allocatable    :: filter(:)
integer                 :: target_to=0
type(eulers)            :: e_one
type(fp), pointer       :: pfplanes(:)

interface fix_comlins
    module procedure fix_comlins_1
    module procedure fix_comlins_2
    module procedure fix_comlins_3
    module procedure fix_comlins_4
end interface

interface corr_lines
    module procedure corr_lines_1
    module procedure corr_lines_2
    module procedure corr_lines_3
    module procedure corr_lines_4
end interface

contains

    subroutine make_comlin( fpls )
    ! constructs the common lines singleton
        type(fp), intent(in), target :: fpls(nptcls)
        integer :: alloc_stat, i
        pfplanes => fpls
        call set_comlin_target_to( lp )
        allocate( ref_lines(nptcls), target_lines(nptcls), filter(nptcls), stat=alloc_stat )
        call alloc_err('In: new_comlin, module: simple_comlin.f90, alloc 1', alloc_stat)
        do i=1,nptcls
            allocate( target_lines(i)%vec(fromk:tok), ref_lines(i)%vec(fromk:tok), stat=alloc_stat )
            call alloc_err('In: new_comlin, module: simple_comlin.f90, alloc 2', alloc_stat)
            target_lines(i)%lin = 0.
            target_lines(i)%found = .false.
            ref_lines(i)%lin = 0.
            ref_lines(i)%found = .false.
        end do
        filter = .false.
    end subroutine make_comlin
    
    subroutine kill_comlin
    ! is a destructor
        integer :: i
        do i=1,nptcls
            deallocate( target_lines(i)%vec, ref_lines(i)%vec )
        end do
        deallocate(ref_lines)     
        deallocate(target_lines)
        deallocate(filter)
    end subroutine kill_comlin

    function extr_comlin_comp( pind, lin, k, x, y ) result( comp )
    ! interpolates Fourier components along a line _lin_ in FT _pfplanes(pind,:,:)_.
    ! _k_ is the resolution step along the line, _x_ & _y_ is the origin shift vec,
    ! and _comp_ is the output comp
        integer, intent(in) :: pind
        real, intent(in)    :: lin(2)
        integer, intent(in) :: k
        real, intent(in)    :: x, y
        complex             :: comp
        integer             :: i, j, istart, istop, jstart, jstop
        real                :: tmp, xa, xb  
        complex             :: shcomp, tmpcomp  
        xa = real(k)*lin(1)
        xb = real(k)*lin(2)
        comp = cmplx(0.,0.)
        ! make window
        call recwin_2d(xa, xb, xdim, winsz, istart, istop, jstart, jstop)
        ! interpolate
        do i=istart,istop
            do j=jstart,jstop
                tmp = sinc(xa-real(i))*sinc(xb-real(j))
                comp = comp+cmplx(real(pfplanes(pind)%arr(i,j))*tmp,aimag(pfplanes(pind)%arr(i,j))*tmp)
            end do
        end do
        ! origin shift
        if( x /= 0. .and. y /= 0. )then
            call origshift( xdim, xa, xb, x, y, shcomp )
            tmpcomp = comp
            comp = cmul(tmpcomp,shcomp)
        endif
    end function extr_comlin_comp

    subroutine set_comlin_target_to( lowpass )
    ! is for setting the lowpass limit of the target transform
        real, intent(in) :: lowpass
        target_to = int(dstep/lowpass)
        if( target_to > tok ) then
            target_to = tok
        else if( target_to < 3 ) then
            target_to = 3
        endif
    end subroutine set_comlin_target_to

    subroutine calc_comlin_algebra( e_ref, e_ptcl, ref )
    ! establishes algebraic expressions of the
    ! common lines in the two respective coordinate systems
        type(eulers),intent(in)     :: e_ref, e_ptcl
        integer,intent(in)          :: ref
        real                        :: normal_ref(3), normal_target(3)
        real                        :: rtot_ref(3,3), rtot_target(3,3)
        logical                     :: found
        call get_euler_normal( e_ref, ref, normal_ref )            
        call get_euler_mat( e_ref, ref, rtot_ref )
        call get_euler_normal( e_ptcl, 1, normal_target )        
        call get_euler_mat( e_ptcl, 1, rtot_target )
        call calc_common_line( normal_target, normal_ref, rtot_target,&
        rtot_ref, target_lines(ref)%lin, ref_lines(ref)%lin, found )
        ref_lines(ref)%found = found
        target_lines(ref)%found = found
    end subroutine calc_comlin_algebra
    
    subroutine fix_comlin_point( ref, targ_trs, reftrs, fixtarget, fixrefs, k )
    ! interpolates a single Fourier component on the common line
        integer,intent(in) :: ref, k
        real, intent(in)   :: targ_trs(2), reftrs(2)
        logical,intent(in) :: fixtarget, fixrefs 
        if( target_lines(ref)%found ) then
            if( fixrefs ) then
                ref_lines(ref)%vec(k) = extr_comlin_comp(ref,&
                ref_lines(ref)%lin, k, reftrs(1), reftrs(2))
            endif
            if( fixtarget ) then
                target_lines(ref)%vec(k) = extr_comlin_comp(ptcl,&
                target_lines(ref)%lin, k, targ_trs(1), targ_trs(2))
            endif
        endif
    end subroutine fix_comlin_point
    
    subroutine fix_comlin( ref, e_ref, e_ptcl, targ_trs, reftrs, fixtarget, fixrefs )
    ! calculates common line algebra and interpolates a single 
    ! target and/or reference common line
        type(eulers), intent(in) :: e_ref, e_ptcl
        integer, intent(in)      :: ref
        real, intent(in)         :: targ_trs(2), reftrs(2)
        logical, intent(in)      :: fixtarget, fixrefs
        integer                  :: k
        call calc_comlin_algebra( e_ref, e_ptcl, ref )
        if( target_lines(ref)%found )then
            do k=fromk,target_to
                call fix_comlin_point( ref, targ_trs, reftrs, fixtarget, fixrefs, k )
            end do
        endif
    end subroutine fix_comlin
    
    subroutine fix_comlins_1( e_ref, e_ptcl, targ_trs, reftrs, fixtarget, fixrefs )
    ! interpolates target and reference common lines. Optional arguments
    ! include _statearr_, _state_ (for heterogeneous reference-free alignment) and _bootarr_
    ! (for bootstrap estimation of the common line correlation)
        type(eulers), intent(in) :: e_ref, e_ptcl
        real, intent(in)         :: targ_trs(2), reftrs(nptcls,2)
        logical, intent(in)      :: fixtarget, fixrefs
        integer                  :: i
        !$omp parallel do default(shared) private(i) schedule(static)
        do i=fromr,tor
            call fix_comlin( i, e_ref, e_ptcl,&
            targ_trs, reftrs(i,:), fixtarget, fixrefs )
        end do
        !$omp end parallel do
    end subroutine fix_comlins_1

    subroutine fix_comlins_2( e_ref, e_ptcl, targ_trs,&
    reftrs, fixtarget, fixrefs, bootarr )
    ! interpolates target and reference common lines. Optional arguments
    ! include _statearr_, _state_ (for heterogeneous reference-free alignment) and _bootarr_
    ! (for bootstrap estimation of the common line correlation)
        type(eulers), intent(in)    :: e_ref, e_ptcl
        real, intent(in)            :: targ_trs(2), reftrs(nptcls,2)
        logical, intent(in)         :: fixtarget, fixrefs
        integer, intent(in)         :: bootarr(:)
        integer                     :: i
        !$omp parallel do default(shared) private(i) schedule(static)
        do i=1,size(bootarr,1)
            call fix_comlin( bootarr(i), e_ref, e_ptcl,&
            targ_trs, reftrs(bootarr(i),:), fixtarget, fixrefs )
        end do
        !$omp end parallel do
    end subroutine fix_comlins_2

    subroutine fix_comlins_3( e_ref, e_ptcl,&
    targ_trs, reftrs, fixtarget, fixrefs, statearr, state )
    ! interpolates target and reference common lines. Optional arguments
    ! include _statearr_, _state_ (for heterogeneous reference-free alignment) and _bootarr_
    ! (for bootstrap estimation of the common line correlation)
        type(eulers), intent(in)    :: e_ref, e_ptcl
        real, intent(in)            :: targ_trs(2), reftrs(nptcls,2)
        logical, intent(in)         :: fixtarget, fixrefs
        integer, intent(in)         :: statearr(nptcls), state
        integer                     :: i
        !$omp parallel do default(shared) private(i) schedule(static)
        do i=fromr,tor
            if( statearr(i) == state ) then
                call fix_comlin( i, e_ref, e_ptcl,&
                targ_trs, reftrs(i,:), fixtarget, fixrefs )
            endif
        end do
        !$omp end parallel do
    end subroutine fix_comlins_3

    subroutine fix_comlins_4( e_ref, e_ptcl,&
    targ_trs, reftrs, fixtarget, fixrefs, bootarr, statearr, state )
    ! interpolates target and reference common lines. Optional arguments
    ! include _statearr_, _state_ (for heterogeneous reference-free alignment) and _bootarr_
    ! (for bootstrap estimation of the common line correlation)
        type(eulers), intent(in)    :: e_ref, e_ptcl
        real, intent(in)            :: targ_trs(2), reftrs(nptcls,2)
        logical, intent(in)         :: fixtarget, fixrefs
        integer, intent(in)         :: bootarr(:), statearr(nptcls), state
        integer                     :: i
        !$omp parallel do default(shared) private(i) schedule(static)
        do i=1,size(bootarr,1)
            if( statearr(bootarr(i)) == state ) then
                call fix_comlin( bootarr(i), e_ref, e_ptcl,&
                targ_trs, reftrs(bootarr(i),:), fixtarget, fixrefs )
            endif
        end do
        !$omp end parallel do
    end subroutine fix_comlins_4

    function corr_lines_1( ) result( corr )
    ! calcluates common line correlation  
        real    :: corr, tmp
        integer :: i, numlines
        corr = -1.
        tmp = 0.
        numlines = 0
        filter = .false.
        do i=fromr,tor
            if( target_lines(i)%found .and. i /= notref ) then
                numlines = numlines+1
                filter(i) = .true.
            endif
        end do
        tmp = corr_lines_basic( )
        if( numlines > 1 ) then ! must be three planes to define an angular orientation
            corr = tmp
        endif
    end function corr_lines_1

    function corr_lines_2( bootarr ) result( corr )
    ! calcluates common line correlation
        integer, intent(in) :: bootarr(:)
        real                :: corr, tmp
        integer             :: i, numlines
        corr = -1.
        tmp = 0.
        numlines = 0
        filter = .false.
        do i=1,size(bootarr,1)
            if( target_lines(bootarr(i))%found .and. bootarr(i) /= notref ) then
                numlines = numlines+1
                filter(bootarr(i)) = .true.
            endif      
        end do
        tmp = corr_lines_basic( )
        if( numlines > 1 ) then ! must be three planes to define an angular orientation
            corr = tmp
        endif
    end function corr_lines_2

    function corr_lines_3( statearr, state ) result( corr )
    ! calcluates common line correlation 
        integer, intent(in) :: statearr(nptcls), state
        real                :: corr, tmp
        integer             :: i, numlines
        corr = -1.
        tmp = 0.
        numlines = 0
        filter = .false.
        do i=fromr,tor
            if( target_lines(i)%found .and. i /= notref .and. statearr(i) == state ) then
                numlines = numlines+1
                filter(i) = .true.
            endif
        end do
        tmp = corr_lines_basic( )
        if( numlines > 1 ) then ! must be three planes to define an angular orientation
            corr = tmp
        endif
    end function corr_lines_3

    function corr_lines_4( bootarr, statearr, state ) result( corr )
    ! calcluates common line correlation
        integer, intent(in) :: bootarr(:), statearr(nptcls), state
        real                :: corr, tmp
        integer             :: i, numlines
        corr = -1.
        tmp = 0.
        numlines = 0
        filter = .false.
        do i=1,size(bootarr,1)
            if( target_lines(bootarr(i))%found .and. &
            bootarr(i) /= notref .and. statearr(bootarr(i)) == state ) then
                numlines = numlines+1
                filter(bootarr(i)) = .true.
            endif  
        end do
        tmp = corr_lines_basic( )       
        if( numlines > 1 ) then ! must be three planes to define an angular orientation
            corr = tmp
        endif
    end function corr_lines_4
    
    function corr_lines_basic( ) result( corr )
    ! calculates the Pearson correlation coefficient in complex space between the reference and target lines
        real :: corr, sumasq, sumbsq, sqrtprod
        integer :: k, i        
        corr   = 0.
        sumasq = 0.
        sumbsq = 0.
        !$omp parallel do default(shared) private(i,k) &
        !$omp reduction(+:corr,sumasq,sumbsq) schedule(static)
        do i=1,nptcls
            if( filter(i) )then
                do k=fromk,target_to
                    ! real part of the complex mult btw a and b*
                    corr = corr+real(ref_lines(i)%vec(k))*real(target_lines(i)%vec(k))+&
                    aimag(ref_lines(i)%vec(k))*aimag(target_lines(i)%vec(k))
                    sumasq = sumasq+csqsum(ref_lines(i)%vec(k))         
                    sumbsq = sumbsq+csqsum(target_lines(i)%vec(k))
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
    end function corr_lines_basic
    
end module simple_comlin