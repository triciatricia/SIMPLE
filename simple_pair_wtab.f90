!==Class simple_pair_wtab

module simple_pair_wtab
use simple_jiffys
implicit none
save

public :: pair_wtab, new_pair_wtab, flush_pair_wtab, recover_pair_wtab, get_wmax_pair,&
kill_pair_wtab, clear_pair_wtab, pair_w_exist, set_pair_w, merge_pair_w, remove_pair_w,&
get_pair_w, alloc_pair_w
private

type :: pair_w
    real, pointer :: w=>null()
end type pair_w

type pair_wtab
	integer                   :: N=0, mloc(2)=0
	type(pair_w), allocatable :: pw(:,:)
	real, allocatable         :: mvals(:), row(:)
	integer, allocatable      :: mpos(:)
	real                      :: mval=-1., filtw=-1.
	logical                   :: exists=.false.
end type pair_wtab

contains

    function new_pair_wtab( Nobjs, fw ) result( num )
    ! constructs a new pair weight table
    	type(pair_wtab)            :: num
        integer, intent(in)        :: Nobjs
        real, intent(in), optional :: fw
        integer                    :: alloc_stat
        allocate(num%pw(Nobjs,Nobjs), num%mvals(Nobjs),&
        num%mpos(Nobjs), num%row(Nobjs), stat=alloc_stat)
        call alloc_err('In: make_pair_wtab, module: simple_pair_wtab.f90', alloc_stat)
        if( present(fw) ) num%filtw = fw
        num%mvals = num%filtw
        num%mval = num%filtw
        num%N = Nobjs
        num%mpos = 0
        num%exists = .true.
    end function new_pair_wtab
    
    subroutine flush_pair_wtab( num, fname )
    	type(pair_wtab)  :: num
        character(len=*) :: fname
        integer          :: wtl, file_stat, i, j
        ! Check rec-length and open file
        inquire(iolength=wtl) num%row
        open(unit=12, file=fname, status='replace', iostat=file_stat,&
        access='direct', action='write', form='unformatted', recl=wtl )
        if( file_stat /= 0 )then ! cannot open file
            write(*,*) 'Cannot open file: ', fname
            write(*,*) 'In: flush_pair_wtab, module: simple_pair_wtab.f90'
            stop
        endif
        do i=1,num%N
            do j=1,num%N
                num%row(j) = get_pair_w(num, i, j)
            end do
            write(12,rec=i) num%row
        end do
        close(12)
    end subroutine flush_pair_wtab
    
    subroutine recover_pair_wtab( num, fname )
    	type(pair_wtab)  :: num
        character(len=*) :: fname
        integer          :: wtl, file_stat, i, j
        ! Check rec-length and open file
        inquire(iolength=wtl) num%row
        open(unit=12, file=fname, status='old', iostat=file_stat,&
        access='direct', action='read', form='unformatted', recl=wtl )
        if( file_stat /= 0 )then ! cannot open file
            write(*,*) 'Cannot open file: ', fname
            write(*,*) 'In: recover_pair_wtab, module: simple_pair_wtab.f90'
            stop
        endif
        do i=1,num%N
            read(12,rec=i) num%row
            do j=1,num%N
                if( num%row(j) /= num%filtw ) call set_pair_w(num,i,j,num%row(j))
            end do
        end do
        close(12)
    end subroutine recover_pair_wtab
      
    subroutine get_wmax_pair( num, k, l, w, halt )
    	type(pair_wtab)      :: num
        integer, intent(out) :: k, l
        real, intent(out)    :: w
        logical, intent(out) :: halt
        k    = num%mloc(1)
        l    = num%mloc(2)
        w    = num%mval
        halt = .false.
        if( k == l ) halt = .true.
        if( w == num%filtw ) halt = .true.
    end subroutine get_wmax_pair
    
    subroutine kill_pair_wtab( num )
    	type(pair_wtab) :: num
        if( num%exists )then
	       deallocate(num%pw, num%mvals, num%mpos, num%row)
	       num%exists = .false.
	    endif
    end subroutine kill_pair_wtab
    
    subroutine clear_pair_wtab( num )
    ! is clearing the table
    	type(pair_wtab) :: num
        integer :: i, j
        if( num%exists )then
            do i=1,num%N-1
                do j=i+1,num%N
                    if( associated(num%pw(i,j)%w) )then
                        deallocate(num%pw(i,j)%w)
                        nullify(num%pw(i,j)%w, num%pw(j,i)%w) ! mirror symmetric nullification
                    endif
                end do
            end do
            num%mpos = 0
            num%mloc = 0
        endif
    end subroutine clear_pair_wtab

    function pair_w_exist( num, i, j ) result(bool)
    ! checks existence of a pair weight
    	type(pair_wtab)     :: num
        integer, intent(in) :: i, j
        logical             :: bool
        if( j == i )then
            bool = .false.
        else
            bool = associated(num%pw(i,j)%w)
        endif
    end function pair_w_exist
    
    subroutine alloc_pair_w( num, i, j )
    	type(pair_wtab)     :: num
        integer, intent(in) :: i, j
        integer             :: alloc_stat
        if( j == i )then
            return
        else
            allocate( num%pw(i,j)%w, stat=alloc_stat ) ! make space for the new weigth
            call alloc_err('In: alloc_pair_w, module: simple_pair_wtab.f90', alloc_stat)
        endif
    end subroutine alloc_pair_w

    subroutine set_pair_w( num, i, j, w )
    ! is storing a pair weight
    	type(pair_wtab)     :: num
        integer, intent(in) :: i, j
        real, intent(in)    :: w
        integer             :: alloc_stat
        if( j == i )then
            return
        else
            if( .not. associated(num%pw(i,j)%w) )then
                allocate( num%pw(i,j)%w, stat=alloc_stat ) ! make space for the new weigth
                call alloc_err('In: set_pair_w, module: simple_pair_wtab.f90', alloc_stat)
            endif
            num%pw(i,j)%w = w
            num%pw(j,i)%w => num%pw(i,j)%w ! Introduction of mirror symmetry in the lookup
            ! update nearest neighs
            if( w > num%mvals(i) )then
                num%mvals(i) = w
                num%mpos(i)  = j
            endif    
            if( w > num%mvals(j) )then
                num%mvals(j) = w
                num%mpos(j)  = i
            endif
            ! update best  
            if( w > num%mval )then
                num%mval    = w
                num%mloc(1) = i
                num%mloc(2) = j
            endif
        endif     
    end subroutine set_pair_w

    subroutine merge_pair_w( num, i, j )
    ! is merging two pairs using the group average method
    	type(pair_wtab)     :: num
        integer, intent(in) :: i, j
        integer             :: k
        ! merge
        do k=1,num%N
            if( k /= i .and. k /= j ) then
                if( associated(num%pw(i,k)%w) .and. associated(num%pw(j,k)%w) )then
                    num%pw(i,k)%w = 0.5*(num%pw(i,k)%w+num%pw(j,k)%w)
                    num%pw(k,i)%w = num%pw(i,k)%w
                endif
            endif
            if( pair_w_exist(num,j,k) )then
                deallocate( num%pw(j,k)%w )
                nullify( num%pw(j,k)%w, num%pw(k,j)%w ) ! mirror symmetric nullification
            endif
        end do
        ! update nearest neighs
        call update_nn( num, i )
        ! remove j from nearest neighs
        num%mvals(j) = num%filtw
        ! translate the positions in neigh
        do k=1,num%N
            if(num%mpos(k) == j) num%mpos(k) = i
        end do
        ! find new best 
        call update_best( num )
    end subroutine merge_pair_w
    
    subroutine update_nn( num, i )
    ! update nearest neighs
    	type(pair_wtab)     :: num
        integer, intent(in) :: i
        integer             :: k, loc(1)
        do k=1,num%N
            if( associated(num%pw(i,k)%w) )then
                num%row(k) = num%pw(i,k)%w
            else
                num%row(k) = num%filtw
            endif 
        end do
        loc = maxloc(num%row)
        num%mpos(i) = loc(1)
        if( associated(num%pw(i,num%mpos(i))%w) )then
            num%mvals(i) = num%pw(i,num%mpos(i))%w
        else
            num%mvals(i) = num%filtw
        endif
    end subroutine update_nn
    
    subroutine update_best( num )
    ! find new best
    	type(pair_wtab) :: num
        integer :: loc(1)
        loc = maxloc(num%mvals)
        num%mval = num%mvals(loc(1))
        num%mloc(1) = loc(1)
        num%mloc(2) = num%mpos(num%mloc(1))
    end subroutine update_best

    subroutine remove_pair_w( num, i, j )
    ! is removing a pair w
    	type(pair_wtab) :: num
        integer, intent(in) :: i, j
        if( pair_w_exist(num,i,j) )then
            deallocate( num%pw(i,j)%w )
            nullify( num%pw(i,j)%w, num%pw(j,i)%w ) ! mirror symmetric nullification
        endif
        call update_nn( num, i )
        call update_nn( num, j )
        call update_best( num )
    end subroutine remove_pair_w

    function get_pair_w( num, i, j ) result( w )
    ! is getting a pair weight
    	type(pair_wtab)     :: num
        integer, intent(in) :: i, j
        real                :: w
        w = num%filtw
        if( pair_w_exist(num,i,j) )then
            w = num%pw(i,j)%w
        endif
    end function get_pair_w

end module simple_pair_wtab