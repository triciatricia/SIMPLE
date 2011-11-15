!==Class simple_d_scalar
!
! simple_d_scalar provides run-time polymorphic lists via the list_object type defined in class 
! simple_list_object . This class provides a chunk of data for a run-time specified (or not) 
! association of a pointer to _d_scalar_. The code is distributed with the hope that it will be 
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the 
! GNU General Public License. *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_d_scalar
use simple_def_precision
implicit none

type d_scalar
! is just a real(double) scalar
    private
    real(double) :: r=0.
end type d_scalar

contains

    function new_d_scalar( r )result( num )
    ! is a constructor that stores _r_ in _num_
        type(d_scalar), target :: num
        real(double), intent(in), optional :: r
        num%r = r
    end function new_d_scalar

    subroutine reset_d_scalar( num )
    ! is a "destructor"
        type(d_scalar) :: num
        num%r = 0.
    end subroutine reset_d_scalar

    subroutine get_d_scalar( num, r )
    ! is a getter
        type(d_scalar), intent(in) :: num
        real(double), intent(out)      :: r
        r = num%r
    end subroutine get_d_scalar

    subroutine set_d_scalar( num, r )
    ! is a setter
        type(d_scalar), intent(inout) :: num
        real(double), intent(in)              :: r
        num%r = r
    end subroutine set_d_scalar

    subroutine print_d_scalar( num )
    ! is for prettier printing
        type(d_scalar), intent(in) :: num
        write(*,*) '[d_scalar]=', num%r
    end subroutine print_d_scalar

end module simple_d_scalar