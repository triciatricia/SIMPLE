! -------------------------------------------------------------------------------------
! The purpose is to test functions and subroutines that I'm working on in dens_map_mod.
! *Note: running this will alter or create the file dens_maps.txt.*
! List of things not tested here: write_dist, write_mass_coord, pearsn_dens_map
! *** center_dens_map *** <- to do.
! -------------------------------------------------------------------------------------
program dens_map_mod_test

use simple_dens_map
use tester_mod
implicit none

type(dens_map)                  :: densmaps(10)
integer                         :: ia, ib, ic, iarra(4,2), iarrb(1,2), iarrc(2), ix(4)
real                            :: ra, rb, rc, pie, rarra(4,2), rarrb(4,2), rarrc(2)
real, allocatable               :: rarr(:)
logical                         :: result(1000)
type(dens_map)                  :: dmap_array(4)

! result stores the results of the tests. .true. = pass. .false. = fail. 
result = .true.

pie = acos(-1.)

! set_dens_map & new_dens_map (also tested below)
densmaps(1) = new_dens_map()
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71, 89, 91, 141/), (/105, 53, 141, 126/), 4)
densmaps(2) = new_dens_map((/106, 217, 94, 12/), (/62, 95, 134, 133/), (/87, 55, 106, 143/), 4)
do ia = 3, size(densmaps)
    densmaps(ia) = new_dens_map()
end do

! -------------------------------------------------------------------------------------
! distances
! (1-9)
! -------------------------------------------------------------------------------------
allocate(rarr(6))
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71, 89, 91, 141/), (/105, 53, 141, 126/), 4)
rarr = (/sqrt((126.-53.)**2.+(141.-89.)**2.), sqrt((141.-53.)**2.+(91.-89.)**2.), sqrt((126.-105.)**2.+(141.-71.)**2.), sqrt((105.-53.)**2.+(71.-89.)**2.), sqrt((126.-141.)**2.+(141.-91.)**2.), sqrt((105.-141.)**2.+(71.-91.)**2.)/)
result(1) = fuzzy_compare(rarr, dist_dens_map(densmaps(1)), 6, 0.1)
densmaps(1) = new_dens_map((/134, 154, 160/), (/71, 89, 91/), (/105, 53, 141/), 3)
rarr = (/sqrt((141.-53.)**2.+(91.-89.)**2.), sqrt((105.-53.)**2.+(71.-89.)**2.),  sqrt((105.-141.)**2.+(71.-91.)**2.), 0., 0., 0./)
result(2) = fuzzy_compare(rarr, dist_dens_map(densmaps(1)), 6, 0.1)
deallocate(rarr)

! -------------------------------------------------------------------------------------
! masses (10)
! -------------------------------------------------------------------------------------
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71, 89, 91, 141/), (/105, 53, 141, 126/), 4)
result(10) = fuzzy_compare(mass_dens_map(densmaps(1)), (/134, 154, 160, 160/), 4, 0)
call set_dens_map(densmaps(1), (/134, 154, 160/), (/71, 89, 91/), (/105, 53, 141/), 3)
result(11) = fuzzy_compare(mass_dens_map(densmaps(1)), (/134, 154, 160, 0/), 4, 0)

! -------------------------------------------------------------------------------------
! coord (20:27)
! -------------------------------------------------------------------------------------
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71, 89, 91, 141/), (/105, 53, 141, 126/), 4)
rarra = coord_dens_map(densmaps(1))
result(20) = fuzzy_compare(rarra(1,:), (/71., 105./), 2, 0.)
result(21) = fuzzy_compare(rarra(2,:), (/89., 53./), 2, 0.)
result(23) = fuzzy_compare(rarra(3,:), (/91., 141./), 2, 0.)
result(24) = fuzzy_compare(rarra(4,:), (/141., 126./), 2, 0.)

call set_dens_map(densmaps(1), (/134, 154, 160/), (/71, 89, 91/), (/105, 53, 141/), 3)
rarra = coord_dens_map(densmaps(1))
result(25) = fuzzy_compare(rarra(4,:), (/0., 0./), 2, 0.)

call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71.1, 89.2, 91.3, 141.4/), (/105., 53.3, 141., 126./), 4)
rarra = coord_dens_map(densmaps(1))
result(26) = fuzzy_compare(rarra(:,1), (/71.1, 89.2, 91.3, 141.4/), 4, 0.)
result(27) = fuzzy_compare(rarra(:,2), (/105., 53.3, 141., 126./), 4, 0.)

! -------------------------------------------------------------------------------------
! n_dens_map (28:29)
! -------------------------------------------------------------------------------------
call set_dens_map(densmaps(1), (/134, 154, 160/), (/71, 89, 91/), (/105, 53, 141/), 3)
result(28) = fuzzy_compare(n_dens_map(densmaps(1)), 3, 0)
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71, 89, 91, 141/), (/105, 53, 141, 126/), 4)
result(29) = fuzzy_compare(n_dens_map(densmaps(1)), 4, 0)

! -------------------------------------------------------------------------------------
! euclid_dens_map(dmap1, dmap2) (30)
! -------------------------------------------------------------------------------------
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71, 89, 91, 141/), (/105, 53, 141, 126/), 4)
call set_dens_map(densmaps(2), (/106, 217, 94, 12/), (/62, 95, 134, 133/), (/87, 55, 106, 143/), 4)
result(30) = euclid_dens_map(densmaps(1), densmaps(2)) == euclid(dist_dens_map(densmaps(1)), dist_dens_map(densmaps(2)))

! -------------------------------------------------------------------------------------
! order_array interface: order_array_r(arr, length), order_array_i(arr, length)
! (40)
! -------------------------------------------------------------------------------------
result(40) = fuzzy_compare(order_array((/8, 6, 5, 7/), 4), (/1, 4, 2, 3/), 4, 0)
result(41) = fuzzy_compare(order_array((/8, 6, 6, 7/), 4), (/1, 4, 2, 3/), 4, 0)
result(42) = fuzzy_compare(order_array((/8., 6., 5., 7./), 4), (/1, 4, 2, 3/), 4, 0)
result(43) = fuzzy_compare(order_array((/1/), 1), (/1/), 1, 0)
result(44) = fuzzy_compare(order_array((/-8., -6., -5., -7./), 4), (/3, 2, 4, 1/), 4, 0)
result(45) = fuzzy_compare(order_array((/-8, -6, -5, -7/), 4), (/3, 2, 4, 1/), 4, 0)

! -------------------------------------------------------------------------------------
! cenmass_dens_map
! (50)
! -------------------------------------------------------------------------------------
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71.5, 89., 91.3, 141./), (/105., 53., 141., 126.1/), 4)
ra = (134.*71.5+154.*89.+160.*91.3+160.*141.)/(134.+154.+160.+160.)
rb = (134.*105.+154.*53.+160.*141.+160.*126.1)/(134.+154.+160.+160.)
result(50) = fuzzy_compare(cenmass_dens_map(densmaps(1)), (/ ra, rb /), 2, 0.)

! -------------------------------------------------------------------------------------
! shift_dens_map
! (60)
! -------------------------------------------------------------------------------------
call shift_dens_map(densmaps(1), - (ra - 100.), - (rb - 100.))
rarrc = cenmass_dens_map(densmaps(2))
call shift_dens_map(densmaps(2), -(rarrc(1) - 100), -(rarrc(2) - 100))
result(60) = fuzzy_compare(cenmass_dens_map(densmaps(1)), (/ 100., 100. /), 2, 0.)
result(61) = fuzzy_compare(cenmass_dens_map(densmaps(2)), (/ 100., 100. /), 2, 0.)

! angle_rotation ! not being used, so don't care about this
! (70)
! call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/150, 100, 100, 100/), (/100, 100, 100, 100/), 4)
! call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/140, 100, 100, 100/), (/130, 100, 100, 100/), 4)
! ra = angle_rotation(densmaps(3), densmaps(4), 200)
! result(70) = ra == -atan2(3.,4.)
! ra = angle_rotation(densmaps(4), densmaps(3), 200)
! result(71) = ra == atan2(3.,4.)
! 
! call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/150, 100, 100, 100/), (/100, 100, 100, 100/), 4)
! call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/140, 100, 100, 100/), (/70, 100, 100, 100/), 4)
! ra = angle_rotation(densmaps(3), densmaps(4), 200)
! result(72) = ra == atan2(3.,4.)
! ra = angle_rotation(densmaps(4), densmaps(3), 200)
! result(73) = ra == -atan2(3.,4.)
! 
! call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/50, 100, 100, 100/), (/100, 100, 100, 100/), 4)
! call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/60, 100, 100, 100/), (/130, 100, 100, 100/), 4)
! ra = angle_rotation(densmaps(3), densmaps(4), 200)
! result(74) = ra < atan2(3.,4.) + .1 .and. ra > atan2(3.,4.) - .1
! ra = angle_rotation(densmaps(4), densmaps(3), 200)
! result(75) = ra < -atan2(3.,4.) + .1 .and. ra > -atan2(3.,4.) - .1
! 
! call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/50, 100, 100, 100/), (/100, 100, 100, 100/), 4)
! call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/60, 100, 100, 100/), (/70, 100, 100, 100/), 4)
! ra = angle_rotation(densmaps(3), densmaps(4), 200)
! result(76) = ra - 2.*pie < -atan2(3.,4.) + .1 .and. ra - 2.*pie > -atan2(3.,4.) - .1
! ra = angle_rotation(densmaps(4), densmaps(3), 200)
! result(77) = ra + 2.*pie < atan2(3.,4.) + .1 .and. ra + 2.*pie > atan2(3.,4.) - .1

! -------------------------------------------------------------------------------------
! closest_pts 
! (80)
! -------------------------------------------------------------------------------------
! for each point in dmap1, finds the closest point in dmap2. Returns a vector of length 4; closest_pts(i) is the index of the point in dmap2 that is closest to point i of dmap1.
! later: test if only 3 densities
call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/10, 30, 40, 20/), (/10, 30, 40, 20/), 4)
call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/10, 40, 30, 20/), (/10, 40, 30, 20/), 4)
result(80) = fuzzy_compare(closest_pts(densmaps(3), densmaps(4)), (/1, 3, 2, 4/), 4, 0)
call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/10, 40, 40, 20/), (/10, 40, 40, 20/), 4)
result(81) = fuzzy_compare(closest_pts(densmaps(3), densmaps(4)), (/1, 2, 2, 4/), 4, 0)
call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/50.1, 10.3, 120.8, 100.4/), (/100.3, 100.1, 20.2, 130.8/), 4)
call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/60.3, 110.9, 90.34, 20.451/), (/90.25, 10.356, 120.71, 110.01/), 4)
result(82) = fuzzy_compare(closest_pts(densmaps(3), densmaps(4)), (/1, 4, 2, 3/), 4, 0)
result(83) = fuzzy_compare(closest_pts(densmaps(4), densmaps(3)), (/1, 3, 4, 2/), 4, 0)

! -------------------------------------------------------------------------------------
! rotate_dens_map(dmap, angle)
! (90:109)
! -------------------------------------------------------------------------------------
call set_dens_map(densmaps(7), (/100, 100, 100, 100/), (/30., 100., 130., 140./), (/40., 150., 180., 80./), 4)

densmaps(8) = densmaps(7)
call rotate_dens_map(densmaps(8), 0., 200)
rarra = coord_dens_map(densmaps(8))
result(90) = fuzzy_compare(rarra(:,1), (/30., 100., 130., 140./), 4, 0.0)
result(91) = fuzzy_compare(rarra(:,2), (/40., 150., 180., 80./), 4, 0.0)

densmaps(8) = densmaps(7)
call rotate_dens_map(densmaps(8), 0.6, 200)
rarra = coord_dens_map(densmaps(8))
result(92) = fuzzy_compare(rarra(:,1), (/76.475,72.1375,79.958,144.676/), 4, 0.01)
result(93) = fuzzy_compare(rarra(:,2), (/10.76,141.07,182.77,105.884/), 4, 0.01)

densmaps(8) = densmaps(7)
call rotate_dens_map(densmaps(8), 4.4, 200)
rarra = coord_dens_map(densmaps(8))
result(94) = fuzzy_compare(rarra(:,1), (/64.595,147.758,167.086,68.85/), 4, 0.01)
result(95) = fuzzy_compare(rarra(:,2), (/186.182,85.763,47.995,69.212/), 4, 0.01)

densmaps(8) = densmaps(7)
call rotate_dens_map(densmaps(8), 46./180.*pie, 200)
rarra = coord_dens_map(densmaps(8))
result(96) = fuzzy_compare(rarra(:,1), (/95.047,64.545,63.805,142.685/), 4, 0.01)
result(97) = fuzzy_compare(rarra(:,2), (/7.760,134.526,176.946,114.673/), 4, 0.01)
call rotate_dens_map(densmaps(8), -46./180.*pie, 200)
rarra = coord_dens_map(densmaps(8))
result(98) = fuzzy_compare(rarra(:,1), (/30., 100., 130., 140./), 4, 0.01) 
result(99) = fuzzy_compare(rarra(:,2), (/40., 150., 180., 80./), 4, 0.01)
call rotate_dens_map(densmaps(8), 360./180.*pie, 200)
rarra = coord_dens_map(densmaps(8))
result(100) = fuzzy_compare(rarra(:,1), (/30., 100., 130., 140./), 4, 0.01) 
result(101) = fuzzy_compare(rarra(:,2), (/40., 150., 180., 80./), 4, 0.01)

!     subroutine center_dens_map(dmap, box)
!     ! center a dens_map based on center of mass
!         type(dens_map), intent(inout)   :: dmap
!         integer, intent(in)             :: box

! -------------------------------------------------------------------------------------
! best_rmsd_dmap
! (110)
! -------------------------------------------------------------------------------------
call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/10, 50, 120, 100/), (/100, 100, 20, 130/), 4)
call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/10, 50, 120, 100/), (/100, 100, 20, 130/), 4)
ra = best_rmsd_dmap(densmaps(3), densmaps(4), 200)
result(110) = fuzzy_compare(ra, 0., .1)
call set_dens_map(densmaps(3), (/134, 154, 160, 160/), (/10, 50, 120, 100/), (/100, 100, 20, 130/), 4)
call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/10, 50, 100, 120/), (/100, 100, 130, 20/), 4)
ra = best_rmsd_dmap(densmaps(3), densmaps(4), 200)
result(111) = fuzzy_compare(ra, 0., .1)
call set_dens_map(densmaps(3), (/100, 100, 100, 100/), (/50, -50, 50, -50/), (/50, 50, -50, -50/), 4)
call set_dens_map(densmaps(4), (/100, 100, 100, 100/), (/-60, -60, 60, 60/), (/-60, 60, -60, 60/), 4)
ra = best_rmsd_dmap(densmaps(3), densmaps(4), 100)
result(112) = fuzzy_compare(ra, 10.*sqrt(2.), .1)
! do some more tests here. 

! -------------------------------------------------------------------------------------
! flush_dens_maps, get_dens_maps
! (120:139)
! -------------------------------------------------------------------------------------
! flush_dens_maps(dmap_arr, arr_size)
! takes an array of dens_map and stores the info in the file dens_maps.txt.
! get_dens_maps(dmap_arr, arr_size)
! Gets the file dens_maps.txt and moves the info to an array of dens_map.
call set_dens_map(densmaps(1), (/134, 154, 160, 160/), (/71.5, 89., 91.3, 141./), (/105., 53., 141., 126.1/), 4)
call set_dens_map(densmaps(2), (/134, 154/), (/71.570, 89.03/), (/105.46, 53.773221/), 2)
call set_dens_map(densmaps(3), (/134, 154, 160/), (/71.5211, 89.235, 191.32093/), (/105.12, 53.33, 141.5555/), 3)
call set_dens_map(densmaps(4), (/134, 154, 160, 160/), (/71, 89, 91, 141/), (/105, 53, 141, 126/), 4)
call flush_dens_maps(densmaps(1:4), 4)
call get_dens_maps(dmap_array, size(dmap_array))
do ia=1,4
    rarra = coord_dens_map(dmap_array(ia))
    rarrb = coord_dens_map(densmaps(ia))
    result(119+ia) = fuzzy_compare(rarra(:,1),rarrb(:,1), 4, 0.0001)
    result(123+ia) = fuzzy_compare(rarra(:,2),rarrb(:,2), 4, 0.0001)
    result(127+ia) = fuzzy_compare(mass_dens_map(dmap_array(ia)),mass_dens_map(densmaps(ia)), 4, 0)
    result(131+ia) = fuzzy_compare(n_dens_map(dmap_array(ia)), n_dens_map(densmaps(ia)), 0)
end do
write(*,*) 'The file dens_maps.txt has been altered.'

! -------------------------------------------------------------------------------------
! dist_btwn_dens_maps
! (140:149)
! -------------------------------------------------------------------------------------
! function dist_btwn_dens_maps(dmap1, dmap2)
! Euclidean distance between two dens_maps. 
call set_dens_map(densmaps(1), (/1, 1, 1, 1/), (/1, 2, 3, 4/), (/1, 2, 3, 4/), 4)
call set_dens_map(densmaps(2), (/1, 1, 1, 1/), (/4, 1, 3, 2/), (/4, 1, 3, 2/), 4)
result(140) = fuzzy_compare(dist_btwn_dens_maps(densmaps(1),densmaps(2)), 0., 0.)
call set_dens_map(densmaps(1), (/1, 1, 1, 1/), (/1, 2, 3, 14/), (/1, 2, 3, 14/), 4)
call set_dens_map(densmaps(2), (/1, 1, 1, 1/), (/17, 0, 3, 2/), (/18, 1, 3, 2/), 4)
result(141) = fuzzy_compare(dist_btwn_dens_maps(densmaps(1),densmaps(2)), 6., 0.)
call set_dens_map(densmaps(1), (/1, 1, 1, 1/), (/1, 2, 3, 4/), (/1, 2, 3, 4/), 4)
call set_dens_map(densmaps(2), (/1, 1, 1, 1/), (/7, 0, 3, 2/), (/8, 1, 3, 2/), 4)
result(142) = fuzzy_compare(dist_btwn_dens_maps(densmaps(1),densmaps(2)), 6., 0.)

! -------------------------------------------------------------------------------------
! Report results of tests
! -------------------------------------------------------------------------------------
if (.not. all(result)) then
    if (count(result==.false.) > 3) then
        write(*,*) 'You are illiterate!', count(result==.false.)
    else 
        write(*,*) 'You fail!', count(result==.false.), 'times.'
    end if
    do ia = 1,size(result)
        if (.not. (result(ia))) write(*,*) ia
    end do
else 
    write(*,*) 'You win!'
end if


end program dens_map_mod_test