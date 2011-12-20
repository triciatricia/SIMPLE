! -------------------------------------------------------------------------------------
! ==Class pts
!
! What's the point? Pts is simply a distribution of points in space. 
! 
! Explanation of Variables:
! 	num_pts		number of points in a pts (>0)
! 	dimen		number of dimensions (>0)
! 	coords		array (m,n), where m is the mth point in the pts, and
! 			n is the dimension
! 	pie		pi = acos(-1.)
! 
! -------------------------------------------------------------------------------------

module simple_pts
use simple_rnd
use simple_math
use simple_stat
use simple_sll_list
use simple_pair_wtab
use gnufor2
implicit none
save

interface kill_pts
    module procedure kill_pts_1
    module procedure kill_pts_arr
end interface

real, private, parameter		:: pie = acos(-1.)

type pts
    private
    integer				:: num_pts, dimen
    real, allocatable			:: coords(:,:)
end type pts

contains

function new_pts(n_pts, dimen, coords_in)
! Create a new pts with points at the specified coordinates
! 	n_pts = number of points
! 	dimen = number of dimensions
! 	coords_in = a 2D array of coordinates (n,m) where n specifies the nth point, 
! 		    and m is the dimension
    integer, intent(in)			:: n_pts, dimen
    real, intent(in), optional		:: coords_in(n_pts, dimen)
    type(pts)				:: new_pts
    integer				:: alloc_stat
    new_pts%num_pts = n_pts
    new_pts%dimen = dimen
    allocate(new_pts%coords(n_pts,dimen), stat=alloc_stat)
    call alloc_err('In module: simple_pts. Function: new_pts.', alloc_stat)
    if (present(coords_in)) then
	new_pts%coords = coords_in
    else
	new_pts%coords = 0.
    end if
    return
end function new_pts

function rnd_pts(n_pts, dimen, maxdist, clashdist)
! Create a new pts with points at random coordinates. 
! 	n_pts = number of points
! 	dimen = number of dimensions
! 	maxdist = maximum distance of a point from the origin
! 	clashdist = minimum distance between two points
    integer, intent(in)			:: n_pts, dimen
    real, intent(in)			:: maxdist
    real, intent(in), optional		:: clashdist
    type(pts)				:: rnd_pts
    integer				:: alloc_stat, i, n
    real				:: mindist
    real, allocatable			:: coords(:,:), origin(:)
    logical				:: clash, calc_coords
    allocate(coords(n_pts,dimen), origin(dimen), stat=alloc_stat)
    call alloc_err('In module: simple_pts. Function: rnd_pts.', alloc_stat)
    ! Check if clashdist is input. mindist = minimum distance between two points.
    if (present(clashdist)) then
	mindist = clashdist
    else
	mindist = 0.
    end if
    clash = .TRUE.
    origin = 0.
    do while (clash)
	do i=1,n_pts
	    calc_coords = .TRUE.
	    do while (calc_coords)
		do n=1,dimen
		    coords(i,n) = 2. * (ran3() - 0.5) * maxdist
		end do
		if (euclid(origin, coords(i,:)) <= maxdist) calc_coords=.FALSE.
	    end do
	end do
	! Create the new pts. 
	rnd_pts = new_pts(n_pts, dimen, coords)
	! Check if there is a clash. If so, redo. 
	clash = is_clashing(rnd_pts, mindist)
	if (clash) call kill_pts(rnd_pts)
    end do
    deallocate(coords, origin)
    return
end function rnd_pts

subroutine kill_pts_1(pts_in)
! Destroy the pts pts_in. 
    type(pts), intent(inout)		:: pts_in
    ! Check if allocated, and if so, deallocate coords. 
    if (allocated(pts_in%coords)) deallocate(pts_in%coords)
end subroutine kill_pts_1

subroutine kill_pts_arr(pts_arr, length)
! Destroy an array of pts. 
! 	pts_arr = array of pts
! 	length = size of pts_arr
    integer, intent(in)			:: length
    type(pts), intent(inout)		:: pts_arr(length)
    integer				:: i
    do i=1,length
	call kill_pts(pts_arr(i))
    end do
end subroutine kill_pts_arr

function get_coords_pts(pts_in)
! Returns the coordinates of the pts pts_in. 
! An array where (m,n) specifies the coordinate of the mth point in the
! nth dimension. 
    type(pts), intent(in)		:: pts_in
    real				:: get_coords_pts(pts_in%num_pts,pts_in%dimen)
    get_coords_pts = pts_in%coords
    return
end function get_coords_pts

function get_npts_pts(pts_in)
! Returns the number of points in pts_in. 
    type(pts), intent(in)		:: pts_in
    integer				:: get_npts_pts
    get_npts_pts = pts_in%num_pts
    return
end function get_npts_pts

function get_dim_pts(pts_in)
! Returns the number of dimensions in pts_in.
    type(pts), intent(in)		:: pts_in
    integer				:: get_dim_pts
    get_dim_pts = pts_in%dimen
    return
end function get_dim_pts

subroutine plot_3d_pts(pts_in, center)
! Plots a 3d pts. Points are plotted as lines (or "vectors") radiating out  
! of the center, assumed to be (0,0,0) if none is provided. 
    type(pts), intent(in)		:: pts_in
    real, intent(in), optional		:: center(3)
    integer				:: alloc_stat, npts, length, i
    real(kind=8), allocatable		:: x(:), y(:), z(:)
    ! Check dimensions
    if (pts_in%dimen /= 3) then
	write(*,*) 'Wrong dimensions for a 3D plot.'
	write(*,*) 'Error in module simple_pts. Function: plot_3d_pts.'
	stop
    end if
    npts = pts_in%num_pts
    length = 2*npts + 1
    allocate(x(length),y(length),z(length), stat=alloc_stat)
    call alloc_err('In module: simple_pts. Subroutine: plot_3d_pts.', alloc_stat)
    ! Since plot3d (from gnufor2 module) can only graph 1 line per plot, fill 
    ! every other point in the line with the center coordinates so that the final 
    ! plot looks like lines radiating from the center. 
    x = 0.
    y = 0.
    z = 0.
    if (present(center)) then
	x = center(1)
	y = center(2)
	z = center(3)
    end if
    do i=1,npts
      x(2*i) = pts_in%coords(i,1)
      y(2*i) = pts_in%coords(i,2)
      z(2*i) = pts_in%coords(i,3)
    end do
    call plot3d(x, y, z, pause=-1.0, persist='no')
    deallocate(x,y,z)
end subroutine plot_3d_pts

function combine_pts(pts_array, length)
! Combine the points in each pts in pts_array into a single pts. 
! 	pts_array = array of pts. Each pts in pts_array must be of the same dimension. 
! 	length = length of the array. 
    integer, intent(in)			:: length
    type(pts), intent(in)		:: pts_array(length)
    type(pts)				:: combine_pts
    integer				:: dimen, i, n, pt, n_pts, alloc_stat
    real, allocatable			:: coords(:,:)
    ! Check if every pts is of the same dimension.
    dimen = pts_array(1)%dimen
    do i=1,length
	if (pts_array(i)%dimen/=dimen) then
	    write(*,*) 'Cannot combine pts of different dimensions.'
	    write(*,*) 'Error in module: simple_pts. Function: combine_pts.'
	    stop
	end if
    end do
    ! Figure out how many points there are in total. 
    pt = 0
    do i=1,length
	pt = pt + pts_array(i)%num_pts
    end do
    allocate(coords(pt,dimen), stat=alloc_stat)
    call alloc_err('In module: simple_pts. Function: combine_pts.', alloc_stat)
    pt = 0
    do i=1,length
	n_pts = pts_array(i)%num_pts
	do n=1,n_pts
	    pt = pt + 1
	    coords(pt,:) = pts_array(i)%coords(n,:)
	end do
    end do
    combine_pts = new_pts(pt, dimen, coords)
    deallocate(coords)
    return
end function combine_pts

function is_clashing(pts_in, mindist)
! Is there a clash between two points? (Is the distance between two points less than mindist?)
    type(pts), intent(in)		:: pts_in
    real, intent(in)			:: mindist
    logical				:: is_clashing
    real				:: dist
    integer				:: i, j, n_pts, alloc_stat
    is_clashing = .FALSE.
    n_pts = pts_in%num_pts
    if (n_pts>1) then
	do i=1,n_pts-1
	    do j=i+1,n_pts
	        dist = euclid(pts_in%coords(i,:), pts_in%coords(j,:))
		if (dist<mindist) then
		    is_clashing = .TRUE.
		    exit
	        end if
	    end do
        end do
    end if
    return
end function is_clashing

function proj2d_pts(pts_in, phi, theta, psi)
! Returns a 2D projection (a 2D pts) of the 3D pts_in optionally rotated by the Euler angles
! phi, theta, and psi, which are in degrees. 
! 	pts_in = the pts to project. It must be in 3 dimensions. 
! 	phi = rotation around z-axis
! 	theta = tilt angle
! 	psi = rotation around z-axis
! 	Rotations are clockwise. (Spider convention)
    type(pts), intent(in)		:: pts_in
    real, intent(in), optional		:: phi, theta, psi
    type(pts)				:: proj2d_pts, temp_pts
    real, allocatable			:: coords(:,:)
    integer				:: alloc_stat
    ! Check that pts_in is 3D.
    if (pts_in%dimen/=3) then
	write(*,*) 'proj2d_pts can only be applied to a 3 dimensional pts.'
	write(*,*) 'Error, in module: simple_pts. function: proj2d_pts.'
	stop
    end if
    ! Copy pts_in
    temp_pts = pts_in
    ! Rotate it if the phi, theta, and psi arguments are present. 
    if (present(phi) .AND. present(theta) .AND. present(psi)) then
	call rotate_pts(temp_pts, phi, theta, psi)
    end if
    ! Project it. 
    allocate(coords(pts_in%num_pts,2), stat=alloc_stat)
    call alloc_err('In module: simple_pts. Function: proj2d_pts.', alloc_stat)
    coords = temp_pts%coords(:,1:2)
    ! Make the resulting 2D pts. 
    proj2d_pts = new_pts(pts_in%num_pts,2,coords)
    deallocate(coords)
    call kill_pts(temp_pts)
    return
end function proj2d_pts

subroutine rotate_pts(pts_in, phi, theta, psi)
! Rotate pts_in
! 	pts_in = the pts to rotate. It must be in 3 dimensions. 
! 	phi = rotation around z-axis (angle between N and the original z-axis)
! 	theta = tilt angle (angle between the two y-axes) [0,180]
! 	psi = rotation around z-axis (angle between N and the new z-axis)
! 	(N is the intersection of the new and old XY planes.)
! 	Rotations are clockwise. Angles are in degrees. (Spider convention)
    type(pts), intent(inout)		:: pts_in
    real, intent(in)			:: phi, theta, psi
    real				:: rotmat(3,3)
    real, allocatable			:: coords(:,:)
    integer				:: i, alloc_stat
    ! Check that pts_in is 3D.
    if (pts_in%dimen/=3) then
	write(*,*) 'rotate_pts can only be applied to a 3 dimensional pts.'
	write(*,*) 'Error, in module: simple_pts. function: rotate_pts.'
	stop
    end if
    allocate(coords(pts_in%num_pts,3), stat=alloc_stat)
    call alloc_err('In module: simple_pts. Function: rotate_pts.', alloc_stat)
    ! Calculate rotation matrix using euler2m function in simple_math (Spider conv)
    rotmat = euler2m(phi, theta, psi)
    ! Apply rotation to coords
    do i=1,pts_in%num_pts
	coords(i,:) = matmul(rotmat,pts_in%coords(i,:))
    end do
    pts_in%coords = coords
    deallocate(coords)
end subroutine rotate_pts

subroutine center_pts(pts_in)
! Center the distribution of points in pts_in at the origin. 
    type(pts), intent(inout)		:: pts_in
    real				:: mean_coords(pts_in%dimen)
    integer				:: i
    mean_coords = 0.
    do i=1,pts_in%num_pts
	mean_coords = mean_coords + pts_in%coords(i,:)
    end do
    mean_coords = mean_coords / pts_in%num_pts
    do i=1,pts_in%num_pts
	pts_in%coords(i,:) = pts_in%coords(i,:) - mean_coords
    end do
end subroutine center_pts

function rmsd_pts(pts1, pts2)
! Returns the RMSD between two pts objects, assumed to be already aligned. 
! If one pts object has fewer points than the other, point(s) will be reused. 
! Will not work for pts with more than 12 points. 
    type(pts), intent(in)		:: pts1, pts2
    real				:: rmsd_pts, rmsd_sum
    integer				:: matchpts(max(pts1%num_pts,pts2%num_pts),2)
    integer				:: i, npts
    ! Check if same dimensions.
    if (pts1%dimen /= pts2%dimen) then
        write(*,*) 'Error: Cannot calculate RMSD between points of different dimensions.'
	write(*,*) 'In module: simple_pts. Function: rmsd_pts.'
	stop
    end if
    npts = max(pts1%num_pts, pts2%num_pts)
    ! If more than 12 points, refuse. (If, in the future, this needs to be calculated for
    ! more than 12 points, make a new, faster function.)
    if (npts > 12) then
	write(*,*) 'Error: Cannot calculate RMSD for more than 12 points.'
	write(*,*) 'In module: simple_pts. Function: rmsd_pts.'
	stop
    end if
    ! Find point pairs (matchpts)
    matchpts = match_pts(pts1, pts2)
    rmsd_sum = 0.
    do i=1, size(matchpts(:,1))
        rmsd_sum = rmsd_sum + sum((pts1%coords(matchpts(i,1),:) - pts2%coords(matchpts(i,2),:))**2.)
    end do
    rmsd_pts = sqrt(rmsd_sum/ npts)
    return
end function rmsd_pts

recursive function match_pts(pts1, pts2) result(match)
! Match the points in pts1 with the points in pts2 to create pairs of points with 
! minimum RMSD. If one pts object has fewer points than the other, point(s) in the
! pts object with fewer points will be used more than once. 
! This is accurate but slow, so don't use it for large numbers of points. 
! The function returns a 2D vector of size (max_number_points, 2) where (m,1) and 
! (m,2) are points from pts1 and pts2, respectively, that are matched up with each other. 
    type(pts), intent(in)		:: pts1, pts2
    integer				:: match(max(pts1%num_pts,pts2%num_pts),2)
    integer				:: swapmatch(max(pts1%num_pts,pts2%num_pts),2)
    real, allocatable			:: dist_table(:,:)
    real				:: d, bestdist
    integer				:: i, j, n, k, alloc_stat, npts, closetoi, bestindex
    logical				:: pts2_is_larger, pt_unused
    type(sll_list), allocatable		:: enum_list(:), temp_enum_list(:)
    type(sll_list)			:: bestlist
    ! If more than 12 points, refuse to compute. 
    if (max(pts1%num_pts,pts2%num_pts) > 12) then
	write(*,*) 'Cannot compute matches for more than 12 points.'
	write(*,*) 'In module simple_pts. Function: match_pts.'
	stop
    end if
    npts = max(pts1%num_pts, pts2%num_pts)
    ! If pts1 has fewer points than pts2, swap pts1 and pts2 and run the function.
    if (pts1%num_pts < pts2%num_pts) then !Messy & doesn't compile. Change.
	swapmatch = match_pts(pts2, pts1)
	match(:,2) = swapmatch(:,1)
	match(:,1) = swapmatch(:,2)
	return
    end if
    ! Allocate dist_table
    allocate(dist_table(pts1%num_pts,pts2%num_pts), stat=alloc_stat)
    call alloc_err('In: simple_pts. Function: match_pts.', alloc_stat)
    ! Fill dist_table
    dist_table = 0.
    do i=1,pts1%num_pts
	do j=1,pts2%num_pts
	    d = euclid(pts1%coords(i,:), pts2%coords(j,:))
	    dist_table(i,j) = d
	end do
    end do
    ! Use dist_table to find the nearest matches. (can put into another function to avoid repeating)
    do i=1,npts
        closetoi = 1
        do j=1,pts2%num_pts
	    if (dist_table(i,j) < dist_table(i,closetoi)) closetoi = j
        end do
        match(i,1) = i
        match(i,2) = closetoi
    end do
    ! Find out if a point is unused.
    pt_unused = .FALSE.
    do i=1,pts1%num_pts
	if (all(match(:,1)/=i)) then
	    pt_unused = .TRUE.
	    exit
	end if
    end do
    do i=1,pts2%num_pts
	if (all(match(:,2)/=i)) then
	    pt_unused = .TRUE.
	    exit
	end if
    end do
    ! If some point is unused, then enumerate all permutations using a recursive function. 
    if (pt_unused) then
	allocate(enum_list(lowfact(pts1%num_pts)), stat=alloc_stat)
	call alloc_err('In module: simple_pts. Function: match_pts.', alloc_stat)
	enum_list = enum_match_pts(1, new_sll_list(), pts1%num_pts)
	! Create new enum_lists for each extra point in pts1. (reuse points in pts1)
	if (pts2%num_pts < pts1%num_pts) then
	    do k=pts2%num_pts+1,pts1%num_pts
		allocate(temp_enum_list(size(enum_list)), stat=alloc_stat)
		call alloc_err('In module: simple_pts. Function: match_pts.', alloc_stat)
		temp_enum_list = copy_int_sll_list(enum_list, size(enum_list)) 
		deallocate(enum_list)
		allocate(enum_list(size(temp_enum_list)*pts2%num_pts), stat=alloc_stat)
		call alloc_err('In module: simple_pts. Function: match_pts.', alloc_stat)
		n = 1
		do i=1,pts2%num_pts
		    do j=1,size(temp_enum_list)
			enum_list(n) = copy_int_sll_list(temp_enum_list(j))
			if (sll_iexists(enum_list(n),k) == 0) then
			    write(*,*) 'Index not present. Module: simple_pts. Function: match_pts.'
			end if
			call set_sll_node(enum_list(n),sll_iexists(enum_list(n),k),i)
			n = n + 1
		    end do
		end do
		do i=1,size(temp_enum_list)
		    call kill_sll_list(temp_enum_list(i))
		end do
		deallocate(temp_enum_list)
	    end do
	end if
	! Sum distances for each permutation and find best permutation 
	! (lowest distance between points). 
	bestindex = 1
	bestdist = 0
	do i=1,npts
	    call get_sll_node(enum_list(1),i,j)
	    bestdist = bestdist + dist_table(i,j)
	end do
	do n=1,size(enum_list)
	    d = 0.
	    do i=1,npts
	        call get_sll_node(enum_list(n),i,j)
	        d = d + dist_table(i,j)
	    end do
	    if (d<bestdist) then
	        bestdist = d
		bestindex = n
	    end if
	end do
	! Replace second column in array to return with new array of indexes.
	bestlist = copy_int_sll_list(enum_list(bestindex))
	do i=1,npts
	    call get_sll_node(bestlist,i,n)
	    match(i,2) = n
	end do
	do i=1,size(enum_list)
	    call kill_sll_list(enum_list(i))
	end do
	deallocate(enum_list)
    end if
    deallocate(dist_table)
end function match_pts

recursive function enum_match_pts(i, oldlist, imax) result(enmatch)
! Helper subroutine for match_pts enumerates permutations. (can make faster by calculating distances as you go, 
! but since there are only ~4 points for current usage, I'm going the slow route.)
! Returns an array of lists. 
! Perhaps, move me to a more appropriate location like simple_math later. 
    integer, intent(in)		:: i, imax
    type(sll_list), intent(in)  :: oldlist
    type(sll_list)		:: enmatch(lowfact(imax)/lowfact(i-1)) !imax - i + 1
    type(sll_list)		:: newlist(i), reslist(i,lowfact(imax)/lowfact(i)) ! lowfact is only for low numbers.
    integer			:: n, m, nextsize
    do n=1,i
	newlist(n) = copy_int_sll_list(oldlist)
	! If i is odd, insert i in the forward direction.
	if (mod(real(i),2.)==1.) then
	    call insert_sll_node(newlist(n), n, i)
	! If i is even, insert i starting from the end of the list.
	else 
	    call insert_sll_node(newlist(n), i-(n-1), i)
	end if
    end do
    if (i == imax) then
        do n=1,size(newlist)
            enmatch(n) = copy_int_sll_list(newlist(n))
	end do
    else
	nextsize = lowfact(imax) / lowfact(i) ! imax - i
        do n=1,i
            reslist(n,:) = enum_match_pts(i+1,newlist(n),imax)
	    do m=1,nextsize
		enmatch((n-1)*nextsize+m) = copy_int_sll_list(reslist(n,m))
	    end do
	end do
	! Kill sll lists. 
	do n=1,size(reslist,1)
            do m=1,size(reslist,2)
                call kill_sll_list(reslist(n,m))
	    end do
        end do
    end if
    do n=1,size(newlist)
        call kill_sll_list(newlist(n))
    end do
end function enum_match_pts

function mean_pts(pts_arr, arr_size, npts)
! Combine and cluster points in pts_arr based on Euclidean distance. Returns a pts object 
! in which each point is a mean (calculated separately in each dimension) of the points in 
! a cluster. Hierarchical clustering from the simple_stat module is used. 
! Note: If this is too slow, alter to use a different method. 
! 	pts_arr		array of pts to combine and then cluster
! 	arr_size	size of the array pts_arr
! 	npts		number of clusters = number of points in the pts object that 
! 			this function returns. 
	integer, intent(in)		:: arr_size, npts
	type(pts), intent(in)		:: pts_arr(arr_size)
	type(pts)			:: mean_pts, all_pts
	type(sll_list), allocatable	:: hac_sll(:)
	real, allocatable		:: dist(:,:)
	real				:: maxdist, coords(npts,pts_arr(1)%dimen)
	type(pair_wtab)			:: pwtab
	integer				:: alloc_stat, i, j, k, n, maxp, clssize, numcls
	! Combine all points in the array.
	all_pts = combine_pts(pts_arr, arr_size)
	! Allocate arrays.
	allocate(hac_sll(all_pts%num_pts), dist(all_pts%num_pts,all_pts%num_pts), stat=alloc_stat)
	call alloc_err('In module simple_pts. Function: mean_pts.', alloc_stat)
	! Calculate distances between points and make the pair-weight table to use for 
	! clustering. 
	pwtab = new_pair_wtab(all_pts%num_pts)
	do i=1,all_pts%num_pts-1
	    do j=i+1,all_pts%num_pts
		dist(i,j) = euclid(all_pts%coords(i,:), all_pts%coords(j,:))
	    end do
	end do
	maxdist = maxval(dist)
	do i=1,all_pts%num_pts-1
	    do j=i+1,all_pts%num_pts
		call set_pair_w(pwtab, i, j, 1.-2.*dist(i,j)/maxdist)
	    end do
	end do
	! Make an array of singly linked lists for hac_cls to use.
	do i=1,all_pts%num_pts
	    hac_sll(i) = new_sll_list()
	    call add_sll_node(hac_sll(i),i)
	end do
	! Hierarchical clustering. 
	maxp = nint(all_pts%num_pts/2.) ! Maximum number of points in a cluster. 
	numcls = npts ! Number of clusters. 
	call hac_cls(pwtab, all_pts%num_pts, numcls, maxp, hac_sll)
	! Averages per cluster. 
	! Assuming some things about the output hac_sll - double check that this works.
	coords = 0.
	k = 1
	do i=1,all_pts%num_pts ! npts
	    clssize = get_sll_size(hac_sll(i))
	    if (clssize > 0) then
		do j=1,clssize
		    call get_sll_node(hac_sll(i), j, n)
		    coords(k,:) = coords(k,:) + all_pts%coords(n,:)
	        end do
	        coords(k,:) = coords(k,:)/clssize
	        k = k + 1
	    end if
	end do
	! Make new pts object. 
	mean_pts = new_pts(npts, all_pts%dimen, coords)
	! Deallocate and kill.
	do i=1,size(hac_sll)
	    call kill_sll_list(hac_sll(i))
	end do
	call kill_pts(all_pts)
	deallocate(hac_sll, dist)
	return
end function mean_pts

subroutine steal_xy_pts(pts3d,pts2d)
! pts3d steals the x and y coordinates of the closest point in pts2d to its projection on the xy-plane. 
! Alters pts3d to change x & y coords to that of the closest point in pts2d.
! pts3d must be a 3-dimensional pts object, and pts2d must be a 2-dimensional pts object. They
! do not have to have the same number of points. 
    type(pts), intent(inout)		:: pts3d
    type(pts), intent(in)		:: pts2d
    type(pts)				:: proj_pts3d
    integer				:: i, ptsmatch(max(pts3d%num_pts,pts2d%num_pts),2)
    if (pts3d%dimen /=3 .OR. pts2d%dimen /=2) then
	write(*,*) 'Error: unusable point dimensions.'
	write(*,*) 'In module: simple_pts. Subroutine: simple_pts.'
	stop
    end if
    proj_pts3d = proj2d_pts(pts3d)
    ptsmatch = match_pts(proj_pts3d,pts2d)
    do i=1,pts3d%num_pts
	pts3d%coords(i,1) = pts2d%coords(ptsmatch(i,2),1)
	pts3d%coords(i,2) = pts2d%coords(ptsmatch(i,2),2)
    end do
    call kill_pts(proj_pts3d)
end subroutine steal_xy_pts

! ***** To add: 
! 	- <added but need to test/try> optimizing angles for the projections using DE
! 	- <added but need to test> Add to simple_dens_map: Convert dens_map to pts (need to center)
! 		- Test center_dens_map. 
! 	- Test em_projopt
! 	- Get rid of memory buildup. (allocate at front)
! 	- Add to get_cls & align_densities: get and align multiple at once. 
! 	  (Maybe make functions/subroutines for these, combine.)

end module simple_pts