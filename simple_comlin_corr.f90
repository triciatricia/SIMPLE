!==Class simple_comlin_corr
!
! simple_comlin_corr acts as a mediator between the builder singleton (see simple_build) and the simple_comlin
! class. The strategy is to have a non-instantatiable class (singleton) in which pointers are 
! assigned to data required for calcuating correlations. In this way, the unit in which correlations
! are calculated only need to know about the builder and this class to be able to calculate common
! line correlations. Note that in several instances bulder variables are modified by
! the method calls (see comments in the code). The code is distributed with the hope that it will be
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the GNU General 
! Public License. *Author:* Hans Elmlund, 2009-06-12.
! 
!==Changes are documented below
!
!* deugged and incorporated in the _SIMPLE_ library, HE 2009-06-25
!* changed to pivot-weighted correlation in the calc_cost_de_otl and calc_cost_de_sol functions
!
module simple_comlin_corr
use simple_eulers
use simple_comlin
use simple_build
implicit none
save

public :: make_comlin_corr, decor_comlin_corr, undecor_comlin_corr, cont_comlin_corr,&
comlin_cost_pl, comlin_cost_pl_sa, comlin_cost_de_sol, comlin_cost_de_otl, comlin_cost_de_inpl,&
comlin_score_pl_ts
private

type(build), pointer :: bp=>null()
integer, pointer     :: pbootarr(:)=>null(), pstatearr(:)=>null(), pstate=>null()
type(eulers)         :: e_one
real                 :: targ_trs(2)=0. 
logical              :: assoc=.false., decor=.false.

contains

    subroutine make_comlin_corr( b )
    ! constructs comlin_corr functionality
        type(build), intent(in), target :: b
        bp => b    
        assoc = .true.
        e_one = new_eulers(1)
    end subroutine make_comlin_corr

    subroutine decor_comlin_corr( bootarr_in, statearr_in, state_in)
    ! decorates additional functionality to the comlin_corr singleton
        integer, intent(in), optional, target :: bootarr_in(:), statearr_in(:), state_in
        if( assoc )then
            if( present(bootarr_in) )then
                pbootarr => bootarr_in
            endif
            if( present(statearr_in) )then
                if( present(state_in) )then
                    pstatearr => statearr_in
                    pstate    => state_in
                else
                    write(*,*) 'Optional argument state_in required for operation!'
                    write(*,*) 'In: decor_comlin_corr, module: simple_comlin_corr.f90'
                endif
            endif
            decor = .true.
         else
            write(*,*) 'Associate comlin_corr before decorating additional functionality!'
            write(*,*) 'In: decor_comlin_corr, module: simple_comlin_corr.f90'
            stop
        endif
    end subroutine decor_comlin_corr

    subroutine undecor_comlin_corr
    ! is for nullifying the pointers associated by decor_comlin_corr
        pstate    => null()
        pbootarr  => null()
        pstatearr => null()
        decor    = .false.
    end subroutine undecor_comlin_corr
    
    function cont_comlin_corr( e1, e2, e3, x, y ) result( corr )
    ! is for calculating the continuous common line correlation coefficient given the 
    ! _e1_, _e2_, _e3_, _x_, _y_ alignment parameters
        real, intent(in) :: e1, e2, e3, x, y
        real :: corr
        corr = -1.
        if( assoc )then
            call set_euler( e_one, 1, e1, e2, e3 )
            targ_trs(1) = x
            targ_trs(2) = y
            if( associated(pbootarr) )then
                if( associated(pstatearr) )then
                    call fix_comlins( bp%e_ref, e_one, targ_trs,bp%reftrs,&
                    .true., .true., pbootarr, pstatearr, pstate )
                    corr = corr_lines( pbootarr, pstatearr, pstate )
                else
                    call fix_comlins( bp%e_ref, e_one, targ_trs, bp%reftrs,&
                    .true., .true., pbootarr )
                    corr = corr_lines( pbootarr )
                endif
            else if( associated(pstatearr) )then
                call fix_comlins( bp%e_ref, e_one, targ_trs, bp%reftrs,&
                .true., .true., pstatearr, pstate )
                corr = corr_lines( pstatearr, pstate )
            else
                call fix_comlins( bp%e_ref, e_one, targ_trs, bp%reftrs,&
                .true., .true. )
                corr = corr_lines( )
            endif
        else
            write(*,*) 'Associate comlin_corr pointers before calculating correlation!'
            write(*,*) 'In: cont_comlin_corr_1, module: simple_comlin_corr.f90'
            stop
        endif
    end function cont_comlin_corr

    function comlin_cost_pl( vec, i, N ) result( cost )
    ! is for calcuating the continuous negative common line correlation coefficient 
    ! given the ptcl _i_, the integer alignment vector _vec_ and its dimensions (_N_,_L_). The method is used by
    ! _rad_ (reference-free alignment in a discrete angular space) in  simple_comlin_search
        integer, intent(in) :: i, N, vec(N)
        real                :: e1, e2, e3, cost
        ptcl = i ! builder ptcl value is modified
        cost = 0.
        call get_euler( bp%e, vec(i), e1, e2 )
        call get_euler( bp%e_ref, i, e3 )
        cost = -cont_comlin_corr( e1, e2, e3, 0., 0.)
    end function comlin_cost_pl
    
    function comlin_score_pl_ts( vec, i, N ) result( score )
        integer, intent(in) :: N, vec(N), i
        real                :: score
        score = -comlin_cost_pl( vec, i, N )
    end function comlin_score_pl_ts
    
    function comlin_cost_pl_sa( vec, i, N, L ) result( cost )
        integer, intent(in) :: i, N, L, vec(N,L)
        real :: cost
        cost = comlin_cost_pl( vec(:,1), i, N )
    end function comlin_cost_pl_sa
    
    function comlin_cost_de_otl( vec, D ) result( cost )
    ! is for calcuating the continuous negative common line correlation coefficient 
    ! given the alignment vector _vec_ and its size _D_. The method is used by
    ! simple_rfree_search for reference-free multiple conformations alignment.
        integer, intent(in) :: D
        real, intent(in)    :: vec(D)
        real                :: cost
        cost = -cont_comlin_corr(vec(1), vec(2) , vec(3), x=vec(4), y=vec(5))
    end function comlin_cost_de_otl
    
    function comlin_cost_de_inpl( vec, D ) result( cost )
    ! is for calcuating the continuous negative common line correlation coefficient 
    ! given the alignment vector _vec_ and its size _D_. The method is used by
    ! simple_rfree_search for reference-free multiple conformations alignment.
        integer, intent(in) :: D
        real, intent(in)    :: vec(D)
        real                :: cost, e1, e2
        call get_euler( bp%e_ref, ptcl, e1, e2 )
        cost = -cont_comlin_corr(e1, e2, vec(1), x=vec(2), y=vec(3))
    end function comlin_cost_de_inpl
    
    function comlin_cost_de_sol( vec, D ) result( cost )
    ! is for calcuating the continuous negative common line correlation coefficient 
    ! given the alignment vector _vec_ and its size _D_. The method is used by
    ! simple_rfree_search for reference-free multiple conformations alignment.
        integer, intent(in) :: D
        real, intent(in)    :: vec(D)
        real                :: cost
        cost = 1.
        if( decor )then
            pstate = int(vec(6))
            cost = -cont_comlin_corr(vec(1), vec(2) , vec(3), x=vec(4), y=vec(5))
        else
            write(*,*) 'Decorate statearr functionality before calculating correlation!'
            write(*,*) 'In: comlin_cost_de_sol, module: simple_comlin_corr.f90'
            stop
        endif
    end function comlin_cost_de_sol
    
end module simple_comlin_corr