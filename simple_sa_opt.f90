!==Class simple_sa_opt
!
! simple_sa_opt performs cobinatorial minimization of an externally defined function by simulated annealing
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution or modification is regulated by the GNU General Public License. 
! *Author:* Hans Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_sa_opt
use simple_syscalls
use simple_rnd
use simple_ran_tabu
use simple_math
use simple_jiffys
implicit none

public :: sa_opt, new_sa_opt, kill_sa_opt, get_sa_solution, sa_comb_min_param ! pt_comb_min_param
private

type sa_opt
! contains all data needed for the annealing
    private
    type(ran_tabu), allocatable :: rt(:)
    integer, allocatable :: vec(:,:), vec_perm(:,:)
    real, allocatable    :: cost(:), cost_perm(:)
    integer, allocatable :: params(:) ! tabulist
    logical, allocatable :: nevars(:) ! variables that should not be equal
    integer :: N=0, L=0 
    logical :: exists=.false., frozen=.false.
end type sa_opt

integer :: nprobs ! number of probabilities calculated at one temperature level
real :: avgprob ! average probability at one temperature level

contains

    function new_sa_opt( params, nevars, N, L ) result( num )
    ! is a constructor that allocates what is needed and makes an inital feasible random solution
        type(sa_opt)        :: num
        integer, intent(in) :: N ! nr of individuals to optimize
        integer, intent(in) :: L ! vector length (problem dimensionality)
        integer, intent(in) :: params(L) ! array with nr of params per discrete variable
        logical, intent(in) :: nevars(L) ! indicates which variables that are not allowed to be equal to each other
        integer             :: alloc_stat, i, j       
        allocate( num%vec(N,L), num%vec_perm(N,L), num%cost(N),num%cost_perm(N),&
        num%params(L), num%nevars(L), num%rt(L), stat=alloc_stat)
        call alloc_err('In: new_sa_opt, module: simple_sa_opt', alloc_stat)
        num%params = params
        num%nevars = nevars
        num%N      = N
        num%L      = L
        do j=1,L
            if( params(j) < 2 )then
                write(*,*) 'Nr of params for variable',j,'is less than 2, which is not allowed!'
                write(*,*) 'In: new_sa_opt, module: simple_sa_opt'
                stop
            endif
            if( nevars(j) ) then
                num%rt(j) = new_ran_tabu( params(j) )
            endif
            do i=1,N
                if( nevars(j) ) then
                    num%vec(i,j)      = irnd_uni_tabu( num%rt(j) )
                    call insert_ran_tabu( num%rt(j), num%vec(i,j) )
                    num%vec_perm(i,j) = num%vec(i,j)
                else
                    num%vec(i,j)      = irnd_uni( params(j) )
                    num%vec_perm(i,j) = num%vec(i,j)
                endif
            end do
        end do
        num%exists = .true.
    end function new_sa_opt

    subroutine kill_sa_opt( num )
    ! is a destructor
        type(sa_opt) :: num
        integer      :: j
        if( num%exists )then
            do j=1,num%L
                if( num%nevars(j) ) then
                    call kill_ran_tabu(num%rt(j))
                endif
            end do
            deallocate( num%vec, num%vec_perm, num%cost,&
            num%cost_perm, num%params, num%nevars, num%rt )   
            num%exists = .false.
        endif
    end subroutine kill_sa_opt

    subroutine get_sa_solution( num, out_solution )
    ! is for getting the final solution out
        type(sa_opt) :: num
        integer, intent(out) :: out_solution(num%N,num%L)
        out_solution =  num%vec
    end subroutine get_sa_solution

    subroutine sa_comb_min_param( num, costfun, permfun, statefun,&
    cost_err, T_init, TC, max_rearr, T_lowlim, use_permfun, use_statefun,&
    out_solution, cost ) 
    ! is the combinatorial minimization. I have found the params defined by Kirkpatrick to work well: 
    ! _T_init_=_1_._000_._000_, _TC_=_0_._9_, _max_rearr_=_10_**_L_*_N_, and 
    ! _T_lowlim_=_0_._01_. The parameter _max_rearr_ (maximum number of rearrangements at each _T_-level) affects 
    ! performance and CPU time most, requires testing for specific problems. 29 Dec 2008, implemented observer 
    ! functions, to map the configuration changes and perform temperature dependent external changes, 
    ! see simple_comlin_search
        type( sa_opt ) :: num
        interface 
            function costfun( vec, i, N, L ) result( cost )
                integer, intent(in) ::  N, L, vec(N,L), i
                real                :: cost
            end function costfun
            subroutine permfun( vec, i, L )
                integer, intent(in) :: L, vec(L), i
            end subroutine permfun
            subroutine statefun( T, Tinit )
                real, intent(in) :: T, Tinit
            end subroutine statefun
        end interface
        real, intent(in)     :: cost_err,  T_init, TC, T_lowlim
        integer, intent(in)  :: max_rearr
        logical, intent(in)  :: use_permfun, use_statefun
        integer, intent(out) :: out_solution(num%N,num%L)
        real, intent(out)    :: cost
        real                 :: joint_cost, T, costs(2)
        integer              :: it, convergence, mits
        logical              :: frozen
        ! Initialization of variables
        call seed_rnd
        T           = T_init
        frozen      = .false. ! To check if frozen
        it          = 0 ! Iteration counter
        convergence = 0 ! To check convergence
        costs       = 99999.! To check convergence
        mits        = nits()
        write(*,'(A)') '>>> ANNEALING_STARTS'
!        write(*,'(A)') '***************************'
        do while (frozen .neqv. .true.)
            it            = it+1
            call print_bar( it, mits, '=' )
            if( use_statefun ) then 
                call statefun(T,T_init) ! use the state function to perform temerature dependent external changes
            endif
            nprobs = 0
            avgprob = 0.
            call sa_comb_min_param_one_chain( num, costfun,&
            permfun, T, max_rearr, use_permfun, joint_cost )
            avgprob = avgprob/real(nprobs)
!            write(*,'(A)') '***************************'
!            write(*,'(A,14XF10.2)') 'T: ', T
!            write(*,'(A,15XF6.2)') 'P(T): ', avgprob
!            write(*,'(A,14XF7.4)') 'CORR: ', -joint_cost
            T = TC*T ! Temperature update
            costs(1) = costs(2) ! Cost update
            costs(2) = joint_cost
            if( abs( costs(1)-costs(2) ) <= cost_err*0.5 ) then
                convergence = convergence+1
            else
                convergence = 0
            end if
            frozen = frozen_state( convergence, T, T_lowlim )
            if( frozen ) then
                write(*,'(A,14XF10.2)') 'T: ', T
                write(*,'(A,15XF6.2)') 'P(T): ', avgprob
                write(*,'(A,14XF7.4)') 'CORR: ', -joint_cost
            end if
            ! Get the actual and relative cpu-time
!            rslask = getabscpu( .true. )
!            rslask = getdiffcpu( .true. )
        end do
        out_solution = num%vec
        cost = joint_cost
        
        contains
        
            function nits( ) result( n )
                integer :: n
                real :: tmp
                tmp = T_init
                n = 0
                do while( tmp > T_lowlim )
                    n = n+1
                    tmp = tmp*TC
                end do
            end function nits
        
    end subroutine sa_comb_min_param

    subroutine sa_comb_min_param_one_chain( num, costfun,&
    permfun, T, max_rearr, use_permfun, cost )
    ! provides the core functionality of the simulated annealing and parallel tempering algorithms
        type(sa_opt)        :: num
        real, external      :: costfun
        external            :: permfun
        real, intent(in)    :: T
        integer, intent(in) :: max_rearr
        logical, intent(in) :: use_permfun
        real, intent(out)   :: cost
        integer             :: i, nr_rearr, accepted, no_change
        logical             :: steady
        ! Initiate costs from input solution 
        do i=1,num%N
            call calc_cost( num, costfun, i )
        end do
        nr_rearr = 0 ! Nr of rearrangements at a certain T
        steady   = .false. ! To check steady state
        do while(steady .neqv. .true.)
            accepted  = 0 ! Nr of accepted permutations at a T level
            no_change = 0 ! Nr of no changes at a T level
            do i=1,num%N
                call rnd_permute_solution( num, i )
                call calc_cost_perm( num, costfun, i )
                call metropolis_accept( num, i, T, accepted, permfun, use_permfun )
            end do
            if( accepted == 0 ) then
                no_change = no_change+1
            else
                no_change = 0
            end if
            nr_rearr = nr_rearr+1
            steady = steady_state( no_change, nr_rearr, max_rearr )
        end do
        cost = 0.
        do i=1,num%N
            cost = cost + num%cost(i)
        end do
        cost = cost/real(num%N)
    end subroutine sa_comb_min_param_one_chain
    
    subroutine calc_cost( num, costfun, i )
    ! is for calculating cost as externally defined
        type(sa_opt)        :: num
        real, external      :: costfun
        integer, intent(in) :: i
        num%cost(i) = costfun( num%vec, i, num%N, num%L )
    end subroutine calc_cost
    
    subroutine calc_cost_perm( num, costfun, i )
    ! is for calculating permuted cost as externally defined
        type(sa_opt)        :: num
        real, external      :: costfun
        integer, intent(in) :: i
        num%cost_perm(i) = costfun( num%vec_perm, i, num%N, num%L )
    end subroutine calc_cost_perm
    
    subroutine rnd_permute_solution( num, i )
    ! is for generating trial solutions
        type(sa_opt)        :: num
        integer, intent(in) :: i
        integer             :: j
        do j=1,num%L
            if( num%nevars(j) ) then
                num%vec_perm(i,j) = irnd_uni_tabu( num%rt(j)  )
            else
                num%vec_perm(i,j) = irnd_uni( num%params(j) )
            endif
        end do
    end subroutine rnd_permute_solution
    
    subroutine metropolis_accept( num, i, T, accepted, permfun, use_permfun )
    ! is for temperature-weighted probabilistic acceptance of trial solutions according to the Metropolis criterion
        type(sa_opt), intent(inout) :: num
        integer, intent(in)         :: i
        real, intent(in)            :: T
        integer, intent(inout)      :: accepted
        external                    :: permfun
        logical, intent(in)         :: use_permfun
        real                        :: prob
        logical                     :: perm_accepted
        integer                     :: j
        real, parameter             :: bolzmann=10000.
        perm_accepted = .false.
        if( num%cost_perm(i) < num%cost(i) ) then
            ! always accept a true downhill path
            perm_accepted = .true.
        else
            prob    = min(1.,exp(((-bolzmann)*(num%cost_perm(i)-num%cost(i)))/T))
            nprobs  = nprobs+1
            avgprob = avgprob+prob
            if( ran3() <= prob ) then
                ! sometimes accept an uphill path
                perm_accepted = .true.
            endif
        endif
        if( perm_accepted )then
            do j=1,num%L
                if( num%nevars(j) ) then
                    call remove_ran_tabu( num%rt(j), num%vec(i,j) )
                    call insert_ran_tabu( num%rt(j), num%vec_perm(i,j) )
                endif
            end do
            num%vec(i,:) = num%vec_perm(i,:)
            num%cost(i)  = num%cost_perm(i)
            accepted     = accepted+1
        endif
        if( perm_accepted .and. use_permfun ) then ! use the observer function to notify the change
            call permfun( num%vec_perm(i,:), i, num%L )
        end if
    end subroutine metropolis_accept
    
    function steady_state( no_change, nr_rearr, max_rearr ) result( steady )
    ! is for checking if a steady state is reached at the temperature level
        logical             :: steady
        integer, intent(in) :: no_change, nr_rearr, max_rearr
        if( no_change >= 2 .or. nr_rearr >= max_rearr ) then 
            steady = .true.
        else
            steady = .false.
        end if
    end function steady_state
    
    function frozen_state( convergence, T, T_lowlim ) result( frozen )
    ! is for checking if the "crystal has formed"
        logical             :: frozen
        integer, intent(in) :: convergence
        real, intent(in)    :: T, T_lowlim
        if( T <= T_lowlim .or. convergence >= 10 ) then
            write(*,'(A)') 'System frozen'
            frozen = .true.
        else
            frozen = .false.
        end if
    end function frozen_state

    function frozen_state_lowlim_only( T, T_lowlim ) result( frozen )
    ! is for checking if the expected temperature for "crystal formation" is reached
        logical          :: frozen
        real, intent(in) :: T, T_lowlim
        if( T <= T_lowlim ) then
            write(*,'(A)') 'System frozen'
            frozen = .true.
        else
            frozen = .false.
        end if
    end function frozen_state_lowlim_only
    
end module simple_sa_opt