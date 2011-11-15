program fim_shift
use simple_build
use simple_fstk
implicit none
save
type(build), target :: b
if( command_argument_count() < 4 )then
    write(*,*) './fim_shift fstk=in.fim outfstk=out.fim oritab=shiftdoc.dat nthr=<nr of openMP threads> [msk=<mask radius (in pixels)>] [trs=<origin shift>]  [debug=<yes|no>]'
    stop
endif
! parse command line
b = new_build( 0 )
call make_empty_fstk( outfstk, nptcls )
if( defined_cmd_rarg('trs') )then
    call sh_fstk( b, outfstk, trs, trs )
else
    ! shift fstk
    call sh_fstk( b, outfstk )
    ! set golbal fstk to shifted stk
    fstk = outfstk
    ! mask fsk
    if( msk > 1. ) call msk_fstk( b )
endif
call haloween( 0 )
write(0,'(a)') "**** FIM_SHIFT NORMAL STOP ****"
end program fim_shift