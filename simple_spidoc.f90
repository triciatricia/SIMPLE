module simple_spidoc
use simple_sll_list
use simple_jiffys
implicit none

interface write_spidoc
    module procedure write_spidoc_1
    module procedure write_spidoc_2
    module procedure write_spidoc_3
end interface write_spidoc

integer, parameter, private :: funit=61

contains

    subroutine write_spidoc_1( fname, arr )
        character(len=*), intent(in) :: fname
        real, intent(in)             :: arr(:)
        integer                      :: N, i, file_stat
        N = size(arr)
        open(unit=funit, file=fname, status='REPLACE', action='WRITE', iostat=file_stat)
        call fopen_err('In: write_spidoc_3, class: simple_spidoc.f90', file_stat)
        do i=1,N
            write(funit,'(I7,1XA,1XF11.4)') i, '1', arr(i)
        end do                
        close(funit)
    end subroutine write_spidoc_1
    
    subroutine write_spidoc_2( fname, arr )
        character(len=*), intent(in) :: fname
        integer, intent(in)          :: arr(:)
        integer                      :: N, i, file_stat
        N = size(arr)
        open(unit=funit, file=fname, status='REPLACE', action='WRITE', iostat=file_stat)
        call fopen_err('In: write_spidoc_3, class: simple_spidoc.f90', file_stat)
        do i=1,N
            write(funit,'(I7,1XA,1XF11.4)') i, '1', real(arr(i))
        end do                
        close(funit)
    end subroutine write_spidoc_2
    
    subroutine write_spidoc_3( fname, arr )
        character(len=*), intent(in) :: fname
        integer, intent(in)          :: arr(:,:) 
        integer                      :: i, j, file_stat, Nptcls, Nentries
        Nptcls = size(arr,1)
        Nentries = size(arr,2)
        open(unit=funit, file=fname, status='REPLACE', action='WRITE', iostat=file_stat)
        call fopen_err('In: write_spidoc_2, class: simple_spidoc.f90', file_stat)
        do i=1,Nptcls
            write(funit,'(I7,1XI)', advance='no') i, Nentries
            do j=1,Nentries
                if( j < Nentries )then
                    write(funit,'(1XI7)',advance='no') arr(i,j)
                else
                    write(funit,'(1XI7)') arr(i,j)
                endif
            end do     
        end do                
        close(funit)
    end subroutine write_spidoc_3
    
    subroutine write_spidoc_4( fname, arr )
        character(len=*), intent(in) :: fname
        real, intent(in)             :: arr(:,:) 
        integer                      :: i, j, file_stat, Nptcls, Nentries
        Nptcls = size(arr,1)
        Nentries = size(arr,2)
        open(unit=funit, file=fname, status='REPLACE', action='WRITE', iostat=file_stat)
        call fopen_err('In: write_spidoc_4, class: simple_spidoc.f90', file_stat)
        do i=1,Nptcls
            write(funit,'(I7,1XI)', advance='no') i, Nentries
            do j=1,Nentries
                if( j < Nentries )then
                    write(funit,'(1XF11.4)',advance='no') arr(i,j)
                else
                    write(funit,'(1XF11.4)') arr(i,j)
                endif
            end do     
        end do                
        close(funit)
    end subroutine write_spidoc_4

    subroutine read_spidoc( fname, arr )
        character(len=*), intent(in) :: fname
        integer, intent(out)         :: arr(:) 
        integer                      :: i, islask, jslask, file_stat, N
        N = size(arr)
        open(unit=funit, file=fname, status='OLD', action='READ', iostat=file_stat)
        call fopen_err('In: read_spidoc, class: simple_spidoc.f90', file_stat)
        do i=1,N
            read(funit,*) islask, jslask, arr(i)
        end do                
        close(funit)
    end subroutine read_spidoc
    
    subroutine make_classdoc( fname, list )
        character(len=*), intent(in) :: fname
        type(sll_list)               :: list
        integer                      :: j, counter, file_stat, ptcl, nobj
        nobj    = get_sll_size(list)
        counter = 0
        if( nobj < 1 ) return
        open(unit=funit, file=fname, status='REPLACE', action='WRITE', iostat=file_stat)
        call fopen_err('In: make_classdoc, class: simple_spidoc.f90', file_stat)
        do j=1,nobj
            call get_sll_node(list, j, ptcl)
            write(funit,'(I7,1XA,1XI7)') j, '1', ptcl
        end do                
        close(funit)
    end subroutine make_classdoc

    subroutine make_classdocs( fname, classes )
        character(len=*), intent(in) :: fname
        type(sll_list)               :: classes(:) ! array of linked lists, for storing the cls-info
        integer                      :: i, j, counter, file_stat, ptcl, nobj
        character(len=120)           :: classdoc, dig
        nobj = size(classes)
        counter = 0
        do i=1,nobj
            if( get_sll_size(classes(i)) /= 0 )then
                counter = counter+1
                write(dig,*) counter
                classdoc = trim(adjustl(fname))//trim(adjustl(dig))//'.spi'
                open(unit=funit, file=classdoc, status='REPLACE', action='WRITE', iostat=file_stat)
                call fopen_err('In: make_classdocs, class: simple_spidoc.f90', file_stat)
                do j=1,get_sll_size(classes(i))
                    call get_sll_node(classes(i), j, ptcl)
                    write(funit,'(I7,1XA,1XI7)') j, '1', ptcl
                end do                
                close(funit)
            endif
        end do
    end subroutine make_classdocs

end module simple_spidoc