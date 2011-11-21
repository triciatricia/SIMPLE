!==Class simple_rfree_search
!
! The simple_rfree_search singleton provides the reference free alignment/heterogeneity analysis functionality in the _SIMPLE_ library.
! Search strategies include exhaustive approaches, Monte Carlo, and directed search via differential evolution optimization. The composite
! object inherits functionality for storing output data, generating random numbers, CPU time checking and calculation of correlations.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated
! by the GNU General Public License. *Author:* Hans Elmlund, 2009-06-11.
!
!==Changes are documented below
!
module simple_rfree_search
use simple_build
use simple_params
use simple_de_opt
use simple_sa_opt
use simple_aligndata
use simple_comlin_corr
use simple_fplanes_corr
use simple_rnd
use simple_ran_tabu
use simple_ts_opt
use simple_syscalls
use simple_math
use simple_jiffys
implicit none
save

public :: make_rfree_search, angreconst, sa_rad, comlin_state_assignment, rfree_de_ori_refinement, ts_rad
private

type(build), pointer :: bp=>null()          ! pointer to builder
type(de_opt)         :: nasty               ! differential evolution objects
type(sa_opt)         :: metro               ! simulated annealing object 
type(ts_opt)         :: ts                  ! tabu search object
type(ran_tabu)       :: tab                 ! for making random numbers
integer, allocatable :: isol(:,:), inpls(:)
integer              :: N_boot=100

contains

    subroutine make_rfree_search( b )
        type(build), intent(inout), target :: b
        integer :: i, alloc_stat, params(1)
        logical :: nevars(1)
        real :: e1, e2, e3
        ! Allocate
        allocate(isol(nptcls,1), inpls(nptcls), stat=alloc_stat )
        call alloc_err( 'In: make_rfree_search, module: simple_rfree_search.f90, alloc 1', alloc_stat)   
        isol  = 0
        inpls = 1
        ! make comlin_corr functionality
        call make_comlin_corr( b )
        ! set ponter to build
        bp => b
        ! Set lowpass limit
        call set_comlin_target_to( lp )
        ! Make simulated annealing functionality 
        params(1) = nspace
        nevars(1) = .true.
        metro = new_sa_opt( params, nevars, nptcls, 1 )
        call get_sa_solution( metro, isol )
        ! Initialize b%e_ref according to initial random solution
        do i=1,nptcls
            call get_euler( b%e, isol(i,1), e1, e2, e3 )  
            call set_euler( b%e_ref, i, e1, e2, 0. )
            oris(i,1) = e1
            oris(i,2) = e2
            oris(i,3) = 0.
        end do
        ! create what is needed for the TS
        ts = new_ts_opt(nptcls, params=params(1), nevars=nevars(1))
        tab = new_ran_tabu( nptcls )
        ! Make differential evolution functionality
        if( nstates > 1 )then
            ! Optimization over 6 df
            nasty = new_de_opt( 6, optlims, nbest, neigh, cyclic=cyclic )
        else
            ! Optimization over 5 df
            nasty = new_de_opt( 5, optlims(:5,:), nbest, neigh, cyclic=cyclic(:5) )
        endif
    end subroutine make_rfree_search           
            
    subroutine sa_rad
    ! is the simulated annealing based algorithm "Reference-free 3D Alignment in a Discrete angular space"
    !* Elmlund H. et al. "A new cryo-EM single-particle _ab_ _initio_ reconstruction method visualizes 
    ! secondary structure elements in an ATP-fueled AAA+ motor" J. Mol. Biol. 2008 Jan 25;375(4):934-47.
        integer :: i
        real    :: e1, e2, e3, cost
        ! anneal, here the cost function comlin_cost_pl_sa takes care of modifying the ptcl var
        call sa_comb_min_param( metro, comlin_cost_pl_sa, update_e_ref, statefun,&
        0.0001, 1000000., 0.9, 500, 0.5, .true., .true., isol, cost )
        do i=1,nptcls
            call get_euler( bp%e, isol(i,1), e1, e2, e3 )
            call set_euler( bp%e_ref, i, e1, e2, 0. )
            oris(i,1) = e1
            oris(i,2) = e2
            oris(i,3) = 0.
            oris(i,4) = 0.
            oris(i,5) = 0.
            call set_aligndata( bp%a, i, e1=e1, e2=e2, e3=0., x=0., y=0., corr=-cost, state=1 )
        end do
    end subroutine sa_rad
    
    subroutine ts_rad
    ! is the simulated annealing based algorithm "Reference-free 3D Alignment in a Discrete angular space"
    !* Elmlund H. et al. "A new cryo-EM single-particle _ab_ _initio_ reconstruction method visualizes 
    ! secondary structure elements in an ATP-fueled AAA+ motor" J. Mol. Biol. 2008 Jan 25;375(4):934-47.
        integer :: i
        real    :: e1, e2, e3, cost
        call ts_comb_max( ts, comlin_score_pl_ts, update_e_ref2, 3, isol(:,1), isol(:,1) )
        do i=1,nptcls
            call get_euler( bp%e, isol(i,1), e1, e2, e3 )
            call set_euler( bp%e_ref, i, e1, e2, 0. )
            oris(i,1) = e1
            oris(i,2) = e2
            oris(i,3) = 0.
            oris(i,4) = 0.
            oris(i,5) = 0.
            call set_aligndata( bp%a, i, e1=e1, e2=e2, e3=0., x=0., y=0., corr=-cost, state=1 )
        end do
    end subroutine ts_rad
    
    subroutine update_bootarr
    ! is for updating the bootstrap sample during annealing. This method is used by statefun
    ! (defined below) as a callback in the RAD annealing. The strategy is to have a small sample 
    ! size at high temperature and increase the sample size during the annealing (to speed things 
    ! up and improve the accuracy of the low temperature alignment)
        integer :: alloc_stat
        if( associated(bp%bootarr) )then
            deallocate(bp%bootarr)
        endif
        allocate( bp%bootarr(N_boot), stat=alloc_stat )
        call alloc_err( 'In: update_bootarr, module: simple_rfree_search.f90', alloc_stat)
        call reset_ran_tabu( tab )
        call ne_ran_iarr( tab, bp%bootarr ) ! bootstrap sample update
        ! Now, decorate bootstrap estimation functionality to the comlin_corr object
        call decor_comlin_corr( bootarr_in=bp%bootarr )
    end subroutine update_bootarr

    subroutine update_e_ref( vec, i, L )
    ! is for updating the Euler angles in _e_ref_ when a configuration is accepted in the RAD
    ! annealing (by using it as a callback)
        integer, intent(in) ::  i, L, vec(L)
        real                :: e1, e2, e3
        call get_euler( bp%e, vec(1), e1, e2, e3 )
        call set_euler( bp%e_ref, i, e1, e2, 0. )
    end subroutine update_e_ref
    
    subroutine update_e_ref2( val, i )
    ! is for updating the Euler angles in _e_ref_ when a configuration is accepted in the RAD
    ! annealing (by using it as a callback)
        integer, intent(in) ::  val, i
        real                :: e1, e2, e3
        call get_euler( bp%e, val, e1, e2, e3 )
        call set_euler( bp%e_ref, i, e1, e2, 0. )
    end subroutine update_e_ref2
    
    subroutine statefun( T, T_init )
    ! is for temperature dependent update of the lowpass limit used for calculating the common line
    ! correlation. statefun also updates the bootstrap sample and it is used as a callback in the RAD annealing. 
        real, intent(in) :: T, T_init
        real :: fract, resfact, dynlim
        ! Temperature dependent update of the low-pass limit
        fract = log(T)/log(T_init)
        if( fract > 0. ) then
            resfact = fract*(hp/2.-lp)
        else
            resfact = 0.
        endif
        dynlim = lp+resfact
        call set_comlin_target_to( dynlim )
!        write(*,'(A,F7.2)') 'LOW-PASS LIMIT (A): ', dynlim
        ! Temperature dependent bootstrap sample update
        if( T > 1. ) then
            N_boot = min(nptcls,min(100,int((1./log(T))*100.)))
        else
            N_boot = min(nptcls,100)
        endif
!        write(*,'(A,I3)') 'STOCHASTIC SAMPLE SIZE: ', N_boot
        call update_bootarr
    end subroutine statefun

    subroutine comlin_state_assignment
    ! is for assinging conformational states to aligned ptcls by GRASP
        integer :: it, imax(1), statearr_prev(nptcls), i, s
        real    :: e1, e2, e3, x, y, corrs(nstates), corr_this, corr_prev
        if( nstates > 1 )then
            write(*,'(A)') '>>> STATE ASSIGNMENT BY GRASP'
            ! Now, decorate statearr functionality to the comlin_corr object
            call decor_comlin_corr( statearr_in=bp%statearr, state_in=state )
            ! assign random states
            call ran_iarr( bp%statearr, nstates )
            ! init local search
            corr_this = -1.
            it = 0
            do ! local search
                it = it+1
                corr_prev = corr_this
                statearr_prev = bp%statearr
                corr_this = 0.
                call update_bootarr
                do i=1,nptcls
                    ptcl = i
                    do s=1,nstates
                        state = s ! modifying the state var in comlin_corr
                        e1 = oris(ptcl,1)
                        e2 = oris(ptcl,2)
                        e3 = oris(ptcl,3)
                        x = oris(ptcl,4)
                        y = oris(ptcl,5)
                        corrs(state) = cont_comlin_corr( e1, e2, e3, x, y )
                    end do
                    imax = maxloc(corrs)
                    corr_this = corr_this+corrs(imax(1))
                    bp%statearr(i) = imax(1)
                    
                end do            
                if( corr_this > corr_prev ) then
                    write(*,*) 'ITERATION: ', it, ' CORR: ', corr_this
                    cycle
                else
                    exit
                endif
            end do
            bp%statearr = statearr_prev
            do i=1,nptcls
                oris(i,6) = real(bp%statearr(i))
                call set_aligndata( bp%a, i, state=bp%statearr(i) )
            end do
         endif
    end subroutine comlin_state_assignment
    
    subroutine angreconst( p1, p2, p3 )
    ! what needs to be adressed here is the selection of the first three
    ! need two versions: one that selects the three worst correlating (by selecting the worst pair
    ! and then selecting the one that
        integer, intent(in) :: p1, p2, p3
        integer        :: i, j, k, ji, ii, loc(4), loc2(2) !p(nptcls)
        type(ran_tabu) :: rt
        real           :: ea1, ea2, ea3, eb1, eb2, eb3, vec(6), rslask, score, best_score
        real           :: corrs2(nspace,360)
        write(*,'(A)') '>>> ANGULAR RECONSTITUTION'
        isol = 0
        ! decorate statearr functionality to the comlin_corr object
        call decor_comlin_corr( statearr_in=bp%statearr, state_in=state )
!         generate a random search order
!        rt = new_ran_tabu( nptcls )
!        call ne_ran_iarr( rt, p )
!        call kill_ran_tabu( rt )
        ! make sure that the first projection has state 1 and all others state 2
        bp%statearr = 2 ! note that this is array assignment
        bp%statearr(p1) = 1
        ! make structure to maintain solution feasibility
        rt = new_ran_tabu( nspace )
        ! put the first projection in orientation 1 and zero inplane
        call get_euler( bp%e, 1, ea1, ea2, ea3 )
        call set_euler( bp%e_ref, p1, ea1, ea2, 0. )
        isol(p1,1) = 1
        inpls(p1)  = 1
        call insert_ran_tabu( rt, 1 )
        ! do the angular reconstitution
        ! include two additional planes in the corr calculation
        bp%statearr(p2) = 1
        bp%statearr(p3) = 1
        ! set particle index
        ptcl = p2
        ! test all possible configurations of the two planes
        best_score = -1.
        do i=2,nspace
            call print_bar( i, nspace, '=' )
            ! get projection direction for p2
            call get_euler( bp%e, i, ea1, ea2 )
            do ii=1,360,10
                ! calc in-plane angle for p2
                ea3 = real(ii-1)
                do j=2,nspace
                    ! get projection direction for p3
                    call get_euler( bp%e, i, eb1, eb2 )
                    do ji=1,360,10
                        ! calc in-plane angle for p3
                        eb3 = real(ji-1)
                        if( i /= j )then
                            ! set orientations
                            call set_euler( bp%e_ref, p2, ea1, ea2, ea3 ) 
                            call set_euler( bp%e_ref, p3, eb1, eb2, eb3 ) 
                            vec(1) = ea1
                            vec(2) = ea2
                            vec(3) = ea3
                            vec(4) = 0.
                            vec(5) = 0.
                            vec(6) = 1.
                            score = -comlin_cost_de_sol( vec, 6 )
                            if( score > best_score )then
                                loc(1) = i
                                loc(2) = ii
                                loc(3) = j
                                loc(4) = ji
                                best_score = score
                            endif
                        endif
                    end do
                end do
            end do
        end do
        ! get the best move     
        isol(p2,1) = loc(1)
        inpls(p2)  = loc(2)
        isol(p3,1) = loc(3)
        inpls(p3)  = loc(4)
        call get_euler( bp%e, loc(1), ea1, ea2 )
        call set_euler( bp%e_ref, p2, ea1, ea2 )
        call set_euler( bp%e_ref, p2, real(inpls(p2)-1) )
        call get_euler( bp%e, loc(3), eb1, eb2 )
        call set_euler( bp%e_ref, p3, eb1, eb2 )
        call set_euler( bp%e_ref, p3, real(inpls(p3)-1) )
        ! filter the orientations found       
        call insert_ran_tabu( rt, isol(p2,1) )
        call insert_ran_tabu( rt, isol(p3,1) )
        ! now, do one round of alignment of all projections to the ones that have been aligned
        write(*,'(A)') '>>> FULL ALIGNMENT'
        do i=1,nptcls
            call print_bar( i, nspace, '=' )
            ptcl = i
            if( isol(i,1) /= 0 )then
                call remove_ran_tabu( rt, isol(i,1) )
            endif
            corrs2 = -1.
            do j=1,nspace
                if( is_ran_tabu(rt,j) ) then ! forbidden move
                    cycle
                endif
                ! get projection direction
                call get_euler( bp%e, j, ea1, ea2 )
                do k=1,360,10
                    ! set in-plane angle
                    ea3 = real(k-1)
                    ! set particle index and orientation
                    call set_euler( bp%e_ref, i, ea1, ea2, ea3 )                   
                    vec(1) = ea1
                    vec(2) = ea2
                    vec(3) = ea3
                    vec(4) = 0.
                    vec(5) = 0.
                    vec(6) = 1.
                    corrs2(j,k) = -comlin_cost_de_sol( vec, 6 )
                end do
            end do
            ! get the best move
            loc2 = maxloc(corrs2)
            ! store the orientation found
            isol(i,1) = loc2(1)
            call get_euler( bp%e, loc2(1), ea1, ea2 )
            inpls(i) = loc2(2)
            ea3 = real(loc2(2)-1)
            call set_euler( bp%e_ref, i, ea1, ea2, ea3 )
            oris(i,1) = ea1
            oris(i,2) = ea2
            oris(i,3) = ea3
            call set_aligndata( bp%a, i, e1=ea1, e2=ea2, e3=ea3 )
            ! filter the orientation found       
            call insert_ran_tabu( rt, isol(i,1) )
            ! include this particle in the corr calculation
!            bp%statearr(i) = 1
        end do
        ! remove decoration from the comlin_corr object
        call undecor_comlin_corr
        ! kill structure for maintaining solution feasibility
        call kill_ran_tabu( rt )
        ! Get the actual and relative cpu-time
        rslask = getabscpu( .true. )
        rslask = getdiffcpu( .true. )
    end subroutine angreconst

    subroutine rfree_de_ori_refinement
    ! is for refining input orientation(s) and state assignment using differential
    ! evolution-based local search iteratively until convergence. The method is used in 
    ! reference-free alignment for refining the discrete angular solution obtained by RAD 
    ! in an orientation continuum.
        integer :: i, round, s
        logical :: frozen
        real    :: corr_this, corr_prev, e1, e2, e3, x, y
        real    :: corrs(nptcls), corrs_copy(nptcls), rslask, cost, oris_copy(nptcls,6)
        ! set bootstrap sample size
        N_boot = min(nptcls,100)
        ! Initialization
        if( nstates > 1 )then
            ! decorate statearr functionality to the comlin_corr object
            call decor_comlin_corr( statearr_in=bp%statearr, state_in=state )
        endif
        ! set low-pass limit
        call set_comlin_target_to( lp )
        write(*,'(A)') '>>> CONTINUOUS REFINEMENT BY DE'      
        round = 0
        frozen = .false.
        corrs = 0.
        corrs_copy = 0.
        corr_this = -1.
        do while( .not. frozen )
            round = round+1
            oris_copy = oris
            corrs_copy = corrs
            call update_bootarr
            write(*,'(A,I2)') 'ITERATION: ', round     
            do i=1,nptcls
                call print_bar( i, nptcls, '=' )
                ptcl = i
                e1 = oris_copy(i,1)
                e2 = oris_copy(i,2)
                e3 = oris_copy(i,3)
                x = oris_copy(i,4)
                y = oris_copy(i,5)
                call de_ori_refinement_rfree( e1, e2, e3, x, y, s, angres, cost )
                corrs(i) = -cost
                oris_copy(i,1) = e1
                oris_copy(i,2) = e2
                oris_copy(i,3) = e3
                oris_copy(i,4) = x
                oris_copy(i,5) = y
                oris_copy(i,6) = real(s)
                call set_euler( bp%e_ref, i, e1, e2, e3 )
                bp%reftrs(i,1) = x
                bp%reftrs(i,2) = y
                bp%statearr(i) = s
            end do     
            ! Get the actual and relative cpu-time
            rslask = getabscpu( .true. )
            rslask = getdiffcpu( .true. )
            corr_prev = corr_this
            corr_this = sum(corrs)/real(nptcls)
            write(*,'(A,F7.4)') 'CORR: ', corr_this
            if( corr_this > corr_prev ) then
                ! still improving
                frozen = .false.
                ! store the best orientations
                oris = oris_copy
                ! store the best correlations
                corrs = corrs_copy
            else
                ! previous round is the converged
                write(*,'(A,F7.4)') 'CONVERGED AT CORR: ', corr_prev
                if( nstates <= 1 ) oris(:,6) = 1
                do i=1,nptcls
                    call set_aligndata( bp%a, i, e1=oris(i,1), e2=oris(i,2), e3=oris(i,3),&
                    x=oris(i,4), y=oris(i,5), corr=corrs(i), state=int(oris(i,6)) )
                end do
                frozen = .true.
            endif        
        end do

        contains
        
            subroutine de_ori_refinement_rfree( e1, e2, e3, x, y, s, tres, cost )
                ! is for refining input orientation(s) and initial state assignment using differential
                ! evolution-based local search, for use in reference-free and reference-based alignment 
                real, intent(inout)    :: e1, e2, e3, x, y, cost
                integer, intent(inout) :: s
                real, intent(in)       :: tres
                real                   :: opt_limits(6,2), rsol(6)
                ! determine optimization limits
                call mkoptlims( e1, e2, e3, x, y, tres, opt_limits )
                if( nstates > 1 )then 
                    ! reference-free refinement, multiple conformations
                    ! Decorate statearr functionality to the comlin_corr object
                    call decor_comlin_corr( statearr_in=bp%statearr, state_in=state )
                    ! The comlin_cost_de_sol method in calc_comlin_corr will modify the state variable
                    call re_init_de_opt( nasty, opt_limits )
                    call de_cont_min( nasty, comlin_cost_de_sol, 20, 0.0001, rsol, cost )
                    s = int(rsol(6))
                else
                    call re_init_de_opt( nasty, opt_limits(:5,:) )
                    call de_cont_min( nasty, comlin_cost_de_otl, 20, 0.0001, rsol(:5), cost )
                    s = 1
                endif          
                e1 = rsol(1) 
                e2 = rsol(2)
                e3 = rsol(3)
                x  = rsol(4)
                y  = rsol(5)
            end subroutine de_ori_refinement_rfree
           
    end subroutine rfree_de_ori_refinement

end module simple_rfree_search