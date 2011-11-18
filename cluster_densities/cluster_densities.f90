! -------------------------------------------------------------------------------------
! cluster_densities clusters images with 3-4 densities per image using heirarchical 
! clustering. Run this after extract_densities to cluster images based 
! on rmsd. At the end, this plots roughly aligned averages of the "best" 5 of these 
! clusters. 
!
! Command Arguments
!   - stk = stack of binarized images that you are analyzing (will be used for plotting 
!     a few clusters to show whether clustering worked). 
!   - maxp = maximum number of particles in a class
!   - box = length of a side of the image in pixels (image is square shaped)
!   - nptcls = number of particles
!   - ncls = maximum number of clusters
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
! 
! Creates the following file: 
!   - cls.txt
!     A direct access text file containing the image number (in the order it was in in 
!     the input image stack) and the cluster the image is in. (Format: "(I7, I7)")
! -------------------------------------------------------------------------------------

program cluster_densities
use simple_stkspi
use simple_imgspi
use simple_math
use simple_cmdline
use simple_params
use simple_jiffys
use simple_dens_map
use simple_pair_wtab
use simple_sll_list
use simple_stat
use simple_heapsort
implicit none

integer                                 :: i, j, k, n, current_cls, num_clusters, num_imgs
integer                                 :: file_stat, alloc_stat, nplot
real, allocatable                       :: rmsd(:,:), cls_dist_table(:,:)
real, allocatable                       :: closest_clust(:,:), sil_cls(:), top_sil(:)
integer, allocatable                    :: top_sil_cls(:)
type(stkspi)                            :: stack, stack_out
type(imgspi)                            :: img
type(imgspi), allocatable               :: imgs(:)
type(dens_map), allocatable             :: dens_maps(:)
type(pair_wtab)                         :: rmsd_pwtab
type(sll_list), allocatable             :: hac_sll(:)
type(heapsort)                          :: sil_cls_heap
character(len=256)                      :: stkconv

if( command_argument_count() < 5 )then
    write(*,*) './cluster_densities stk=inputstk.spi maxp=<maximum nr of ptcls in class> box=200 nptcls=10329 ncls=1000  [debug=<yes|no>]'
    stop
endif

! parse command line args
call parse_cmdline
call make_params(2) ! Mode 2 = unsupervised agglomerative hierachical 2D classification with greedy adaptive refinement

! allocate
allocate(dens_maps(nptcls), rmsd(nptcls,nptcls), hac_sll(nptcls), stat=alloc_stat)
call alloc_err('In program: cluster_densities', alloc_stat)

! -------------------------------------------------------------------------------------
! Recover Data from File
! -------------------------------------------------------------------------------------

! read dens_maps from file
write(*,*) 'Reading dens_maps from file.'
call get_dens_maps(dens_maps, nptcls)

! read rmsd_table.txt from file
open(unit=15, file='rmsd_table.txt', status='old', iostat=file_stat,&
access='direct', action='read', form='formatted', recl=7 )
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: rmsd_table.txt'
    write(*,*) 'In program: extract_densities.f90'
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

! -------------------------------------------------------------------------------------
! Heirarchical Clustering
! -------------------------------------------------------------------------------------

! Make the simple linked list for hac_cls to use
do i=1,nptcls
    hac_sll(i) = new_sll_list()
    call add_sll_node( hac_sll(i), i )
end do
! Heirarchical clustering
call hac_cls( rmsd_pwtab, nptcls, ncls, maxp, hac_sll) 
num_clusters = 1
call sll_to_arr_cls( hac_sll, nptcls, cls, num_clusters ) 
! Recluster ~30% of particles. 
call refine_hac_cls( rmsd_pwtab, nptcls, num_clusters, nint(.3*nptcls), cls, maxp )
! Convert array to sll and back again so they are synced up and there are 
! no empty classes. 
call arr_to_sll_cls( cls, nptcls, hac_sll)
num_clusters = 1
call sll_to_arr_cls( hac_sll, nptcls, cls, num_clusters )

! Output cls to file
open(unit=17, file='cls.txt', status='replace', iostat=file_stat,&
access='direct', form='formatted', recl=14, action='write')
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: ', 'cls.txt'
    write(*,*) 'In program: cluster_densities.f90'
    stop
endif
do i=1,nptcls
    write(17, "(I7, I7)", rec=i) i, cls(i)
end do
close(17)

! -------------------------------------------------------------------------------------
! Plot 5 "Best" Clusters
! -------------------------------------------------------------------------------------
! Number to plot
nplot = min(num_clusters,5)

! cls_dist_table is a table of the distances between clusters
allocate(cls_dist_table(num_clusters,num_clusters), sil_cls(num_clusters), stat=alloc_stat)
call alloc_err('In program: cluster_densities', alloc_stat)
 cls_dist_table = avg_dist_table( rmsd, num_clusters, nptcls, cls )

! Use silhouette width to find "best" clusters. Don't bother calculating the 
! silhouette width for clusters with 5 or fewer particles (value will be 0). 
sil_cls = sil_width_cls( cls, cls_dist_table, nptcls, num_clusters, rmsd, 5 )
sil_cls_heap = new_heapsort(num_clusters)
do i=1,num_clusters
    ! These sil values are negative because the heapsort sorts the max values first.
    call set_heapsort(sil_cls_heap, i, -sil_cls(i), i)
end do
call sort_heapsort(sil_cls_heap)
allocate(top_sil_cls(nplot), top_sil(nplot), stat=alloc_stat)
call alloc_err('In program: cluster_densities', alloc_stat)
! top_sil holds the silhouette widths for the top clusters
! top_sil_cls holds the cluster number corresponding to the silhouette widths in top_sil
do i=1,size(top_sil_cls)
    call get_heapsort( sil_cls_heap, i, top_sil(i), top_sil_cls(i) )
end do
top_sil = -top_sil

! Plot the 5 "best" avg cluster imgs
img = new_imgspi(box)
stack = new_stkspi( name=stk )
! determine how to convert the stack
call find_stkconv( stack, stk, stkconv )
do i=1,size(top_sil_cls)
    current_cls=top_sil_cls(i) 
    if (any(cls==current_cls)) then
        num_imgs = count(cls == current_cls)
        stack_out = new_stkspi(box,num_imgs)
        allocate(imgs(num_imgs), stat=alloc_stat)
        call alloc_err('In program: cluster_densities', alloc_stat)
        n = 1
        write(*,'(A, I6)', advance='no') 'Cluster', current_cls, 'Members:'
        do k=1,nptcls
            if (cls(k) == current_cls) then
                write(*,'(I6)',advance='no') k
                call read_imgspi(stack, stk, k, img, stkconv) 
                imgs(n) = img
                n = n + 1
            end if
        end do
        write(*,*) ''
        call align_cls_imgspi( imgs, size(imgs), cls, current_cls, rmsd_pwtab, dens_maps, nptcls, box )
        deallocate(imgs)
    end if
end do

end program cluster_densities