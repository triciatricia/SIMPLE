!==Class simple_imgspi
!
! simple_imgspi handles 2D images in Spider format. Functionality includes reading, writing
! individual image files to to stack and interpolation of pixel values at arbitrary grid positions.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution
! or modification is regulated by the GNU General Public License. *Author:* Hans Elmlund, 2011-06-05.
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

module simple_imgspi
use simple_math
use gnufor2
use simple_jiffys
use simple_stat
use simple_params
use simple_dens_map
implicit none
save

interface bin_imgspi
    module procedure bin_imgspi_1
    module procedure bin_imgspi_2
end interface

type imgspi
    private
    real, allocatable :: rmat(:,:), img_hed(:,:)
    integer           :: lenbyt=0,  labrec=0, labbyt=0, bx
    logical           :: exists=.false.
end type imgspi

contains

    function new_imgspi( inbox ) result( num )
    ! is a constructor
        type(imgspi) :: num
        integer, intent(in), optional :: inbox
        integer :: alloc_stat
        ! set box size
        num%bx = box
        if( present(inbox) ) num%bx = inbox
        ! from spider:
        num%lenbyt = num%bx*4
        num%labrec = 1024/num%lenbyt
        if( mod(1024,num%lenbyt) /= 0 ) num%labrec = num%labrec+1
        num%labbyt = num%labrec*num%lenbyt
        ! allocate:
        allocate( num%rmat(num%bx,num%bx), num%img_hed(num%labrec,num%bx), stat=alloc_stat )
        call alloc_err('In: new_imgspi, module: simple_imgspi.f90', alloc_stat)
        num%rmat = 0.
        num%img_hed = 0.
        num%img_hed(1,1) = 1.
        num%img_hed(1,2) = real(num%bx)
        num%img_hed(1,3) = real(num%bx+num%labrec)
        num%img_hed(1,5) = 1.
        num%img_hed(1,6) = 0. !!
        num%img_hed(1,12) = real(num%bx)
        num%img_hed(1,13) = real(num%labrec)
        num%img_hed(1,22) = real(num%labbyt)
        num%img_hed(1,23) = real(num%lenbyt)
        num%img_hed(1,24) = 0.
        num%exists = .true.
    end function new_imgspi
    
    function clone_imgspi( num_in ) result( num_out )
        ! is a constructor
        type(imgspi) :: num_in, num_out
        integer :: alloc_stat
        ! set box size
        num_out%bx = num_in%bx
        ! from spider
        num_out%lenbyt = num_in%lenbyt
        num_out%labrec = num_in%labrec
        num_out%labbyt = num_in%labbyt
        ! allocate:
        allocate( num_out%rmat(num_in%bx,num_in%bx),&
        num_out%img_hed(num_in%labrec,num_in%bx), stat=alloc_stat )
        call alloc_err('In: clone_imgspi, module: simple_imgspi.f90', alloc_stat)
        num_out%rmat = num_in%rmat
        num_out%img_hed = num_in%img_hed
        num_out%exists = .true.
    end function clone_imgspi
    
    subroutine kill_imgspi( num )
    ! is a destructor
        type(imgspi), intent(inout) :: num  
        if( num%exists )then
            deallocate( num%rmat, num%img_hed )
            num%exists = .false.
        endif
    end subroutine kill_imgspi
    
    subroutine get_imgspi( num, image )
    ! is for getting a spider image
        type(imgspi), intent(in) :: num
        real, intent(out) :: image(num%bx,num%bx)
        image = num%rmat(:,:)
    end subroutine get_imgspi
    
    subroutine set_imgspi( num, image )
    ! is for setting a spider image
        type(imgspi), intent(inout) :: num
        real, intent(in) :: image(num%bx,num%bx)
        num%rmat(:,:) = image
    end subroutine set_imgspi
    
    subroutine shift_imgspi( num )
    ! is for shifting an image before FFT
        type(imgspi), intent(inout) :: num
        real                        :: tmp(num%bx,num%bx)
        tmp = 0.
        ! quadr(1)(:num%bx/2,num%bx/2+1:)
        ! quadr(3)(num%bx/2+1:,:num%bx/2)
        ! quadr(4)(:num%bx/2,:num%bx/2)
        ! quadr(2)(num%bx/2+1:,num%bx/2+1:)
        ! quadr(3) <- quadr(1)
        tmp(num%bx/2+1:,:num%bx/2) = num%rmat(:num%bx/2,num%bx/2+1:)
        ! quadr(1) <- quadr(3)
        tmp(:num%bx/2,num%bx/2+1:) = num%rmat(num%bx/2+1:,:num%bx/2)
        ! quadr(4) <- quadr(2)
        tmp(:num%bx/2,:num%bx/2) = num%rmat(num%bx/2+1:,num%bx/2+1:)
        ! quadr(2) <- quadr(4)
        tmp(num%bx/2+1:,num%bx/2+1:) = num%rmat(:num%bx/2,:num%bx/2)
        num%rmat(:,:) = tmp
    end subroutine shift_imgspi
    
    subroutine mirror_imgspi( num, md )
    ! is for mirroring an image
        type(imgspi), intent(inout)  :: num
        character(len=*), intent(in) :: md
        integer :: i
        if( md == 'col' )then
            do i=1,num%bx
                call reverse_rarr(num%rmat(:,i))
            end do
        else if( md == 'row' )then
            do i=1,num%bx
                call reverse_rarr(num%rmat(i,:))
            end do
        else
            write(*,*) 'Mode needs to be either col or row'
            write(*,*) 'In: mirror imgspi, module: simple_imgspi'
            stop
        endif
    end subroutine mirror_imgspi
    
    function get_npcapix( num, mskrad ) result( cnt )
        type(imgspi)     :: num
        real, intent(in) :: mskrad
        real             :: ci, cj
        integer          :: cnt, i, j
        cnt = 0
        ci = -real(num%bx)/2.
        do i=1,num%bx
            cj = -real(num%bx)/2.
            do j=1,num%bx
                if( hardedge(ci,cj,mskrad) == 1. )then
                    cnt = cnt+1
                endif
                cj = cj+1.
            end do
            ci = ci+1.
        end do
    end function get_npcapix
    
    subroutine extract_pcavec( num, mskrad, pcavec )
        type(imgspi)        :: num
        real, intent(in)    :: mskrad
        real, intent(inout) :: pcavec(:)
        integer :: i, j, cnt
        real    :: ci, cj
        cnt = 0
        ci = -real(num%bx)/2.
        do i=1,num%bx
            cj = -real(num%bx)/2.
            do j=1,num%bx
                if( hardedge(ci,cj,mskrad) == 1. )then
                    cnt = cnt+1
                    pcavec(cnt) = num%rmat(i,j)
                endif
                cj = cj+1.
            end do
            ci = ci+1.
        end do
    end subroutine extract_pcavec
    
    subroutine mask_imgspi( num, mskrad )
        type(imgspi) :: num
        real, intent(in) :: mskrad
        integer :: i, j
        real :: ci, cj
        ci = -real(num%bx)/2.
        do i=1,num%bx
            cj = -real(num%bx)/2.
            do j=1,num%bx
                num%rmat(i,j) = num%rmat(i,j)*cosedge(ci,cj, mskrad, 0.2*real(num%bx) )
                cj = cj+1.
            end do
            ci = ci+1.
        end do
    end subroutine mask_imgspi

    subroutine norm_imgspi( num )
        type(imgspi) :: num
        integer      :: i, j
        logical      :: err
        call normalize( num%rmat, err )
        if( err )then
            do i=1,num%bx
                do j=1,num%bx
                    num%rmat(i,j) = ran3()
                end do
            end do
            call normalize( num%rmat, err )
        endif
    end subroutine norm_imgspi
    
    subroutine get_imgspi_ptr( num, ptr )
    ! returns a pointer to the volume data
        type(imgspi), intent(inout), target :: num
        real, pointer, intent(out)          :: ptr(:,:)
        ptr => num%rmat
    end subroutine get_imgspi_ptr
    
    subroutine get_imgspi_ptr_hed( num, ptr )
    ! returns a pointer to the volume data
        type(imgspi), intent(inout), target :: num
        real, pointer, intent(out)          :: ptr(:,:)
        ptr => num%img_hed
    end subroutine get_imgspi_ptr_hed
    
    subroutine imgspi_gau( num )
        type(imgspi), intent(inout) :: num
        real :: x, y, wsz, xw
        integer :: i, j
        wsz = real(num%bx)/2.
        x = -wsz
        do i=1,num%bx
            xw = gauwfun(x, int(wsz), 0.5)
            y = -wsz
            do j=1,num%bx
                num%rmat(i,j) = xw*gauwfun(y, int(wsz), 0.5)
                write(*,*) i, j, num%rmat(i,j)
                y = y+1.
            end do
            x = x+1.
        end do
    end subroutine imgspi_gau
    
    subroutine masscen_imgspi( num, xvar, yvar )
    ! determines the center of mass of the positive pixels in the image
        type(imgspi), intent(in) :: num
        real, intent(out) :: xvar, yvar
        integer :: i, j, ix, jx
        real :: spix, pix
        spix = 0.
        xvar = 0.
        yvar = 0.
        !$omp parallel do default(shared) private(i,j,ix,jx,pix) schedule(static) reduction(+:xvar,yvar,spix)
        do i=-num%bx/2,num%bx
            ix = min(i+num%bx/2+1,num%bx)
            do j=-num%bx/2,num%bx
                jx = min(j+num%bx/2+1,num%bx)
                pix = max(0.,num%rmat(ix,jx))
                xvar = xvar+pix*real(i)
                yvar = yvar+pix*real(j)
                spix = spix+pix
            end do
        end do
        !$omp end parallel do 
        xvar = xvar/spix
        yvar = yvar/spix
    end subroutine masscen_imgspi
    
    subroutine bin_imgspi_1( num )
    ! is for binarizing an image with k-means
        type(imgspi), intent(inout) :: num
        real :: binimg(num%bx,num%bx)
        real :: cen0, cen1, dist0, dist1, sum0, sum1, sumdist
        integer :: j, k, cnt0, cnt1, l
        ! One pass to get initial centers
        do j=1,num%bx
            do k=1,num%bx
                if(num%rmat(j,k) > cen1) cen1 = num%rmat(j,k)
                if(num%rmat(j,k) < cen0) cen0 = num%rmat(j,k)
            end do
        end do
        do l=1,num%bx
            sum1 = 0.
            sum0 = 0.
            cnt0 = 0
            cnt1 = 0
            sumdist= 0.
            do j=1,num%bx
                do k=1,num%bx
                    dist1 = sqrt((num%rmat(j,k)-cen1)**2)**2
                    dist0 = sqrt((num%rmat(j,k)-cen0)**2)**2
                    if( dist1 <= dist0 )then
                        sum1 = sum1+num%rmat(j,k)
                        cnt1 = cnt1+1
                        sumdist = sumdist+dist1
                        binimg(j,k) = 1.
                    else
                        sum0 = sum0+num%rmat(j,k)
                        cnt0 = cnt0+1
                        sumdist = sumdist+dist0
                        binimg(j,k) = 0.
                    endif
                end do
            end do
            cen1 = sum1/real(cnt1)
            cen0 = sum0/real(cnt0)
        end do
        num%rmat(:,:) = binimg
    end subroutine bin_imgspi_1
    
    subroutine bin_imgspi_2( num, tres, msk )
    ! is for binarizing an image with k-means and changing pixels beyond a radius of msk from the center to the background value (0)
        type(imgspi), intent(inout) :: num
        real, intent(in) :: tres, msk
        real :: binimg(num%bx,num%bx), maxv, minv, dist_to_center
        integer :: j, k
        call norm_imgspi( num )
        maxv = maxval(num%rmat)
        minv = minval(num%rmat)
!        write(*,*) maxv, minv
        do j=1,num%bx
            do k=1,num%bx
                if( num%rmat(j,k) > tres )then
                    binimg(j,k) = 1.
                else
                    binimg(j,k) = 0.
                endif
            end do
        end do
        do j=1,num%bx
            do k=1,num%bx
              dist_to_center = sqrt((real(j)-num%bx/2)**2+(real(k)-num%bx/2)**2)
                  if ( dist_to_center > msk )then
                      binimg(j,k) = 0.
                  endif
            end do
        end do
        num%rmat(:,:) = binimg
    end subroutine bin_imgspi_2
    
    subroutine plot_imgspi( num )
    ! is for plotting an image
        type(imgspi), intent(in) :: num
        call image(num%rmat(:,:), palette='gray')
    end subroutine plot_imgspi
    
    subroutine identify_densities_imgspi( num, box, max_densities, min_density_size, img_dens_map )
    ! is for identifying the centers and "masses" (in pixels) of densities in a binary image (num) of size box. max_densities is the maximum number of densities to identify. min_density_size is the minimum size of a density in pixels. identify_densities_imgspi stores the positions of the density centers and their "masses" in img_dens_map (see dens_map_mod for more information about the dens_map class). 
        type(imgspi), intent(in)      :: num
        integer, intent(in)           :: box, max_densities, min_density_size
        integer                       :: j, k, label_count, i, n, alloc_stat
        integer                       :: img_labels(box,box,2)
        integer, allocatable          :: mass_order(:)
        real, allocatable             :: centers(:,:)
        type(imgspi)                  :: temp_imgspi
        type(dens_map), intent(inout) :: img_dens_map
        
        call label_connected_pixels(num, img_labels, label_count)
        ! Count # of pixels with each label (integer) and find the center coordinates: 
        ! centers(i,1) = number of pixels with label i; (i,2:3) = x and y coordinates for each density center with label i.
        allocate(centers(label_count,3), stat=alloc_stat)  
        call alloc_err('In: identify_densities, module: simple_imgspi.f90', alloc_stat)
        centers = centers_of_mass(label_count, img_labels, box)
        
        ! Get rid of densities smaller than a specified # of pixels (min_density_size). (~4-6 seems like a good number for current data set.)
        do i=1,label_count
            if (centers(i,1) < min_density_size) then
!                write(*,*) 'mass less than min_density_size for label', i
                do j=1,box
                    do k=1,box
                        if (img_labels(j,k,2) == i) img_labels(j,k,2) = 0
                    end do
                end do
                call remove_row_array_2d(centers, i)
                label_count = label_count - 1
            end if
        end do

        ! Correct for the issue when two densities are so close together that they are connected. If fewer than max_densities were found, try shrinking each density, starting with the largest. If shrinking results in more centers, use them.  
        if (label_count < max_densities) then
            allocate(mass_order(label_count), stat=alloc_stat)
            call alloc_err('In: identify_densities, module: simple_imgspi.f90', alloc_stat)
            mass_order = order_array(centers(:,1),size(centers(:,1)))
            do i=1,size(centers,1)
                if (label_count >= max_densities) exit
                temp_imgspi = new_imgspi(box)
                call imgspi_from_img_labels(img_labels, temp_imgspi, mass_order(i), box)
                call split_density(temp_imgspi, centers, label_count, box, mass_order(i))
            end do
            deallocate(mass_order)
        end if
            
        ! If more than max_densities were found, get rid of the density labels with the fewest pixels
        do
            if (label_count <= max_densities) exit
            n = minval(centers(:,1))
            do i=1,label_count
                if (nint(centers(i,1)) == n) then
!                   write(*,*) i, 'mass=', centers(i,1), 'removed'
                    call remove_row_array_2d(centers, i)
                    do j=1,box
                        do k=1,box
                            if (img_labels(j,k,2) == i) img_labels(j,k,2) = 0
                        end do
                    end do
                    label_count = label_count - 1
                    exit
                end if
            end do
        end do
        
        ! Store info in img_dens_map. 
        img_dens_map = new_dens_map()
        call set_dens_map(img_dens_map, nint(centers(:,1)), centers(:,2), centers(:,3), label_count)
        
        ! Deallocate
        deallocate(centers)
    end subroutine identify_densities_imgspi

    subroutine label_connected_pixels(num, img_labels, label_count)
    ! labels connected pixels in the binary imgspi (num). img_labels is a vector that stores the labels (x-coord,y-coord,1=read?,2=label), and label_count holds the number of labels. 
        type(imgspi), intent(in) :: num
        integer, intent(inout)   :: img_labels(num%bx,num%bx,2), label_count
        integer                  :: j, k
        img_labels = 0 !all pixels are labelled 0 and no pixels have been checked yet
        label_count = 0
        do j=1,num%bx
            do k=1,num%bx
                if ( img_labels(j,k,1) == 0 )then
                    if ( num%rmat(j,k) == 1. )then
                        label_count = label_count + 1
                        call search_neighbors( num, img_labels, j, k, label_count, num%bx )
                    end if
                end if
            end do
        end do
    end subroutine label_connected_pixels

    recursive subroutine search_neighbors( num, img_labels, j, k, label_count, box )
    ! is used in label_connected_pixels to check a pixel's neighbors' densities.         
        type(imgspi), intent(in) :: num
        integer, intent(in)      :: box, j, k, label_count
        integer, intent(inout)   :: img_labels(box,box,2)
        integer                  :: a, b
        if ( j <= box .AND. k <= box .AND. j > 0 .AND. k > 0 .AND. img_labels(j,k,1) == 0 )then
            img_labels(j,k,1) = 1
            if ( num%rmat(j,k) == 1. )then
                img_labels(j,k,2) = label_count
                do a=-1,1
                    do b=-1,1
                        call search_neighbors( num, img_labels, j+a, k+b, label_count, box )
                    end do
                end do
            end if
        end if
    end subroutine search_neighbors

    function centers_of_mass(number_centers, img_labels, box)
    ! Count # of pixels with each label and find the center coordinates. number_centers is the number of centers, and box is the box size. img_labels is an array with the labeled image. centers_of_mass(i,1) = number of pixels with label i; (i,2:3) = center coordinates for each density with label i. 
        implicit none
        integer, intent(in)  :: number_centers, box, img_labels(box,box,2)
        real                 :: centers_of_mass(number_centers,3)
        integer              :: i, j, k
        i = 1;
        centers_of_mass(:,2:3) = 0.
        do i=1,number_centers
            centers_of_mass(i,1) = real(count(img_labels(:,:,2) == i))
        end do
        do j=1,box
            do k=1,box
                i = img_labels(j,k,2)
                if (i > 0) then
                    centers_of_mass(i,2) = centers_of_mass(i,2) + j
                    centers_of_mass(i,3) = centers_of_mass(i,3) + k
                end if
            end do
        end do
        centers_of_mass(:,2) = centers_of_mass(:,2) / centers_of_mass(:,1)
        centers_of_mass(:,3) = centers_of_mass(:,3) / centers_of_mass(:,1)
        return
    end function centers_of_mass

    subroutine remove_row_array_2d(array_2d, i)
    ! removes row i from the 2 dimensional array array_2d; Move me to somewhere more applicable. 
        real, allocatable, intent(inout)    :: array_2d(:,:)
        integer, intent(in)                 :: i
        real, allocatable                   :: temp_holder(:,:)
        integer                             :: n, alloc_stat
        allocate(temp_holder(size(array_2d,1),size(array_2d,2)), stat=alloc_stat)
        call alloc_err('In: remove_row_array_2d, module: simple_imgspi.f90', alloc_stat)
        temp_holder = array_2d
        deallocate(array_2d)
        allocate(array_2d(size(temp_holder,1)-1,size(temp_holder,2)), stat=alloc_stat)
        call alloc_err('In: remove_row_array_2d, module: simple_imgspi.f90', alloc_stat)
        do n=1,size(temp_holder,1)
            if (n<i) array_2d(n,:) = temp_holder(n,:)
            if (n>i) array_2d(n-1,:) = temp_holder(n,:)
        end do
        deallocate(temp_holder)
    end subroutine remove_row_array_2d

    subroutine append_row_array_2d(array_2d, array_to_add)
    ! appends the rows of array_to_add to the 2 dimensional array array_2d. The second dimension of both arrays must be the same. Move me to somewhere more applicable. 
        real, allocatable, intent(inout)    :: array_2d(:,:)
        real, intent(in)                    :: array_to_add(:,:)
        real, allocatable                   :: temp_holder(:,:)
        integer                             :: n, alloc_stat
        allocate(temp_holder(size(array_2d,1),size(array_2d,2)), stat=alloc_stat)
        call alloc_err('In: append_row_array_2d, module: simple_imgspi.f90', alloc_stat)
        temp_holder = array_2d
        deallocate(array_2d)
        allocate(array_2d(size(temp_holder,1)+size(array_to_add,1),size(temp_holder,2)), stat=alloc_stat)
        call alloc_err('In: append_row_array_2d, module: simple_imgspi.f90', alloc_stat)
        do n=1,size(temp_holder,1)
            array_2d(n,:) = temp_holder(n,:)
        end do
        do n=1,size(array_to_add,1)
            array_2d(n+size(temp_holder,1),:) = array_to_add(n,:)
        end do
        deallocate(temp_holder)
    end subroutine append_row_array_2d

    subroutine shrink_binary_imgspi(num)
    ! removes 1 layer of pixels bordering the background in a binary imgspi (num). 
        type(imgspi), intent(inout)   :: num
        integer                       :: j, k, a, b
        logical                       :: remove_pixels(num%bx,num%bx)
        ! Figure out which pixels to remove. 
        remove_pixels = .false.
        do j=1,num%bx
            do k=1,num%bx
                if (num%rmat(j,k)==1.) then
                    do a=-1,1
                        do b=-1,1
                            if (j+a>0 .and. k+b>0 .and. j+a<num%bx .and. k+b<num%bx .and. num%rmat(j+a,k+b)==0.) remove_pixels(j,k) = .true.
                        end do
                    end do
                end if
            end do
        end do
        ! Remove pixels. 
        do j=1,num%bx
            do k=1,num%bx
                if (remove_pixels(j,k)) num%rmat(j,k) = 0.
            end do
        end do
    end subroutine shrink_binary_imgspi

    subroutine grow_binary_imgspi(num)
    ! adds 1 layer of pixels bordering the background in a binary imgspi (num). 
        type(imgspi), intent(inout)   :: num
        integer                       :: j, k, a, b
        logical                       :: add_pixels(num%bx,num%bx)
        ! Figure out which pixels to add. 
        add_pixels = .false.
        do j=1,num%bx
            do k=1,num%bx
                if (num%rmat(j,k)==0.) then
                    do a=-1,1
                        do b=-1,1
                            if (j+a>0 .and. k+b>0 .and. j+a<num%bx .and. k+b<num%bx .and. num%rmat(j+a,k+b)==1.) add_pixels(j,k) = .true.
                        end do
                    end do
                end if
            end do
        end do
        ! Add pixels. 
        do j=1,num%bx
            do k=1,num%bx
                if (add_pixels(j,k)) num%rmat(j,k) = 1.
            end do
        end do
    end subroutine grow_binary_imgspi

    subroutine imgspi_from_img_labels(img_labels, imgspi_out, label, box)
    ! makes a binary imgspi (imgspi_out) from the pixels labeled with label according to array img_labels. box is the length of one side of the image in pixels. 
        type(imgspi), intent(inout) :: imgspi_out
        integer, intent(in)         :: box, label, img_labels(box,box,2)
        integer                     :: j, k
        real                        :: temp_image(box,box)
        temp_image = 0.
        do j=1,box
            do k=1,box
                if (img_labels(j,k,2) == label) temp_image(j,k) = 1.
            end do
        end do
        call set_imgspi(imgspi_out,temp_image)
    end subroutine imgspi_from_img_labels

    subroutine make_avg_imgspi(imgs, imgs_length, img)
    ! makes an imgspi by averaging the rmat values for each individual imgspi in the array of imgspi's (imgs). imgs_length is the number of imgspi's in the array, and img is the output imgspi. 
        type(imgspi), intent(inout)     :: img
        integer, intent(in)             :: imgs_length
        type(imgspi), intent(in)        :: imgs(imgs_length)
        integer                         :: j, k, n, box
        real                            :: rmat_sum
        if (imgs_length > 0) then
            box = imgs(1)%bx
            img = new_imgspi(box)
            do j=1,box
                do k=1,box
                    rmat_sum = 0.
                    do n=1,imgs_length
                        rmat_sum = rmat_sum + imgs(n)%rmat(j,k)
                    end do
                    img%rmat(j,k) = rmat_sum/imgs_length
                end do
            end do
        end if
    end subroutine make_avg_imgspi
    
    subroutine split_density(img, centers, label_count, box, density_index)
    ! splits density of the imgspi _img_ to two densities if it detects that two densities are connected into one. _centers_ is the array of density centers (see above), _label_count_ is the number of density labels. _box_ is the box size of the image. _density_index_ is the index of the centers array, and it refers to which density one wants to split. split_density is called in identify_densities_imgspi. 
        type(imgspi), intent(inout)      :: img
        integer, intent(inout)           :: label_count
        real, allocatable, intent(inout) :: centers(:,:)
        integer, intent(in)              :: box, density_index
        integer                          :: n, j, temp_img_labels(box,box,2), temp_label_count, alloc_stat
        real, allocatable                :: temp_holder(:,:)
        type(imgspi)                     :: img2
        
        do n=1,box
            call shrink_binary_imgspi(img)
            if (maxval(img%rmat) == 0.) exit
            call label_connected_pixels(img, temp_img_labels, temp_label_count)
            if (temp_label_count == 2) then
!                write(*,*) 'Two densities are connected.'
                ! Separate the two densities into img and img2. 
                img2 = new_imgspi(box)
                call imgspi_from_img_labels(temp_img_labels, img2, 2, box)
                call imgspi_from_img_labels(temp_img_labels, img, 1, box)
                do j=1,n
                    call grow_binary_imgspi(img)
                    call grow_binary_imgspi(img2)
                end do
                ! Modify centers to replace the old density with the two new densities. 
                call remove_row_array_2d(centers, density_index)
                call label_connected_pixels(img, temp_img_labels, temp_label_count)
                allocate(temp_holder(1,3), stat=alloc_stat)
                call alloc_err('In: identify_densities, module: simple_imgspi.f90', alloc_stat)
                temp_holder = centers_of_mass(1, temp_img_labels, box)
                call append_row_array_2d(centers, temp_holder)
                call label_connected_pixels(img2, temp_img_labels, temp_label_count)
                temp_holder = centers_of_mass(1, temp_img_labels, box)
                call append_row_array_2d(centers, temp_holder)
                deallocate(temp_holder)
                label_count = label_count + 1
                exit
            end if
        end do
    end subroutine split_density
    
    subroutine shift_imgspi_2( img, vec )
    ! shifts an imgspi according to the vector vec. Unfilled area becomes solid black (rmat = 0). 
        type(imgspi), intent(inout) :: img
        integer, intent(in)         :: vec(2)
        real                        :: tmp(img%bx,img%bx)
        integer                     :: i, j
        tmp = 0.
        do i=1, img%bx
            do j=1, img%bx
                if ( i+vec(1) > 0 .and. j+vec(2) > 0 .and. i+vec(1) <= img%bx .and. j+vec(2) <= img%bx) then
                    tmp(i+vec(1),j+vec(2)) = img%rmat(i,j)
                end if
            end do
        end do
        img%rmat = tmp
    end subroutine shift_imgspi_2
    
    subroutine shift_imgspi_3( img, vec )
    ! shifts an imgspi according to the vector vec. Pixels that are shifted outside of the image overflow
    ! to the other side. (So there is no unfilled area.) 
        type(imgspi), intent(inout) :: img
        integer, intent(in)         :: vec(2)
        real                        :: tmp(img%bx,img%bx)
        integer                     :: i, j, newx, newy
        tmp = 0.
        do i=1, img%bx
            do j=1, img%bx
		newx = i+vec(1)
		newy = j+vec(2)
		if ( newx <= 0 ) then
		    newx = img%bx + newx
		else if ( newx > img%bx ) then
		    newx = newx - img%bx
		end if
		if ( newy <= 0 ) then
		    newy = img%bx + newy
		else if ( newy > img%bx ) then
		    newy = newy - img%bx
		end if
                tmp(newx,newy) = img%rmat(i,j)
            end do
        end do
        img%rmat = tmp
    end subroutine shift_imgspi_3
    
    subroutine rotate_imgspi( img, angle )
    ! rotates binary imgspi counterclockwise by angle (in radians). The rotation is done by sampling and iterates over the source image, so it will miss some pixels, so it is only an approximation. 
        type(imgspi), intent(inout)     :: img
        real, intent(in)                :: angle
        real                            :: tmp(img%bx,img%bx), cosang, sinang
        integer                         :: i, j, x, y, center
        tmp = 0
        center = nint(real(img%bx+1.)/2.)
        cosang = cos(angle)
        sinang = sin(angle)
        do i=1, img%bx
            do j=1, img%bx
                if (img%rmat(i,j) == 1.) then
                    x = nint(cosang*(i-center)-sinang*(j-center)) + center
                    y = nint(sinang*(i-center)+cosang*(j-center)) + center
                    if (all((/x, y/)>0) .and. all((/x, y/)<=img%bx)) then
                        tmp(x,y) = img%rmat(i, j)
                    end if
                end if
            end do
        end do
        img%rmat = tmp
    end subroutine rotate_imgspi
    
    subroutine align_cls_imgspi( imgs, num_imgs, cls, current_cls, pwtab, dens_maps, nptcls, box, save_angles )
    ! imprecisely aligns and plots a cluster of binary imgspi (in imgs array). cls is the array resulting from heirarchical clustering, current_cls is the number of the cluster to align and plot, pwtab is the pair weight table for the dens_maps, dens_maps is the dens_maps, nptcls = number of particles, and box = pixel length of one side of the image. If save_angles is TRUE, the angles will be saved to the file angles_init.txt. 
        integer, intent(in)             :: num_imgs, cls(nptcls), current_cls, box, nptcls
        type(imgspi), intent(in)        :: imgs(num_imgs)
        type(dens_map), intent(in)      :: dens_maps(nptcls)
        type(pair_wtab), intent(in)     :: pwtab
        logical, intent(in), optional   :: save_angles
        type(imgspi)                    :: img, img_temp, avg_img, imgs2(num_imgs)
        type(dens_map)                  :: dens_maps2(nptcls)
        integer                         :: current_cls_members(num_imgs), centroid, n, j, k
        real                            :: best_angle(num_imgs)
        integer                         :: file_stat
        real                            :: pi, cls_weights(num_imgs, num_imgs), shift(2)
        real                            :: cls_weights_avg(num_imgs), center, center_mass(2)
        real                            :: pix_in_common, best_pix_in_common
        pi = acos(-1.)
        ! Copy imgs and dens_maps because they will be modified. 
        imgs2 = imgs
        dens_maps2 = dens_maps
        n = 1
        ! Find out which images are members of the current cluster. 
        do j=1,nptcls
            if (cls(j) == current_cls) then
                current_cls_members(n) = j ! current_cls_members is an array of the indices of images that are members of the current cluster (current_cls) being iterated over. 
                n = n + 1
            end if
        end do
        ! find the centroid of the cluster:
        !   1. Store the weights from the pair_wtab in the array cls_weights
        !   2. Calculate the average weight for each image in the cluster. 
        !   3. Find the image with the highest average weight. 
        !      This is the image that is on average closest to the other images so we'll consider it the "centroid". 
        cls_weights = 0.
        do j=1,num_imgs
            do k=1,num_imgs
                cls_weights(j,k)=get_pair_w(pwtab, current_cls_members(j), current_cls_members(k))
            end do
        end do
        cls_weights_avg = sum(cls_weights,2)/real(size(cls_weights(1,:)))
        centroid = 1
        do j=2,num_imgs
            if (cls_weights_avg(j)>cls_weights_avg(centroid)) centroid = j
        end do
        ! read, shift, and rotate images to roughly align with centroid
        center = (box+1.)/2.
        center_mass = cenmass_dens_map(dens_maps2(centroid))
        shift = center - center_mass
        call shift_dens_map(dens_maps2(centroid), shift(1), shift(2))
        call shift_imgspi_2 (imgs2(centroid), nint(shift))
        avg_img = imgs2(centroid)
        do n=1,num_imgs
            k = current_cls_members(n)
            img = imgs2(n) 
            ! center of mass, shift dens map and imgspi, find angle of rotation, rotate imgspi
            center_mass = cenmass_dens_map(dens_maps2(k))
            shift = center - center_mass
            call shift_dens_map(dens_maps2(k),shift(1), shift(2))
            call shift_imgspi_2( img, nint(shift) ) 
            best_pix_in_common = 0.
            ! try different rotations and use the best
            do j=1,360
                img_temp = img
                call rotate_imgspi(img_temp, j*pi/180.)
                pix_in_common = shared_pixels_imgspi(avg_img, img_temp)
                if (pix_in_common > best_pix_in_common) then
                    best_pix_in_common = pix_in_common
                    imgs2(n) = img_temp
                    best_angle(n) = j*pi/180.
                end if
            end do
            call make_avg_imgspi(imgs2(:n), n, avg_img)
        end do
        ! write best angle to file
        if( present(save_angles) .AND. save_angles ) then
            open(unit=17, file='angles_init.txt', status='replace', iostat=file_stat,&
            access='direct', action='write', form='formatted', recl=8 )
            if( file_stat /= 0 )then ! cannot open file
                write(*,*) 'Cannot open file: angles_init.txt'
                write(*,*) 'In program: simple_imgspi.f90'
                stop
            endif
            do n=1,num_imgs
                write(17,'(F8.5)',rec=(n)) best_angle(n)
            end do
            close(17)
            write(*,*) 'Angles of rotation saved to file angles_init.txt '
        end if
        call plot_imgspi(avg_img)
    end subroutine align_cls_imgspi
    
    function shared_pixels_imgspi(img1, img2)
    ! How many forground pixels in img1 are also forground pixels in img2?
    ! not tested
        type(imgspi), intent(in)        :: img1, img2
        real                            :: shared_pixels_imgspi
        integer                         :: i, j
        shared_pixels_imgspi = 0.
        do i=1,img1%bx
            do j=1, img1%bx
                if (img1%rmat(i,j)>0. .and. img2%rmat(i,j)>0.) then
                    shared_pixels_imgspi = shared_pixels_imgspi + img2%rmat(i,j)
                end if
            end do
        end do
        return
    end function shared_pixels_imgspi
    
    subroutine plot_dens_map_imgspi(img, dmap)
    ! given the imgspi _img_ and dens_map _dmap_, plot_dens_map creates a new imgspi with x's where the dens_map points are.  (can use this to visually test identify_densities_imgspi) 
        type(imgspi), intent(in)        :: img
        type(dens_map), intent(in)      :: dmap
        logical                         :: is_binary
        type(imgspi)                    :: img2
        integer                         :: x, y, n, i
        real                            :: dmap_coords(4,2), minrmat
        img2 = img
        dmap_coords = coord_dens_map(dmap)
        is_binary = all(img%rmat == 0. .or. img%rmat == 1.)
        if (.not. is_binary) minrmat = minval(img%rmat)
        do n=1,4
            x = nint(dmap_coords(n,1))
            y = nint(dmap_coords(n,2))
            do i=-2,2
                if (all((/x+i,y+i/)<=img%bx) .and. all((/x+i,y+i/)>0)) then
                    if (is_binary) then
                        img2%rmat(x+i,y+i) = abs(1. - img%rmat(x+i,y+i))
                    else
                        img2%rmat(x+i,y+i) = minrmat
                    end if
                end if
                if (all((/x+i,y-i/)<=img%bx) .and. all((/x+i,y-i/)>0)) then
                    if (is_binary) then
                        img2%rmat(x+i,y-i) = abs(1. - img%rmat(x+i,y-i))
                    else
                        img2%rmat(x+i,y-i) = minrmat
                    end if
                end if
            end do
        end do
        call plot_imgspi(img2)
    end subroutine plot_dens_map_imgspi

end module simple_imgspi