!==Class simple_volspi
!
! simple_volspi handles volumes in Spider format. Functionality includes reading, writing, and Fourier transforming
! individual volume files to to stack. The code is distributed with the hope that it will be useful, but _WITHOUT_
! _ANY_ _WARRANTY_. Redistribution or modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund, 2011-06-05.
!
!==Changes are documented below
!
! Spider definitions
! * Simple volume with: NSAM x NROW x NSLICE voxels. Unformatted direct access file containing a total of LABREC + NROW * NSLICE records. 
! * The volume data is preceeded by a header. There are LABREC records in the header (where LABREC is available in the object as num%labrec)
! * #FROM#                      #TO#                   #CONTENT#
! * 1                           num%labrec             : volume header
! * num%labrec+1                num%labrec+nrow        : slice no. 1
! * num%labrec+nrow+1           num%labrec+2*nrow      : slice no. 2
! * ...                         ...   
! * num%labrec+nrow*(nslice-1)  num%labrec+nslice*nrow : slice no. nslice
!
!==Changes are documented below
! 
module simple_volspi
use simple_math
use simple_jiffys
use simple_params
use simple_stat
implicit none

type volspi
    private
    real, pointer :: rmat(:,:,:)=>null()
    real, allocatable :: row(:), hed(:,:)
    integer, allocatable :: indextab(:,:)
    integer :: recsz=0, hedsz=0, bx
    integer :: lenbyt=0, labrec=0, labbyt=0
    logical :: exists=.false.
end type volspi

contains

    function new_volspi( rmat, inbox ) result( num )
    ! is a constructor
        real, intent(in), dimension(inbox,inbox,inbox), target :: rmat
        integer, intent(in) :: inbox
        type(volspi) :: num
        integer :: alloc_stat, cnt, i, j
        ! target input
        num%bx = inbox
        num%rmat => rmat
        ! from spider:
        num%lenbyt = num%bx*4
        num%labrec = 1024/num%lenbyt
        if( mod(1024,num%lenbyt) /= 0 ) num%labrec = num%labrec+1
        num%labbyt = num%labrec*num%lenbyt
        ! allocate:
        allocate( num%row(num%bx), num%indextab(num%bx,2),&
        num%hed(num%labrec,num%bx), stat=alloc_stat )
        call alloc_err('In: new_volspi, module: simple_volspi.f90', alloc_stat)
        ! make a header
        num%hed = 0.
        num%hed(1,1) = real(num%bx)
        num%hed(1,2) = real(num%bx)
        num%hed(1,3) = real(num%bx+num%labrec)
        num%hed(1,5) = 3.
        num%hed(1,6) = 0.
        num%hed(1,12) = real(num%bx)
        num%hed(1,13) = real(num%labrec)
        num%hed(1,22) = real(num%labbyt)
        num%hed(1,23) = real(num%lenbyt)
        ! make index array for extracting the slices of the volume
        cnt = num%labrec
        do j=1,num%bx
            num%indextab(j,1) = cnt+1 ! from
            do i=1,num%bx
                cnt = cnt+1
            end do
            num%indextab(j,2) = cnt   ! to
        end do
        ! calc record size (one record = one row of pixels)
        inquire( iolength=num%recsz ) num%row
        num%exists = .true.
    end function new_volspi
    
    subroutine kill_volspi( num )
    ! is a destructor
        type(volspi), intent(inout) :: num  
        if( num%exists )then
            deallocate( num%row, num%indextab, num%hed )
            num%rmat=>null()
            num%exists = .false.
        endif
    end subroutine kill_volspi
    
    subroutine mask_volspi( num, mskrad )
        type(volspi)     :: num
        real, intent(in) :: mskrad
        integer          :: i, j, k
        real             :: ci, cj, ck, fwght
        ci = -real(num%bx/2)+0.5
        do i=1,num%bx
            cj = -real(num%bx/2)+0.5
            do j=1,num%bx
                ck = -real(num%bx/2)+0.5
                do k=1,num%bx
                    fwght = cosedge(ci,cj,ck,mskrad, 0.1*real(num%bx))
                    num%rmat(i,j,k) = num%rmat(i,j,k)*fwght
                    ck = ck+1.
                end do
                cj = cj+1.
            end do
            ci = ci+1.
        end do
    end subroutine mask_volspi
    
    subroutine norm_volspi( num )
        type(volspi) :: num
        logical      :: err
        call normalize( num%rmat, err )
        if( err )then
            write(*,*) 'Normalization error, volume variance is zero!'
            write(*,*) 'In: norm_volspi, module: simple_volspi'
            stop
        endif
    end subroutine norm_volspi
        
    subroutine bin_volspi( num, npix )
    ! is for binarizing a volume using nr of pixels treshold
        type(volspi), intent(inout) :: num
        integer, intent(in)         :: npix
        real, allocatable           :: forsort(:)
        real                        :: tres
        integer                     :: cnt, i, j, k, alloc_stat
        allocate( forsort(num%bx**3), stat=alloc_stat )
        call alloc_err('In: bin_volspi_2', alloc_stat)
        ! fill up the array for sorting
        cnt = 0
        do i=1,num%bx
            do j=1,num%bx
                do k=1,num%bx
                    cnt = cnt+1
                    forsort(cnt) = num%rmat(i,j,k)
                end do
            end do
        end do
        ! sort
        call hpsort(num%bx**3, forsort)
        cnt = 0
        do i=1,num%bx
            do j=1,num%bx
                do k=1,num%bx
                    cnt = cnt+1
                end do
            end do
        end do
        tres = forsort(num%bx**3-npix-1) ! everyting above this value 1 else 0
        ! binarize
        do i=1,num%bx
            do j=1,num%bx
                do k=1,num%bx
                    if( num%rmat(i,j,k) >= tres )then
                        num%rmat(i,j,k) = 1.
                    else
                        num%rmat(i,j,k) = 0.
                    endif
                end do
            end do
        end do
        deallocate( forsort ) 
    end subroutine bin_volspi

    subroutine find_volconv( num, volnam, volconv )
        type(volspi), intent(inout)   :: num
        integer, parameter            :: filnum=50
        character(len=*), intent(in)  :: volnam
        character(len=*), intent(out) :: volconv
        integer                       :: i, ier
        ! initialize conversion directive
        volconv = ''
        open(unit=filnum, convert='LITTLE_ENDIAN', status='old', action='read', file=volnam,&
        access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        ! read header
        do i=1,num%labrec
            read(filnum, rec=i) num%hed(i,:)
        end do
        close(filnum)
        if( int(num%hed(1,1)) == num%bx .and. int(num%hed(1,5)) == 3 ) volconv = 'LITTLE_ENDIAN' 
        open(unit=filnum, convert='BIG_ENDIAN', status='old', action='read',&
        file=volnam, access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        ! read header
        do i=1,num%labrec
            read(filnum, rec=i) num%hed(i,:)
        end do
        close(filnum)
        if( int(num%hed(1,1)) == num%bx .and. int(num%hed(1,5)) == 3 ) volconv = 'BIG_ENDIAN'
        if( volconv == '' )then
            write(*,*) 'ERROR, could not determine endianess of file!'
            write(*,*) 'File corrupt or box parameter incorrect?'
            stop    
        endif
   end subroutine find_volconv
    
    subroutine read_volspi( num, volnam )
    ! is for reading the volume
        type(volspi), intent(inout)  :: num
        character(len=*), intent(in) :: volnam
        integer, parameter           :: filnum=50
        integer                      :: i, j, k, ier, cnt
        character(len=256)           :: volconv
        ! find file-conversion (LITTLE or BIG endian)
        call find_volconv( num, volnam, volconv )
        open(unit=filnum, convert=volconv, status='old', action='read', file=volnam,&
        access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        call fopen_err('In: read_volspi, module: simple_volspi.f90', ier)
        ! read header
        do i=1,num%labrec
            read(filnum, rec=i) num%hed(i,:)
        end do
        ! read volume
        do i=1,num%bx
            cnt = 0
            do j=num%indextab(i,1),num%indextab(i,2)
                cnt = cnt+1
                read(filnum, rec=j) num%row
                do k=1,num%bx
                    num%rmat(i,k,cnt) = num%row(k)
                end do
            end do
        end do
        close(unit=filnum)
    end subroutine read_volspi

    subroutine masscen_volspi( num, xvar, yvar, zvar )
    ! determines the center of mass of a binary volume
        type(volspi), intent(in) :: num
        real, intent(out) :: xvar, yvar, zvar
        integer :: i, j, k, ix, jx, kx
        real :: spix, pix
        spix = 0.
        xvar = 0.
        yvar = 0.
        zvar = 0.
        do i=-num%bx/2,num%bx
            ix = min(i+num%bx/2+1,num%bx)
            do j=-num%bx/2,num%bx
                jx = min(j+num%bx/2+1,num%bx)
                do k=-num%bx/2,num%bx
                    kx = min(k+num%bx/2+1,num%bx)
                    pix = num%rmat(ix,jx,kx)
                    xvar = xvar+pix*real(i)
                    yvar = yvar+pix*real(j)
                    zvar = zvar+pix*real(k)
                    spix = spix+pix
                end do
            end do
        end do
        xvar = xvar/spix
        yvar = yvar/spix
        zvar = zvar/spix
    end subroutine masscen_volspi
    
    subroutine shift_volspi( num )
        type(volspi), intent(inout) :: num
        integer :: i, j, k
        real :: rswap       
        do i=0,num%bx/2-1        
            do j=0,num%bx/2-1 
                do k=0,num%bx/2-1
                    rswap = num%rmat(num%bx/2+1+i,1+j,num%bx/2+1+k)
                    num%rmat(num%bx/2+1+i,1+j,num%bx/2+1+k) = num%rmat(1+i,num%bx/2+1+j,1+k)
                    num%rmat(1+i,num%bx/2+1+j,1+k) = rswap                 
                    rswap = num%rmat(1+i,1+j,1+k)
                    num%rmat(1+i,1+j,1+k) = num%rmat(num%bx/2+1+i,num%bx/2+1+j,num%bx/2+1+k)
                    num%rmat(num%bx/2+1+i,num%bx/2+1+j,num%bx/2+1+k) = rswap
                    rswap = num%rmat(1+i,num%bx/2+1+j,num%bx/2+1+k)
                    num%rmat(1+i,num%bx/2+1+j,num%bx/2+1+k) = num%rmat(num%bx/2+1+i,1+j,1+k)
                    num%rmat(num%bx/2+1+i,1+j,1+k) = rswap                 
                    rswap = num%rmat(1+i,1+j,num%bx/2+1+k)
                    num%rmat(1+i,1+j,num%bx/2+1+k) = num%rmat(num%bx/2+1+i,num%bx/2+1+j,1+k)
                    num%rmat(num%bx/2+1+i,num%bx/2+1+j,1+k) = rswap
                end do
            end do
        end do
!        tmp(:num%bx/2,num%bx/2+1:,:num%bx/2) = num%rmat(num%bx/2+1:,:num%bx/2,num%bx/2+1:)
!        tmp(num%bx/2+1:,:num%bx/2,num%bx/2+1:) = num%rmat(:num%bx/2,num%bx/2+1:,:num%bx/2)
!        tmp(:num%bx/2,:num%bx/2,:num%bx/2) = num%rmat(num%bx/2+1:,num%bx/2+1:,num%bx/2+1:)
!        tmp(num%bx/2+1:,num%bx/2+1:,num%bx/2+1:) = num%rmat(:num%bx/2,:num%bx/2,:num%bx/2)
!        tmp(num%bx/2+1:,:num%bx/2,:num%bx/2) = num%rmat(:num%bx/2,num%bx/2+1:,num%bx/2+1:)
!        tmp(:num%bx/2,num%bx/2+1:,num%bx/2+1:) = num%rmat(num%bx/2+1:,:num%bx/2,:num%bx/2)
!        tmp(num%bx/2+1:,num%bx/2+1:,:num%bx/2) = num%rmat(:num%bx/2,:num%bx/2,num%bx/2+1:)
!        tmp(:num%bx/2,:num%bx/2,num%bx/2+1:) = num%rmat(num%bx/2+1:,num%bx/2+1:,:num%bx/2)
    end subroutine shift_volspi

    subroutine get_volspi_ptr( num, ptr )
    ! returns a pointer to the volume data
        type(volspi), intent(inout), target :: num
        real, pointer, intent(out) :: ptr(:,:,:)
        ptr => num%rmat
    end subroutine get_volspi_ptr
    
    subroutine set_volspi_ptr( num, rvol )
    ! returns a pointer to the volume data
        type(volspi), intent(inout) :: num
        real, intent(in), target :: rvol(num%bx,num%bx,num%bx)
        num%rmat => rvol
    end subroutine set_volspi_ptr
    
    function get_voxel( num, i, j, k ) result( vox )
        type(volspi), intent(in) :: num
        integer, intent(in)      :: i, j, k
        real :: vox
        vox = num%rmat(i,j,k)
    end function get_voxel
           
    subroutine write_volspi( num, volnam )
    ! is for writing the volume
        type(volspi), intent(inout) :: num
        character(len=*) :: volnam
        integer, parameter :: filnum=51
        integer :: i, j, k, ier, cnt
        ! open file
        open(unit=filnum, convert='LITTLE_ENDIAN', status='replace', action='write',&
        file=volnam, access = 'direct', form = 'unformatted', recl=num%recsz, iostat=ier)
        call fopen_err('In: write_volspi, module: simple_volspi.f90', ier)
        ! write header
        do i=1,num%labrec
            write(filnum, rec=i) num%hed(i,:)
        end do
        ! write volume
        do i=1,num%bx
            cnt = 0
            do j=num%indextab(i,1),num%indextab(i,2)
                cnt = cnt+1
                do k=1,num%bx
                    num%row(k) = num%rmat(i,k,cnt)
                end do
                write(filnum, rec=j) num%row
            end do
        end do
        close(unit=filnum)
    end subroutine write_volspi

end module simple_volspi