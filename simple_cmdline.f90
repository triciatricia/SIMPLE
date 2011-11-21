!==Class simple_cmdline
!
! simple_cmdline is for parsing command line arguments. The code is distributed with the hope that it will be useful,
! but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund, 2011-08-17.
! 
!==Changes are documented below
!
module simple_cmdline
implicit none

private :: NMAX, cmds, cmdarg
public

type cmdarg
    character(len=32) :: key = ''
    real              :: rarg=0.
    character(len=32) :: carg = ''
end type cmdarg

integer, parameter :: NMAX = 60
type(cmdarg) :: cmds(NMAX)
    
contains

    subroutine parse_cmdline
        character(len=32) :: arg
        integer :: i, pos1, ri, ierr
        do i=1,command_argument_count()   
            call get_command_argument(i, arg)
            pos1 = index(arg, '=') ! position of '='
            ! parse everyting containing '='
            if( pos1 /= 0 )then
                cmds(i)%key = arg(:pos1-1) ! KEY
                if( index(arg(pos1+1:), '.spi') /= 0 )then
                    cmds(i)%carg = arg(pos1+1:)
                else if( index(arg(pos1+1:), '.fim') /= 0 )then
                    cmds(i)%carg = arg(pos1+1:)
                else if( index(arg(pos1+1:), '.dat') /= 0 )then
                    cmds(i)%carg = arg(pos1+1:)
                else if( index(arg(pos1+1:), '.log') /= 0 )then
                    cmds(i)%carg = arg(pos1+1:)
                else if( index(arg(pos1+1:), '.') /= 0 )then
                    read(arg(pos1+1:),'(F6.3)') cmds(i)%rarg
                else
                    read(arg(pos1+1:),'(I10)', iostat=ierr) ri
                    if( ierr==0 )then 
                        cmds(i)%rarg = real(ri)
                    else
                        cmds(i)%carg = arg(pos1+1:)
                    endif
                endif
            endif
        end do
    end subroutine parse_cmdline
    
    function defined_cmd_rarg( key ) result( def )
        character(len=*), intent(in) :: key
        logical :: def
        integer :: i
        def = .false.
        do i=1,NMAX
            if( cmds(i)%key == key )then
                if( cmds(i)%rarg /= 0. )then
                    def = .true.
                    return
                endif
            endif
        end do
    end function defined_cmd_rarg
    
    pure function get_cmd_rarg( key ) result( rval )
        character(len=*), intent(in) :: key
        real :: rval
        integer :: i
        rval = 0.
        do i=1,NMAX
            if( cmds(i)%key == key )then
                rval = cmds(i)%rarg
                return
            endif
        end do
    end function get_cmd_rarg
    
    function defined_cmd_carg( key ) result( def )
        character(len=*), intent(in) :: key
        logical :: def
        integer :: i
        def = .false.
        do i=1,NMAX
            if( cmds(i)%key == key )then
                if( cmds(i)%carg /= '' )then
                    def = .true.
                    return
                endif
            endif
        end do
    end function defined_cmd_carg
    
    pure function get_cmd_carg( key ) result( cval )
        character(len=*), intent(in) :: key
        character(len=32) :: cval
        integer :: i
        cval = ''
        do i=1,NMAX
            if( cmds(i)%key == key )then
                cval = cmds(i)%carg
                return
            endif
        end do
    end function get_cmd_carg

end module simple_cmdline