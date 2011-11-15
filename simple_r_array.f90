!==Class simple_r_array
!
! simple_r_array provides run-time polymorphic lists via the list_object type defined in class 
! simple_list_object . This class provides a chunk of data for a run-time specified (or not) 
! association of a pointer to _r_array_. The code is distributed with the hope that it will be 
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the 
! GNU General Public License. *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_r_array
use simple_jiffys
implicit none

type r_array
! is just a real array
    private
    integer :: N
    real, allocatable :: rarr(:)
end type r_array

contains

    function new_r_array( rarr )result( num )
    ! determines the size of, allocates space for, and stores _rarr_
        type(r_array), target :: num
        real, intent(in)      :: rarr(:)
        integer               :: alloc_stat
        num%N    = size(rarr,1)
        allocate( num%rarr(num%N), stat= alloc_stat )
        call alloc_err('In: new_r_array, module: simple_r_array.f90', alloc_stat)
        num%rarr = rarr
    end function new_r_array
    
    subroutine deallocate_r_array( num )
    ! is a destructor
        type(r_array) :: num
        if( allocated(num%rarr) ) then
            deallocate( num%rarr )
        endif
    end subroutine deallocate_r_array

    subroutine get_r_array( num, rarr )
    ! is a getter
        type(r_array), intent(in) :: num
        real, intent(out)         :: rarr(num%N)
        if( num%N > 0 ) then
            rarr = num%rarr
        else
            write(*,*) 'The r_array that you are trying to print does not exist!'
            write(*,*) 'In: get_r_array, module: simple_r_array.f90'
            stop
        endif
    end subroutine get_r_array

    subroutine set_r_array( num, rarr, err )
    ! is a getter
        type(r_array), intent(inout) :: num
        real, intent(in)             :: rarr(num%N)
        logical, intent(out)         :: err
        err = .false.
        if( num%N > 0 ) then
            num%rarr = rarr 
        else
            err = .true.
        endif
    end subroutine set_r_array

     subroutine print_r_array( num )
     ! is for prettier printing
        type(r_array), intent(in) :: num
        if( num%N > 0 ) then
            write(*,*) '[r_array]=', num%rarr
        else
            write(*,*) 'The r_array that you are trying to get does not exist!'
            write(*,*) 'In: get_r_array, module: simple_r_array.f90'
            stop
        endif
    end subroutine print_r_array


end module simple_r_array