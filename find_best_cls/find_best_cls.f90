! -------------------------------------------------------------------------------------
! Find best cluster(s) from the results from cluster_densities. 
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
! Note: For testing purposes; this is separate from cluster_densities. Use this after
! using cluster_densities to look at some of the clusters to judge clustering by eye. 
! Uses silhouette width to judge which clusters are "good." 
! Writes the spider image stacks of the "best" 7 clusters to separate files: 
! cls1.spi for the best, cls2,spi for second best, etc. 
! Also, you can uncomment various sections of the code below to get various stats
! about the clustering. 
! -------------------------------------------------------------------------------------

program find_best_cls
use simple_stkspi
use simple_imgspi
use simple_math
use simple_params
use simple_dens_map
use simple_pair_wtab
use simple_stat
use simple_heapsort
implicit none

integer                                 :: i, j, k, n, current_cls, num_clusters, num_imgs
integer                                 :: file_stat, alloc_stat, best_cls
real                                    :: silhouette
real, allocatable                       :: closest_img(:,:), rmsd(:,:), cls_dist_table(:,:)
real, allocatable                       :: closest_clust(:,:), dist_owncls(:), sil_cls(:), top_sil(:)
integer, allocatable                    :: match(:), top_sil_cls(:)
character(len=10)                       :: chari
type(stkspi)                            :: stack, stack_out
type(imgspi)                            :: img
type(imgspi), allocatable               :: imgs(:)
type(dens_map), allocatable             :: dens_maps(:)
type(pair_wtab)                         :: rmsd_pwtab, dist_pwtab
type(sll_list), allocatable             :: hac_sll(:)
type(heapsort)                          :: sil_cls_heap
character(len=256)                      :: stkconv

if( command_argument_count() < 5 )then
    write(*,*) './find_best_cls stk=inputstk.spi box=100 nptcls=10000 smpd=1.85 [debug=<yes|no>]'
    stop
endif

! parse command line args
call make_params

! allocate
allocate(closest_img(nptcls,2), match(nptcls), dens_maps(nptcls), rmsd(nptcls,nptcls), hac_sll(nptcls), cls(nptcls), dist_owncls(nptcls), stat=alloc_stat)
call alloc_err('In program: find_best_cls', alloc_stat)

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


! Read cls from file
write(*,*) 'Reading cls from file.'
open(unit=17, file='cls.txt', status='unknown', iostat=file_stat,&
access='direct', form='formatted', recl=14, action='read')
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: ', 'cls.txt'
    write(*,*) 'In program: best_cls.f90'
    stop
endif
do i=1,nptcls
    read(17, "(I7, I7)", rec=i) n, cls(i)
end do
close(17)

! -------------------------------------------------------------------------------------
! Clustering Stats (Uncomment blocks of code below as you wish.)
! -------------------------------------------------------------------------------------

! cls_dist_table is a table of the distances between clusters
write(*,*) 'Calculating cluster stats.'
num_clusters = maxval(cls)
allocate(cls_dist_table(num_clusters,num_clusters), sil_cls(num_clusters), stat=alloc_stat)
call alloc_err('In program: find_best_cls', alloc_stat)
  cls_dist_table = avg_dist_table( rmsd, num_clusters, nptcls, cls )

! Uncomment the code below to calculate the silhouette width. Larger is better. 
! silhouette = sil_width( cls, cls_dist_table, nptcls, num_clusters, rmsd )
! write(*,*) 'Silhouette Width:', silhouette

! Uncomment the code below to calculate distance to own cluster (in PIXELS) and 
! output to a file.
! dist_owncls = dist_self( cls, cls_dist_table, nptcls, num_clusters, rmsd )
! open(unit=18, file='dist_own_cls.txt', status='replace', iostat=file_stat,&
! access='direct', form='formatted', recl=9, action='write')
! if( file_stat /= 0 )then ! cannot open file
!     write(*,*) 'Cannot open file: ', 'rmsd.txt'
!     write(*,*) 'In program: cluster_densities.f90'
!     stop
! endif
! do i=1,nptcls
!     write(18, "(F9.4)", rec=i) dist_owncls(i)
! end do
! close(18)

! Uncomment the code below to calculte distances between closest clusters (Angstroms)
! and output to a file. 
! ! Find closest clusters;
! allocate(closest_clust(num_clusters,2), stat=alloc_stat)
! call alloc_err('In program: find_best_cls', alloc_stat)
!  closest_clust = 0
! ! The closest image to i is image j. 
! do i=1,num_clusters
!     if (any(cls==i)) then
!         j = closest_obj(i, cls_dist_table, num_clusters)
!         closest_clust(i,1) = j
!         closest_clust(i,2) = cls_dist_table(i,j)
!     end if
! end do
! ! Convert RMSD from pixels to Angstroms. 
!  closest_clust(:,2) = closest_clust(:,2) * smpd
! ! output to file
! open(unit=16, file='cls_rmsd.txt', status='replace', iostat=file_stat,&
! access='direct', form='formatted', recl=20, action='write')
! if( file_stat /= 0 )then ! cannot open file
!     write(*,*) 'Cannot open file: ', 'cls_rmsd.txt'
!     write(*,*) 'In program: cluster_densities.f90'
!     stop
! endif
! do i=1,num_clusters
!     write(16, "(I6, I6, F8.4)", rec=i) i, nint(closest_clust(i,1)), closest_clust(i,2)
! end do
! close(16)

! -------------------------------------------------------------------------------------
! Roughly Align, Plot, and Write Spider Stacks to File for 7 "Best" Clusters
! -------------------------------------------------------------------------------------

! Try to use silhouette width to find best clusters.
sil_cls = sil_width_cls( cls, cls_dist_table, nptcls, num_clusters, rmsd, 5 )
 best_cls = maxloc(sil_cls,1)
write(*,*) sil_cls(best_cls)
sil_cls_heap = new_heapsort(num_clusters)
do i=1,num_clusters
    call set_heapsort(sil_cls_heap, i, -sil_cls(i), i) ! These values are negative because the heapsort sorts the max values first. 
end do
call sort_heapsort(sil_cls_heap)
! Change the numbers in the allocate command below to get fewer or more clusters.
allocate(top_sil_cls(7), top_sil(7), stat=alloc_stat)
call alloc_err('In program: find_best_cls', alloc_stat)
! top_sil holds the silhouette widths for the top clusters
! top_sil_cls holds the cluster number corresponding to the silhouette widths in top_sil
do i=1,size(top_sil_cls)
    call get_heapsort( sil_cls_heap, i, top_sil(i), top_sil_cls(i) )
end do
top_sil = -top_sil

! Plot the "best" avg cluster imgs, output to spider stack files
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
        call alloc_err('In program: find_best_cls', alloc_stat)
        n = 1
        write(*,'(A, I6)', advance='no') 'Cluster', current_cls, 'Members:'
        do k=1,nptcls
            if (cls(k) == current_cls) then
                write(*,'(I6)',advance='no') k
                call read_imgspi(stack, stk, k, img, stkconv) 
                imgs(n) = img
                write(chari,'(I10)') i
                chari = adjustl(chari)
                call write_stk_hed( stack_out, 'cls'//trim(chari)//'.spi' ) 
                call write_imgspi( stack_out, 'cls'//trim(chari)//'.spi', n, img )
                n = n + 1
            end if
        end do
        write(*,*) ''
        call align_cls_imgspi( imgs, size(imgs), cls, current_cls, rmsd_pwtab, dens_maps, nptcls, box )
        deallocate(imgs)
    end if
end do

end program find_best_cls