program fim_to_spi
use simple_fstk
use simple_params
use simple_jiffys
use simple_cmdline
implicit none
save
logical :: cmderr(2)
if( command_argument_count() < 2 )then
    write(*,*) './fim_to_spi fstk=fprojs.fim outstk=stk.spi [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr    = .false.
cmderr(1) = .not. defined_cmd_carg('fstk')
cmderr(2) = .not. defined_cmd_carg('outstk')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for fim_to_spi defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! make params
call make_params
if( debug == 'yes' )then
    call print_fstk_hed( hed )
else
    ! make spider stack
    call fstk_mk_stkspi( fstk, outstk )
endif
call haloween(0)
write(0,'(a)') "**** FIM_TO_SPI NORMAL STOP ****"
end program fim_to_spi