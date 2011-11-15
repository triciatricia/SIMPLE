!==Class simple_aligndata
!
! simple_aligndata stores stores/modifies/accesses output from all alignment methods in _SIMPLE_. 
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution or modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund, 2009-06-11.
! 
!==Changes are documented below
!
!* incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_aligndata
use simple_heapsort
use simple_jiffys
implicit none

private :: align
public

interface print_aligndata
    module procedure print_aligndata_1
    module procedure print_aligndata_2
end interface

type :: align
! contains all ptcl specific output parameters of the alignment methods of _SIMPLE_.
    integer :: index=0, inplane=0
    integer :: class=0, ix=0, iy=0, state=1
    real    :: e1=0., e2=0., e3=0., x=0., y=0., corr=-1.
    real    :: q=0., lowpass=0., dist=0.
    real    :: err=0.
end type align

type aligndata
! contains an array of align:s (see private type align, below) that is indexed
! from _from_ptcl_ to _to_ptcl_
    private
    integer :: from_ptcl=0, to_ptcl=0, N=0
    type(align), allocatable :: vec(:)
    logical :: exists=.false.
end type

contains

    function new_aligndata( from_ptcl, to_ptcl ) result( num )
        ! allocates space for an array of align:s (see private type align, below) 
        integer,intent(in) :: from_ptcl, to_ptcl
        type(aligndata)    :: num
        integer            :: alloc_stat
        allocate( num%vec(from_ptcl:to_ptcl), stat=alloc_stat )
        call alloc_err( 'In: new_aligndata, module: simple_aligndata.f90', alloc_stat )
        num%from_ptcl = from_ptcl
        num%to_ptcl   = to_ptcl
        num%N         = to_ptcl-from_ptcl+1
        num%exists    = .true.
    end function new_aligndata
    
    subroutine kill_aligndata( num )
        ! is a destructor
        type(aligndata), intent(inout) :: num
        if( num%exists )then
            deallocate( num%vec )
            num%exists = .false.
        endif
    end subroutine kill_aligndata

    subroutine assign_aligndata( num, in )
        ! assigns aligndata object _in_ to _num_. The method is overloaded as
        ! (=) in the simple_abstr_vec class
        type(aligndata), intent(inout) :: num
        type(aligndata), intent(in)    :: in
        integer                        :: i
        call kill_aligndata( num )
        num = new_aligndata( in%from_ptcl, in%to_ptcl )
        do i=in%from_ptcl,in%to_ptcl
            num%vec(i) = in%vec(i)
        end do
        num%exists = .true.
    end subroutine assign_aligndata
    
    subroutine write_aligndata( num, outfile )
        type(aligndata) :: num
        character(len=*), intent(in) :: outfile
        integer :: file_stat, i
        open(unit=23, file=outfile, status='replace', iostat=file_stat, action='write', form='formatted')
        call fopen_err( 'In: print_aligndata_3', file_stat )
        do i=num%from_ptcl,num%to_ptcl
            call print_aligndata( num, i, 23, corr='CORR:', q='Q:', lowpass='HRES:', state='STATE:' )
        end do
        close(23)
    end subroutine write_aligndata

    subroutine print_aligndata_1( num, i, corr, q, lowpass, state, err, class, awksome )
    ! prints aligndata vec index _i_. The convention is to always print 
    ! Eulers and translations. Other data are printed based on the existence of intent(in) character strings 
    ! whose variable names are equivalent to the variables contained in the align derived type. The input
    ! character variables are printed first, preceeding the printing of their associated value (key-value style
    ! for simple parsing of data)
        type(aligndata)                        :: num
        integer, intent(in)                    :: i
        character(len=*), intent(in), optional :: corr, q, lowpass, state, err, class, awksome
        write(*, "(1X,F7.2,1X,F7.2,1X,F7.2)", advance="no") num%vec(i)%e1,num%vec(i)%e2,num%vec(i)%e3
        write(*, "(1X,F8.4,1X,F8.4)", advance="no") num%vec(i)%x,num%vec(i)%y
        if( present(corr) )then
            write(*,"(1X,A)", advance="no") corr
            write(*,"(1X,F7.4)", advance="no") num%vec(i)%corr
        endif
        if( present(q) )then
            write(*,"(1X,A)", advance="no") q
            write(*,"(1X,F6.2)", advance="no") num%vec(i)%q
        endif
        if( present(lowpass) )then
            write(*,"(1X,A)", advance="no") lowpass
            write(*,"(1X,F6.2)", advance="no") num%vec(i)%lowpass
        endif
        if( present(state) )then
            write(*,"(1X,A)", advance="no") state
            write(*,"(1X,I1)", advance="no") num%vec(i)%state
        endif
        if( present(err) )then
            write(*,"(1X,A)", advance="no") err
            write(*,"(1X,F6.2)", advance="no") num%vec(i)%err
        endif
        if( present(class) )then
            write(*,"(1X,A)", advance="no") class
            write(*,"(1X,I5)", advance="no") num%vec(i)%class
        endif
        if( present(awksome) )then
            write(*,"(1X,A)") awksome
        else
            write(*,"(1X,A)") 'AWKSOME'
        endif
    end subroutine print_aligndata_1
    
    subroutine print_aligndata_2( num, i, fhandle, corr, q, lowpass, state, err, class, awksome )
        type(aligndata), intent(in) :: num
        integer, intent(in)         :: i
        integer                     :: fhandle
        character(len=*), intent(in), optional :: corr, q, lowpass, state, err, class, awksome
        write(fhandle, "(1X,F7.2,1X,F7.2,1X,F7.2)", advance="no") num%vec(i)%e1,num%vec(i)%e2,num%vec(i)%e3
        write(fhandle, "(1X,F8.4,1X,F8.4)", advance="no") num%vec(i)%x,num%vec(i)%y
        if( present(corr) )then
            write(fhandle,"(1X,A)", advance="no") corr
            write(fhandle,"(1X,F7.4)", advance="no") num%vec(i)%corr
        endif
        if( present(q) )then
            write(fhandle,"(1X,A)", advance="no") q
            write(fhandle,"(1X,F6.2)", advance="no") num%vec(i)%q
        endif
        if( present(lowpass) )then
            write(fhandle,"(1X,A)", advance="no") lowpass
            write(fhandle,"(1X,F6.2)", advance="no") num%vec(i)%lowpass
        endif
        if( present(state) )then
            write(fhandle,"(1X,A)", advance="no") state
            write(fhandle,"(1X,I1)", advance="no") num%vec(i)%state
        endif
        if( present(err) )then
            write(fhandle,"(1X,A)", advance="no") err
            write(fhandle,"(1X,F6.2)", advance="no") num%vec(i)%err
        endif
        if( present(class) )then
            write(fhandle,"(1X,A)", advance="no") class
            write(fhandle,"(1X,I5)", advance="no") num%vec(i)%class
        endif
        if( present(awksome) )then
            write(fhandle,"(1X,A)") awksome
        else
            write(fhandle,"(1X,A)") 'AWKSOME'
        endif
    end subroutine print_aligndata_2
    
    subroutine set_aligndata( num, i, index, inplane, class, ix, iy, state, e1, e2, e3,&
    x, y, corr, q, lowpass, dist, err )
    ! is for storing data in position _i_ of the aligndata vec.
        type(aligndata)             :: num
        integer, intent(in)         :: i
        integer,intent(in),optional :: index, inplane
        integer,intent(in),optional :: class, ix, iy, state
        real,intent(in),optional    :: e1, e2, e3, x, y, corr, q
        real,intent(in),optional    :: lowpass, dist, err
        if( present(index) ) then
            num%vec(i)%index = index
        endif
        if( present(inplane) ) then
            num%vec(i)%inplane = inplane
        endif
        if( present(class) ) then
            num%vec(i)%class = class
        endif
        if( present(ix) ) then
            num%vec(i)%ix = ix
        endif
        if( present(iy) ) then
            num%vec(i)%iy = iy
        endif
        if( present(state) ) then
            num%vec(i)%state = state
        endif
        if( present(e1) ) then
            num%vec(i)%e1 = e1
        endif
        if( present(e2) ) then
            num%vec(i)%e2 = e2
        endif
        if( present(e3) ) then
            num%vec(i)%e3 = e3
        endif
        if( present(x) ) then
            num%vec(i)%x = x
        endif
        if( present(y) ) then
            num%vec(i)%y = y
        endif
        if( present(corr) ) then
            num%vec(i)%corr = corr
        endif
        if( present(q) ) then
            num%vec(i)%q = q
        endif
        if( present(lowpass) ) then
            num%vec(i)%lowpass = lowpass
        endif
        if( present(dist) ) then
            num%vec(i)%dist = dist
        endif
        if( present(err) ) then
            num%vec(i)%err = err
        endif
    end subroutine set_aligndata

    subroutine get_aligndata( num, i, index, inplane, class, ix, iy, state, e1, e2, e3,&
    x, y, corr, q, lowpass, dist, err )
    ! is for getting the data in position _i_ of the aligndata vec.
        type(aligndata)              :: num
        integer, intent(in)          :: i
        integer,intent(out),optional :: index, inplane
        integer,intent(out),optional :: class, ix, iy, state
        real,intent(out),optional    :: e1, e2, e3, x, y, corr, q
        real,intent(out),optional    :: lowpass, dist, err
        if( present(index) ) then
            index = num%vec(i)%index
        endif
        if( present(inplane) ) then
            inplane = num%vec(i)%inplane 
        endif
        if( present(class) ) then
            class = num%vec(i)%class 
        endif
        if( present(ix) ) then
            ix = num%vec(i)%ix
        endif
        if( present(iy) ) then
            iy = num%vec(i)%iy
        endif
        if( present(state) ) then
            state = num%vec(i)%state
        endif
        if( present(e1) ) then
            e1 = num%vec(i)%e1
        endif
        if( present(e2) ) then
            e2 = num%vec(i)%e2
        endif
        if( present(e3) ) then
            e3 = num%vec(i)%e3
        endif
        if( present(x) ) then
            x = num%vec(i)%x
        endif
        if( present(y) ) then
            y = num%vec(i)%y
        endif
        if( present(corr) ) then
            corr = num%vec(i)%corr
        endif
         if( present(q) ) then
            q = num%vec(i)%q
        endif
        if( present(lowpass) ) then
            lowpass = num%vec(i)%lowpass
        endif
        if( present(dist) ) then
            dist = num%vec(i)%dist
        endif
        if( present(err) ) then
            err = num%vec(i)%err
        endif
    end subroutine get_aligndata

    function get_lowpass_median( num ) result( lowpass_median )
    ! simpleulates the median lowpass limits of all existing 
    ! lowpass limits in aligndata
        type(aligndata), intent(in) :: num
        real                        :: lowpass_median
        type(heapsort)              :: hso
        integer                     :: i, counter
        hso = new_heapsort(num%N)
        counter = 0
        do i=num%from_ptcl,num%to_ptcl
            counter = counter+1
            call set_heapsort(hso, counter, num%vec(i)%lowpass )
        end do
        call sort_heapsort( hso ) 
        call get_heapsort( hso, num%N/2, lowpass_median )
        call kill_heapsort( hso )
    end function get_lowpass_median

    function get_max_trs( num ) result( max_trs )
    ! returns the maximum absolute translation in aligndata
        type(aligndata), intent(in)     :: num
        real                            :: max_trs, rmax(1)
        real, allocatable, dimension(:) :: trsarr
        integer                         :: i, alloc_stat, counter
        allocate( trsarr(num%N*2), stat=alloc_stat )
        call alloc_err( 'In: get_max_trs, module: simple_aligndata.f90', alloc_stat )
        counter = 0
        do i=num%from_ptcl,num%to_ptcl
            counter               = counter+1
            trsarr(counter)       = abs(num%vec(i)%x)
            trsarr(counter+num%N) = abs(num%vec(i)%y)
        end do
        rmax = maxval(trsarr)
        max_trs = rmax(1)
        deallocate( trsarr )
    end function get_max_trs

end module simple_aligndata