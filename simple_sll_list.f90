!==Class simple_sll_list
!
! simple_sll_list is a runtime polymorphic singly linked list class. In the present implementation each node of the list 
! can contain up to four different types of data:  _ival_, _rval_, _iarr_, and _rarr_, or any combination thereof. 
! The code is distributed with the hope that it will be useful, but 
! _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the GNU General Public License. 
! *Author:* Dominika Elmlund, 2009-05-25.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_sll_list
use simple_list_object
use simple_def_precision
implicit none
save 

private :: sll_node
public

interface copy_int_sll_list
    module procedure copy_int_sll_list_scalar
    module procedure copy_int_sll_list_arr
end interface

type sll_node
! contains the list_object _content_ and a pointer _next_ to the nextcoming node
    type(list_object)       :: content
    type(sll_node), pointer :: next => null()
end type sll_node

type sll_list
! contains the list. In this implementation I have separated the head of the list from the rest of the list 
! (Donald Knuth-style) 
    private
    integer                 :: list_size=0
    type(sll_node), pointer :: head
end type sll_list

contains

    function new_sll_list() result( num )
    ! allocates the head of the list and nullifies its pointer to the nextcoming node
        type(sll_list) :: num
        allocate(num%head)     ! allocate memory for the object
        nullify(num%head%next) ! start with an empty list
    end function new_sll_list
  
    subroutine add_sll_node( num, ival, rval, dval, iarr, rarr, darr )
    ! does polymorphic addition of a node to the end of the singly linked list and updates the list size
        type(sll_list), intent(inout)      :: num
        integer, intent(in), optional      :: ival, iarr(:)
        real, intent(in), optional         :: rval, rarr(:)
        real(double), intent(in), optional :: dval, darr(:)
        type(sll_node), pointer            :: prev, curr
        ! initialization, begin at the 0:th position
        prev => num%head 
        curr => prev%next
        do while( associated(curr) )! find location to insert new node
          prev => curr
          curr => curr%next
        end do
        allocate( curr ) ! insert it at the end of the list
        curr%content = new_list_object( ival=ival, rval=rval,&
        dval=dval, iarr=iarr, rarr=rarr, darr=darr )
        num%list_size = num%list_size+1  
        ! Redirect the old last
        prev%next => curr
    end subroutine add_sll_node
  
    subroutine get_sll_node( num, pos, ival, rval, dval, iarr, rarr, darr )
    ! is a polymorphic getter
        type(sll_list), intent(in)          :: num
        integer, intent(in)                 :: pos
        integer, intent(out), optional      :: ival, iarr(:)
        real, intent(out), optional         :: rval, rarr(:)
        real(double), intent(out), optional :: dval, darr(:)
        type(sll_node), pointer             :: curr
        integer                             :: counter
        if ( pos < 1 .or. pos > num%list_size ) then
          write(*,*) 'Variable pos is out of range!'
          write(*,*) 'In: get_sll_node, module: simple_sll_list.f95'
          stop
        endif
        curr => num%head%next
        counter = 0
        do ! find location of node
            counter = counter+1
            if( counter == pos ) exit
            curr => curr%next
        end do
        call get_list_object( curr%content, ival=ival, rval=rval,&
        dval=dval, iarr=iarr, rarr=rarr, darr=darr )
    end subroutine get_sll_node
    
    subroutine set_sll_node( num, pos, ival, rval, dval, iarr, rarr, darr )
    ! is a polymorphic getter
        type(sll_list), intent(in)         :: num
        integer, intent(in)                :: pos
        integer, intent(in), optional      :: ival, iarr(:)
        real, intent(in), optional         :: rval, rarr(:)
        real(double), intent(in), optional :: dval, darr(:)
        type(sll_node), pointer            :: curr
        integer                            :: counter
        logical                            :: err
        if ( pos < 1 .or. pos > num%list_size ) then
          write(*,*) 'Variable pos is out of range!'
          write(*,*) 'In: set_sll_node, module: simple_sll_list.f90'
          stop
        endif
        curr => num%head%next
        counter = 0
        do ! find location of node
            counter = counter+1
            if( counter == pos ) exit
            curr => curr%next
        end do
        call set_list_object( curr%content, err, ival=ival, rval=rval,&
        dval=dval, iarr=iarr, rarr=rarr, darr=darr )
        if( err )then
            write(*,*) 'No space allocated for position:', pos
            write(*,*) 'In: set_sll_node, module: simple_sll_list.f90'
        endif 
    end subroutine set_sll_node
    
    subroutine insert_sll_node( num, pos, ival, rval, dval, iarr, rarr, darr )
    ! does polymorphic insertion of a node into the singly linked list and updates the list size
        type(sll_list), intent(inout)      :: num
	integer, intent(in)		   :: pos
        integer, intent(in), optional      :: ival, iarr(:)
        real, intent(in), optional         :: rval, rarr(:)
        real(double), intent(in), optional :: dval, darr(:)
        type(sll_node), pointer            :: prev, curr, toadd
	integer				   :: counter
	! Check if pos is out of range
        if ( pos < 1 .or. pos > num%list_size+1 ) then
          write(*,*) 'Variable pos is out of range!'
          write(*,*) 'In: insert_sll_node, module: simple_sll_list.f90'
          stop
        endif
        ! initialization, begin at the 0:th position
        prev => num%head 
        curr => prev%next
	counter = 0
	do ! find location of node
	    counter = counter + 1
	    if (counter == pos) exit
	    prev => curr
	    curr => curr%next
	end do
        allocate( toadd ) ! insert it after prev and before curr
        toadd%content = new_list_object( ival=ival, rval=rval,&
        dval=dval, iarr=iarr, rarr=rarr, darr=darr )
        num%list_size = num%list_size+1  
        ! Redirect
        prev%next => toadd
	if (associated(curr)) toadd%next => curr
    end subroutine insert_sll_node
    
    function sll_minloc( num, imin, rmin, dmin ) result( loc )
        type(sll_list)                      :: num
        integer, intent(out), optional      :: imin
        real, intent(out), optional         :: rmin
        real(double), intent(out), optional :: dmin
        integer                             :: loc
        type(sll_node), pointer             :: curr
        integer                             :: pos, iv
        real                                :: rv
        real(double)                        :: dv
        ! initialization, begin at the 1:th position 
        curr => num%head%next
        if( present(imin) ) call get_list_object( curr%content, ival=imin )
        if( present(rmin) ) call get_list_object( curr%content, rval=rmin )
        if( present(dmin) ) call get_list_object( curr%content, dval=dmin )      
        pos  = 1 ! with pos set to 1
        do while( associated(curr) )
            if( present(imin) )then
                call get_list_object( curr%content, ival=iv )
                if( iv <= imin )then
                    loc = pos
                    imin = iv
                endif
            endif
            if( present(rmin) )then
                call get_list_object( curr%content, rval=rv )
                if( rv <= rmin )then
                    loc = pos
                    rmin = rv
                endif  
            endif
            if( present(dmin) )then
                call get_list_object( curr%content, dval=dv )
                if( dv <= dmin )then
                    loc = pos
                    dmin = dv
                endif
            endif
            curr => curr%next
            pos = pos+1
        end do
    end function sll_minloc
    
    function sll_maxloc( num, imax, rmax, dmax ) result( loc )
        type(sll_list)                      :: num
        integer, intent(out), optional      :: imax
        real, intent(out), optional         :: rmax
        real(double), intent(out), optional :: dmax
        integer                             :: loc
        type(sll_node), pointer             :: curr
        integer                             :: pos, iv
        real                                :: rv
        real(double)                        :: dv
        ! initialization, begin at the 1:th position 
        curr => num%head%next
        if( present(imax) ) call get_list_object( curr%content, ival=imax )
        if( present(rmax) ) call get_list_object( curr%content, rval=rmax )
        if( present(dmax) ) call get_list_object( curr%content, dval=dmax )      
        pos  = 1 ! with pos set to 1
        do while( associated(curr) )
            if( present(imax) )then
                call get_list_object( curr%content, ival=iv )
                if( iv >= imax )then
                    loc = pos
                    imax = iv
                endif
            endif
            if( present(rmax) )then
                call get_list_object( curr%content, rval=rv )
                if( rv >= rmax )then
                    loc = pos
                    rmax = rv
                endif  
            endif
            if( present(dmax) )then
                call get_list_object( curr%content, dval=dv )
                if( dv >= dmax )then
                    loc = pos
                    dmax = dv
                endif
            endif
            curr => curr%next
            pos = pos+1
        end do
    end function sll_maxloc
      
    subroutine delete_sll_node( num, pos )
    ! deallocates a sll_list node and redirects the pointer to next node
        type(sll_list), intent(inout) :: num
        integer, intent(in)           :: pos
        type(sll_node), pointer       :: prev, curr
        integer                       :: counter
        if ( pos < 1 .or. pos > num%list_size ) then
          write(*,*) 'Variable pos is out of range!'
          write(*,*) 'In: get_sll_node, module: simple_sll_list.f95'
          stop
        endif
        ! initialization, begin at the 0:th position
        prev => num%head
        curr => prev%next
        if( .not. associated(curr) ) then ! end of list
            num%list_size = 0
            return
        endif     
        counter = 0
        do ! find node to delete
          counter = counter+1
          if( pos == counter ) then
            exit
          else ! move to the next node of the list
            prev => curr
            curr => curr%next
          endif
        end do
        ! delete the node
        if( associated( curr%next ) ) then       
          prev%next => curr%next                ! redirect pointer
          call delete_list_object( curr%content ) ! free space for the List Object    
          deallocate( curr )                    ! free space for node
          nullify( curr )
        else
          call delete_list_object( curr%content ) ! free space for the list object
          deallocate( curr )                    ! free space for node
          nullify( curr, prev%next )
        endif
        num%list_size = num%list_size-1          ! update the list size
    end subroutine delete_sll_node
    
    subroutine kill_sll_list( num )
    ! is a destructor
        type(sll_list), intent(inout) :: num
        integer                       :: i
        if( num%list_size >= 0 )then
	    do i=1,num%list_size
		call delete_sll_node( num, 1 )
	    end do
	    endif
        if( associated(num%head) )then
	    deallocate(num%head)
	    nullify(num%head)
	    endif
    end subroutine kill_sll_list
    
!    subroutine redirect_sll_list( targ, point )
!        type(sll_list) :: targ, point
!        point%list_size = targ%list_size
!        ! make resulting list a replica of num_in
!        point%head%next => targ%head%next
!    end subroutine redirect_sll_list
    
    function clone_sll_list( num_in ) result( num )
        type(sll_list) :: num_in, num
        ! Make resulting list
        allocate( num%head )
        num%list_size = num_in%list_size
        ! make resulting list a replica of num_in
        num%head%next => num_in%head%next
    end function clone_sll_list
    
    function copy_int_sll_list_scalar( num_in ) result( num )
    ! Copy the ival sll list. Unlike clone_sll_list, the returned list will have different
    ! pointers. Doesn't work for arrays. 
        type(sll_list), intent(in)	:: num_in
	type(sll_list)			:: num
	integer				:: i
	integer 			:: ival
        ! Make resulting list
	num = new_sll_list()
	do i=1,num_in%list_size
	    call get_sll_node( num_in, i, ival )
	    call add_sll_node( num, ival )
	end do
    end function copy_int_sll_list_scalar

    function copy_int_sll_list_arr( sll_arr, size_arr ) result( arr_out )
    ! Copy the ival sll lists in an array. Unlike clone_sll_list, the returned list will have different
    ! pointers. Doesn't work for arrays (iarr). 
        integer, intent(in)		:: size_arr
	type(sll_list), intent(in)	:: sll_arr(size_arr)
	type(sll_list)			:: arr_out(size_arr)
	integer				:: i
	do i=1,size_arr
	    arr_out(i) = copy_int_sll_list( sll_arr(i) )
	end do
    end function copy_int_sll_list_arr
    
    function add_sll_lists( num1, num2 ) result( num )
    ! is joining two singly linked lists together, leaving the two lists as they are and 
    ! returning a merged list without allocating any new memory other than the head
        type(sll_list)                :: num
        type(sll_list), intent(inout) :: num1
        type(sll_list), intent(inout) :: num2
        type(sll_node), pointer    :: prev, curr
        ! Make resulting list
        allocate( num%head )
        num%list_size = num1%list_size + num2%list_size
        ! make resulting list a replica of num1
        num%head%next => num1%head%next
        ! do the choka choka
        prev => num%head
        curr => prev%next
        do while( associated(curr) )
          prev => curr
          curr => curr%next
        end do
        prev%next => num2%head%next
    end function add_sll_lists 
  
    function append_sll_lists( num1, num2 ) result( num )
    ! is joining two singly linked lists together. The first node of 
    ! the second list (_num2_) is joined with the last node of the 
    ! first list (_num1_). The input lists do not exist anymore after this operation.
        type(sll_list)             :: num
        type(sll_list), intent(inout) :: num1
        type(sll_list), intent(inout) :: num2
        type(sll_node), pointer    :: prev, curr
        ! Make resulting list
        allocate( num%head )
        num%list_size = num1%list_size + num2%list_size
        ! make resulting list a replica of num1
        num%head%next => num1%head%next
        ! remove list 1
        deallocate( num1%head )
        nullify( num1%head )
        num1%list_size = 0
        ! do the choka choka
        prev => num%head
        curr => prev%next
        do while( associated(curr) )
          prev => curr
          curr => curr%next
        end do
        prev%next => num2%head%next
        ! remove list 2
        deallocate( num2%head )
        nullify( num2%head )
        num2%list_size = 0
    end function append_sll_lists 
  
    subroutine print_sll_list( num )
    ! is for prettier printing
        type(sll_list), intent(in) :: num
        type(sll_node), pointer    :: curr
        integer                    :: pos
        ! initialization, begin at the 1:th position 
        curr => num%head%next
        pos  = 0 ! with pos set to 0 
        do while( associated( curr ) )
          pos = pos+1
          write( *,* ) 'DATA IN NODE: ', pos
          call print_list_object( curr%content )
          curr => curr%next
        end do
    end subroutine print_sll_list
  
    function sll_iexists( num, ival ) result( pos )
    ! checks the existence of _ival_ 
        type(sll_list), intent(in) :: num
        integer, intent(in)        :: ival
        integer                    :: pos
        type(sll_node), pointer    :: curr
        logical                    :: exists=.false.
        pos = 0
        curr => num%head%next
        do while( associated( curr ) )
            pos = pos+1
            exists = i_scalar_exists_( curr%content, ival )
            curr => curr%next
            if( exists ) exit
        end do
        if( exists .neqv. .true. ) pos = 0
    end function sll_iexists
   
    pure function get_sll_size( num ) result( list_size )
    ! returns the size of the list
        type(sll_list), intent(in) :: num
        integer                    :: list_size
        list_size = num%list_size   
    end function get_sll_size

end module simple_sll_list