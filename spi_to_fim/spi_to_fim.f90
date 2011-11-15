!==Program spi_to_fim
!
! _spi_to_fim_ is the SIMPLE program for making 2D Fourier transform stacks.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License. 
! *Author:* Hans Elmlund 2011-08-16.
!
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2011-08-16
!
program spi_to_fim
use simple_params
use simple_cmdline
use simple_fstk
use simple_jiffys
implicit none
save
! declaration section:
character(len=60) :: out_hed, out_stk
logical :: cmderr(6)
if( command_argument_count() < 6 )then
    write(*,*) './spi_to_fim stk=projs.spi box=100 nptcls=10000 smpd=2.33 outbdy=projs msk=<mask radius (in pixels)> [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr    = .false.
cmderr(1) = .not. defined_cmd_carg('stk')
cmderr(2) = .not. defined_cmd_rarg('box')
cmderr(3) = .not. defined_cmd_rarg('nptcls')
cmderr(4) = .not. defined_cmd_rarg('smpd')
cmderr(5) = .not. defined_cmd_carg('outbdy')
cmderr(6) = .not. defined_cmd_rarg('msk')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for spi_to_fim defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! make parameters
call make_params
! make output stack names:
out_hed = trim(adjustl(outbdy))//'.hed'
out_stk = trim(adjustl(outbdy))//'.fim'
call make_fstk( out_stk, out_hed )
call haloween(0)
if( debug == 'yes' )then
    write(0,'(a,1xa)') "GENERATED SPIDER STACK FOR INSPECTION: debug.spi"
else
    write(0,'(a,1xa)') "GENERATED FOURIER STACK:", trim(out_stk)
endif
write(0,'(a)') "**** SPI_TO_FIM NORMAL STOP ****"
end program spi_to_fim