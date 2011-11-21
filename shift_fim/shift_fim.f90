program shift_fim
use simple_fstk
use simple_params
use simple_cmdline
use simple_build
implicit none
save
logical     :: cmderr(3)
type(build) :: b
if( command_argument_count() < 3 )then
    write(*,*) './shift_fim fstk=fprojs.fim outfstk=fprojs_shifted.fim oritab=<previous rounds aligndoc> outfile=<aligndoc with zeroed shifts> [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line args
cmderr    = .false.
cmderr(1) = .not. defined_cmd_carg('fstk')
cmderr(2) = .not. defined_cmd_carg('outfstk')
cmderr(3) = .not. defined_cmd_carg('oritab')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for shift_fim defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! build
b = new_build(0)
if( debug == 'yes' )then
    call print_fstk_hed( hed )
else
    ! shift spider stack
    call sh_fstk( b, 'outfstk' )
    ! zero the shifts
    oris(:,4) = 0.
    oris(:,5) = 0.
    ! output the alignment doc
    do i=1,nptcls
        call set_aligndata( b%a, i, e1=oris(i,1), e2=oris(i,2), e3=oris(i,3), x=0., y=0., state=int(oris(i,6)) )
    end do
    ! write to file
    call write_aligndata( b%a, outfile )
endif
call haloween(0)
write(0,'(a)') "**** SHIFT_FIM NORMAL STOP ****"
end program shift_fim