!==Class simple_NAME
!
! simple_CLASS is ...
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution or modification is regulated by the GNU General Public License. 
! *Author:* Hans Elmlund, 2011
! 
!==Changes are documented below
!
!*
!
module simple_NAME
use simple_THAT
use simple_THIS
implicit none
save

type NAME
    private
    ...
    logical :: exists=.false.
end type NAME

contains

    function new_NAME( ) result( num )
    ! is a constructor
        type(NAME) :: num
        
    end function new_NAME
    
    subroutine kill_NAME( num )
    ! is a destructor
        type(NAME) :: num
    
    end subroutine kill_NAME

end module simple_NAME