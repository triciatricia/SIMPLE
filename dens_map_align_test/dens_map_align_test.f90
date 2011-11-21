! -------------------------------------------------------------------------------------
! The purpose is to test functions and subroutines in dens_map_align.
! List of things not tested here: 
! -------------------------------------------------------------------------------------
program dens_map_align_test
use simple_dens_map
use simple_dens_map_align
use tester_mod
implicit none

logical                         :: result(1000)
type(dens_map)                  :: dmaps(4)
integer                         :: bx

! Initialize
result = .TRUE.

bx = 24

dmaps(1) = new_dens_map((/1, 1, 1, 1/), (/4,8,16,18/), (/10,4,14,3/), 4)
dmaps(2) = new_dens_map((/1, 1, 1, 1/), (/4,8,16,18/), (/10,4,14,3/), 4)
dmaps(3) = new_dens_map((/1, 1, 1, 1/), (/4,6,15,17/), (/7, 4, 7, 14/), 4)
dmaps(4) = new_dens_map((/1, 1, 1, 1/), (/4,6,15,17/), (/7, 4, 7, 14/), 4)


! -------------------------------------------------------------------------------------
! init_dmap_align
! <tested indirectly>
! -------------------------------------------------------------------------------------
! subroutine init_dmap_align(dmap_arr_in, num_dmap_in, box_in)
! ! Initialize values for optimization alignment. 
!     integer, intent(in)             :: num_dmap_in, box_in
!     type(dens_map), intent(in)      :: dmap_arr_in(num_dmap_in)

! -------------------------------------------------------------------------------------
! cost_dmap
! (10:19)
! -------------------------------------------------------------------------------------
! function cost_dmap(param,param_size)
! ! Cost for aligning dmap. Parameters in param (aka: vec). Size of the vector param = param_size (aka: D). 
!     real                            :: cost_dmap
!     integer, intent(in)             :: param_size
!     real, intent(in)                :: param(param_size)

! cost of two identical dens_maps. 
call init_dmap_align((/dmaps(1:2)/), 2, bx)
result(10) = fuzzy_compare(cost_dmap((/0./),1), 0., 0.)

! rotate one dens_map
call center_dens_map(dmaps(1), bx)
call rotate_dens_map(dmaps(1), -.6, bx)
call init_dmap_align(dmaps(1:2), 2, bx)
result(11) = fuzzy_compare(cost_dmap((/0.6/),1), 0., 0.01)


dmaps(1) = new_dens_map((/1, 1, 1, 1/), (/2,4,16,18/), (/4,7,7,10/), 4)
dmaps(2) = new_dens_map((/1, 1, 1, 1/), (/2,4,16,18/), (/4,7,7,10/), 4)
dmaps(3) = new_dens_map((/1, 1, 1, 1/), (/3,4,15,18/), (/4,10,11,3/), 4)
dmaps(4) = new_dens_map((/1, 1, 1, 1/), (/3,4,15,18/), (/4,10,11,3/), 4)

! test distance measure
call init_dmap_align(dmaps(2:3), 2, bx)
result(12) = fuzzy_compare(cost_dmap((/0./),1), 23.269, 0.01)

! rotations again
call center_dens_map(dmaps(1), bx)
call rotate_dens_map(dmaps(1), -.6, bx)
call center_dens_map(dmaps(3), bx)
call rotate_dens_map(dmaps(3), -.4, bx)
 call init_dmap_align(dmaps, size(dmaps), bx)
 result(13) = fuzzy_compare(cost_dmap((/0.6,0.,0.4/),3), 93.075, 0.01)
! write(*,*) cost_dmap((/0.6,0.,0.4/),3)

! Test 3-density dens_maps. 
! identical
dmaps(1) = new_dens_map((/1, 1, 1/), (/2,4,16/), (/4,7,7/), 3)
dmaps(2) = new_dens_map((/1, 1, 1/), (/2,4,16/), (/4,7,7/), 3)
call init_dmap_align(dmaps(1:2), 2, bx)
result(14) = fuzzy_compare(cost_dmap((/0./),1), 0., 0.)

! rotate
call center_dens_map(dmaps(1), bx)
call rotate_dens_map(dmaps(1), -.35, bx)
call init_dmap_align(dmaps(1:2), 2, bx)
result(15) = fuzzy_compare(cost_dmap((/0.35/),1), 0., 0.001)

! distance measure
dmaps(1) = new_dens_map((/1, 1, 1/), (/2,5,8/), (/3,5,7/), 3)
dmaps(2) = new_dens_map((/1, 1, 1/), (/1,5,9/), (/2,5,8/), 3)
call init_dmap_align(dmaps(1:2), 2, bx)
result(16) = fuzzy_compare(cost_dmap((/0./),1), 5.6568, 0.001)

! -------------------------------------------------------------------------------------
! Report results of tests
! -------------------------------------------------------------------------------------
call report(result, size(result))

end program dens_map_align_test
