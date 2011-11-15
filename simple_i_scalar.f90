!==Class simple_i_scalar
!
! simple_i_scalar provides run-time polymorphic lists via the list_object type defined in class 
! simple_list_object . This class provides a chunk of data for a run-time specified (or not) 
! association of a pointer to _i_scalar_. The code is distributed with the hope that it will be 
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the 
! GNU General Public License. *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_i_scalar
implicit none

type i_scalar
! is just an integer scalar
    private
    integer :: i=0
end type i_scalar

contains
  
    function new_i_scalar( i )result( num )
    ! is a constructor that stores _i_ in _num_
        type(i_scalar), target :: num
        integer, intent(in) :: i
        num%i = i
    end function new_i_scalar

    subroutine reset_i_scalar( num )
    ! is a "destructor"
        type(i_scalar) :: num
        num%i = 0
    end subroutine reset_i_scalar

    subroutine get_i_scalar( num, i )
    ! is a getter
        type(i_scalar), intent(in) :: num
        integer, intent(out)       :: i
        i = num%i
    end subroutine get_i_scalar

    subroutine set_i_scalar( num, i )
    ! is a setter
        type(i_scalar), intent(inout) :: num
        integer, intent(in)           :: i
        num%i = i
    end subroutine set_i_scalar

    function i_scalar_exists( num, i )result( yes )
    ! makes the question "Is _i_ in _i_scalar_?" possible to ask.
        type(i_scalar), intent(in) :: num
        integer, intent(in)        :: i
        logical                    :: yes
        yes = .false.
        if( num%i == i ) then
            yes = .true.
        endif
    end function i_scalar_exists

    subroutine print_i_scalar( num )
    ! is for prettier printing
        type(i_scalar), intent(in) :: num
        write(*,*) '[i_scalar]=', num%i
    end subroutine print_i_scalar

end module simple_i_scalar