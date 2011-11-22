! -------------------------------------------------------------------------------------
! Uses Simple's differential evolution algorithm to align the gold density images 
! in a cluster. Densities are represented by dens_map. 
! 
! Arguments:
!   box      - The length of the input image (a square) in pixels. 
!   nptcls   - Total number of particles being analyzed (= number of images in the
!              stack)
!   neigh    - The fraction of the population in each neighborhood. A lower value
!              results in more diversity in the search. 0 <= neigh <= 1
!   GENMAX   - The maximum number of generations (iterations) for the differential
!              evolution. 
!   clsnr    - The cluster to get initial rotation angles for. (Note: this isn't the
!              nth best cluster as in get_best_cls. Rather, this is the actual cluster
!              number that can be found in cls.txt (and it is printed out when running
!              get_best_cls.)
!
! Requires the following files present: 
!   - dens_maps.txt
!     A direct access text file containing the four masses, four x-coordinates, four y-coordinates
!     and number of densities for each image. If an image has fewer than 4 densities, the
!     extra values will be 0. (Format: "(4I5, 8F9.4, I2)")
!   - cls.txt
!     A direct access text file containing the image number (in the order it was in in 
!     the input image stack) and the cluster the image is in. (Format: "(I7, I7)")
!   - angles_init.txt
!     A direct access text file containing rough, initial rotation angles for aligning
!     the images in a cluster. (Format: "(F8.5)")
!   - <stk>
!     A spider stack file containing the spider images to be aligned (size = nptcls). 
!     (The file name is speified by the command argument stk.)
! 
! For example:
!   One can run extract_densities to get dens_maps.txt.
!   One can run cluster_densities to get cls.txt. 
!   One can get the inital angles of rotation by running get_best_cls. 
!
! If you use angles from get_best_cls, you initialize with a set of solutions, 
! one of which is from roughly aligning all images to a continuous avg starting with
! the centroid. The rest of the inital solutions are very different from the first
! to encourage diversification in the search over converging on a local minimum. 
! 
! Outputs 2 files:
!    - angles<clsnr>.txt
!      A direct access text file containing the rotation angles. (Format: "(F8.5)")
!    - <outstk>
!      A spider stack file containing rotated spider images. (The file name is
!      specified by the command argument outstk.)
! -------------------------------------------------------------------------------------
program align_densities
use simple_cmdline
use simple_params
use simple_dens_map
use simple_dens_map_align
use simple_de_opt
use simple_imgspi
use simple_stkspi
use simple_ffts
use simple_fplane
implicit none
save

type(de_opt)                            :: cls_de_opt
integer                                 :: num_imgs, size_pop, alloc_stat
integer                                 :: i, n, m
integer                                 :: file_stat, centroid
integer, allocatable			:: cls_imgs(:)
type(dens_map)                          :: temp_dens_map, avg_dens_map
type(dens_map), allocatable             :: dens_maps(:), dmap_cls(:), rotated_dens_maps(:)
real                                    :: cost_error, cost_fittest, pie, theta, shift(2)
real                                    :: dangle, best_dist, dist, init_spread, center, cmass(2)
real, allocatable                       :: angles(:), limits(:,:), r(:), angles_init(:), init_sol(:,:)
real, allocatable                       :: dist_table(:,:), dist_sum(:), all_angles_init(:)
character(len=32)                       :: clsnr_char, angles_file_name
type(imgspi)				:: img
type(imgspi), allocatable		:: imgs(:)
type(stkspi)				:: stack, stack_out
real, pointer				:: img_pointer(:,:)=>null()
complex, allocatable			:: ft(:,:)
character(len=256)			:: stkconv

if( command_argument_count() < 7 )then
    write(*,*) './align_densities  stk=inputstk.spi outstk=outstack.spi box=200 nptcls=10329 neigh=0.05 GENMAX=200 clsnr=67  [debug=<yes|no>]'
    stop
endif

! parse command line args
call parse_cmdline
call make_params(2) ! Mode 2 = unsupervised agglomerative hierachical 2D classification with greedy adaptive refinement

! -------------------------------------------------------------------------------------
! Other parameters
! -------------------------------------------------------------------------------------
! The larger this number is, the more varied the initial solutions for differential 
! evolution (not inluding the one supplied by angles_init.txt) are. The smaller this 
! number is, the more likely it is that the initial solutions will be more different 
! from the one supplied by angles_init.txt, thus forcing more exploration of alternate 
! solutions. 
! 0 <= init_spread <= 2pi
init_spread = 0.3

! File name for the output.
write(clsnr_char,'(I10)') clsnr
 clsnr_char = adjustl(clsnr_char)
angles_file_name = 'angles'//trim(clsnr_char)//'.txt'

! -------------------------------------------------------------------------------------
! Read information from file and allocate arrays
! -------------------------------------------------------------------------------------

! Allocate cls and dens_maps
allocate(dens_maps(nptcls), stat=alloc_stat)
call alloc_err('In Program: align_densities', alloc_stat)

! Read dens_maps from file
write(*,*) 'Reading dens_maps from file.'
call get_dens_maps(dens_maps, nptcls)

! Read cls from file
write(*,*) 'Reading cls from file.'
open(unit=17, file='cls.txt', status='unknown', iostat=file_stat,&
access='direct', form='formatted', recl=14, action='read')
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: ', 'cls.txt'
    write(*,*) 'In program: align_densities.f90'
    stop
endif
do i=1,nptcls
    read(17, "(I7, I7)", rec=i) n, cls(i)
end do
close(17)

! Number of images in our cluster
num_imgs = count(cls == clsnr)

! Allocate arrays
! Note: size(angles) = num_imgs-1 because the last image doesn't need to be rotated. 
allocate(dmap_cls(num_imgs), angles(num_imgs-1), limits(num_imgs-1,2), cls_imgs(num_imgs), stat=alloc_stat)
call alloc_err('In Program: align_densities', alloc_stat)

! Store all dens_maps from our cluster into the array dmap_cls; record 
! indices of the images in our cluster into the array cls_imgs. 
n = 0
do i=1,nptcls
    if (cls(i) == clsnr) then
        n = n + 1
        dmap_cls(n) = dens_maps(i)
	cls_imgs(n) = i
    end if
end do

! Initialize information for the cost function
call init_dmap_align(dmap_cls, num_imgs, box)

! -------------------------------------------------------------------------------------
! Other parameters for differential evolution
! -------------------------------------------------------------------------------------
pie = acos(-1.)
limits(:,1) = 0
limits(:,2) = 2*pie
size_pop = 10*num_imgs
 cyclic = .TRUE.
! The error in the cost function is unknown, but we will use the value below. 
 cost_error = 4.

! -------------------------------------------------------------------------------------
! Generate initial solutions:
! -------------------------------------------------------------------------------------
! Allocate arrays
allocate(r(num_imgs-1), angles_init(num_imgs-1), init_sol(size_pop,num_imgs-1), dist_table(num_imgs,num_imgs), dist_sum(num_imgs), all_angles_init(num_imgs), rotated_dens_maps(num_imgs), imgs(num_imgs), stat=alloc_stat)
call alloc_err('In Program: align_densities', alloc_stat)

! Read initial angles from file
open(unit=17, file='angles_init.txt', status='unknown', iostat=file_stat,&
access='direct', action='read', form='formatted', recl=8 )
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: angles_init.txt'
    write(*,*) 'In program: align_densities.f90'
    stop
endif
do n=1,num_imgs
    read(17,'(F8.5)',rec=(n)) all_angles_init(n)
end do
close(17)

! Convert angles to rotate to match centroid to angles to rotate to match the last dens_map. 
all_angles_init = all_angles_init - all_angles_init(num_imgs)
angles_init = all_angles_init(1:num_imgs-1)
do i=1,size(angles_init)
    if (angles_init(i) < 0.) angles_init(i) = angles_init(i) + 2.*pie
end do

write(*,*) 'Initial angles:'
write(*,*) angles_init
write(*,*) 'Cost init:', cost_dmap(angles_init, size(angles_init))

! Generate initial population of solutions
do i=1,size_pop-1
    call RANDOM_NUMBER(r)
    init_sol(i,:) = (angles_init + pie) - (r-0.5)*init_spread ! "+ pie" to make these angles very different from angles_init to increase diversity and force more exploration to find a more global optimum
    do n=1,size(angles_init)
        if (init_sol(i,n)<0) init_sol(i,n) = init_sol(i,n) + 2.*pie
        if (init_sol(i,n)>2.*pie) init_sol(i,n) = init_sol(i,n) - 2.*pie
    end do
end do
init_sol(size_pop,:) = angles_init

! -------------------------------------------------------------------------------------
! Differential evolution:
! -------------------------------------------------------------------------------------
write(*,'(A)') '>>> Differential evolution'
! Initialize
 cls_de_opt = new_de_opt( size(angles), limits, size_pop, neigh, cyclic, init_sol)
! Run differential evolution
call de_cont_min( cls_de_opt, cost_dmap, GENMAX, cost_error, angles, cost_fittest )

! -------------------------------------------------------------------------------------
! Output Results
! -------------------------------------------------------------------------------------

write(*,*) 'Angles:'
write(*,*) angles
write(*,*) 'Final cost:', cost_fittest

! Output angles to the file <anglesfilename>
! ------------------------------------------
open(unit=17, file=angles_file_name, status='replace', iostat=file_stat,&
access='direct', action='write', form='formatted', recl=8 )
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: '//angles_file_name
    write(*,*) 'In program: align_densities'
    stop
endif
n = 1
do i=1,size(angles)
    write(17,'(F8.5)',rec=(i)) angles(i)
end do
! The last image wasn't rotated: 
write(17,'(F8.5)',rec=num_imgs) 0.
close(17)
write(*,*) 'Angles of rotation saved to file: ', angles_file_name

! Center and rotate images and output to image stack file.
! --------------------------------------------------------
! make image
img = new_imgspi()

! make stacks
stack = new_stkspi( name=stk )
stack_out = new_stkspi(box, num_imgs)
call write_stk_hed( stack_out, outstk )

! determine how to convert the stack
 call find_stkconv( stack, stk, stkconv )

! allocate
allocate( ft(-xdim:xdim,-xdim:xdim) )

center = (box + 1.)/2.
do i=1,num_imgs
    if (i<num_imgs) then
	! theta is in degrees, positive is clockwise. 
	theta = 2. * pie - angles(i) * 180. / pie
    else 
	theta = 0.
    end if
    call read_imgspi( stack, stk, cls_imgs(i), img, stkconv )
    ! Center images using dens_map info
    cmass = cenmass_dens_map(dens_maps(cls_imgs(i)))
    shift = center - cmass
    call shift_imgspi_3(img, nint(shift))
    ! For each image, convert to fplane
    call shift_imgspi( img )
    call get_imgspi_ptr( img, img_pointer ) !returns a pointer img_pointer to volume data (rmat)
    call simple_2dfft( img_pointer, box, ft )
    call shiftrot_fplane( ft, theta, 0., 0. ) 
    call simple_2dfft_rev(ft, box, img_pointer)
    call shift_imgspi( img )
    imgs(i) = img
    call write_imgspi(stack_out, outstk, i, img )
end do

! Plot class average. 
call make_avg_imgspi(imgs, size(imgs), img)
call plot_imgspi(img)

end program align_densities