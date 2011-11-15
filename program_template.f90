!==Program NAME
!
! _NAME_ is a SIMPLE program for ...
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2011.
!
!==Changes are documented below
!
!* new code
!
program NAME
use simple_cmdline
use simple_build
use simple_params
implicit none
save
! declaration section
type(build) :: b
logical :: cmderr(3)
if( command_argument_count() < 3 )then
    write(*,*) './NAME fstk=instk.fim lp=<low-pass limit(in A){15-30}> nthr=<nr of openMP threads> [hp=<high-pass limit (in A)>] [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr(1) = .not. defined_cmd_carg('fstk')
cmderr(2) = .not. defined_cmd_rarg('lp')
cmderr(3) = .not. defined_cmd_rarg('nthr')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for NAME defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! build objects
b = new_build()

! execution section

end program NAME