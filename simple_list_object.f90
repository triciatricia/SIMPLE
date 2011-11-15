!==Class simple_list_object
!
! simple_list_object provides run-time polymorphic lists when used together with a list class (simple_sll_list).
! An instance of this class contains data and pointers to the desired data types that are nullified or
! assigned at runtime. The code is distributed with the hope that it will be 
! useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the 
! GNU General Public License. *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_list_object
use simple_i_scalar
use simple_r_scalar
use simple_d_scalar
use simple_i_array
use simple_r_array
use simple_d_array
implicit none

private :: nullify_list_object
public

type list_object
! contains all objects targeted for run-time polymorphism and pointers to them 
    private
    type(i_scalar)          :: ival
    type(r_scalar)          :: rval
    type(d_scalar)          :: dval
    type(i_array)           :: iarr
    type(r_array)           :: rarr
    type(d_array)           :: darr
    type(i_scalar), pointer :: pt_to_ival => null()
    type(r_scalar), pointer :: pt_to_rval => null()
    type(d_scalar), pointer :: pt_to_dval => null()
    type(i_array), pointer  :: pt_to_iarr => null()
    type(r_array), pointer  :: pt_to_rarr => null()
    type(d_array), pointer  :: pt_to_darr => null()
    logical                 :: exists=.false.
end type list_object

! interface list_object_exists
!     module procedure i_scalar_exists_
! end interface 

contains

  function new_list_object( ival, iarr, rval, rarr, dval, darr ) result( num )
  ! is a polymorphic constructor
    type(list_object), target          :: num
    integer, intent(in), optional      :: ival, iarr(:)
    real, intent(in), optional         :: rval, rarr(:)
    real(double), intent(in), optional :: dval, darr(:)
    if( present(ival) ) then
        num%ival = new_i_scalar( ival )
        num%pt_to_ival => num%ival     
    endif
    if( present(rval) ) then
        num%rval = new_r_scalar( rval )
        num%pt_to_rval => num%rval      
    endif
    if( present(dval) ) then
        num%dval = new_d_scalar( dval )
        num%pt_to_dval => num%dval      
    endif   
    if( present(iarr) ) then
        num%iarr = new_i_array( iarr )
        num%pt_to_iarr => num%iarr     
    endif
    if( present(rarr) ) then
        num%rarr = new_r_array( rarr )
        num%pt_to_rarr => num%rarr    
    endif
    if( present(darr) ) then
        num%darr = new_d_array( darr )
        num%pt_to_darr => num%darr    
    endif
    num%exists = .true.
  end function new_list_object

  subroutine set_list_object( num, err, ival, iarr, rval, rarr, dval, darr )
      type(list_object), intent(inout) :: num
      logical, intent(out)             :: err
      integer, intent(in), optional    :: ival, iarr(:)
      real, intent(in), optional       :: rval, rarr(:)
      real(double), intent(in), optional :: dval, darr(:)
      err = .false.
      if( present(ival) ) then
          if( associated( num%pt_to_ival ) ) then
              call set_i_scalar( num%ival, ival )
          else
              err = .true.
          endif
      endif
      if( present(rval) ) then
          if( associated( num%pt_to_rval ) ) then
              call set_r_scalar( num%rval, rval )
          else
              err = .true.
          endif
      endif
      if( present(dval) ) then
          if( associated( num%pt_to_dval ) ) then
              call set_d_scalar( num%dval, dval )
          else
              err = .true.
          endif
      endif   
      if( present(iarr) ) then
          if( associated( num%pt_to_iarr ) ) then
              call set_i_array( num%iarr, iarr, err )
          else
              err = .true.
          endif
      endif
      if( present(rarr) ) then
          if( associated( num%pt_to_rarr ) ) then
              call set_r_array( num%rarr, rarr, err )
          else
              err = .true.
          endif
      endif
      if( present(darr) ) then
          if( associated( num%pt_to_darr ) ) then
              call set_d_array( num%darr, darr, err )
          else
              err = .true.
          endif
      endif 
  end subroutine set_list_object 

  subroutine nullify_list_object( num )
  ! nullifies all pointers in the list_object
    type(list_object), intent(out)  :: num
    nullify( num%pt_to_ival )
    nullify( num%pt_to_iarr )
    nullify( num%pt_to_rval )
    nullify( num%pt_to_dval )
    nullify( num%pt_to_rarr )
    nullify( num%pt_to_darr )
  end subroutine nullify_list_object

  subroutine delete_list_object( num )
  ! deallocates the associated part of the list_object, and sets the rest to 0
    type(list_object), intent(inout)    :: num
    if( num%exists )then
        if( associated( num%pt_to_ival ) ) then
          call reset_i_scalar( num%ival )
        endif
        if( associated( num%pt_to_rval ) ) then
          call reset_r_scalar( num%rval )
        endif
        if( associated( num%pt_to_dval ) ) then
          call reset_d_scalar( num%dval )
        endif
        if( associated( num%pt_to_iarr ) ) then
          call deallocate_i_array( num%iarr )
        endif
        if( associated( num%pt_to_rarr ) ) then
          call deallocate_r_array( num%rarr )
        endif
        if( associated( num%pt_to_darr ) ) then
          call deallocate_d_array( num%darr )
        endif
        call nullify_list_object( num )
        num%exists = .false.
    endif
  end subroutine delete_list_object

  subroutine get_list_object( num, ival, iarr, rval, rarr, dval, darr )
  ! is a polymorphic getter
    type(list_object)              :: num
    integer, intent(out), optional :: ival, iarr(:)
    real, intent(out), optional    :: rval, rarr(:)
    real(double), intent(out), optional :: dval, darr(:)
    if( num%exists )then
        if( present(ival) ) then
          call get_i_scalar( num%ival, ival )
        endif
        if( present(rval) ) then
          call get_r_scalar( num%rval, rval ) 
        endif
        if( present(dval) ) then
          call get_d_scalar( num%dval, dval ) 
        endif
        if( present(iarr) ) then
          call get_i_array( num%iarr, iarr ) 
        endif
        if( present(rarr) ) then
          call  get_r_array( num%rarr, rarr ) 
        endif
        if( present(darr) ) then
          call get_d_array( num%darr, darr ) 
        endif
    else
        write(*,*) 'Cannot get from non-existing object!'
        write(*,*) 'In: get_list_object, class: simple_list_object.f95'
        stop
    endif
  end subroutine get_list_object

  subroutine print_list_object( num )
  ! is for prettier printing
    type(list_object), intent(in) :: num 
    if( associated( num%pt_to_ival ) ) then
      call print_i_scalar( num%ival ) 
    endif
    if( associated( num%pt_to_rval ) ) then
      call print_r_scalar( num%rval )
    endif
    if( associated( num%pt_to_dval ) ) then
      call print_d_scalar( num%dval )
    endif
    if( associated( num%pt_to_iarr ) ) then
      call print_i_array( num%iarr )
    endif
    if( associated( num%pt_to_rarr ) ) then
      call print_r_array( num%rarr )
    endif
    if( associated( num%pt_to_darr ) ) then
      call print_d_array( num%darr )
    endif
  end subroutine print_list_object

  function list_object_exists( num ) result( exists )
  ! returns existence status of the list object
      type(list_object), intent(in) :: num
      logical :: exists
      exists = num%exists
  end function list_object_exists

  function i_scalar_exists_( num, ival )result( exists )
  ! makes the question "Is _ival_ in list_object?" possible to ask.
      type(list_object)   :: num 
      integer, intent(in) :: ival
      logical             :: exists
      exists = .false.
      if( associated( num%pt_to_ival ) ) then
          exists = i_scalar_exists( num%ival, ival )
      endif
  end function i_scalar_exists_

  function is_ival_associated( num ) result( is )
  ! checks the association status of _i_scalar_.
      type(list_object), intent(in) :: num
      logical                       :: is 
      is = associated( num%pt_to_ival )
  end function is_ival_associated

  function is_iarr_associated( num ) result( is )
  ! checks the association status of _i_array_
      type(list_object), intent(in) :: num
      logical                       :: is 
      is = associated( num%pt_to_iarr )
  end function is_iarr_associated

  function is_rval_associated( num ) result( is )
  ! checks the association status of _r_scalar_
      type(list_object), intent(in) :: num
      logical                       :: is 
      is = associated( num%pt_to_rval )
  end function is_rval_associated
  
  function is_dval_associated( num ) result( is )
  ! checks the association status of _r_scalar_
      type(list_object), intent(in) :: num
      logical                       :: is 
      is = associated( num%pt_to_dval )
  end function is_dval_associated

  function is_rarr_associated( num ) result( is )
      ! checks the association status of _r_array_
      type(list_object), intent(in) :: num
      logical                       :: is 
      is = associated( num%pt_to_rarr )
  end function is_rarr_associated
  
  function is_darr_associated( num ) result( is )
      ! checks the association status of _r_array_
      type(list_object), intent(in) :: num
      logical                       :: is 
      is = associated( num%pt_to_darr )
  end function is_darr_associated  

end module  simple_list_object