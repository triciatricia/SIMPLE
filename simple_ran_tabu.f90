!==Class simple_ran_tabu
!
! simple_ran_tabu contains routines for generation of directed random numbers. The code is distributed 
! with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution
! or modification is regulated by the GNU General Public License. *Author:* Hans Elmlund, 2009-05-12.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
! 
module simple_ran_tabu
use simple_rnd
use simple_jiffys
implicit none

type :: ran_tabu
    private
    integer :: NP=0, N_tabus=0 ! integer ranges from 1 to NP
    logical, allocatable :: list(:)
    logical :: exists=.false.
end type ran_tabu

contains

    function new_ran_tabu( NP ) result( num )
    ! constructs a new tabulist
        integer, intent(in) :: NP
        type(ran_tabu)      :: num
        integer             :: alloc_stat
        num%NP = NP
        num%N_tabus = 0
        allocate( num%list(NP), stat=alloc_stat )
        call alloc_err('In: new_ran_tabu, module: simple_ran_tabu.f90', alloc_stat)
        num%list(:) = .true. ! all integers from 1 to NP made available
        num%exists  = .true.
    end function new_ran_tabu

    subroutine copy_ran_tabu( num_in, num_copy )
        type(ran_tabu), intent(in) :: num_in
        type(ran_tabu), intent(inout) :: num_copy
        if( num_in%NP /= num_copy%NP )then
            write(*,*) 'Cannot copy objects with different size (NP)!'
            write(*,*) 'In: copy_ran_tabu, module: simple_ran_tabu.f90'
            stop
        endif
        num_copy%NP      = num_in%NP
        num_copy%N_tabus = num_in%N_tabus
        num_copy%list    = num_in%list
    end subroutine copy_ran_tabu

    subroutine kill_ran_tabu( num )
    ! is a destructor
        type(ran_tabu), intent(inout) :: num
        if( num%exists ) then
            deallocate( num%list )
            num%NP = 0
            num%N_tabus = 0
            num%exists = .false.
        endif
    end subroutine kill_ran_tabu

    subroutine reset_ran_tabu( num )
    ! is for clearing the tabu history
        type(ran_tabu), intent(inout) :: num
        num%N_tabus = 0
        num%list(:) = .true. ! all integers from 1 to NP made available
    end subroutine reset_ran_tabu

    subroutine insert_ran_tabu( num, i )
    ! is for insertion of a tabu
        type(ran_tabu), intent(inout) :: num
        integer, intent(in) :: i
        if( num%list(i) ) then
            num%N_tabus = num%N_tabus+1
        endif
        num%list(i) = .false.
    end subroutine insert_ran_tabu

    function is_ran_tabu( num, i ) result( is )
        type(ran_tabu), intent(in) :: num
        integer, intent(in)        :: i
        logical :: is
        if( num%exists )then
            is = .not. num%list(i)
        else
            is = .false.
        endif
    end function is_ran_tabu

    subroutine remove_ran_tabu( num, i )
    ! is for removal of a tabu
        type(ran_tabu), intent(inout) :: num
        integer, intent(in) :: i
        if( .not. num%list(i) )then
            num%N_tabus = num%N_tabus-1
        endif
        num%list(i) = .true.
    end subroutine remove_ran_tabu

    function irnd_uni_tabu( num ) result( irnd )
    ! generates a uniform random integer [_1_,_NP_] not in the tabulist, 
    ! used to direct Monte Carlo search out of forbidden regions.
        type(ran_tabu), intent(in) :: num
        integer                    :: irnd
        do
            irnd = irnd_uni(num%NP)
            if( num%list(irnd) ) exit
        end do
    end function irnd_uni_tabu

     subroutine irnd_uni_pair_tabu( num, irnd, jrnd )
    ! generates a random disjoint pair
        type(ran_tabu), intent(in) :: num
        integer, intent(out)       :: irnd, jrnd
        irnd = irnd_uni_tabu( num ) 
        jrnd = irnd
        do while( irnd == jrnd ) 
            jrnd = irnd_uni_tabu( num )
        end do
    end subroutine irnd_uni_pair_tabu

    function irnd_gasdev_tabu( num, mean, stdev ) result( irnd )
    ! generates a normal random integer [_1_,_NP_] not in the tabulist, 
    ! used to direct Monte Carlo search out of forbidden regions.
        type(ran_tabu), intent(in) :: num
        real, intent(in)           :: mean, stdev
        integer                    :: irnd
        do
            irnd = irnd_gasdev( mean, stdev, num%NP )
            if( num%list(irnd) ) exit
        end do
    end function irnd_gasdev_tabu

    subroutine ne_ran_iarr( num, rndiarr )
    ! generates sequence of uniform random numbers [_1_,_NP_] without repetition
        type(ran_tabu), intent(inout) :: num
        integer, intent(out)          :: rndiarr(:)
        integer                       :: i, szrndiarr
        szrndiarr = size(rndiarr,1)
        if( szrndiarr == num%NP )then
            do i=1,szrndiarr
                rndiarr(i) = i
                call insert_ran_tabu( num, rndiarr(i) )
            end do
        else if( szrndiarr+num%N_tabus > num%NP ) then
            write( *,* ) 'Random numbers must be generated from a larger set'
            write( *,* ) 'In: ne_ran_iarr, module: simple_tabu.f90'
            stop
        else
            do i=1,szrndiarr
                rndiarr(i) = irnd_uni_tabu( num )
                call insert_ran_tabu( num, rndiarr(i) )  
            end do
        endif
    end subroutine ne_ran_iarr

end module simple_ran_tabu