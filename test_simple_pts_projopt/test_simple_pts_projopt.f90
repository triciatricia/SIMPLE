! -------------------------------------------------------------------------------------
! The purpose is to test functions and subroutines in simple_pts_projopt. 
! -------------------------------------------------------------------------------------
program test_simple_pts
use simple_pts
use simple_pts_projopt
use simple_params
use tester_mod
implicit none

logical                         :: result(1000)
type(pts)			:: pts_arr(2), pts3d, pts3D_arr(6)
real				:: coords42(4,2), coords32(3,2), coords43(4,3), cost
real				:: solution(6), angle_arr(5,6)
type(pts)			:: em_pts_arr(15), em_pts3D_arr(6)
real				:: em_angle_arr(5,45), three(3)
integer				:: i

! Initialize
result = .TRUE.
pwfile='pwfile.bin'

! -------------------------------------------------------------------------------------
! init_propjopt, cost_projopt
! (1:9)
! -------------------------------------------------------------------------------------
coords42(:,1) = (/65.75,123.75,26.75,106.75/)
coords42(:,2) = (/75.,54.,108.,33./)
coords32(:,1) = (/74.4167,132.4167,35.4167/)
coords32(:,2) = (/63.5,42.5,96.5/)
pts_arr(2) = new_pts(4,2,coords42)
pts_arr(1) = new_pts(3,2,coords32)
coords43(:,1) = (/20.25,-45.75,-47.75,73.25/)
coords43(:,2) = (/-29.5,-2.5,41.5,-9.5/)
coords43(:,3) = (/0.,0.,0.,0./)
pts3d = new_pts(4,3,coords43)
call rotate_pts(pts3d, -30., -20., -25.)
call init_projopt(pts_arr, size(pts_arr), pts3d)
cost = cost_projopt((/25.,20.,30.,25.,20.,30./),6)
result(1) = fuzzy_compare(cost, 25.5682, 0.001)
write(*,*) cost
call kill_pts(pts_arr, 2)
call kill_pts(pts3d)

! -------------------------------------------------------------------------------------
! de_projopt
! em_projopt(proj_arr_in, n_proj, npts, iter, angle_arr, pts3D_arr, maxdist, clashdist, neigh, GENMAX)
! -------------------------------------------------------------------------------------
coords42(:,1) = (/65.75,123.75,26.75,106.75/)
coords42(:,2) = (/75.,54.,108.,33./)
coords32(:,1) = (/74.4167,132.4167,35.4167/)
coords32(:,2) = (/63.5,42.5,96.5/)
pts_arr(2) = new_pts(4,2,coords42)
pts_arr(1) = new_pts(3,2,coords32)
coords43(:,1) = (/20.25,-45.75,-47.75,73.25/)
coords43(:,2) = (/-29.5,-2.5,41.5,-9.5/)
coords43(:,3) = (/0.,0.,0.,0./)
pts3d = new_pts(4,3,coords43)
call de_projopt(pts_arr, 2, pts3d, 0.02, 200, solution, cost)
write(*,*) 'Solution:'
write(*,*) solution
write(*,*) 'Final cost: ', cost

call rotate_pts(pts3d, -30., -20., -25.)
call de_projopt(pts_arr, 2, pts3d, 0.02, 200, solution, cost)
write(*,*) 'Solution:'
write(*,*) solution
write(*,*) 'Final cost: ', cost

call rotate_pts(pts3d, -30., 0., 0.)
call de_projopt(pts_arr, 2, pts3d, 0.02, 200, solution, cost)
write(*,*) 'Solution:'
write(*,*) solution
write(*,*) 'Final cost: ', cost

! call em_projopt(pts_arr, 2, 4, 5, angle_arr, pts3D_arr)
! write(*,*) 'Solution:'
! write(*,*) angle_arr(5,:)
! write(*,*) get_coords_pts(pts3D_arr(6))

call kill_pts(pts_arr, 2)
call kill_pts(pts3d)

coords43(:,1) = (/-20.,0.,35.,25./)
coords43(:,2) = (/-30.,-10.,-10.,40./)
coords43(:,3) = (/-4.,40.,20.,30./)
pts_arr(1) = new_pts(4,3,coords43)
do i=1,15
    call RANDOM_NUMBER(three)
    em_pts_arr(i)=proj2d_pts(pts_arr(1), 360.*three(1), 180.*three(2), 360.*three(3))
end do
call em_projopt(em_pts_arr, 15, 4, 5, em_angle_arr, em_pts3D_arr)
write(*,*) 'Solution:'
write(*,*) em_angle_arr(5,:)
write(*,*) get_coords_pts(em_pts3D_arr(6))
call kill_pts(pts_arr,2)

! -------------------------------------------------------------------------------------
! Report results of tests
! -------------------------------------------------------------------------------------
call report(result, size(result))

end program test_simple_pts