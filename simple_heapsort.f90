!==Class simple_heapsort
!
! simple_heapsort provides polymorphic data storage and sorting. The code is distributed 
! with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution
! or modification is regulated by the GNU General Public License. *Author:* Hans Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-09-24
! 
module simple_heapsort
use simple_sll_list
use simple_math
use simple_def_precision
implicit none

public

type :: heapsort
! is the heapsort instance
    private
    real, allocatable           :: scores(:)
    integer, allocatable        :: indices(:)
    type(sll_list), allocatable :: slls(:)
    integer                     :: N=0
    logical                     :: sorted=.false., exists=.false.
end type heapsort

contains
    
    function new_heapsort( N ) result( num )
    ! is a constructor
        integer, intent(in) :: N
        type(heapsort)      :: num
        integer             :: alloc_stat, i
        num%N = N
        allocate(num%scores(N), num%indices(N), num%slls(N), stat=alloc_stat)
        call alloc_err('In: new_heapsort, module: simple_heapsort.f90', alloc_stat)
        num%indices = (/(i,i=1,N)/)
        num%scores  = 0.
        num%exists  = .true.
    end function new_heapsort
    
    subroutine kill_heapsort( num )
    ! is a destructor
        type(heapsort) :: num
        integer        :: i
        if( num%exists )then
            do i=1,num%N
                call kill_sll_list(num%slls(i))
            end do
            deallocate(num%scores, num%indices, num%slls)
            num%N      = 0
            num%sorted = .false.
            num%exists = .false.
        endif
    end subroutine kill_heapsort

    subroutine reset_heapsort( num )
    ! is a destructor
        type( heapsort ) :: num
        integer          :: i
        if( num%exists )then
            num%indices = (/(i,i=1,num%N)/)
            num%sorted  = .false.
        endif
    end subroutine reset_heapsort

    subroutine set_heapsort( num, i, score, ival, rval, iarr, rarr )
    ! is a polymorphic setter
        type(heapsort)                :: num
        integer, intent(in)           :: i
        real, intent(in)              :: score
        integer, intent(in), optional :: ival, iarr(:)
        real, intent(in), optional    :: rval, rarr(:)
        if( i < 1 .or. i > num%N ) then
            write( *,* ) 'Setting is out of bound!'
            write( *,* ) 'in public method: set_heapsort, module: simple_heapsort.f90'
            stop
        endif
        num%scores(i) = score
        call kill_sll_list( num%slls(i) )
        num%slls(i) = new_sll_list()
        call add_sll_node( num%slls(i), ival=ival, rval=rval, iarr=iarr, rarr=rarr )
    end subroutine set_heapsort

    subroutine get_heapsort_min( num, score, ival, rval, iarr, rarr )
    ! is a polymorphic getter
        type(heapsort)                 :: num
        real, intent(out)              :: score
        integer, intent(out), optional :: ival, iarr(:)
        real, intent(out), optional    :: rval, rarr(:)
        call get_heapsort( num, 1, score, ival, rval, iarr, rarr )
    end subroutine get_heapsort_min

    subroutine get_heapsort_max( num, score, ival, rval, iarr, rarr )
    ! is a polymorphic getter
        type(heapsort)                 :: num
        real, intent(out)              :: score
        integer, intent(out), optional :: ival, iarr(:)
        real, intent(out), optional    :: rval, rarr(:)
        call get_heapsort( num, num%N, score, ival, rval, iarr, rarr )
    end subroutine get_heapsort_max

    subroutine print_heapsort( num )
    ! is for pretty printing
        type(heapsort), intent(in) :: num
        integer :: i
        do i=1,num%N
            call print_sll_list( num%slls(num%indices(i)) )
            write(*,*) '[score]=', num%scores(i)
        end do
    end subroutine print_heapsort

    subroutine get_heapsort( num, which, score, ival, rval, iarr, rarr )
     ! is for getting the object at the _which_ position in the sort struct out
        type(heapsort)                 :: num
        integer, intent(in)            :: which
        real, intent(out)              :: score
        integer, intent(out), optional :: ival, iarr(:)
        real, intent(out), optional    :: rval, rarr(:)
        if( .not. num%sorted ) then
            call sort_heapsort(num)
        endif
        score = num%scores(which)
        call get_sll_node( num%slls(num%indices(which)), 1, ival=ival, rval=rval, iarr=iarr, rarr=rarr )
    end subroutine get_heapsort

    function get_heapsort_size( num ) result( s )
    ! is a getter
        type(heapsort) :: num
        integer        :: s
        s = num%N
    end function get_heapsort_size

    subroutine sort_heapsort( num )
    ! sorts the sort struct using the heapsort algorithm
        type(heapsort) :: num
        integer        :: i
        num%indices = (/(i,i=1,num%N)/)
        call hpsort_1( num%N, num%scores, num%indices )
        num%sorted = .true.
    end subroutine sort_heapsort

    subroutine reverse_heapsort( num )
    ! reverses the order from ascending to descending
        type(heapsort) :: num
        call reverse_iarr( num%indices )
        call reverse_rarr( num%scores )
    end subroutine reverse_heapsort

end module simple_heapsort