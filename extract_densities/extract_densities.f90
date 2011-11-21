! -------------------------------------------------------------------------------------
! extract_densities takes a stack of binary imgspi's (spider images), identifies the
! position of the centers and masses of a maximum of 4 densities per image, and creates
! a dens_map object with this information. Also, it calculates the rmsd's among all
! images and finds the closest match for each image. 
! 
! Outputs (and/or replaces) these files: 
!   - dens_maps.txt
!     A direct access text file containing the four masses, four x-coordinates, four y-coordinates
!     and number of densities for each image. If an image has fewer than 4 densities, the
!     extra values will be 0. (Format: "(4I5, 8F9.4, I2)")
!   - rmsd.txt
!     A direct access text file containing the matches of one image and the closest image
!     to it (based on RMSD between densities) and the RMSD between them. 
!     (Format: "(I6, I6, F8.4)" = (Image#, ClosestImage#, RMSD))
!   - rmsd_table.txt
!     A direct access text file containing the RMSD between each image with each other
!     image. (Format: "(F7.2)")
!   - rmsd_pwtab.bin
!     An unformatted direct access file for the pair weight table containing weights
!     based on RMSDs between images. (See the module simple_pair_wtab for more info.)
! 
! Input:
!   - stk = stack of binarized spider images (you can use the program binarize on them
!     first)
!   - box = length of an edge of the image in pixels
!   - nptcls = number of images in the stack
!   - smpd = sampling distance in Angstroms per pixel
! -------------------------------------------------------------------------------------

program extract_densities

use simple_stkspi
use simple_imgspi
use simple_math
use simple_cmdline
use simple_params
use simple_dens_map
use simple_pair_wtab
use simple_sll_list
implicit none
save
type(stkspi)                            :: stack, stack_out
type(imgspi)                            :: img, img2
integer                                 :: i, j, k, n, num_clusters, alloc_stat, num_imgs
type(dens_map)                          :: img_dens_map
type(dens_map), allocatable             :: dens_maps(:)
type(pair_wtab)                         :: dens_pair_wtab, rmsd_pwtab
real, allocatable                       :: r(:,:), rmsd(:,:), closest_img(:,:), rmsd_row(:)
type(sll_list), allocatable             :: hac_sll(:)
type(imgspi), dimension(:), allocatable :: imgs
real                                    :: max_r, max_rmsd, rmsd_tmp
integer                                 :: current_cls, center(2), center_mass(2), file_stat
integer, allocatable                    :: cls_no_refinement(:)
logical                                 :: halt
integer                                 :: rlength
character(len=256)                      :: stkconv

if( command_argument_count() < 4 )then
    write(*,*) './extract_densities stk=inputstk.spi box=200 nptcls=10329 smpd=1.85 [debug=<yes|no>]'
    stop
endif

! parse command line args
call parse_cmdline
call make_params

! allocate
allocate(dens_maps(nptcls), hac_sll(nptcls), cls(nptcls), r(nptcls,nptcls), rmsd_row(nptcls), stat=alloc_stat)
call alloc_err('In program: extract_densities', alloc_stat)

! make stacks
stack = new_stkspi( name=stk )
stack_out = new_stkspi()

! determine how to convert the stack
call find_stkconv( stack, stk, stkconv )

! make image
img = new_imgspi()

! for each image, identify densities and store information in dens_maps
do i=1,nptcls
    call read_imgspi( stack, stk, i, img, stkconv )
    call identify_densities_imgspi( img, box, 4, 4, img_dens_map )
    dens_maps(i) = img_dens_map
end do
! output dens_maps to the file dens_maps.txt
call flush_dens_maps(dens_maps, size(dens_maps))
write(*,'(A)') '>>> DONE IDENTIFYING DENSITIES'

! calculate best RMSD for rotations among all data
allocate(rmsd(nptcls,nptcls), stat=alloc_stat)
call alloc_err('In program: extract_densities', alloc_stat)
rmsd_pwtab = new_pair_wtab(nptcls)
do i=1,nptcls-1
    if( i == 1 .or. mod(i,500) == 0 ) then
                write(*,"(1X,A)", advance="no") 'Calculating RMSDs:'
                write(*,"(1X,I7)") i
    end if
    do j=i+1,nptcls
        rmsd_tmp = best_rmsd_dmap(dens_maps(i), dens_maps(j), box)
        rmsd(j,i) = rmsd_tmp
        rmsd(i,j) = rmsd_tmp
    end do
end do
max_rmsd = maxval(rmsd)
do i=1,nptcls-1
    do j=i+1,nptcls
        call set_pair_w( rmsd_pwtab, i, j, 1-2*rmsd(i,j)/max_rmsd )
    end do
end do
call flush_pair_wtab(rmsd_pwtab, 'rmsd_pwtab.bin')
call flush_pair_wtab( rmsd_pwtab, 'pw_copy_from_hac_cls.bin' )
write(*,'(A)') '>>> DONE CALCULATING RMSD'

! Output rmsd to the file rmsd_table.txt before modifying it
open(unit=15, file='rmsd_table.txt', status='replace', iostat=file_stat,&
access='direct', action='write', form='formatted', recl=7 )
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: rmsd_table.txt'
    write(*,*) 'In program: extract_densities.f90'
    stop
endif
n = 1
do i=1,nptcls-1
    do j=i+1,nptcls
        write(15,'(F7.2)',rec=(n)) rmsd(i,j)
        n = n + 1
    end do
end do
close(15)

! Find closest images; (roughly) 
allocate(closest_img(nptcls,2), stat=alloc_stat)
call alloc_err('In program: extract_densities', alloc_stat)
do i=1,nptcls
    rmsd(i,i) = box*sqrt(2.)+1. !largest value possible so it's ignored
end do
 closest_img = 0
! The closest image to i is image j. 
do i=1,nptcls
    j = minloc(rmsd(i,:),1)
    closest_img(i,1) = j
    closest_img(i,2) = rmsd(i,j)
end do

! Convert RMSD from pixels to Angstroms. 
 closest_img(:,2) = closest_img(:,2) * smpd

! Output RMSD to file. 
open(unit=13, file='rmsd.txt', status='replace', iostat=file_stat,&
access='direct', form='formatted', recl=20, action='write')
if( file_stat /= 0 )then ! cannot open file
    write(*,*) 'Cannot open file: ', 'rmsd.txt'
    write(*,*) 'In program: extract_densities.f90'
    stop
endif
do i=1,nptcls
    write(13, "(I6, I6, F8.4)", rec=i) i, nint(closest_img(i,1)), closest_img(i,2)
end do
close(13)

end program extract_densities