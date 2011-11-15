!==Module simple_syscalls
!
! simple_syscalls is a little module for calculating the relative and actual CPU-time.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution or modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund, 2009-10-01.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-10-01
!
module simple_syscalls
implicit none

contains

    real function dtime( time )
    ! is the fortran 90 variant of the classical dtime
        real                  :: time(2)
        double precision,save :: last_time = 0
        double precision      :: this_time
        intrinsic cpu_time
        call cpu_time(this_time)
        time(1) = this_time - last_time
        time(2) = 0
        dtime = time(1)
        last_time = this_time
    end function dtime

    real function etime( time )
    ! is the fortran 90 variant of the classical etime
        real :: time(2)
        call cpu_time(etime)
        time(1) = etime
        time(2) = 0
    end function etime 

    function getabscpu( lprint ) result( actual )
    ! is for getting the actual cputime
        logical, intent(in) :: lprint
        real                :: tarray(2)
        real                :: actual
        actual = etime( tarray )
        if( lprint )then
            write(*,'(A,2XF9.2)') 'Actual cpu-time:', actual
        endif
    end function getabscpu

    function getdiffcpu( lprint ) result( delta )
    ! is for getting the relative cpu-time
        logical, intent(in) :: lprint
        real                :: tarray(2)
        real                :: delta
        delta = dtime( tarray )
        if( lprint )then
            write(*,'(A,F9.2)') 'Relative cpu-time:', delta
        endif
    end function getdiffcpu

end module simple_syscalls