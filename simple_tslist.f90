module simple_tslist
use simple_heapsort
use simple_math
use simple_ran_tabu
use simple_jiffys
implicit none

private :: update_moves
public

! change so that the heapsort stores the moves
! the elite candidate list structure gives excellent performance, but it is computationally demanding
! implement the same speedup as in teh GRASP scheme, with 10% randomly selected elements
! and 20 % worst


type tslist
    private
    type(ran_tabu)       :: r
    integer, allocatable :: list(:,:) ! list of candidate moves
    integer, allocatable :: moves(:) ! randomly ordered moves that are ordered in quality by the process
    real, allocatable    :: scores(:) ! list of scores
    real, allocatable    :: sums(:) ! sums of best move evaluations
    integer, allocatable :: so(:) ! search order
    integer              :: params ! nr of parameters per solution attribute
    integer              :: nbest ! nr of best moves to store per solution attribute
    integer              :: N ! N=Nptcls
    logical              :: exists=.false.
end type tslist

contains

    function new_tslist( params, N, nbest ) result( num )
        integer, intent(in) :: N ! nr of individuals
        integer, intent(in) :: nbest ! nr of best moves to store per solution attribute
        integer, intent(in) :: params ! nr of discrete parameters
        type(tslist)        :: num
        integer             :: alloc_stat
        allocate( num%list(N,nbest), num%moves(params),&
        num%sums(N), num%scores(params), num%so(N), stat=alloc_stat )
        call alloc_err('In: new_tslist, module: simple_tslist.f90', alloc_stat)
        ! Init vars
        num%params = params
        num%N = N
        num%nbest = nbest
        num%r = new_ran_tabu(params)
        num%exists = .true.
    end function new_tslist

    subroutine kill_tslist( num )
        type(tslist), intent(inout) :: num
        if( num%exists ) then
            deallocate( num%list, num%moves, num%sums, num%scores, num%so )
            call kill_ran_tabu(num%r)
            num%exists = .false.
        endif
    end subroutine kill_tslist

    subroutine update_moves( num )
        type(tslist), intent(inout) :: num
        call reset_ran_tabu( num%r )
        call ne_ran_iarr( num%r, num%moves )
    end subroutine update_moves

    subroutine get_tslist_move( num, i, j, pos, move )
        type(tslist), intent(in) :: num
        integer, intent(in)  :: i, j ! indices correspond to solution attr and move
        integer, intent(out) :: pos, move
        pos  = num%so(i)
        move = num%list(pos,j)
    end subroutine get_tslist_move

    subroutine update_tslist_aplus( num, x, s, asplevel, plus, scorefun )
    ! is for updating the list structure using the aspiration plus criterion and establishing a move priority 
        type(tslist), intent(inout) :: num
        integer, intent(inout)      :: x(num%N) ! input solution
        real, intent(in)            :: s(num%N) ! input scores
        real, intent(in)            :: asplevel ! aspiration level
        integer, intent(in)         :: plus ! nr of moves executed after asplevel has been found
        real, external              :: scorefun ! score function        
        integer                     :: old, i, k, send
        logical                     :: found
        write(*,'(a)') '>>> MAKING ASPIRATION PLUS LIST STRUCTURE'
        num%sums = 0.
        num%so = (/(i,i=1,num%N)/)
        do i=1,num%N
            ! generate a random search order
            call update_moves( num )
            ! store the old attribute
            old = x(i)
            ! init found
            found = .false.
            ! init search end param
            send = num%params 
            do k=1,num%params 
                ! move
                x(i) = num%moves(k)
                ! calculate score
                num%scores(k) = scorefun( x, i, num%N )
                if( num%scores(k) > asplevel .and. .not. found )then
                    ! set search end parameter
                    send = min(num%params,k+plus)
                    ! indicate that aspiration level is found
                    found = .true.
                endif
                if( k == send )then
                    exit
                endif
            end do
            ! sort scores and update list structure
            call hpsort( size(num%scores(:send)), num%scores(:send), num%moves(:send) )
            do k=1,num%nbest
                num%list(i,k) = num%moves(send-(k-1))
                num%sums(i)   = num%sums(i)+num%scores(send-(k-1))
            end do
            num%sums(i) = num%sums(i)/real(num%nbest)-s(i)            
            ! put the old attribute back
            x(i) = old
        end do
        call hpsort( size(num%sums), num%sums, num%so ) ! sort score sums to determine a move priority
        call reverse_iarr( num%so ) ! compensate for the worst first order
    end subroutine update_tslist_aplus

    subroutine update_tslist_ecan( num, x, s, scorefun )
    ! for making an elite candidate list structure and establish a move priority
        type(tslist), intent(inout) :: num
        integer, intent(inout)      :: x(num%N) ! input solution
        real, intent(in)            :: s(num%N) ! input scores
        real, external              :: scorefun ! score function
        integer                     :: old, i, k
        real                        :: score
        write(*,'(a)') '>>> MAKING ELITE CANDIDATE LIST STRUCTURE'
        num%sums = 0.
        num%so = (/(i,i=1,num%N)/)
        do i=1,num%N
            ! store the old attribute
            old = x(i)
            num%moves = (/(i,i=1,num%params)/)
            do k=1,num%params
                ! move
                x(i) = num%moves(k)
                ! calculate score
                score = scorefun( x, i, num%N )
                num%scores(k) = score-s(i)
            end do
            ! put the old attribute back
            x(i) = old
            ! sort       
            call hpsort( num%params, num%scores, num%moves )
            ! store the best attributes in the candidate list structure
            do k=1,num%nbest
                num%list(i,k) = num%moves(num%params-(k-1))
                num%sums(i) = num%sums(i)+num%scores(num%params-(k-1))
            end do
            num%sums(i) = num%sums(i)/real(num%nbest)-s(i) 
        end do
        call hpsort( num%N, num%sums, num%so )
        call reverse_iarr(num%so)
    end subroutine update_tslist_ecan

end module simple_tslist