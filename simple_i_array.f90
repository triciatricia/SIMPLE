!==Class simple_i_array
!
! simple_i_array provides run-time polymorphic lists via the list_object type defined in class 
! simple_list_object . This class provides a chunk of data for a run-time specified (or not) 
! association of a pointer to _i_array_. The code is distributed with the hope that it will be 
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the 
! GNU General Public License. *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_i_array
use simple_jiffys
implicit none

type i_array
! is just an integer array
  private
  integer :: N=0 
  integer, allocatable :: iarr(:)
end type i_array

contains
 
    function new_i_array( iarr ) result( num )
    ! determines the size of, allocates space for, and stores _iarr_
        type(i_array), target :: num
        integer, intent(in)   :: iarr(:)
        integer               :: alloc_stat
        num%N = size(iarr,1)
        allocate( num%iarr( num%N ), stat=alloc_stat )
        call alloc_err('In: new_i_array, module: simple_i_array.f90', alloc_stat)
        num%iarr = iarr
    end function new_i_array
 
    subroutine deallocate_i_array( num )
    ! is a destructor
      type(i_array) :: num
      integer       :: alloc_stat
      if( allocated(num%iarr) ) then
        deallocate( num%iarr, stat=alloc_stat )
      endif
    end subroutine deallocate_i_array

    subroutine get_i_array( num, iarr )
    ! is a getter
        type(i_array), intent(in) :: num
        integer, intent(out)      :: iarr(num%N)
        if( num%N > 0 ) then
            iarr = num%iarr
        else
            write(*,*) 'The i_array that you are trying to get does not exist!'
            write(*,*) 'In: get_i_array, module: simple_i_array.f90'
            stop
        endif
    end subroutine get_i_array

    subroutine set_i_array( num, iarr, err )
    ! is a setter
        type(i_array), intent(inout) :: num
        integer, intent(in)          :: iarr(num%N)
        logical, intent(out)         :: err
        err = .false.
        if( num%N > 0 ) then
            num%iarr = iarr
        else
            err = .true.
        endif
    end subroutine set_i_array

    subroutine print_i_array( num )
    ! is for prettier printing
        type(i_array), intent(in) :: num
        if( num%N > 0 ) then
            write(*,*) '[i_array]=', num%iarr
        else
            write(*,*) 'The i_array that you are trying to print does not exist!'
            write(*,*) 'In: print_i_array, module: simple_iarr.f90'
            stop
        endif
    end subroutine print_i_array

end module simple_i_array