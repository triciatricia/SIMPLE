! -------------------------------------------------------------------------------------
! Module simple_pts_projopt. 
! Used for optimization of projection angles of an array of 2D pts objects that are 
! projections of a given 3D pts object. 
! 
! Explanation of Variables:
! 	pts_3d		pts to be projected
! 	proj_arr	array of 2D pts (the observed projections)
! 	num_proj	number of projections (size of proj_arr)
! 	initialized	value is .TRUE. if initialization has occurred
! -------------------------------------------------------------------------------------

module simple_pts_projopt
use simple_pts
use simple_de_opt
implicit none
save

logical, private			:: initialized
type(pts), private			:: pts_3d
type(pts), private, allocatable		:: proj_arr(:)
integer, private			:: num_proj

real, private, parameter		:: pie = acos(-1.)

contains

subroutine init_projopt(proj_arr_in, num_proj_in, pts_3d_in)
! Initialize values for optimization of projection angles. 
! 	proj_arr_in	array of 2D pts (projections)
! 	num_proj_in	size of proj_arr_in
! 	pts_3d_in	3D pts object to be projected
    integer, intent(in)		:: num_proj_in
    type(pts), intent(in)	:: proj_arr_in(num_proj_in), pts_3d_in
    integer			:: alloc_stat, i
    ! Set variables pts_3d, num_proj
    pts_3d = pts_3d_in
    num_proj = num_proj_in
    ! Check if proj_arr is already allocated from previous call. 
    if (allocated(proj_arr)) then
        call kill_pts(proj_arr,size(proj_arr))
        deallocate(proj_arr)
    end if
    allocate(proj_arr(num_proj), stat=alloc_stat)
    call alloc_err('In: simple_pts_projopt. Subroutine: init_projopt.', alloc_stat)
    proj_arr = proj_arr_in
    do i=1,size(proj_arr)
	call center_pts(proj_arr(i))
    end do
    initialized = .TRUE.
end subroutine init_projopt

function cost_projopt(param, paramsize)
! Cost function used for assigning angles to projections. 
! Project according to each of the angles in param. 
! (ZYZ Euler convention, degrees, positive is clockwise) 
! paramsize = 3 * num_proj
! Calculate avg RMSD between calculated and observed projections. 
    integer, intent(in)		:: paramsize
    real, intent(in)		:: param(paramsize)
    real			:: cost_projopt, rmsd_sum
    integer			:: i
    type(pts)			:: proj_calc
    rmsd_sum = 0.
    do i=0,num_proj-1
	proj_calc = proj2d_pts(pts_3d, param(3*i+1), param(3*i+2), param(3*i+3))
	call center_pts(proj_calc)
	rmsd_sum = rmsd_sum + rmsd_pts(proj_calc, proj_arr(i+1))
	call kill_pts(proj_calc)
    end do
    cost_projopt = rmsd_sum / num_proj
    return
end function cost_projopt

subroutine de_projopt(proj_arr_in, num_proj_in, pts_3d_in, neigh, GENMAX, solution, final_cost)
! Subroutine for differential evolution (using simple_de_opt module). 
! Optimization of projection angles to project a give 3D pts object (pts_3d_in) to obtain each
! of the 2D pts objects in an array (proj_arr_in). 
! 	proj_arr_in	Aray of 2D pts (projections)
! 	num_proj_in	Size of proj_arr_in
! 	pts_3d_in	3D pts object to be projected
! 	neigh		Fraction of the population in each neighborhood for the differential 
! 			evolution. [0,1]
! 	GENMAX		Maximum number of generations (iterations) for the differential evolution
! 	solution	The solution (an output of this subroutine), an array of Euler angles for
! 			projecting the 3D pts object, using Spider conventions (ZYZ, positive 
! 			clockwise rotations, degrees). The first angle is phi for the first 
! 			projection. The second is theta for the 1st projection. The third is psi 
! 			for the 1st projection. The fourth is phi for the 2nd projection. And so on. 
! 			Therefore, size(solution) = 3*num_proj_in
! 	final_cost	The cost (avg RMSD) of the final solution
    integer, intent(in)		:: num_proj_in, GENMAX
    type(pts), intent(in)	:: proj_arr_in(num_proj_in), pts_3d_in
    real, intent(in)		:: neigh
    real, intent(out)		:: solution(3*num_proj_in), final_cost
    type(de_opt)		:: de
    ! Other parameters for DE:
    real			:: limits(3*num_proj_in,2), cost_error
    integer			:: size_pop
    logical			:: cyclic(3*num_proj_in)
    ! Other variables:
    integer			:: i
    ! Intialize information for the cost function.
    call init_projopt(proj_arr_in, num_proj_in, pts_3d_in)
    ! Set other parameters for differential evolution.
    cyclic = .TRUE.
    do i=0,num_proj_in-1
	limits(3*i+1,:) = (/0.,360./)
	limits(3*i+2,:) = (/0.,180./)
	limits(3*i+3,:) = (/0.,360./)
	cyclic(3*i+2) = .FALSE.
    end do
    size_pop = 10 * num_proj_in
    ! I don't know the error in the cost function, so I'll use 0.1 for now and see what happens. 
    cost_error = 0.1
    ! Initialize and run differential evolution.
    de = new_de_opt(size(solution), limits, size_pop, neigh, cyclic)
    write(*,'(A)') '>>> Differential evolution'
    call de_cont_min(de, cost_projopt, GENMAX, cost_error, solution, final_cost)
end subroutine de_projopt

subroutine em_projopt(proj_arr_in, n_proj, npts, iter, angle_arr, pts3D_arr, maxdist_in, clashdist_in, neigh_in, GENMAX_in)
! Subroutine for expectation maximization of a 3D pts object from projections. Angles in the output are Euler 
! angles of rotation. 
! Arguments:
! 	proj_arr_in	Array of projections (2D pts)
! 	n_proj		Size of the array proj_arr_in
! 	npts		Number of points in the 3D object
! 	iter		Number of iterations
! 	angle_arr	2D array to hold the Euler angle solutions from each iteration. Shape = (iter,3*n_proj).
! 			Format = (n,3(m-1)+i) where n is the nth iteration, and m is the mth projection in the array, 
! 			i = 1 for phi, i = 2 for theta, and i = 3 for psi. (The Euler angles follow the Spider
! 			convention: ZYZ, clockwise is positive, and angles are in degrees.)
! 	pts3D_arr	An array of the 3D model from each iteration (pts object with npts points). size = iter + 1
! 	maxdist_in	An optional argument for the initial random solution. The maximum distance between the origin 
! 			and points in the 3D pts object that will be projected to produce the input projections in 
! 			proj_arr_in. 
! 	clashdist_in	An optional argument (for initial solution). The minimum distance between points in the 3D object. 
! 			(default = 0.) *** Try to implement this for later steps, too.***
! 	neigh_in	Optional argument for differential evolution step. (default = ?)
! 			Fraction of the population in each neighborhood for the differential evolution. [0,1]
! 	GENMAX_in	Optional argument for differential evolution step. (default = 100)
! 			Maximum number of generations (iterations) for the differential evolution
    integer, intent(in)			:: n_proj, npts, iter
    type(pts), intent(in)		:: proj_arr_in(n_proj)
    real, intent(out)			:: angle_arr(iter,3*n_proj)
    type(pts), intent(out)		:: pts3D_arr(iter+1)
    real, intent(in), optional		:: maxdist_in, clashdist_in, neigh_in
    integer, intent(inout), optional	:: GENMAX_in
    integer				:: n, i, j, alloc_stat, temp_npts, GENMAX
    real				:: cost(iter), temp_dist, maxdist, clashdist, neigh
    real				:: phi, theta, psi
    real, allocatable			:: temp_coords(:,:)
    type(pts)				:: rot_pts(n_proj), projrot(n_proj), temp_pts
    ! Set maxdist, clashdist, neigh, GENMAX to default if not present. 
    ! If maxdist isn't present, use the maximum distance between a point in the centered projections and the origin. 
    if (not(present(maxdist_in))) then
	maxdist = 0.
	do i=1,n_proj
	    temp_pts = proj_arr_in(i)
	    call center_pts(temp_pts)
	    temp_npts = get_npts_pts(temp_pts)
	    allocate(temp_coords(temp_npts,2), stat=alloc_stat)
	    call alloc_err('In module: simple_pts_projopt. Subroutine: em_projopt.', alloc_stat)
	    temp_coords = get_coords_pts(temp_pts)
	    do j=1,temp_npts
		temp_dist = euclid(temp_coords(j,:), (/0.,0./))
		if (temp_dist > maxdist) maxdist = temp_dist
	    end do
	    deallocate(temp_coords)
	end do
    else
        maxdist = maxdist_in
    end if
    if (not(present(clashdist_in))) then
	clashdist = 0.
    else
        clashdist = clashdist_in
    end if
    if (not(present(neigh_in))) then
        neigh = 0.05 !testing
    else
        neigh = neigh_in
    end if
    if (not(present(GENMAX_in))) then
        GENMAX = 100
    else
        GENMAX = GENMAX_in
    end if
    ! Make initial 3D pts object to project: 
    pts3D_arr(1) = rnd_pts(npts, 3, maxdist, clashdist)
    do n=1,iter
     	call de_projopt(proj_arr_in, n_proj, pts3D_arr(n), neigh, GENMAX, angle_arr(n,:), cost(n))
    ! 	Rotate 3D pts object according to angles:
        rot_pts = pts3D_arr(n)
	do i=1,n_proj
	    phi = angle_arr(n,3*(i-1)+1)
	    theta = angle_arr(n,3*(i-1)+2)
	    psi = angle_arr(n,3*(i-1)+3)
	    call rotate_pts(rot_pts(i), phi, theta, psi)
	    ! For each rotated 3D pts object, change x & y coords to that of closest
	    ! point in proj_arr_in, then rotate back. 
	    call steal_xy_pts(rot_pts(i),proj_arr_in(i))
	    call rotate_pts(rot_pts(i), -psi, -theta, -phi)
	end do
	! Make 3D pts for next round using clustering (using heirarchical clust. right now, but k-means could work, too)
	pts3D_arr(n+1) = mean_pts(rot_pts, n_proj, npts)
	write(*,'(A,I4,A,F7.4)') '>>>Finished with iteration #: ', n, ' Cost: ', cost(n)
    end do
    ! graph final result, output angles to file?
    call plot_3d_pts(pts3D_arr(iter+1))
end subroutine em_projopt

end module simple_pts_projopt