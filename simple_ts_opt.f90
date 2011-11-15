module simple_ts_opt
use simple_ran_tabu
use simple_rnd
use simple_tabu_end
use simple_math
use simple_tslist
use simple_sll_list
use simple_jiffys
implicit none

private :: restart_mixed, sum_best_score, avg_best_score, biex_ts_exec,&
monoex_ts_exec, ts_master, swap_ts_exec
public

type ts_opt
    private 
    type(ran_tabu)              :: rtab ! structure to maintain feasibility of the solutions
    type(tabu_end), allocatable :: tend(:) ! structure to record when tabu classification ends
    type(tslist)                :: list ! candidate list structure
    type(sll_list)              :: s_opt ! local optimal solution scores found
    type(sll_list)              :: x_opt ! the local optimal solutions found
    type(sll_list)              :: next_move ! list for storing the next move taken after a local optima was found
    integer, allocatable        :: x(:), x_best(:) ! current and best solution
    real, allocatable           :: s(:), s_best(:) ! current and best scores
    integer                     :: tmin=2, tmax=8 ! limits for systematic dynamic tenure
    integer                     :: params ! nr of parameters per solution attribute
    integer                     :: nbest ! nr of best moves to store per solution attribute
    integer                     :: restarts=0 ! nr of restarts to perform
    integer                     :: N ! N=Nptcls
    integer                     :: it ! to check iteration number
    logical                     :: update=.true. ! indicates if bak-snippen individuals should be updated or not
    logical                     :: nevars=.false. ! indicates if variables should not be equal
    logical                     :: exists=.false.
end type ts_opt

contains

    function new_ts_opt( N, params, nevars, nbest, tmin, tmax, update ) result( num )
    ! is a constructor
        type(ts_opt)                  :: num
        integer, intent(in)           :: N       ! nr of individuals 
        integer, intent(in), optional :: params  ! nr of discrete parameters
        logical, intent(in), optional :: nevars  ! if true the variables are not to be equal
        integer, intent(in), optional :: nbest   ! nr of best moves to store per solution attribute
        integer, intent(in), optional :: tmin    ! dynamic tenure lower limit
        integer, intent(in), optional :: tmax    ! dynamic tenure upper limit
        logical, intent(in), optional :: update  ! indicates if bak-snippen individuals should be updated or not
        integer                       :: i, alloc_stat
        allocate( num%x(N), num%x_best(N), num%tend(N), num%s(N), num%s_best(N), stat=alloc_stat )
        call alloc_err('In: new_ts_opt, module: simple_ts_opt', alloc_stat)
        ! make lists for storing local optimal info
        num%x_opt     = new_sll_list()
        num%s_opt     = new_sll_list()
        num%next_move = new_sll_list()
        ! init variables
        num%N = N
        num%nbest = max(7,nint(0.1*N))
        if( present(nbest)  ) num%nbest  = nbest
        num%params = N
        if( present(params) ) then
            num%params = params
            if( present(nevars) ) num%nevars = nevars  
        else
            num%params = N
        endif
        if( present(tmin) )   num%tmin   = tmin
        if( present(tmax) )   num%tmax   = tmax
        if( present(update) ) num%update = update
        ! Build tabu structure
        do i=1,N
            num%tend(i) = new_tabu_end( num%params, tmin=num%tmin, tmax=num%tmax )
        end do
        ! Build structure to check solution feasibility
        if( num%nevars ) num%rtab = new_ran_tabu( params )
        num%list = new_tslist( num%params, num%N, num%nbest )
        num%exists = .true.
    end function new_ts_opt

    subroutine kill_ts_opt( num )
        type(ts_opt), intent(inout) :: num
        integer                     :: i
        if( num%exists )then
            call kill_ran_tabu(num%rtab)
            do i=1,num%N
                call kill_tabu_end( num%tend(i) )
            end do
            call kill_sll_list( num%x_opt )
            call kill_sll_list( num%s_opt )
            call kill_sll_list( num%next_move )
            call kill_tslist( num%list )
            deallocate( num%x, num%tend, num%s )
        endif
    end subroutine kill_ts_opt

    subroutine ts_comb_max( num, scorefun, permfun, maxrestarts, out_sol, in_sol )
        type(ts_opt), intent(inout) :: num
        interface
            function scorefun( vec, i, N ) result( score )
                integer, intent(in) :: N, vec(N), i
                real                :: score
            end function scorefun
            subroutine permfun( val, i )
                integer, intent(in) :: val, i
            end subroutine permfun
        end interface
        integer, intent(in)  :: maxrestarts
        integer, intent(out) :: out_sol(num%N)
        integer, intent(in)  :: in_sol(num%N) ! input solution
        integer              :: i
        write(*,'(a)') '>>> TABU SEARCH'
        num%x = in_sol
        ! clear the structure for feasibility check
        if( num%nevars ) call reset_ran_tabu( num%rtab )
        ! begin with reporting the initial solution back via the permfun
        ! and add the solution elements to the structure for feasibility check 
        do i=1,num%N
            call permfun( num%x(i), i )
            if( num%nevars ) call insert_ran_tabu( num%rtab, num%x(i) )
        end do
        ! initialize scores
        do i=1,num%N
            num%s(i) = scorefun( num%x, i, num%N )
        end do
        ! initialize the lists containing local optimum information
        call add_sll_node( num%s_opt, rarr=num%s )
        call add_sll_node( num%x_opt, iarr=num%x )
        ! initialize the exisiting best solution
        num%s_best = num%s
        num%x_best = num%x
        ! reset any previously established tabus
        do i=1,num%N
            call reset_tabu_end( num%tend(i) )
        end do
        ! start with exhange neighbourhood search       
        call ts_simple( num, scorefun, permfun, maxrestarts )
        ! output the best solution found
        out_sol = num%x_best
    end subroutine ts_comb_max
    
    subroutine ts_simple( num, scorefun, permfun, maxrounds )
        type(ts_opt), intent(inout) :: num
        real, external              :: scorefun
        external                    :: permfun
        integer, intent(in)         :: maxrounds
        integer                     :: it, old, i, j, round
        integer                     :: pos, move
        logical                     :: store_next_move
        real                        :: cscores(2)
        ! Init variables to check convergence
        it              = 0
        cscores         = avg_best_score(num) ! convergence scores
        store_next_move = .false.
        round           = 0
        do
            round = round+1
            call update_tslist_ecan( num%list, num%x, num%s, scorefun )  
            do j=1,num%nbest
                do i=1,num%N
                    it = it+1
                    call get_tslist_move( num%list, i, j, pos, move )
                    if( is_ran_tabu( num%rtab, move ) ) cycle ! infeasible move
                    old = num%x(pos) ! store the old attribute for reversal
                    call monoex_ts_exec( num, pos, move, old, it, store_next_move, scorefun, permfun )
                    if( mod(it,100) == 0 .or. it == 1 )then
                        write(*,*) 'Iteration:', it, 'avg_score:',&
                        sum(num%s)/real(num%N), 'best_score:', avg_best_score( num )
                    endif
                end do
                cscores(1) = cscores(2) ! Score update
                cscores(2) = avg_best_score( num )
            end do
            if( round == maxrounds ) exit
        end do
    end subroutine ts_simple

    subroutine ts_master( num, scorefun, permfun, score_err, maxrestarts )
        type(ts_opt), intent(inout) :: num
        real, external              :: scorefun
        external                    :: permfun
        real, intent(in)            :: score_err
        integer, intent(in)         :: maxrestarts
        integer                     :: it, old, old2, i, j, k, round, nochange, nochange2
        integer                     :: pos, move, move2, pos2, print_count
        logical                     :: converged, store_next_move, change_neigh, accepted
        real                        :: cscores(2)
        write(*,'(a)') '>>> MIXED NEIGHBORHOOD'
        ! Init variables to check convergence
        it              = 0
        converged       = .false. ! to indicate convergence
        nochange        = 0 ! to indicate that the search stalled
        nochange2       = 0 
        cscores         = avg_best_score(num) ! convergence scores
        store_next_move = .false.
        round           = 0
        change_neigh    = .false.
        num%restarts    = 0
        print_count     = 0
        do
            round = round+1
            call update_tslist_ecan( num%list, num%x, num%s, scorefun )
            if( nochange >= 20 ) then ! apply restart procedure
                if( maxrestarts /= 0 ) then
                    num%restarts = num%restarts+1
                    if( mod(num%restarts,2) /= 0 )then
                        write(*,'(a)') '>>> NEIGHBOURHOOD CHANGE'              
                        change_neigh = .true.
                    else
                        write(*,'(a)') '>>> RESTARTING FOR INTENSIFICATION'
                        call restart_mixed( num, it, scorefun, permfun=permfun )
                        call update_tslist_ecan( num%list, num%x, num%s, scorefun ) 
                        nochange = 0
                    endif
                else
                    exit
                endif
            endif        
            if( nochange2 >= 20 ) then ! end phase with changed neighbourhood
                change_neigh = .false.
                nochange2 = 0
            endif
            do j=1,num%nbest
                if( .not. change_neigh ) then
                    do i=1,num%N
                        it = it+1
                        call get_tslist_move( num%list, i, j, pos, move )
                        if( is_ran_tabu( num%rtab, move ) ) cycle ! infeasible move
                        old = num%x(pos) ! store the old attribute for reversal
                        call monoex_ts_exec( num, pos, move, old, it, store_next_move, scorefun, permfun )
                        if( mod(it,100) == 0 .or. it == 1 )then
                            write(*,*) 'Iteration:', it, 'avg_score:',&
                            sum(num%s)/real(num%N), 'best_score:', avg_best_score( num )
                        endif
                    end do
                else
                    ! The purpose here is to do a neighbourhood change from a mono-exchange 
                    ! to a swap/bi-exchange neighbourhood. First, get one feasible move out.         
                    do i=1,num%N
                        call get_tslist_move( num%list, i, j, pos, move )
                        if( is_ran_tabu( num%rtab, move ) )then
                            cycle
                        else
                            exit
                        endif
                    end do
                    if( mod(it,100) == 0 .or. it == 1 )then
                        write(*,*) 'Iteration:', it, 'avg_score:',&
                        sum(num%s)/real(num%N), 'best_score:', avg_best_score( num )
                    endif
                    if( is_ran_tabu( num%rtab, move ) ) cycle                    
                    ! establish a second random attribute
                    k = i
                    do while( k == i )
                        k = irnd_uni(num%N)
                    end do
                    ! test the possibility of a swap move
                    call swap_ts_exec( num, pos, k, it, store_next_move, accepted, scorefun, permfun )
                    if( accepted ) cycle
                    ! get the second move
                    do i=1,num%N
                        call get_tslist_move( num%list, k, j, pos2, move2 )
                        if( is_ran_tabu( num%rtab, move2 ) .or. move == move2 )then
                            cycle
                        else
                            exit
                        endif
                    end do
                    ! store the old attributes for reversal
                    old = num%x(pos)
                    old2 = num%x(pos2)
                    if( is_ran_tabu( num%rtab, move2 ) .or. move == move2 )then
                        ! let it be a mono-exchange neighbourhood
                        call monoex_ts_exec( num, pos, move, old, it,&
                        store_next_move, scorefun, permfun )
                    else
                        call biex_ts_exec( num, pos, pos2, move, move2,&
                        old, old2, it, store_next_move, scorefun, permfun )
                    endif
                endif
                cscores(1) = cscores(2) ! Score update
                cscores(2) = avg_best_score( num )
                if( abs(cscores(1)-cscores(2)) <= score_err*0.5 ) then
                    nochange = nochange+1
                else
                    nochange = 0
                end if
            end do
            if( abs(cscores(1)-cscores(2)) <= score_err*0.5 ) then
                nochange2 = nochange2+1
            else
                nochange2 = 0
            end if
            if( num%restarts == maxrestarts ) exit
        end do
    end subroutine ts_master

    subroutine monoex_ts_exec( num, pos, move, old, it, store_next_move, scorefun, permfun )
        type(ts_opt), intent(inout) :: num
        integer, intent(in)         :: pos, move, old, it
        logical, intent(inout)      :: store_next_move
        real, external              :: scorefun
        external                    :: permfun
        integer                     :: i, next_move(2)
        real                        :: score
        ! Execute the move and calc score
        num%x(pos) = move 
        score = scorefun( num%x, pos, num%N )
        ! check if this is the "best so far" encountered solution (aspiration criteria)
        if( sum(num%s)-num%s(pos)+score > sum_best_score(num) )then
            ! keep the move, update the scores and insert appropriate tabus    
            call permfun( num%x(pos), pos )
            num%s(pos) = score
            if( num%update )then
                do i=1,num%N
                    if( i /= pos ) num%s(i) = scorefun( num%x, i, num%N )
                end do
            endif
            call insert_tabu( num%tend(pos), it, move, old )
            if( num%nevars ) call remove_ran_tabu( num%rtab, old )
            if( num%nevars ) call insert_ran_tabu( num%rtab, move )
            ! add solution to the set of local optimas
            call add_sll_node( num%s_opt, rarr=num%s )
            call add_sll_node( num%x_opt, iarr=num%x )
            ! override the exisiting best solution
            num%s_best = num%s
            num%x_best = num%x
            store_next_move = .true.
        else if( test_tabu_status( num%tend(pos), it, move, old ) )then 
            ! move is tabu, put the old value back
            num%x(pos) = old
        else ! keep the move, update the scores and insert appropriate tabus           
            call permfun( num%x(pos), pos )
            num%s(pos) = score
            if( num%update )then
                do i=1,num%N
                    if( i /= pos ) num%s(i) = scorefun( num%x, i, num%N )
                end do
            endif
            call insert_tabu( num%tend(pos), it, move, old )
            if( num%nevars ) call remove_ran_tabu( num%rtab, old )
            if( num%nevars ) call insert_ran_tabu( num%rtab, move )
            if( store_next_move )then
                next_move(1) = pos ! position
                next_move(2) = move ! value
                call add_sll_node( num%next_move, iarr=next_move )
                store_next_move = .false.
            endif
        endif
    end subroutine monoex_ts_exec

    subroutine biex_ts_exec( num, pos1, pos2, move1, move2, old1, old2, it,&
    store_next_move, scorefun, permfun )
        type(ts_opt), intent(inout) :: num
        integer, intent(in)            :: pos1, pos2, move1, move2, old1, old2, it
        logical, intent(inout)         :: store_next_move
        real, external                 :: scorefun
        external                       :: permfun
        integer                        :: i, next_move(2)
        real                           :: score1, score2
        ! Execute the moves and calc scores
        num%x(pos1) = move1
        num%x(pos2) = move2
        score1 = scorefun( num%x, pos1, num%N )
        score2 = scorefun( num%x, pos2, num%N )
        ! check if this is the "best so far" encountered solution (aspiration criteria)
        if( sum(num%s)-num%s(pos1)-num%s(pos2)+score1+score2 > sum_best_score(num) )then
            ! keep the move, update the scores and insert appropriate tabus
            call permfun( num%x(pos1), pos1 )
            call permfun( num%x(pos2), pos2 )
            num%s(pos1) = score1
            num%s(pos2) = score2
            if( num%update )then
                do i=1,num%N
                    if( i /= pos1 .and. i /= pos2 ) num%s(i) = scorefun( num%x, i, num%N )
                end do
            endif
            call insert_tabu( num%tend(pos1), it, move1, old1 )
            call insert_tabu( num%tend(pos2), it, move2, old2 )
            if( num%nevars ) call remove_ran_tabu( num%rtab, old1 )
            if( num%nevars ) call remove_ran_tabu( num%rtab, old2 )
            if( num%nevars ) call insert_ran_tabu( num%rtab, move1 )
            if( num%nevars ) call insert_ran_tabu( num%rtab, move2 )
            ! add solution to the set of local optimas
            call add_sll_node( num%s_opt, rarr=num%s )
            call add_sll_node( num%x_opt, iarr=num%x )
            ! override the exisiting best solution
            num%s_best = num%s
            num%x_best = num%x
            store_next_move = .true.
        else if( test_tabu_status( num%tend(pos1), it, move1, old1 ) .and.&
        test_tabu_status( num%tend(pos2), it, move2, old2 ) )then 
            ! the compound move is tabu, put the old values back
            num%x(pos1) = old1
            num%x(pos2) = old2
        else if( test_tabu_status( num%tend(pos1), it, move1, old1 ) )then
            ! move1 is tabu, put the old value back
            num%x(pos1) = old1
            ! go for mono-exchange on the other move 
            call monoex_ts_exec( num, pos2, move2, old2, it, store_next_move, scorefun, permfun )
        else if( test_tabu_status( num%tend(pos2), it, move2, old2 ) )then
            ! move2 is tabu, put the old value back
            num%x(pos2) = old2
            ! go for mono-exchange on the other move 
            call monoex_ts_exec( num, pos1, move1, old1, it, store_next_move, scorefun, permfun )
        else ! keep the move, update the scores and insert appropriate tabus    
            call permfun( num%x(pos1), pos1 )
            call permfun( num%x(pos2), pos2 )
            num%s(pos1) = score1
            num%s(pos2) = score2
            if( num%update )then
                do i=1,num%N
                    if( i /= pos1 .and. i /= pos2 ) num%s(i) = scorefun( num%x, i, num%N )
                end do
            endif
            call insert_tabu( num%tend(pos1), it, move1, old1 )
            call insert_tabu( num%tend(pos2), it, move2, old2 )
            if( num%nevars ) call remove_ran_tabu( num%rtab, old1 )
            if( num%nevars ) call remove_ran_tabu( num%rtab, old2 )
            if( num%nevars ) call insert_ran_tabu( num%rtab, move1 )
            if( num%nevars ) call insert_ran_tabu( num%rtab, move2 )
            if( store_next_move )then
                next_move(1) = pos1 ! position
                next_move(2) = move1 ! value
                call add_sll_node( num%next_move, iarr=next_move )
                store_next_move = .false.
            endif
        endif
    end subroutine biex_ts_exec

    subroutine swap_ts_exec( num, pos1, pos2, it, store_next_move, accepted, scorefun, permfun )
        type(ts_opt), intent(inout) :: num
        integer, intent(in)         :: pos1, pos2, it
        logical, intent(inout)      :: store_next_move
        logical, intent(out)        :: accepted
        real, external              :: scorefun
        external                    :: permfun
        integer                     :: i, next_move(2)
        real                        :: score1, score2        
        integer                     :: iswap
        ! set accepted indicator
        accepted = .false.
        ! error check positions
        if( pos1 == pos2 )then
            store_next_move = .false.
            return
        endif
        ! execute the swap and calc scores
        iswap = num%x(pos1)
        num%x(pos1) = num%x(pos2)
        num%x(pos2) = iswap 
        score1 = scorefun( num%x, pos1, num%N )
        score2 = scorefun( num%x, pos2, num%N )
        ! check if this is the "best so far" encountered solution (aspiration criteria)
        if( sum(num%s)-num%s(pos1)-num%s(pos2)+score1+score2 > sum_best_score(num) )then
            ! keep the move, update the scores and insert appropriate tabus
            call permfun( num%x(pos1), pos1 )
            call permfun( num%x(pos2), pos2 )
            num%s(pos1) = score1
            num%s(pos2) = score2
            if( num%update )then
                do i=1,num%N
                    if( i /= pos1 .and. i /= pos2 ) num%s(i) = scorefun( num%x, i, num%N )
                end do
            endif
            call insert_tabu( num%tend(pos1), it, num%x(pos1), num%x(pos2) )
            call insert_tabu( num%tend(pos2), it, num%x(pos2), num%x(pos1) )
            ! add solution to the set of local optimas
            call add_sll_node( num%s_opt, rarr=num%s )
            call add_sll_node( num%x_opt, iarr=num%x )
            ! override the exisiting best solution
            num%s_best = num%s
            num%x_best = num%x
            store_next_move = .true.
            accepted = .true.
        else if( test_tabu_status( num%tend(pos1), it, num%x(pos1), num%x(pos2) ) .or.&
        test_tabu_status( num%tend(pos2), it, num%x(pos2), num%x(pos1) ) )then 
            ! the swap move is tabu, put the old values back
            iswap = num%x(pos1)
            num%x(pos1) = num%x(pos2)
            num%x(pos2) = iswap
        else ! keep the move, update the scores and insert appropriate tabus            
            ! report the move back to 
            call permfun( num%x(pos1), pos1 )
            call permfun( num%x(pos2), pos2 )
            num%s(pos1) = score1
            num%s(pos2) = score2
            if( num%update )then
                do i=1,num%N
                    if( i /= pos1 .and. i /= pos2 ) num%s(i) = scorefun( num%x, i, num%N )
                end do
            end if
            call insert_tabu( num%tend(pos1), it, num%x(pos1), num%x(pos2) )
            call insert_tabu( num%tend(pos2), it, num%x(pos2), num%x(pos1) )
            if( store_next_move )then
                next_move(1) = pos1 ! position
                next_move(2) = num%x(pos1) ! value
                call add_sll_node( num%next_move, iarr=next_move )
                store_next_move = .false.
            endif
            accepted = .true.
        endif
    end subroutine swap_ts_exec

    function avg_best_score( num ) result( score )
        type(ts_opt), intent(in) :: num
        real :: score
        score = sum_best_score(num)/real(num%N)
    end function avg_best_score

    function sum_best_score( num ) result( score )
        type(ts_opt), intent(in) :: num
        real :: score
        score = sum(num%s_best)
    end function sum_best_score

    subroutine restart_mixed( num, it, scorefun, permfun )
        type(ts_opt), intent(inout) :: num
        integer, intent(in)         :: it
        real, external              :: scorefun
        external                    :: permfun
        integer                     :: i, next_move(2)
        if( get_sll_size(num%x_opt) == 0 )then ! add the best to the list of local optimas
            call add_sll_node( num%s_opt, rarr=num%s_best )
            call add_sll_node( num%x_opt, iarr=num%x_best )
            next_move(1) = irnd_uni( num%N )
            next_move(2) = irnd_uni( num%params )
            call add_sll_node( num%next_move, iarr=next_move )
        endif
        ! get the best solution so far
        call get_sll_node( num%x_opt, get_sll_size(num%x_opt), iarr=num%x )
        call get_sll_node( num%s_opt, get_sll_size(num%s_opt), rarr=num%s )
        call get_sll_node( num%next_move, get_sll_size(num%next_move), iarr=next_move )
        ! Remove it (this is essentially a diversification manouver)
        ! Bear in mind that we could probably improve things by clustering the local optimal solutions
        call delete_sll_node( num%x_opt, get_sll_size(num%x_opt) )
        call delete_sll_node( num%s_opt, get_sll_size(num%s_opt) )
        call delete_sll_node( num%next_move, get_sll_size(num%next_move) )
        ! restart the structure for feasibility check
        ! begin with clearing the structure for feasibility check
        if( num%nevars ) call reset_ran_tabu( num%rtab )
        ! report the best solution back via the permfun
        ! and add the solution elements to the structure for feasibility check 
        do i=1,num%N
            call permfun( num%x(i), i )
            if( num%nevars ) call insert_ran_tabu( num%rtab, num%x(i) )
        end do
        ! Update the best score
        call delete_sll_node( num%s_opt, get_sll_size(num%s_opt) )
        call add_sll_node( num%s_opt, rarr=num%s )
        ! reset any previously established tabus
        do i=1,num%N
            call reset_tabu_end( num%tend(i) )
        end do   
        ! make sure that the previous next move is not applied, to assure divergence
        call insert_tabu( num%tend(next_move(1)), it+1, next_move(2), 0 )
    end subroutine restart_mixed

end module simple_ts_opt