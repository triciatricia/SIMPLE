program inplrot
use simple_fstk
use simple_fplane
use simple_build
use simple_cmdline
use simple_params
implicit none
save
! declaration section
type(build)  :: b
logical      :: cmderr(3)
integer      :: i
if( command_argument_count() < 3 )then
    write(*,*) './inplrot fstk=fstkin.fim outfstk=fstkout.fim oritab=oris.dat'
    stop
endif
! parse command line
call parse_cmdline
! check command line arguments
cmderr(1) = .not. defined_cmd_carg('fstk')
cmderr(2) = .not. defined_cmd_carg('outfstk')
cmderr(3) = .not. defined_cmd_carg('oritab')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for inplrot defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
wchoice = 2
winsz   = 2
! Build all objects required for alignment
b = new_build(0)
call shrot_fstk(b, outfstk)
end program inplrot