module simple_tabu_end
use simple_jiffys
implicit none

! this module is used to modify the space available for optimization, 1..N are all attributes
! and the accessability of them is controlled via the add and drop tabu tenures. drop_tenure 
! is the number of iterations that an added element is forbidden to be dropped from the current
! solution and add_tenure is the number of iterations that a dropped element is forbidden to be added
! to the current solution  
type tabu_end
    private
    integer, allocatable :: a(:)
    integer, allocatable :: addts(:), dropts(:)
    integer :: addt=3, dropt=2, N, NT=0, cyc=0
    logical :: exists=.false., dyn=.false.
end type tabu_end

contains

    function new_tabu_end( N, tmin, tmax ) result( num )
        integer, intent(in)           :: N
        integer, intent(in), optional :: tmin, tmax
        type(tabu_end)                :: num
        integer                       :: i, counter, alloc_stat    
        allocate( num%a(N), stat=alloc_stat )
        call alloc_err('In: new_tabu_end, module simple_tabu_end.f90, alloc 1', alloc_stat)
        if( present(tmin) )then
            if( present(tmax) )then
                num%dyn = .true.
                num%NT = (tmax-tmin+1)*2
                allocate( num%addts(num%NT), num%dropts(num%NT), stat=alloc_stat )
                call alloc_err('In: new_tabu_end, module simple_tabu_end.f90, alloc 2', alloc_stat)
                ! generate tenure cycle
                num%dropt   = tmin
                num%addt    = tmin+(tmax-tmin)/2
                counter = 0
                do i=tmin,tmax
                    counter = counter+1
                    num%addt  = num%addt+1
                    if( num%addt > tmax ) then
                        num%addt = tmin
                    endif
                    num%addts(counter)  = num%addt
                    num%dropts(counter) = num%dropt
                    num%dropt = num%dropt+1
                end do
                num%dropt = tmin
                num%addt  = tmin+(tmax-tmin)/2
                do i=tmin,tmax
                    counter = counter+1
                    num%addt = num%addt-1
                    if( num%addt < tmin ) then
                        num%addt = tmax
                    endif
                    num%addts(counter)  = num%addt
                    num%dropts(counter) = num%dropt
                    num%dropt = num%dropt+1
                end do
            endif
        endif
        num%cyc    = 1      
        num%a      = 0 ! all integers from 1 to N made available for it >= 1 
        num%N      = N
        num%exists = .true.
    end function new_tabu_end

    subroutine kill_tabu_end( num )
        type(tabu_end), intent(inout) :: num
        if( num%exists ) then
            deallocate( num%a )
            if( num%dyn ) deallocate( num%addts, num%dropts )
            num%exists = .false.
        endif
    end subroutine kill_tabu_end

    subroutine reset_tabu_end( num )
        type(tabu_end), intent(inout) :: num
        num%a = 0
        num%cyc = 1
    end subroutine reset_tabu_end

    subroutine insert_tabu( num, it, added, dropped )
        type(tabu_end), intent(inout) :: num
        integer, intent(in)           :: it, added, dropped
        if( num%dyn )then
            num%cyc = num%cyc+1
            if( num%cyc > num%NT )then
                num%cyc = 1
            endif 
            if( added /= 0 )then
                num%a(added) = it+num%dropts(num%cyc)
            endif
            if( dropped /= 0 )then
                num%a(dropped) = it+num%addts(num%cyc)
            endif
        else
            if( added /= 0 )then
                num%a(added) = it+num%dropt
            endif
            if( dropped /= 0 )then
                num%a(dropped) = it+num%addt
            endif
        endif
    end subroutine insert_tabu

    function test_tabu_status( num, it, add, drop ) result( tabu )
        type(tabu_end), intent(inout) :: num
        integer, intent(in) :: it, add, drop
        logical :: tabu
        tabu = .false.
        if( add == 0 .or. drop == 0 )then
            return
        else if( it <= num%a(add) )then
            tabu = .true.
        else if( it <= num%a(drop) )then
            tabu = .true.
        endif
    end function test_tabu_status

end module simple_tabu_end