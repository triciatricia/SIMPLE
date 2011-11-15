module simple_dock
use simple_eulers
use simple_jiffys
use simple_build
use simple_params
use simple_de_opt
use simple_fvols_corr
use simple_heapsort
use simple_math
use simple_volspi
use simple_syscalls
use simple_fgridvol
implicit none
save

! set optlims in params


public :: make_dock, dock_fvols
private

type(build), pointer :: bp=>null() ! pointer to builder
type(de_opt)         :: nasty      ! differential evolution object

contains

    subroutine make_dock( b )
        type(build), intent(in), target :: b
        real :: rslask
        ! setting nbest to 3*10+10
        nbest = 40
        ! make the differential evolution optimization obj
        nasty = new_de_opt( 3, optlims(:3,:), nbest, neigh, cyclic=cyclic(:3) )
        ! make fvols corr obj
        call make_fvols_corr( b )
        ! make gridding functionality
        call make_fgridvol( b, 'old' )
        ! Assign ptr to builder in this object
        bp => b
    end subroutine make_dock

    subroutine exhaustive_proj_dock( refvol, targvol, e3 )
    ! is for exhaustive projection direction search
        integer, intent(in) :: refvol, targvol
        real, intent(in)    :: e3
        real                :: e1, e2, corr, rsol(3), rslask
        integer             :: j
        ! set ref and targ in fvos_corr obj
        call set_volpair( refvol, targvol )
        do j=1,nspace! projection direction loop
            call get_euler( bp%e, j, e1, e2, rslask )
            rsol(1) = e1
            rsol(2) = e2
            rsol(3) = e3
            corr = corr_fvols( e1, e2, e3 )    
            call set_heapsort( bp%hso, j, corr, rarr=rsol )
        end do
        rsol = 0.
        do j=nspace+1,ninpl*nspace
            call set_heapsort( bp%hso, j, -1., rarr=rsol )
        end do
        call sort_heapsort( bp%hso )
    end subroutine exhaustive_proj_dock

    subroutine de_refine_dock( refvol, targvol, e1, e2, e3, lowpass, cost )
    ! is for global template-based refinement given an input solution population
        integer, intent(in)         :: refvol, targvol
        real, intent(out)           :: e1, e2, e3
        real, intent(in)            :: lowpass
        real, intent(out), optional :: cost
        real                        :: rsol(3), cost_here
        ! set ref and targ in fvos_corr obj
        call set_volpair( refvol, targvol )
        ! set dynamic lowpass
        lp_dyn = lowpass
        ! re-init de-obj
        call re_init_de_opt( nasty, optlims(:3,:) )
        call de_cont_min( nasty, cost_fvols, 200, 0.0001, rsol, cost_here )
        e1 = rsol(1) 
        e2 = rsol(2)
        e3 = rsol(3)
        if( present(cost) )then
            cost = cost_here
        endif
    end subroutine de_refine_dock

    subroutine dock_fvols( refvol, targvol, round )
    ! center the volumes according to center of mass first
    ! Fourier transform and run this routine
        integer, intent(in) :: refvol, targvol, round
        real :: e1, e2, e3, corr, rslask, rsol(3), cost
        integer, parameter :: filnum=67 
        integer :: k
        ! set lowpass lim
        lp_dyn = lp        
        write(*,'(a)') '>>> CONTINUOUS SEARCH OVER ALL DEGREES OF FREEDOM'
        call de_refine_dock( refvol, targvol, e1, e2, e3, lp, cost )
        call set_aligndata( bp%a, round, e1=e1, e2=e2, e3=e3, corr=-cost )
    end subroutine dock_fvols

end module simple_dock