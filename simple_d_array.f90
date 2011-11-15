!==Class simple_d_array
!
! simple_d_array provides run-time polymorphic lists via the list_object type defined in class 
! simple_list_object . This class provides a chunk of data for a run-time specified (or not) 
! association of a pointer to _d_array_. The code is distributed with the hope that it will be 
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the 
! GNU General Public License. *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_d_array
use simple_def_precision
use simple_jiffys
implicit none

type d_array
! is just a real(double) array
    private
    integer :: N
    real(double), allocatable :: darr(:)
end type d_array

contains

    function new_d_array( darr )result( num )
    ! determines the size of, allocates space for, and stores _darr_
        type(d_array), target :: num
        real(double), intent(in)      :: darr(:)
        integer               :: alloc_stat
        num%N    = size(darr,1)
        allocate(num%darr(num%N), stat=alloc_stat)
        call alloc_err('In: new_d_array, module: simple_d_array.f90', alloc_stat)
        num%darr = darr
    end function new_d_array
    
    subroutine deallocate_d_array( num )
    ! is a destructor
        type(d_array) :: num
        if( allocated(num%darr) ) then
            deallocate( num%darr )
        endif
    end subroutine deallocate_d_array

    subroutine get_d_array( num, darr )
    ! is a getter
        type(d_array), intent(in) :: num
        real(double), intent(out)         :: darr(num%N)
        if( num%N > 0 ) then
            darr = num%darr
        else
            write(*,*) 'The d_array that you are trying to print does not exist!'
            write(*,*) 'In: get_d_array, module: simple_d_array.f95'
            stop
        endif
    end subroutine get_d_array

    subroutine set_d_array( num, darr, err )
    ! is a getter
        type(d_array), intent(inout) :: num
        real(double), intent(in)             :: darr(num%N)
        logical, intent(out)         :: err
        err = .false.
        if( num%N > 0 ) then
            num%darr = darr 
        else
            err = .true.
        endif
    end subroutine set_d_array

     subroutine print_d_array( num )
     ! is for prettier printing
        type(d_array), intent(in) :: num
        if( num%N > 0 ) then
            write(*,*) '[d_array]=', num%darr
        else
            write(*,*) 'The d_array that you are trying to get does not exist!'
            write(*,*) 'In: get_d_array, module: simple_d_array.f95'
            stop
        endif
    end subroutine print_d_array

end module simple_d_array