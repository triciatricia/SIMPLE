module simple_jiffys

interface file_exists
    module procedure file_exists_1
    module procedure file_exists_2
end interface

contains

    subroutine file_exists_1( file )
        character(len=*), intent(in) :: file
        logical :: here
        inquire(FILE=file, EXIST=here)
        if( .not. here )then
            write(*,*) 'The below file does not exist at the given location!'
            write(*,*) file
            stop
        endif
    end subroutine file_exists_1
    
    subroutine file_exists_2( file, here )
        character(len=*), intent(in) :: file
        logical, intent(out) :: here
        inquire(FILE=file, EXIST=here)
    end subroutine file_exists_2
    
    subroutine alloc_err( message, alloc_stat )
        character(len=*), intent(in) :: message
        integer, intent(in)          :: alloc_stat
        if( alloc_stat /= 0 ) then
            write(*,*) 'ERROR: Allocation failure!'
            write(*,*) message
            stop
        endif
    end subroutine alloc_err
    
    subroutine fopen_err( message, file_stat )
        character(len=*), intent(in) :: message
        integer, intent(in)          :: file_stat
        if( file_stat /= 0 ) then
            write(*,*) 'ERROR: File opening failure!'
            write(*,*) message
            stop
        endif
    end subroutine fopen_err
    
    subroutine del_binfile( file )
    	character(len=*), intent(in) :: file
		open (29, file=file, form='unformatted')
		close (29, status='delete')
    end subroutine del_binfile
    
    subroutine del_txtfile( file )
    	character(len=*), intent(in) :: file
		open (29, file=file, form='formatted')
		close (29, status='delete')
    end subroutine del_txtfile
    
    subroutine print_bar( i, imax, bar )
        integer, intent(in) :: i, imax
        character(len=1), intent(in) :: bar
        character(len=1) :: back
        integer :: k
        back = char(8)
        ! delete the bar and the percentage
        write(6,'(256a1)', advance='no') (back, k =1,(50*i/imax)+9)
        ! print the percentage and the bar
        write(6,'(2x,1i3,1a1,2x,1a1,256a1)', advance='no') &
        100*i/imax,'%','|', (bar, k=1,50*i/imax)
        close(6)
        open(6)
        if( i == imax ) write(6,'(a)') '| done.'
    end subroutine print_bar
    
    subroutine check_file_kind( fname, suffix )
        character(len=*), intent(in) :: fname, suffix
        integer :: pos
        pos = index(fname, suffix) ! position of suffix
        if( pos == 0 )then
            write(*,*) 'ERROR, ', fname, ' needs to have suffix: ', suffix
            write(*,*) 'In: check_file_kind, module: simple_jiffys.f90'
            stop
        endif
    end subroutine check_file_kind
    
    function add_to_fbody( fname, suffix, str ) result( newname )
        character(len=*), intent(in) :: fname, suffix, str
        character(len=32) :: newname
        integer :: pos
        pos = index(fname, suffix) ! position of suffix
        newname = fname(:pos-1)//trim(str)//trim(suffix)
    end function add_to_fbody
    
    function get_unit( ) result( iunit )
    ! GET_UNIT returns a free FORTRAN unit number.
    !
    !  Discussion:
    !
    !    A "free" FORTRAN unit number is a value between 1 and 99 which
    !    is not currently associated with an I/O device.  A free FORTRAN unit
    !    number is needed in order to open a file with the OPEN command.
    !
    !    If IUNIT = 0, then no free FORTRAN unit could be found, although
    !    all 99 units were checked (except for units 5, 6 and 9, which
    !    are commonly reserved for console I/O).
    !
    !    Otherwise, IUNIT is a value between 1 and 99, representing a
    !    free FORTRAN unit.  Note that GET_UNIT assumes that units 5 and 6
    !    are special, and will never return those values.
    !
    !  Licensing:
    !
    !    This code is distributed under the GNU LGPL license.
    !
    !  Modified:
    !
    !    26 October 2008
    !
    !  Author:
    !
    !    John Burkardt
    !
    !  Parameters:
    !
    !    Output, integer ( kind = 4 ) IUNIT, the free unit number.
    !
        integer :: i, ios, iunit, lopen
        iunit = 0
        do i=1,99
            if ( i /= 5 .and. i /= 6 .and. i /= 9 ) then
                inquire ( unit = i, opened = lopen, iostat = ios )
                if ( ios == 0 ) then
                    if ( .not. lopen ) then
                        iunit = i
                        return
                    end if
                end if
            end if
        end do
    end function get_unit
    
    subroutine timestamp ( )

!*****************************************************************************80
!
!! TIMESTAMP prints the current YMDHMS date as a time stamp.
!
!  Example:
!
!    May 31 2001   9:45:54.872 AM
!
!  Licensing:
!
!    This code is distributed under the GNU LGPL license.
!
!  Modified:
!
!    31 May 2001
!
!  Author:
!
!    John Burkardt
!
!  Parameters:
!
!    None
!
  implicit none

  character ( len = 8 )  ampm
  integer   ( kind = 4 ) d
  character ( len = 8 )  date
  integer   ( kind = 4 ) h
  integer   ( kind = 4 ) m
  integer   ( kind = 4 ) mm
  character ( len = 9 ), parameter, dimension(12) :: month = (/ &
    'January  ', 'February ', 'March    ', 'April    ', &
    'May      ', 'June     ', 'July     ', 'August   ', &
    'September', 'October  ', 'November ', 'December ' /)
  integer   ( kind = 4 ) n
  integer   ( kind = 4 ) s
  character ( len = 10 ) time
  integer   ( kind = 4 ) values(8)
  integer   ( kind = 4 ) y
  character ( len = 5 )  zone

  call date_and_time ( date, time, zone, values )

  y = values(1)
  m = values(2)
  d = values(3)
  h = values(5)
  n = values(6)
  s = values(7)
  mm = values(8)

  if ( h < 12 ) then
    ampm = 'AM'
  else if ( h == 12 ) then
    if ( n == 0 .and. s == 0 ) then
      ampm = 'Noon'
    else
      ampm = 'PM'
    end if
  else
    h = h - 12
    if ( h < 12 ) then
      ampm = 'PM'
    else if ( h == 12 ) then
      if ( n == 0 .and. s == 0 ) then
        ampm = 'Midnight'
      else
        ampm = 'AM'
      end if
    end if
  end if

  write ( *, '(a,1x,i2,1x,i4,2x,i2,a1,i2.2,a1,i2.2,a1,i3.3,1x,a)' ) &
    trim ( month(m) ), d, y, h, ':', n, ':', s, '.', mm, trim ( ampm )

  return
end subroutine timestamp

    
    subroutine haloween( handle )
        integer, intent(in) :: handle    
        write(handle,'(A)') " #                   #### # ##   ## ####  #    #####"     
        write(handle,'(A)') " ##                 #     # # # # # #   # #    #"
        write(handle,'(A)') " ###                ##### # # # # # ####  #    ###"   
        write(handle,'(A)') "  ####                  # # #  #  # #     #    #"   
        write(handle,'(A)') "   #####            ####  # #     # #     #### #####"
        write(handle,'(A)') "   #######"
        write(handle,'(A)') "    #######     #   #  ###  #    #     ###  #     # ##### ##### ##   #"
        write(handle,'(A)') "    ########    #   # #   # #    #    #   # #     # #     #     ##   #"
        write(handle,'(A)') "    ########    ##### ##### #    #    #   # #  #  # ###   ###   # #  #"
        write(handle,'(A)') "    #########   #   # #   # #    #    #   # #  #  # #     #     #  # #"
        write(handle,'(A)') "    ##########  #   # #   # #### ####  ###   ## ##  ##### ##### #   ##"
        write(handle,'(A)') "   ############"
        write(handle,'(A)') " ##############     ####   ##### #    #####  ###   #### #####"    
        write(handle,'(A)') "################    #   #  #     #    #     #   # #     #"
        write(handle,'(A)') " ################   ####   ###   #    ###   ##### ##### ###     #"
        write(handle,'(A)') "   ##############   #   #  #     #    #     #   #     # #      ##"
        write(handle,'(A)') "    ##############  #    # ##### #### ##### #   # ####  ##### ###"
        write(handle,'(A)') "    ##############                                          #####"
        write(handle,'(A)') "     ##############                                     ########"
        write(handle,'(A)') "     ##############                                 ###########"
        write(handle,'(A)') "     ###############                              ############"
        write(handle,'(A)') "     ################                           #############"
        write(handle,'(A)') "    #################      #                  ###############"
        write(handle,'(A)') "    ##################     ##    #           ################"
        write(handle,'(A)') "   ####################   ###   ##          #################"
        write(handle,'(A)') "      ##################  ########         ###################"
        write(handle,'(A)') "         ################  #######        #####################"
        write(handle,'(A)') "           #######################       #######################"
        write(handle,'(A)') "            #####################       #####################"
        write(handle,'(A)') "              #############################################"
        write(handle,'(A)') "               ###########################################"
        write(handle,'(A)') "               ##########################################"
        write(handle,'(A)') "                ########################################"
        write(handle,'(A)') "                #######################################"
        write(handle,'(A)') "                 ######################################"
        write(handle,'(A)') "                 ######################################"
        write(handle,'(A)') "                  ##########################      ######"
        write(handle,'(A)') "                  ###  ###################           ###"
        write(handle,'(A)') "                  ##    ###############               ##"
        write(handle,'(A)') "                  #     ##  ##########                 #"
        write(handle,'(A)') "                            #### ####"
        write(handle,'(A)') "                            ##    ###"
        write(handle,'(A)') "                            #     ##"
        write(handle,'(A)') "                                  #"
    end subroutine haloween

end module simple_jiffys