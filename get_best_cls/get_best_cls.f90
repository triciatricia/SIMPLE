! -------------------------------------------------------------------------------------
! Get initial rotation angles for a cluster from the results from cluster_densities. 
! These angles will be stored in the file angles_init.txt (ie: for use in 
! align_densities).
!
! Clusters are ordered by their cluster sillhoutte width. This indicates how well 
! cluster members are similar to other members of the same cluster and different from
! other clusters. In this program, the clusters with the highest sillhoutte widths are
! considered the "best" clusters. This program gets rotation angles for the nth "best"
! cluster, where n is an integer supplied by the user. The rotation angles are obtained 
! by roughly aligning all images to a continuous avg starting with the centroid, 
! The rotation angles are stored in angles_init.txt and can be used to initialize the 
! differential evolution in align_densities.
!
! Requires the following files to be present: 
!   - dens_maps.txt
!     A direct access text file containing the four masses, four x-coordinates, four y-coordinates
!     and number of densities for each image. If an image has fewer than 4 densities, the
!     extra values will be 0. (Format: "(4I5, 8F9.4, I2)")
!   - rmsd.txt
!     A direct access text file containing the matches of one image and the closest image
!     to it (based on RMSD between densities) and the RMSD between them. 
!     (Format: "(I6, I6, F8.4)" = (Image#, ClosestImage#, RMSD))
!   - rmsd_pwtab.bin
!     An unformatted direct access file for the pair weight table containing weights
!     based on RMSDs between images. (See the module simple_pair_wtab for more info.)
!   - cls.txt
!     A direct access text file containing the image number (in the order it was in in 
!     the input image stack) and the cluster the image is in. (Format: "(I7, I7)")
! 
! Arguments:
!   stk      - The file name of the spider image stack of the images being analyzed 
!              (used to do some rough calculations and to plot a rough estimate of 
!              the class average). Use the binarized images that were output
!              from the program binarize.
!   box      - The length of the input image (a square) in pixels. 
!   nptcls   - Total number of particles being analyzed (= number of images in the
!              stack)
!   clsnr    - The nth "best" cluster to get initial rotation angles for. (See
!              above for more information.)
! 
! Creates the file:
!   - angles_init.txt
!     A direct access text file containing rough, initial rotation angles for aligning
!     the images in a cluster. (Format: "(F8.5)")
! -------------------------------------------------------------------------------------

program get_best_cls
use simple_stkspi
use simple_imgspi
use simple_cmdline
use simple_params
use simple_dens_map
use simple_pair_wtab
use simple_stat
use simple_heapsort
implicit none

integer                                 :: i, j, k, n, num_clusters, num_imgs
integer                                 :: file_stat, alloc_stat, selected_cls
real                                    :: selected_sil
real, allocatable                       :: rmsd(:,:), cls_dist_table(:,:), sil_cls(:)
type(stkspi)                            :: stack
type(imgspi)                            :: img
type(imgspi), allocatable               :: imgs(:)
type(dens_map), allocatable             :: dens_maps(:)
type(pair_wtab)                         :: rmsd_pwtab
type(heapsort)                          :: sil_cls_heap
character(len=256)                      :: stkconv

if( command_argument_count() < 4 )then
    write(*,*) './get_best_cls stk=inputstk.spi box=200 nptcls=10329 clsnr=3 [debug=<yes|no>]'
    stop
endif

! parse command line args
call parse_cmdline
call make_params

! allocate
allocate(dens_maps(nptcls), rmsd(nptcls,nptcls), cls(nptcls), stat=alloc_stat)
call alloc_err('In program: get_best_cls', alloc_stat)

! read dens_maps from file
write(*,*) 'Reading dens_maps from file.'
call get_dens_maps(dens_maps, nptcls)

! read rmsd_table.txt from file
open(unit=15, file='rmsd_table.txt', status='old', iostat=file_stat,&
access='direct', action='read', form='formatted', recl=7 )
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: rmsd_table.txt'
    write(*,*) 'In program: get_best_cls.f90'
    stop
endif
n = 1
do i=1,nptcls-1
    do j=i+1,nptcls
        read(15,'(F7.2)',rec=(n)) rmsd(i,j)
        rmsd(j,i) = rmsd(i,j)
        n = n + 1
    end do
end do
close(15)

! recover pair_wtab from file. 
write(*,*) 'Reading rmsd_pwtab from file.'
rmsd_pwtab = new_pair_wtab(nptcls)
call recover_pair_wtab( rmsd_pwtab, 'rmsd_pwtab.bin' )


! Read cls from file
write(*,*) 'Reading cls from file.'
open(unit=17, file='cls.txt', status='unknown', iostat=file_stat,&
access='direct', form='formatted', recl=14, action='read')
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: ', 'cls.txt'
    write(*,*) 'In program: get_best_cls.f90'
    stop
endif
do i=1,nptcls
    read(17, "(I7, I7)", rec=i) n, cls(i)
end do
close(17)

! cls_dist_table is a table of the distances between clusters
write(*,*) 'Calculating cluster stats.'
num_clusters = maxval(cls)
allocate(cls_dist_table(num_clusters,num_clusters), sil_cls(num_clusters), stat=alloc_stat)
call alloc_err('In program: get_best_cls', alloc_stat)
  cls_dist_table = avg_dist_table( rmsd, num_clusters, nptcls, cls )

! Use silhoutte width to find the nth best cluster. (n = clsnr)
sil_cls = sil_width_cls( cls, cls_dist_table, nptcls, num_clusters, rmsd, 5 )
sil_cls_heap = new_heapsort(num_clusters)
do i=1,num_clusters
    ! These values are negative because the heapsort sorts the max values first. 
    call set_heapsort(sil_cls_heap, i, -sil_cls(i), i)
end do
call sort_heapsort(sil_cls_heap)
! selected_sil hols the silhoutte width for the selected cluster. 
! selected_cls holds the cluster number corresponding to the nth "best" cluster.
call get_heapsort( sil_cls_heap, clsnr, selected_sil, selected_cls )
selected_sil = -selected_sil

! Write the angles to rotate and plot avg cluster image. 
img = new_imgspi(box)
stack = new_stkspi( name=stk )
! determine how to convert the stack
call find_stkconv( stack, stk, stkconv )
if (any(cls==selected_cls)) then
    num_imgs = count(cls == selected_cls)
    allocate(imgs(num_imgs), stat=alloc_stat)
    call alloc_err('In program: get_best_cls', alloc_stat)
    write(*,'(A, I6)', advance='no') 'Cluster:', selected_cls, 'Members:'
    n = 1
    do k=1,nptcls
        if (cls(k) == selected_cls) then
            write(*,'(I6)',advance='no') k
            call read_imgspi(stack, stk, k, img, stkconv) 
            imgs(n) = img
            n = n + 1
        end if
    end do
    write(*,*) ''
    call align_cls_imgspi( imgs, size(imgs), cls, selected_cls, rmsd_pwtab, dens_maps, nptcls, box, .TRUE. )
    deallocate(imgs)
end if

end program get_best_cls