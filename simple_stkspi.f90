!==Class simple_stkspi
!
! simple_stkspi handles spider stacks. Functionality includes reading, writing individual image files to to stack.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution
! or modification is regulated by the GNU General Public License. *Author:* Hans Elmlund, 2011-09-03.
! 
! Spider definitions
! * The first pixel in an image represents the upper left corner of the image
! * Each unformatted direct access record contains NSAM 4-byte words which are stored as floating point numbers, where NSAM is the number of pixels per row
! * The image data is preceeded by a header. There are LABREC records in the header (where LABREC is available in the object as num%labrec)
! * #FROM#                #TO#                  #CONTENT#
! * 1                     num%labrec            : overall stack header
! * num%labrec+1          2*num%labrec          : first stacked image header
! * 2*num%labrec+1        2*num%labrec+num%bx    : first image
! * 2*num%labrec+num%bx+1  3*num%labrec+num%bx   : second image header
! * 3*num%labrec+num%bx+1  3*num%labrec+2*num%bx : second image
!
!==Changes are documented below
!
!* deugged and incorporated in the _SIMPLE_ library, HE 2011-08-16
!

module simple_stkspi
use simple_jiffys
use simple_params
use simple_imgspi
implicit none
save 

private :: nr_to_stk_inds
public

type stkspi
    private
    real, allocatable  :: stk_hed(:,:)
    integer            :: recsz=0
    integer            :: lenbyt=0,  labrec=0, labbyt=0, bx, nimgs=0
    logical            :: exists=.false.
end type stkspi

contains

    function new_stkspi( box_in, nimgs, name ) result( num )
    ! stack constructor
        type(stkspi)                           :: num
        integer, intent(in), optional          :: box_in, nimgs
        character(len=*), intent(in), optional :: name
        integer                                :: i, ier
        integer, parameter                     :: filnum=60
        character(len=256)                     :: stkconv
        ! set const
        if( present(box_in) ) then
            num%bx = box_in
        else
            num%bx = box
        endif
        if( present(nimgs) ) then
            num%nimgs = nimgs
        else
            num%nimgs = nptcls
        endif
        ! from spider:
        num%lenbyt = num%bx*4
        num%labrec = 1024/num%lenbyt
        if( mod(1024,num%lenbyt) /= 0 ) num%labrec = num%labrec+1
        num%labbyt = num%labrec*num%lenbyt
        ! alloc:
        allocate( num%stk_hed(num%labrec,num%bx), stat=ier )
        call alloc_err('In: new_stkspi, module: simple_stkspi', ier)
        ! calc record size (one record = one row of pixels)
        inquire( iolength=num%recsz ) num%stk_hed(1,:)
        if( present(name) )then
            call find_stkconv( num, name, stkconv )
            open(unit=filnum, convert=stkconv, status='unknown', action='read',&
            file=name, access='direct', form='unformatted', recl=num%recsz, iostat=ier)
            call fopen_err('In: mk_new_stk, module: simple_stkspi', ier)
            ! read header values
            do i=1,num%labrec
                read(filnum, rec=i) num%stk_hed(i,:)
            end do
            close(filnum)
        else
            ! set header values
            num%stk_hed = 0.
            num%stk_hed(1,1)  = 1.
            num%stk_hed(1,2)  = real(num%bx)
            num%stk_hed(1,3)  = real(num%bx+num%labrec)
            num%stk_hed(1,5)  = 1.
            num%stk_hed(1,6)  = 0.
            num%stk_hed(1,10) = -1.
            num%stk_hed(1,12) = real(num%bx)
            num%stk_hed(1,13) = real(num%labrec)
            num%stk_hed(1,21) = 1.
            num%stk_hed(1,22) = real(num%labbyt)
            num%stk_hed(1,23) = real(num%lenbyt)
            num%stk_hed(1,24) = 2.              ! for stack
            num%stk_hed(1,25) = -1.
            num%stk_hed(1,26) = real(num%nimgs) ! maximum nr of images
        endif
    end function new_stkspi

    subroutine find_stkconv( num, fname, stkconv )
        type(stkspi), intent(inout)   :: num
        character(len=*), intent(in)  :: fname
        character(len=*), intent(out) :: stkconv
        integer, parameter            :: filnum=60
        integer                       :: i, ier
        ! initialize conversion directive
        stkconv = ''
        open(unit=filnum, convert='LITTLE_ENDIAN', status='old', action='read', file=fname,&
        access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        call fopen_err('In: find_stkconv, module: simple_stkspi', ier)
        ! read header
        do i=1,num%labrec
            read(filnum, rec=i) num%stk_hed(i,:)
        end do
        close(filnum)
        if( int(num%stk_hed(1,2)) == num%bx .and. int(num%stk_hed(1,5)) == 1 ) stkconv = 'LITTLE_ENDIAN' 
        open(unit=filnum, convert='BIG_ENDIAN', status='old', action='read',&
        file=fname, access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        ! read header
        do i=1,num%labrec
            read(filnum, rec=i) num%stk_hed(i,:)
        end do
        close(filnum)
        if( int(num%stk_hed(1,2)) == num%bx .and. int(num%stk_hed(1,5)) == 1 ) stkconv = 'BIG_ENDIAN'
        if( stkconv == '' )then
            write(*,*) 'ERROR, could not determine endianess of file!'
            write(*,*) 'In: find_stkconv, module: simple_stkspi'
            write(*,*) 'File corrupt or box parameter incorrect?'
            stop
        endif
    end subroutine find_stkconv

    subroutine kill_stkspi( num )
        type(stkspi), intent(inout) :: num
        deallocate( num%stk_hed )
        num%exists = .false.
    end subroutine kill_stkspi
    
    subroutine nr_to_stk_inds( num, nr, hedinds, iminds )
        type(stkspi), intent(in) :: num 
        integer, intent(in)      :: nr
        integer, intent(out)     :: hedinds(2), iminds(2)
        integer                  :: cnt, j
        cnt = num%labrec
        do j=1,nr
            hedinds(1) = cnt+1   ! hed from
            cnt = cnt+num%labrec 
            hedinds(2) = cnt     ! hed to
            iminds(1) = cnt+1    ! im from
            cnt = cnt+num%bx
            iminds(2) = cnt      ! im to
        end do
    end subroutine nr_to_stk_inds

    subroutine read_imgspi( num, name, i, img, conv )
    ! is for reading a single image from a spider stack
        type(stkspi), intent(inout)  :: num
        character(len=*), intent(in) :: name
        integer, intent(in)          :: i
        type(imgspi)                 :: img
        character(len=*)             :: conv
        real, pointer                :: img_hed(:,:)=>null(), rmat(:,:)=>null()
        integer, parameter           :: filnum=52
        integer                      :: ier, hedinds(2), iminds(2), j, k, cnt
        real                         :: row(num%bx)
        open(unit=filnum, convert=conv, status='unknown', action='read',&
        file=name, access='direct', form='unformatted', recl=num%recsz, iostat=ier)
        call fopen_err('In: read_imgspi, module: simple_stkspi.f90', ier)
        call nr_to_stk_inds( num, i, hedinds, iminds )
        ! set pointers to image
        call get_imgspi_ptr_hed( img, img_hed )
        call get_imgspi_ptr( img, rmat )
        ! read header data
        cnt = 0
        do j=hedinds(1),hedinds(2)
            cnt = cnt+1
            read(filnum, rec=j) img_hed(cnt,:)
            do k=1,num%bx
                rmat(k,cnt) = row(k)
            end do
        end do
        ! read image data
        cnt = 0
        do j=iminds(1),iminds(2)
            cnt = cnt+1
            read(filnum, rec=j) row
            do k=1,num%bx
                rmat(k,cnt) = row(k)
            end do
        end do
        close(unit=filnum)
    end subroutine read_imgspi
    
    subroutine write_stk_hed( num, name )
    ! is for writing the stack header
        type(stkspi), intent(inout) :: num
        character(len=*)            :: name
        integer, parameter          :: filnum=53
        integer                     :: ier, j, cnt
        open(unit=filnum, status='replace', action='write', file=name,&
        access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        call fopen_err('In: write_stk_hed, module: simple_stkspi.f90', ier)
        cnt = 0
        do j=1,num%labrec
            cnt = cnt+1
            write(filnum, rec=j) num%stk_hed(cnt,:)
        end do
        close(unit=filnum)
    end subroutine write_stk_hed
    
    subroutine write_imgspi( num, name, i, img )
    ! is for writing an image to stack
        type(stkspi), intent(inout) :: num
        character(len=*)            :: name
        integer, intent(in)         :: i
        type(imgspi)                :: img
        real, pointer               :: img_hed(:,:)=>null(), rmat(:,:)=>null()
        integer, parameter          :: filnum=54
        integer                     :: ier, hedinds(2), iminds(2), j, k, cnt
        real                        :: row(num%bx), image(num%bx,num%bx)
        open(unit=filnum, status='unknown', action='write', file=name,&
        access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        call fopen_err('In: write_imgspi, module: simple_stkspi.f90', ier)
        ! get image indices in stk file
        call nr_to_stk_inds( num, i, hedinds, iminds )
         ! set pointers to image
        call get_imgspi_ptr_hed( img, img_hed )
        call get_imgspi_ptr( img, rmat )
        ! write image header
        cnt = 0
        do j=hedinds(1),hedinds(2)
            cnt = cnt+1
            write(filnum, rec=j) img_hed(cnt,:)
        end do
        ! convert
        do k=1,num%bx
            row = rmat(k,:)
            do j=1,num%bx
                image(j,k) = row(j)
            end do
        end do
        ! write image
        cnt = 0
        do j=iminds(1),iminds(2)
            cnt = cnt+1
            write(filnum, rec=j) image(cnt,:)
        end do
        close(unit=filnum)
    end subroutine write_imgspi
    
end module simple_stkspi