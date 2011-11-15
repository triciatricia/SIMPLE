!==Class simple_r_scalar
!
! simple_r_scalar provides run-time polymorphic lists via the list_object type defined in class 
! simple_list_object . This class provides a chunk of data for a run-time specified (or not) 
! association of a pointer to _r_scalar_. The code is distributed with the hope that it will be 
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the 
! GNU General Public License. *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_r_scalar
implicit none

type r_scalar
! is just a real scalar
    private
    real    :: r=0.
end type r_scalar

contains

    function new_r_scalar( r )result( num )
    ! is a constructor that stores _r_ in _num_
        type(r_scalar), target :: num
        real, intent(in), optional :: r
        num%r = r
    end function new_r_scalar

    subroutine reset_r_scalar( num )
    ! is a "destructor"
        type(r_scalar) :: num
        num%r = 0.
    end subroutine reset_r_scalar

    subroutine get_r_scalar( num, r )
    ! is a getter
        type(r_scalar), intent(in) :: num
        real, intent(out)      :: r
        r = num%r
    end subroutine get_r_scalar

    subroutine set_r_scalar( num, r )
    ! is a setter
        type(r_scalar), intent(inout) :: num
        real, intent(in)              :: r
        num%r = r
    end subroutine set_r_scalar

    subroutine print_r_scalar( num )
    ! is for prettier printing
        type(r_scalar), intent(in) :: num
        write(*,*) '[r_scalar]=', num%r
    end subroutine print_r_scalar

end module simple_r_scalar