module simple_fstk
use simple_params
use simple_fftw3
use simple_stkspi
use simple_imgspi
use simple_math
use simple_stat
use simple_build
use simple_jiffys
use simple_fplane
implicit none

interface fstk_mk_cavgs
    module procedure fstk_mk_cavgs_1
    module procedure fstk_mk_cavgs_2
end interface

contains

    subroutine make_fstk( stknam, hednam )
        character(len=*), intent(in) :: stknam, hednam
        type(imgspi)                 :: img
        type(stkspi)                 :: stack
        real, pointer                :: img_ptr(:,:)
        complex, allocatable         :: outft(:,:)
        character(len=256)           :: stkconv
        integer :: alloc_stat, file_stat, i
        ! allocate:
        allocate( outft(-xdim:xdim,-xdim:xdim), stat=alloc_stat )
        if( alloc_stat /= 0 ) then
            write(*,*) 'Aborting, memory allocation failed!'
            write(*,*) 'In: make_fstk, module: simple_fstk.f90'
            stop
        endif
        ! define rec length:
        inquire( iolength=ftsz ) outft
        ! make header
        call make_fstk_hed( hednam, nptcls )
        ! make stack:
        open( unit=20, file=stknam, status='replace', iostat=file_stat,&
        access='direct', action='write', form='unformatted', recl=ftsz )
        call fopen_err('In: make_fstk, module: simple_fstk.f90', file_stat)
        ! make spider stack
        stack = new_stkspi( nimgs=2 )
        if( debug == 'yes' ) call write_stk_hed( stack, 'debug.spi' )
        ! determine how to convert the stack
        call find_stkconv( stack, stk, stkconv )
        do i=1,nptcls
            ! make image
            img = new_imgspi()
            call read_imgspi( stack, stk, i, img, stkconv )
            call norm_imgspi(img)
            if( msk > 1. ) call mask_imgspi( img, msk )
            if( debug == 'yes' ) call write_imgspi( stack, 'debug.spi', 1, img )
            call shift_imgspi( img )
            if( debug == 'yes' ) call write_imgspi( stack, 'debug.spi', 2, img )
            if( debug == 'yes' ) return
            call get_imgspi_ptr( img, img_ptr )
            call simple_2dfft( img_ptr, box, outft )
            write( 20, rec=i ) outft
            call kill_imgspi( img )
        end do
        close(20)
    end subroutine make_fstk
    
    subroutine make_fstk_hed( hednam, nobjs )
        character(len=*), intent(in) :: hednam
        integer, intent(in) :: nobjs
        integer :: file_stat, hrecsize
        real :: rval
        inquire( iolength=hrecsize ) rval
        ! make stack header:
        open( unit=19, file=hednam, status='replace', iostat=file_stat,&
        access='direct', action='write', form='unformatted', recl=hrecsize)
        if( file_stat /= 0 )then ! cannot open file
            write(*,*) 'Cannot open file: ', hednam
            write(*,*) 'In: make_fstk_hed, module: simple_fstk.f90'
            stop
        endif
        write(19,rec=1) real(nobjs)    ! number of transforms
        write(19,rec=2) real(xdim)   ! Fourier dim
        write(19,rec=3) smpd           ! sampling distance
        write(19,rec=4) real(ftsz)     ! 2D FT size
        write(19,rec=5) real(hrecsize) ! header rec size
        close(19)
    end subroutine make_fstk_hed
    
    subroutine print_fstk_hed( hednam )
        character(len=*), intent(in) :: hednam
        integer :: file_stat, hrecsize
        real :: rval
        inquire( iolength=hrecsize ) rval
        ! make stack header:
        open( unit=19, file=hednam, status='old', iostat=file_stat,&
        access='direct', action='read', form='unformatted', recl=hrecsize)
        if( file_stat /= 0 )then ! cannot open file
            write(*,*) 'Cannot open file: ', hednam
            write(*,*) 'In: print_fstk_hed, module: simple_fstk.f90'
            stop
        endif
        read(19,rec=1) rval
        write(*,'(A,I6)') 'NR OF TRANSFORMS: ',int(rval)
        read(19,rec=2) rval
        write(*,'(A,5XI6)') 'FOURIER DIM: ',int(rval)
        read(19,rec=3) rval
        write(*,'(A,4XF5.2)') 'SAMPLING DIST: ',rval
        read(19,rec=4) rval
        write(*,'(A,4XI6)') 'FOURIER SIZE: ',int(rval)
        read(19,rec=5) rval
        write(*,'(A,1XI6)') 'HEADER REC SIZE: ',int(rval)
        close(19)
    end subroutine print_fstk_hed
    
    subroutine make_empty_fstk( stknam, nobjs )
        character(len=*), intent(in) :: stknam
        integer, intent(in)          :: nobjs
        character(len=32) :: hednam
        integer :: file_stat, pos
        ! make header
        hednam = stknam
        pos = index(hednam, '.fim') ! position of '.fim'
        hednam(pos:pos+3) = '.hed'  ! replacing .fim with .hed
        call make_fstk_hed( hednam, nobjs )
        ! make stack:
        open( unit=20, file=stknam, status='replace', iostat=file_stat,&
        access='direct', action='write', form='unformatted', recl=ftsz )
        call fopen_err('In: make_empty_fstk, module: simple_fstk.f90', file_stat)
        close(20)
    end subroutine make_empty_fstk
    
    subroutine sh_fstk( b, newstk )
        type(build), intent(inout) :: b
        character(len=*), optional :: newstk
        logical :: isthere
        integer :: i
        if( present(newstk) )then
            ! check existence of file
            call file_exists( newstk, isthere )
            if( isthere )then
            else
                call make_empty_fstk( newstk, nptcls )
            endif
        endif
        do i=1,nptcls
            call read_fplane( b%f(ptcl)%arr, fstk, i )
            call shift_fplane( b%f(ptcl)%arr, oris(i,4), oris(i,5) )
            if( present(newstk) ) then
                call write_fplane( b%f(ptcl)%arr, newstk, i )    
            else
                call write_fplane( b%f(ptcl)%arr, fstk, i )  
            endif
        end do
    end subroutine sh_fstk
    
    subroutine shrot_fstk( b, newstk )
        type(build), intent(inout) :: b
        character(len=*), optional :: newstk
        logical :: isthere
        integer :: i
        if( present(newstk) )then
            ! check existence of file
            call file_exists( newstk, isthere )
            if( isthere )then
            else
                call make_empty_fstk( newstk, nptcls )
            endif
        endif
        do i=1,nptcls
            call read_fplane( b%f(ptcl)%arr, fstk, i )
            call shiftrot_fplane( b%f(ptcl)%arr, -oris(i,3), oris(i,4), oris(i,5) )
            if( present(newstk) ) then
                call write_fplane( b%f(ptcl)%arr, newstk, i )    
            else
                call write_fplane( b%f(ptcl)%arr, fstk, i )   
            endif
        end do
    end subroutine shrot_fstk
    
    subroutine lp_fstk( b, lplim, newstk )
        type(build), intent(inout) :: b
        real, intent(in)           :: lplim
        character(len=*), optional :: newstk
        logical :: isthere
        integer :: i
        if( present(newstk) )then
            ! check existence of file
            call file_exists( newstk, isthere )
            if( isthere )then
            else
                call make_empty_fstk( newstk, nptcls )
            endif
        endif
        do i=1,nptcls
            call read_fplane( b%f(ptcl)%arr, fstk, i )
            call lp_fplane( b%f(ptcl)%arr, lplim )
            if( present(newstk) ) then
                call write_fplane( b%f(ptcl)%arr, newstk, i )   
            else
                call write_fplane( b%f(ptcl)%arr, fstk, i )   
            endif
        end do
    end subroutine lp_fstk
    
    subroutine msk_fstk( b, newstk )
        type(build), intent(inout) :: b
        character(len=*), optional :: newstk
        type(imgspi) :: img
        real, pointer :: ip(:,:)
        logical :: isthere
        integer :: i
        img = new_imgspi()
        call get_imgspi_ptr( img, ip ) 
        if( present(newstk) )then
            ! check existence of file
            call file_exists( newstk, isthere )
            if( isthere )then
            else
                call make_empty_fstk( newstk, nptcls )
            endif
        endif
        do i=1,nptcls
            call read_fplane( b%f(ptcl)%arr, fstk, i )
            call simple_2dfft_rev( b%f(ptcl)%arr, box, ip )
            call shift_imgspi( img )
            call mask_imgspi( img, msk )
            call shift_imgspi( img )
            call simple_2dfft( ip, box, b%f(ptcl)%arr )
            if( present(newstk) ) then
                call write_fplane( b%f(ptcl)%arr, newstk, i )   
            else
                call write_fplane( b%f(ptcl)%arr, fstk, i )   
            endif
        end do
    end subroutine msk_fstk
    
    subroutine fstk_mk_stkspi( fstknam, spistknam )
        character(len=*), intent(in) :: fstknam, spistknam
        character(len=256) :: hednam
        complex :: fplane(-xdim:xdim,-xdim:xdim)
        type(stkspi) :: stack
        type(imgspi) :: img
        real, pointer :: ip(:,:)
        integer :: i, file_stat, pos, np, hrecsize
        real :: rval
        ! make .hed file
        hednam = fstknam
        pos = index(hednam, '.fim') ! position of '.fim'
        hednam(pos:pos+3) = '.hed'  ! replacing .fim with .hed
        ! read nr of ptcls from header
        inquire( iolength=hrecsize ) rval
        open(unit=19, file=hednam, status='old', iostat=file_stat,&
        access='direct', action='read', form='unformatted', recl=hrecsize )
        call fopen_err( 'In: fstk_mk_stkspi, module: simple_fstk.f90, open 1', file_stat )
        read(19,rec=1) rval
        np = int(rval)  ! number of transforms                           
        close(19)
        stack = new_stkspi( nimgs=np )
        call write_stk_hed( stack, spistknam )
        img = new_imgspi()
        call get_imgspi_ptr( img, ip )
        ! open the fstack
        open( unit=20, file=fstknam, status='old', iostat=file_stat,&
        access='direct', action='read', form='unformatted', recl=ftsz )
        call fopen_err('In: fstk_mk_stkspi, module: simple_fstk.f90, open 2', file_stat)
        do i=1,np
            ! read Fourier plane
            read( unit=20, rec=i ) fplane
            call simple_2dfft_rev( fplane, box, ip )
            call shift_imgspi( img )
            call write_imgspi( stack, spistknam, i, img )
        end do
        close(20)
        call kill_stkspi( stack )
        call kill_imgspi( img )
    end subroutine fstk_mk_stkspi
    
    subroutine fstk_mk_cavgs_1( b, fstk_out )
        type(build), intent(inout) :: b
        character(len=*), intent(in) :: fstk_out
        integer :: i, file_stat, ncls_here, cnt, pop
        ! zero the Fourier references holding the cavgs
        do i=1,nfrefs
            b%frefs(i)%arr = cmplx(0.,0.)
        end do
        do i=1,nptcls
            write(*,*) 'READ PLANE:', i
            call read_fplane( b%f(ptcl)%arr, fstk, i )
            ! add the ptcl transform
            write(*,*) 'ADDED TO CLASS:', cls(i)
            b%frefs(cls(i))%arr = b%frefs(cls(i))%arr+b%f(ptcl)%arr
        end do
        ! divide with the class counters to get the Fourier averages
        ncls_here = 0
        do i=1,ncls
            pop = cls_pop(cls,i)
            write(*,*) 'CLASS:', i, 'POP:', pop
            b%frefs(i)%arr = b%frefs(i)%arr/real(pop)
            if( pop > minp )then
                ncls_here = ncls_here+1
            endif
        end do
        write(*,*) 'ADJUSTED NR OF CLASSES TO:', ncls_here
        ! output the Fourier class averages
        call make_empty_fstk( fstk_out, ncls_here )
        open( unit=20, file=fstk_out, status='replace', iostat=file_stat,&
        access='direct', action='write', form='unformatted', recl=ftsz )
        call fopen_err( 'In: fstk_mk_cavgs_1, module: simple_fstk.f90', file_stat )
        cnt = 0
        do i=1,ncls
            if( cls_pop(cls,i) > minp )then
                cnt = cnt+1
                write( unit=20, rec=cnt ) b%frefs(i)%arr
                write(*,*) 'WROTE CLASS:', i, 'TO FILE'
            endif
        end do
        close(20)
    end subroutine fstk_mk_cavgs_1
    
    subroutine fstk_mk_cavgs_2( b, gammas, fstk_out )
        type(build), intent(inout) :: b
        real, intent(in) :: gammas(nptcls,ncls)
        character(len=*), intent(in) :: fstk_out
        real :: pops(ncls)
        integer :: i, j, file_stat, ncls_here, cnt
        ! zero the Fourier references holding the cavgs
        do i=1,nfrefs
            b%frefs(i)%arr = cmplx(0.,0.)
        end do
        pops = 0.
        do i=1,nptcls
            call read_fplane( b%f(ptcl)%arr, fstk, i )
            do j=1,ncls            
                ! add the ptcl transform
                b%frefs(j)%arr = b%frefs(j)%arr+gammas(i,j)*b%f(ptcl)%arr
                pops(j) = pops(j)+gammas(i,j)
            end do
        end do
        ! divide with the class counters to get the Fourier averages
        ncls_here = 0
        do i=1,ncls
            b%frefs(i)%arr = b%frefs(i)%arr/pops(i)
            if( pops(i) > minp )then
                ncls_here = ncls_here+1
            endif
        end do
        ! output the Fourier class averages
        call make_empty_fstk( fstk_out, ncls_here )
        open( unit=20, file=fstk_out, status='replace', iostat=file_stat,&
        access='direct', action='write', form='unformatted', recl=ftsz )
        call fopen_err( 'In: fstk_mk_cavgs_2, module: simple_fstk.f90', file_stat )
        cnt = 0
        do i=1,ncls
            if( pops(i) > minp )then
                cnt = cnt+1
                write( unit=20, rec=cnt ) b%frefs(i)%arr
            endif
        end do
        close(20)
    end subroutine fstk_mk_cavgs_2
    
end module simple_fstk