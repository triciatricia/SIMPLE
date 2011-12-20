! -------------------------------------------------------------------------------------
! The purpose is to test functions and subroutines in simple_pts.
! -------------------------------------------------------------------------------------
program test_simple_pts
use simple_pts
use simple_math
use simple_sll_list
use tester_mod
use simple_params
implicit none

logical                         :: result(1000), showplot
type(pts)			:: pts_arr(4)
real				:: coords43(4,3), coords42(4,2), coords83(8,3)
real				:: coords123(12,3), coords11(1,1), coords23(2,3)
real				:: coords23b(2,3), rmat(3,3), coords42b(4,2)
real				:: coords32(3,2),  coords33(3,3), coords22(2,2)
integer				:: i, icoords42(4,2)
type(sll_list)			:: testlist(24)
real				:: three(3)

! Initialize
result = .TRUE.
showplot = .FALSE.
pwfile='pwfile.bin'

! -------------------------------------------------------------------------------------
! new_pts, kill_pts, get_coords_pts, get_npts_pts, get_dim_pts
! (1:9)
! -------------------------------------------------------------------------------------
write(*,*) 'A'
! Make new empty pts
pts_arr(1) = new_pts(4,3)
coords43 = 0.
result(1) = fuzzy_compare(coords43, get_coords_pts(pts_arr(1)), 4, 3, 0.)
! Kill pts
call kill_pts(pts_arr(1))
! New non-empty pts
coords42(:,1) = (/1.,2.,3.,4./)
coords42(:,2) = (/4.,3.,2.,1./)
pts_arr(1) = new_pts(4,2,coords42)
result(2) = fuzzy_compare(coords42, get_coords_pts(pts_arr(1)), 4, 2, 0.)
result(3) = fuzzy_compare(4, get_npts_pts(pts_arr(1)), 0)
result(4) = fuzzy_compare(2, get_dim_pts(pts_arr(1)), 0)
call kill_pts(pts_arr(1))

! -------------------------------------------------------------------------------------
! combine_pts
! (10:19)
! -------------------------------------------------------------------------------------
write(*,*) 'B'
coords43(:,1) = (/1.,2.,3.,4./)
coords43(:,2) = (/3.,3.,3.,3./)
coords43(:,3) = (/-1.,-2.,2.,1./)
coords83(:,1) = (/1.,2.,3.,4.,0.,1.,2.,3./)
coords83(:,2) = (/3.,3.,3.,3.,2.,2.,2.,2./)
coords83(:,3) = (/-1.,-2.,2.,1.,-2.,-3.,1.,0./)
pts_arr(1) = new_pts(4,3,coords43)
pts_arr(2) = new_pts(4,3,coords43-1.)
pts_arr(3) = combine_pts(pts_arr(1:2), 2)
result(10) = fuzzy_compare(8, get_npts_pts(pts_arr(3)), 0)
result(11) = fuzzy_compare(3, get_dim_pts(pts_arr(3)), 0)
result(12) = fuzzy_compare(coords83, get_coords_pts(pts_arr(3)), 8, 3, 0.)
! Adding different #s of pts. 
coords123(:,1) = (/0.,1.,2.,3.,1.,2.,3.,4.,0.,1.,2.,3./)
coords123(:,2) = (/2.,2.,2.,2.,3.,3.,3.,3.,2.,2.,2.,2./)
coords123(:,3) = (/-2.,-3.,1.,0.,-1.,-2.,2.,1.,-2.,-3.,1.,0./)
pts_arr(4) = combine_pts(pts_arr(2:3), 2)
result(13) = fuzzy_compare(12, get_npts_pts(pts_arr(4)), 0)
result(14) = fuzzy_compare(3, get_dim_pts(pts_arr(4)), 0)
result(15) = fuzzy_compare(coords123, get_coords_pts(pts_arr(4)), 12, 3, 0.)
call kill_pts(pts_arr, 4)

! -------------------------------------------------------------------------------------
! is_clashing
! (20:29)
! -------------------------------------------------------------------------------------
write(*,*) 'C'
coords43(:,1) = (/1.,3.,13.,23./)
coords43(:,2) = (/2.,3.,13.,23./)
coords43(:,3) = (/1.,3.,13.,23./)
pts_arr(1) = new_pts(4,3,coords43)
result(20) = not(is_clashing(pts_arr(1),1.))
result(21) = is_clashing(pts_arr(1),4.)
result(23) = not(is_clashing(pts_arr(1),0.))
coords11(1,1) = 1.
pts_arr(2) = new_pts(1,1,coords11(1,1))
result(24) = not(is_clashing(pts_arr(2),1.))
call kill_pts(pts_arr(1))
call kill_pts(pts_arr(2))

! -------------------------------------------------------------------------------------
! rnd_pts, plot_3d_pts
! (30:39)
! -------------------------------------------------------------------------------------
write(*,*) 'D'
! Not a rigorous test - just judge by eye. 
pts_arr(1) = rnd_pts(4,3,100.,10.)
if (showplot) call plot_3d_pts(pts_arr(1))
do i=1,30
    pts_arr(2) = rnd_pts(4,3,100.,10.)
    pts_arr(1) = combine_pts(pts_arr(1:2),2)
end do
if (showplot) call plot_3d_pts(pts_arr(1))
! Testing use of center
if (showplot) call plot_3d_pts(pts_arr(2),(/100.,100.,100./))
pts_arr(3) = rnd_pts(4,2,100.,10.)
! Should error
! call plot_3d_pts(pts_arr(3))
call kill_pts(pts_arr(1))
call kill_pts(pts_arr(2))
call kill_pts(pts_arr(3))

! -------------------------------------------------------------------------------------
! rotate_pts, proj2d_pts
! (40:49)
! -------------------------------------------------------------------------------------
write(*,*) 'E'
coords23(:,1) = (/1.,2./)
coords23(:,2) = (/3.,3./)
coords23(:,3) = (/-1.,-2./)
pts_arr(1) = new_pts(2,3,coords23)
! 0.,0.,0. rotation
call rotate_pts(pts_arr(1),0.,0.,0.)
result(40) = fuzzy_compare(coords23, get_coords_pts(pts_arr(1)), 2, 3, 0.)
rmat = euler2m(30.,55.,302.)
coords23b(1,:) = matmul(rmat,coords23(1,:))
coords23b(2,:) = matmul(rmat,coords23(2,:))
if (showplot) write(*,*) 'Plotting before rotation:'
if (showplot) call plot_3d_pts(pts_arr(1))
pts_arr(2) = pts_arr(1)
call rotate_pts(pts_arr(2), 30., 55., 302.)
result(41) = fuzzy_compare(coords23b, get_coords_pts(pts_arr(2)), 2, 3, 0.)
if (showplot) write(*,*) 'Plotting after rotation:'
if (showplot) call plot_3d_pts(pts_arr(2))
! Test proj2d_pts.
pts_arr(3) = proj2d_pts(pts_arr(1), 30., 55., 302.)
result(42) = fuzzy_compare(coords23b(:,1:2), get_coords_pts(pts_arr(3)), 2, 2, 0.)
pts_arr(4) = proj2d_pts(pts_arr(1))
result(43) = fuzzy_compare(coords23(:,1:2), get_coords_pts(pts_arr(4)), 2, 2, 0.)
call kill_pts(pts_arr, 4)

! -------------------------------------------------------------------------------------
! enum_match_pts, match_pts, rmsd_pts
! (50:69)
! -------------------------------------------------------------------------------------
! coords42(:,1) = (/1.,2.,3.,4./)
! coords42(:,2) = (/4.,3.,2.,1./)
! pts_arr(1) = new_pts(4,2,coords42)
! ! Compare to self.
! result(50) = fuzzy_compare(match_pts(pts_arr(1), pts_arr(1)), (/1,2,3,4/), 4, 0)
! result(60) = fuzzy_compare(rmsd_pts(pts_arr(1), pts_arr(1)), 0., 0.)
! ! Different numbers of points. 
! coords42(:,1) = (/101.,35.,33.,154./)
! coords42(:,2) = (/38.,65.,109.,58./)
! coords32(:,1) = (/52.,110.,13./)
! coords32(:,2) = (/76.,55.,109./)
! pts_arr(2) = new_pts(4,2,coords42)
! pts_arr(3) = new_pts(3,2,coords32)
! result(51) = fuzzy_compare(match_pts(pts_arr(2), pts_arr(3)), (/2,1,3,2/), 4, 0)
! result(61) = fuzzy_compare(rmsd_pts(pts_arr(2), pts_arr(3)), 27.951, 0.001)
! result(52) = fuzzy_compare(match_pts(pts_arr(3), pts_arr(2)), (/2,1,3/), 3, 0)
! ! RMSD calculation will assume that one of the 3 points represents 2 to match up
! ! with the 4-point object. 
! result(62) = fuzzy_compare(rmsd_pts(pts_arr(3), pts_arr(2)), 27.951, 0.001)
! ! Same numbers of points but distances between messy. 
! coords42b(:,1) = (/52.,110.,13.,93./)
! coords42b(:,2) = (/76.,55.,109.,34./)
! pts_arr(4) = new_pts(4,2,coords42b)
! result(63) = fuzzy_compare(rmsd_pts(pts_arr(2), pts_arr(4)), 26.622, 0.001)
! call kill_pts(pts_arr,4)

write(*,*) 'F'

 testlist = enum_match_pts(1,new_sll_list(),3)

 do i=1,6
    write(*,*) 'i=', i
    call print_sll_list(testlist(i))
 end do

coords42(:,1) = (/1.,2.,3.,4./)
coords42(:,2) = (/4.,3.,2.,1./)
pts_arr(1) = new_pts(4,2,coords42)
! Compare to self.
icoords42(:,1) = (/1,2,3,4/)
icoords42(:,2) = (/1,2,3,4/)
result(50) = fuzzy_compare(match_pts(pts_arr(1), pts_arr(1)), icoords42, 4, 2, 0)
result(60) = fuzzy_compare(rmsd_pts(pts_arr(1), pts_arr(1)), 0., 0.)

! Different numbers of points. 
coords42(:,1) = (/101.,35.,33.,154./)
coords42(:,2) = (/38.,65.,109.,58./)
coords32(:,1) = (/52.,110.,13./)
coords32(:,2) = (/76.,55.,109./)
pts_arr(2) = new_pts(4,2,coords42)
pts_arr(3) = new_pts(3,2,coords32)
icoords42(:,1) = (/1,2,3,4/)
icoords42(:,2) = (/2,1,3,2/)
result(51) = fuzzy_compare(match_pts(pts_arr(2), pts_arr(3)), icoords42, 4, 2, 0)
result(61) = fuzzy_compare(rmsd_pts(pts_arr(2), pts_arr(3)), 27.951, 0.001)
icoords42(:,1) = (/2,1,3,2/)
icoords42(:,2) = (/1,2,3,4/)
result(52) = fuzzy_compare(match_pts(pts_arr(3), pts_arr(2)), icoords42, 4, 2, 0)
! RMSD calculation will assume that one of the 3 points represents 2 to match up
! with the 4-point object. 
result(62) = fuzzy_compare(rmsd_pts(pts_arr(3), pts_arr(2)), 27.951, 0.001)

! Same numbers of points. 
coords42b(:,1) = (/52.,110.,13.,93./)
coords42b(:,2) = (/76.,55.,109.,34./)
pts_arr(4) = new_pts(4,2,coords42b)
icoords42(:,1) = (/1,2,3,4/)
icoords42(:,2) = (/4,1,3,2/)
result(53) = fuzzy_compare(match_pts(pts_arr(2), pts_arr(4)), icoords42, 4, 2, 0)
result(63) = fuzzy_compare(rmsd_pts(pts_arr(2), pts_arr(4)), 26.622, 0.001)

! Distances messy, same number of points. 
call kill_pts(pts_arr(4))
coords42b(:,1) = (/52.,110.,13.,72./)
coords42b(:,2) = (/76.,55.,109.,21./)
pts_arr(4) = new_pts(4,2,coords42b)
icoords42(:,1) = (/1,2,3,4/)
icoords42(:,2) = (/4,1,3,2/)
result(54) = fuzzy_compare(match_pts(pts_arr(2), pts_arr(4)), icoords42, 4, 2, 0)
result(64) = fuzzy_compare(rmsd_pts(pts_arr(2), pts_arr(4)), 31.1649, 0.001)

! Distances messy, different number of points.
call kill_pts(pts_arr(4))
coords22(:,1) = (/13,40/)
coords22(:,2) = (/109,102/)
pts_arr(4) = new_pts(2,2,coords22)
icoords42(:,1) = (/1,2,3,4/)
icoords42(:,2) = (/2,2,1,2/)
result(55) = fuzzy_compare(match_pts(pts_arr(2), pts_arr(4)), icoords42, 4, 2, 0)
result(65) = fuzzy_compare(rmsd_pts(pts_arr(2), pts_arr(4)), 78.33103, 0.001)

call kill_pts(pts_arr,4)
 
! -------------------------------------------------------------------------------------
! center_pts
! (70:79)
! -------------------------------------------------------------------------------------
write(*,*) 'G'
! Already centered pts.
coords42(:,1) = (/2.,2.,-2.,-2./)
coords42(:,2) = (/2.,-2.,-2.,2./)
pts_arr(1) = new_pts(4,2,coords42)
call center_pts(pts_arr(1))
result(70) = fuzzy_compare(coords42,get_coords_pts(pts_arr(1)),4,2,0.)
! Not already centered.
coords42(:,1) = (/1.,2.,-2.,-3./)
coords42(:,2) = (/2.,-5.,-2.,2./)
pts_arr(1) = new_pts(4,2,coords42)
call center_pts(pts_arr(1))
coords42b(:,1) = (/1.5,2.5,-1.5,-2.5/)
coords42b(:,2) = (/2.75,-4.25,-1.25,2.75/)
result(71) = fuzzy_compare(coords42b,get_coords_pts(pts_arr(1)),4,2,0.)
call kill_pts(pts_arr(1))

! -------------------------------------------------------------------------------------
! mean_pts
! (80:89)
! -------------------------------------------------------------------------------------
write(*,*) 'H'
coords23(:,1) = (/5.,-5./)
coords23(:,2) = (/5.,-5./)
coords23(:,3) = (/5.,-5./)
coords23b(:,1) = (/2.,6./)
coords23b(:,2) = (/2.,6./)
coords23b(:,3) = (/2.,6./)
pts_arr(1) = new_pts(2,3,coords23)
pts_arr(2) = new_pts(2,3,coords23b)
pts_arr(3) = mean_pts(pts_arr(1:2),2,3)
coords33(:,1) = (/5.5, -5., 2./)
coords33(:,2) = (/5.5, -5., 2./)
coords33(:,3) = (/5.5, -5., 2./)
result(80) = fuzzy_compare(coords33, get_coords_pts(pts_arr(3)), 3, 3, 0.)
call kill_pts(pts_arr,4)

! -------------------------------------------------------------------------------------
! steal_xy_pts
! (90:99)
! -------------------------------------------------------------------------------------
write(*,*) 'I'
coords23(:,1) = (/5.,1./)
coords23(:,2) = (/0.,-5./)
coords23(:,3) = (/3.,2./)
coords22(:,1) = (/22.,62./)
coords22(:,2) = (/23.,63./)
pts_arr(1) = new_pts(2,3,coords23)
pts_arr(2) = new_pts(2,2,coords22)
call steal_xy_pts(pts_arr(1),pts_arr(2))
coords23(:,1) = (/22.,62./)
coords23(:,2) = (/23.,63./)
coords23(:,3) = (/3.,2./)
result(80) = fuzzy_compare(coords23, get_coords_pts(pts_arr(1)), 2, 3, 0.)
call kill_pts(pts_arr,4)

! -------------------------------------------------------------------------------------
! Get some values to use (not testing anything)
! -------------------------------------------------------------------------------------
! coords43(:,1) = (/-20.,0.,35.,25./)
! coords43(:,2) = (/-30.,-10.,-10.,40./)
! coords43(:,3) = (/-4.,40.,20.,30./)
! pts_arr(1) = new_pts(4,3,coords43)
! do i=1,10
    ! call RANDOM_NUMBER(three)
    ! write(*,*) get_coords_pts(proj2d_pts(pts_arr(1), 360.*three(1), 180.*three(2), 360.*three(3)))
! end do
! call kill_pts(pts_arr,4)

! -------------------------------------------------------------------------------------
! Report results of tests
! -------------------------------------------------------------------------------------
call report(result, size(result))

end program test_simple_pts