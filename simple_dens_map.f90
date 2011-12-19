! -------------------------------------------------------------------------------------
! ==Class dens_map
!
! A 2D map of density centers (max 4) and their masses. 
! 
! Explanation of Variables:
!   - mass: an array of the mass of each density (in # pixels) 
!   - coord: an array of the coordinates of each density in a spider image 
!   - dist: an array of the Euclidean distances between densities in order of 
!     largest to smallest. 
!   - n_dens: the number of densities. 
! 
! dens_map is sometimes abbreviated as dmap in the function/subroutine names. 
! -------------------------------------------------------------------------------------

module simple_dens_map
use simple_math
use simple_stat
use simple_pts
implicit none
save

type dens_map
    private
    integer     :: mass(4), n_dens
    real        :: dist(6), coord(4,2)
end type dens_map

interface new_dens_map
    module procedure new_dens_map_empty
    module procedure new_dens_map_set_i
    module procedure new_dens_map_set_r
end interface new_dens_map

interface order_array
    module procedure order_array_r
    module procedure order_array_i
end interface order_array

interface set_dens_map
    module procedure set_dens_map_i
    module procedure set_dens_map_r
end interface set_dens_map

interface shift_dens_map
    module procedure shift_dens_map_i
    module procedure shift_dens_map_r
end interface shift_dens_map

contains

    function new_dens_map_empty()
    ! is a contructor for a dens_map. 
        type(dens_map) :: new_dens_map_empty
        new_dens_map_empty%n_dens = 0
        new_dens_map_empty%mass = 0
        new_dens_map_empty%coord = 0.
        new_dens_map_empty%dist = 0.
        return
    end function new_dens_map_empty
    
    function new_dens_map_set_i(masses, xcoords, ycoords, n)
    ! constructor for a dens_map where the xcoords and ycoords are of type integer. 
    ! masses is an array containing the mass of each density, and xcoords & ycoords contain the x and y coordinates. These need to be listed for densities in the same order. n is the number of densities (max 4). 
        integer, intent(in)           :: n, masses(n), xcoords(n), ycoords(n)
        type(dens_map)                :: new_dens_map_set_i
        new_dens_map_set_i = new_dens_map()
        call set_dens_map(new_dens_map_set_i, masses, xcoords, ycoords, n)
        return
    end function new_dens_map_set_i
    
    function new_dens_map_set_r(masses, xcoords, ycoords, n)
    ! constructor for a dens_map where the xcoords and ycoords are of type real. 
    ! masses is an array containing the mass of each density, and xcoords & ycoords contain the x and y coordinates. These need to be listed for densities in the same order. n is the number of densities (max 4). 
        integer, intent(in)           :: n, masses(n)
        real, intent(in)              :: xcoords(n), ycoords(n)
        type(dens_map)                :: new_dens_map_set_r
        new_dens_map_set_r = new_dens_map()
        call set_dens_map(new_dens_map_set_r, masses, xcoords, ycoords, n)
        return
    end function new_dens_map_set_r
    
    subroutine set_dens_map_i(dmap, masses, xcoords, ycoords, n)
    ! is to set the dens_map dmap. 
    ! masses is an array containing the mass of each density, and xcoords & ycoords contain the x and y coordinates. These need to be listed for densities in the same order. n is the number of densities (max 4). 
        type(dens_map), intent(inout) :: dmap
        integer, intent(in)           :: n
        integer, intent(in)           :: masses(n), xcoords(n), ycoords(n)
        integer                       :: i, j, k, order(6)
        real                          :: temp_holder(6)
        dmap%mass = 0
        dmap%coord = 0
        dmap%dist = 0.
        dmap%n_dens = n
        do i=1,n
            dmap%mass(i) = masses(i)
            dmap%coord(i,1) = xcoords(i)
            dmap%coord(i,2) = ycoords(i)
        end do
        k = 0
        do i=1,n-1
            do j=i+1,n
                k = k + 1
                dmap%dist(k) = euclid(dmap%coord(i,:), dmap%coord(j,:))
            end do
        end do
        ! sort values in dist. 
        order = order_array(dmap%dist, 6)
        temp_holder = dmap%dist
        do i=1,6
            dmap%dist(i) = temp_holder(order(i))
        end do
    end subroutine set_dens_map_i
    
    subroutine set_dens_map_r(dmap, masses, xcoords, ycoords, n)
    ! is to set the dens_map dmap. 
    ! masses is an array containing the mass of each density, and xcoords & ycoords contain the x and y coordinates. These need to be listed for densities in the same order. n is the number of densities (max 4). 
        type(dens_map), intent(inout) :: dmap
        integer, intent(in)           :: n
        integer, intent(in)           :: masses(n)
        real, intent(in)              :: xcoords(n), ycoords(n)
        integer                       :: i, j, k, order(6)
        real                          :: temp_holder(6)
        dmap%mass = 0
        dmap%coord = 0.
        dmap%dist = 0.
        dmap%n_dens = n
        do i=1,n
            dmap%mass(i) = masses(i)
            dmap%coord(i,1) = xcoords(i)
            dmap%coord(i,2) = ycoords(i)
        end do
        k = 0
        do i=1,n-1
            do j=i+1,n
                k = k + 1
                dmap%dist(k) = euclid(dmap%coord(i,:), dmap%coord(j,:))
            end do
        end do
        ! sort values in dist. 
        order = order_array(dmap%dist, 6)
        temp_holder = dmap%dist
        do i=1,6
            dmap%dist(i) = temp_holder(order(i))
        end do
    end subroutine set_dens_map_r
    
    function dist_dens_map(dmap)
    ! returns an array with the distances between points in a dist_map (dmap) starting with the largest value. 
        type(dens_map), intent(in)      :: dmap
        real                            :: dist_dens_map(6)
        dist_dens_map = dmap%dist
        return
    end function dist_dens_map
    
    function mass_dens_map(dmap)
    ! returns an array with the masses of points in dist_map (dmap). 
        type(dens_map), intent(in)      :: dmap
        integer                         :: mass_dens_map(4)
        mass_dens_map = dmap%mass
        return
    end function mass_dens_map
    
    function coord_dens_map(dmap)
    ! returns an array with the x and y coordinates of points in dist_map (dmap). 
        type(dens_map), intent(in)      :: dmap
        real                            :: coord_dens_map(4,2)
        coord_dens_map = dmap%coord
        return
    end function coord_dens_map
    
    function n_dens_map(dmap)
    ! returns the number of densities in the dens_map dmap. 
        type(dens_map), intent(in)      :: dmap
        integer                         :: n_dens_map
        n_dens_map = dmap%n_dens
        return
    end function n_dens_map
    
    function pearsn_dens_map(dmap1, dmap2)
    ! calculates the pearson coefficient between two dens_maps. 
    ! not tested
        type(dens_map), intent(in)      :: dmap1, dmap2
        real                            :: pearsn_dens_map
        pearsn_dens_map = pearsn(dmap1%dist, dmap2%dist, 6)
        return
    end function pearsn_dens_map
    
    function euclid_dens_map(dmap1, dmap2)
    ! calculates the Euclidian distance between two dens_maps based on distances between points. 
        type(dens_map), intent(in)      :: dmap1, dmap2
        real                            :: euclid_dens_map
        euclid_dens_map = euclid(dmap1%dist, dmap2%dist)
        return
    end function euclid_dens_map
    
    subroutine write_dist(dmap)
    ! writes the distances between points in the dens_map (dmap). 
        type(dens_map), intent(in)      :: dmap
        write(*,*) dmap%dist(1), dmap%dist(2), dmap%dist(3), dmap%dist(4), dmap%dist(5), dmap%dist(6)
    end subroutine write_dist
    
    subroutine write_mass_coord(dmap)
    ! writes the masses and coordinates of points in the dens_map (dmap). 
        type(dens_map), intent(in)      :: dmap
        integer                         :: n
        write(*,*) '    mass        x-coord        y-coord'
        do n=1,4
            write(*,*) dmap%mass(n), dmap%coord(n,1), dmap%coord(n,2)
        end do
    end subroutine write_mass_coord
    
    function order_array_r(arr, length)
    ! finds the order of a 1D array (arr) of size length of real numbers. Returns an array of equal size listing the coordinates from largest to smallest. (Move to another location?)
        integer, intent(in)        :: length
        real, intent(in)           :: arr(length)
        integer                    :: order_array_r(length)
        integer                    :: i, n
        real                       :: arr_holder(length)
        arr_holder = arr
        do i=1,length
            do n=1,length
                if ( arr_holder(n) == maxval(arr_holder) ) then
                    order_array_r(i) = n
                    arr_holder(n) = minval(arr_holder)-1.
                    exit
                end if
            end do
        end do
        return
    end function order_array_r
    
    function order_array_i(arr, length)
    ! finds the order of a 1D array (arr) of size length of real numbers. Returns an array of equal size listing the coordinates from largest to smallest. (Move to another location?)
        integer, intent(in)        :: length
        integer, intent(in)        :: arr(length)
        integer                    :: order_array_i(length)
        integer                    :: i, n
        real                       :: arr_holder(length)
        arr_holder = arr
        do i=1,length
            do n=1,length
                if ( arr_holder(n) == maxval(arr_holder) ) then
                    order_array_i(i) = n
                    arr_holder(n) = minval(arr_holder)-1
                    exit
                end if
            end do
        end do
        return
    end function order_array_i
    
    function cenmass_dens_map(dmap)
    ! finds the center of mass of the dens_map (dmap). cenmass_dens_map(1) = x-coord; cenmass_dens_map(2) = y-coord. 
        real                                    :: cenmass_dens_map(2)
        type(dens_map), intent(in)              :: dmap
        real                                    :: xsum, ysum, msum
        integer                                 :: i
        msum = sum(dmap%mass)
        xsum = 0.
        ysum = 0.
        do i=1,4
            xsum = xsum + (dmap%coord(i,1) * real(dmap%mass(i)))
            ysum = ysum + (dmap%coord(i,2) * real(dmap%mass(i)))
        end do
        cenmass_dens_map(1) = xsum / msum
        cenmass_dens_map(2) = ysum / msum
        return
    end function cenmass_dens_map
    
    subroutine shift_dens_map_i(dmap, xshift, yshift)
    ! shift a dens_map (dmap) by xshift and yshift. 
        type(dens_map), intent(inout)   :: dmap
        integer, intent(in)             :: xshift, yshift
        integer                         :: i
        do i=1,4
            if (dmap%mass(i) .ne. 0) then
                dmap%coord(i,1) = dmap%coord(i,1) + xshift
                dmap%coord(i,2) = dmap%coord(i,2) + yshift
            end if
        end do
    end subroutine shift_dens_map_i
    
    subroutine shift_dens_map_r(dmap, xshift, yshift)
    ! shift a dens_map (dmap) by xshift and yshift. 
        type(dens_map), intent(inout)   :: dmap
        real, intent(in)                :: xshift, yshift
        integer                         :: i
        do i=1,4
            if (dmap%mass(i) .ne. 0) then
                dmap%coord(i,1) = dmap%coord(i,1) + xshift
                dmap%coord(i,2) = dmap%coord(i,2) + yshift
            end if
        end do
    end subroutine shift_dens_map_r
    
    function closest_pts(dmap1, dmap2)
    ! for each point in dmap1, finds the closest point in dmap2. Returns a vector of length 4; closest_pts(i) is the index of the point in dmap2 that is closest to point i of dmap1. 
        type(dens_map), intent(in)      :: dmap1, dmap2
        integer                         :: closest_pts(4)
        real                            :: dist_table(4,4), d
        integer                         :: i, j, n
        dist_table = 0
        do i=1,4
            do j=1,4
                d = euclid(dmap1%coord(i,:), dmap2%coord(j,:))
                dist_table(i,j) = d
            end do
        end do
        do i=1,4
            n = 1
            do j=2,4
                if ((dist_table(i,j) < dist_table(i,n)) .and. (dmap2%mass(j) /= 0)) n=j
            end do
            closest_pts(i) = n
        end do
        return
    end function closest_pts
    
    subroutine rotate_dens_map(dmap, angle, box)
    ! rotates dens_map (dmap) counter clockwise by the angle in radians. 
        type(dens_map), intent(inout)   :: dmap
        real, intent(in)                :: angle
        real                            :: cosangle, sinangle, center, x(4), y(4)
        integer, intent(in)             :: box
        center = (box+1.)/2. !changed
        cosangle = cos(angle)
        sinangle = sin(angle)
        x = (dmap%coord(:,1)-center)*cosangle - (dmap%coord(:,2)-center)*sinangle + center
        y = (dmap%coord(:,1)-center)*sinangle + (dmap%coord(:,2)-center)*cosangle + center
        dmap%coord(:,1) = x
        dmap%coord(:,2) = y
    end subroutine rotate_dens_map
    
    subroutine center_dens_map(dmap, box)
    ! center a dens_map based on center of mass
        type(dens_map), intent(inout)   :: dmap
        integer, intent(in)             :: box
        real                            :: cmass(2), shift(2), center
        center = (box+1.)/2.
        cmass = cenmass_dens_map(dmap)
        shift = center - cmass
        call shift_dens_map(dmap, shift(1), shift(2))
    end subroutine center_dens_map
    
    function best_rmsd_dmap(dmap1, dmap2, box)
    ! finds rmsd between centers of two dens_maps, dmap1 and dmap2, for every 1 degree out of 360 degrees (rotating dmap1) and returns the best one. box is the length of the image in pixels. Note: dmap1 and dmap2 should have the same number of densities, but best_rmsd_dmap will return something even if they don't. 
        type(dens_map), intent(in)      :: dmap1, dmap2
        integer, intent(in)             :: box
        real                            :: best_rmsd_dmap, pi, rmsd_tmp, angle_to_rotate
        real                            :: center, shift(2)
        integer                         :: angle_degrees, i, n, closest(4)
        type(dens_map)                  :: dm1, dm2, dm1_temp
        if (n_dens_map(dmap1) /= n_dens_map(dmap2)) then
            best_rmsd_dmap = box*sqrt(2.) ! largest possible; don't bother computing if # densities is different
        else
            pi = acos(-1.)
            dm1 = dmap1
            dm2 = dmap2
            ! shift dm1 and dm2 so that the center is at the center of mass. 
            center = (box+1.)/2.
            shift = center - cenmass_dens_map(dm1)
            call shift_dens_map(dm1, shift(1), shift(2))
            shift = center - cenmass_dens_map(dm2)
            call shift_dens_map(dm2, shift(1), shift(2))
            best_rmsd_dmap = box*sqrt(2.) ! largest possible rmsd
            angle_to_rotate = (2.*pi)/360.
            n = n_dens_map(dmap1)
            do angle_degrees = 1, 360
                dm1_temp = dm1
                call rotate_dens_map(dm1_temp, angle_to_rotate*real(angle_degrees), box)
                closest = closest_pts(dm1_temp, dm2)
                rmsd_tmp = 0.
                do i=1,n
                    rmsd_tmp = rmsd_tmp + (dm1_temp%coord(i,1) - dm2%coord(closest(i),1))**2. + (dm1_temp%coord(i,2) - dm2%coord(closest(i),2))**2. 
                end do
                rmsd_tmp = sqrt(rmsd_tmp/n)
                if (rmsd_tmp < best_rmsd_dmap) best_rmsd_dmap=rmsd_tmp
            end do
        end if
        return
    end function best_rmsd_dmap
    
    function dist_btwn_dens_maps(dmap1, dmap2)
    ! Euclidean distance between two dens_maps. 
        type(dens_map), intent(in)      :: dmap1, dmap2
        integer                         :: closest1(4), closest2(4), n
        real                            :: dist_btwn_dens_maps, dist1, dist2
        logical                         :: same(4)
        ! closest1(i) is the index of the point in dmap2 that is closest to point i of dmap1.
        closest1 = closest_pts(dmap1, dmap2)
        closest2 = closest_pts(dmap2, dmap1)
        dist1 = 0.
        dist2 = 0.
        same = .TRUE.
        do n=1,dmap1%n_dens
            dist1 = dist1 + euclid(dmap1%coord(n,:),dmap2%coord(closest1(n),:))
            ! Check if any points are used twice in the calculation. 
            same(n) = closest2(closest1(n)) == n
        end do
        if (any(same /= .TRUE.)) then
            do n=1,dmap2%n_dens
                dist2 = dist2 + euclid(dmap1%coord(closest2(n),:),dmap2%coord(n,:))
            end do
        end if
        dist_btwn_dens_maps = max(dist1, dist2)
        return
    end function dist_btwn_dens_maps
    
    subroutine flush_dens_maps(dmap_arr, arr_size)
    ! takes an array of dens_map and stores the info in the file dens_maps.txt. 
        integer, intent(in)                     :: arr_size
        type(dens_map), intent(in)              :: dmap_arr(arr_size)
        integer                                 :: i, file_stat, temp_mass(4)
        real                                    :: temp_coord(4,2)
        open(unit=14, file='dens_maps.txt', status='replace', iostat=file_stat,&
        access='direct', form='formatted', recl=94, action='write')
        if( file_stat /= 0 )then ! cannot open file
            write(*,*) 'Cannot open file: ', 'dens_maps.txt'
            write(*,*) 'In module: simple_dens_map; subroutine: flush_dens_maps'
            stop
        endif
        do i=1,arr_size
            temp_mass = mass_dens_map(dmap_arr(i))
            temp_coord = coord_dens_map(dmap_arr(i))
            write(14, "(4I5, 8F9.4, I2)", rec=i) temp_mass(1), temp_mass(2), temp_mass(3), temp_mass(4), temp_coord(1,1), temp_coord(2,1), temp_coord(3,1), temp_coord(4,1), temp_coord(1,2), temp_coord(2,2), temp_coord(3,2), temp_coord(4,2), dmap_arr(i)%n_dens
        end do
        close(14)
    end subroutine flush_dens_maps
    
    subroutine get_dens_maps(dmap_arr, arr_size)
    ! Gets the file dens_maps.txt and moves the info to an array of dens_map. 
        integer, intent(in)                     :: arr_size
        type(dens_map)                          :: dmap_arr(arr_size)
        integer                                 :: i, file_stat, temp_mass(4), n_densities
        real                                    :: temp_coord(4,2)
        open(unit=14, file='dens_maps.txt', status='old', iostat=file_stat,&
        access='direct', form='formatted', recl=94, action='read')
        if( file_stat /= 0 )then ! cannot open file
            write(*,*) 'Cannot open file: ', 'dens_maps.txt'
            write(*,*) 'In module: simple_dens_map; subroutine: get_dens_maps'
            stop
        endif
        do i=1,arr_size
            read(14, "(4I5, 8F9.4, I2)", rec=i) temp_mass(1), temp_mass(2), temp_mass(3), temp_mass(4), temp_coord(1,1), temp_coord(2,1), temp_coord(3,1), temp_coord(4,1), temp_coord(1,2), temp_coord(2,2), temp_coord(3,2), temp_coord(4,2), n_densities
            call set_dens_map(dmap_arr(i), temp_mass(:n_densities), temp_coord(:n_densities,1), temp_coord(:n_densities,2), n_densities)
        end do
        close(14)
    end subroutine get_dens_maps
    
    function avg_dmap(dmap1, dmap2, weight1, weight2)
    ! Makes a new dens_map by averaging masses and coordinates of points according to weights
    ! Note: masses are integers so this isn't very accurate for masses!! (doesn't matter right now
    ! so not bothering to change but could affect things in the future)
        real, intent(in)                :: weight1, weight2
        type(dens_map), intent(in)      :: dmap1, dmap2
        type(dens_map)                  :: avg_dmap
        real                            :: coord_avg(4,2)
        integer                         :: mass_avg(4), n_dens
        integer                         :: closest12(4), i
        ! will have to think about this more...
        n_dens = max(dmap1%n_dens,dmap2%n_dens)
        closest12 = closest_pts(dmap1, dmap2)
        do i=1,n_dens
            coord_avg(i,:) = (dmap1%coord(i,:)*weight1 + dmap2%coord(closest12(i),:)*weight2) / (weight1 + weight2)
            mass_avg(i) = nint(dmap1%mass(i)*weight1 + dmap2%mass(closest12(i))*weight2) / (weight1 + weight2)
        end do
        avg_dmap = new_dens_map(mass_avg, coord_avg(:,1), coord_avg(:,2), n_dens)
        return
    end function avg_dmap
    
    function dmap_to_pts(dmap, box)
    ! Converts a dens_map object to a pts object (loses information about mass) and returns the 
    ! pts object. 
    ! 	    dmap	dens_map to convert
    ! 	    box		box size in pixels (width of the square image), used for centering
        type(dens_map), intent(in)	:: dmap
	integer, intent(in)		:: box
	type(pts)			:: dmap_to_pts
	type(dens_map)			:: temp_dmap
	real				:: coords(dmap%n_dens,2)
	integer				:: i
	temp_dmap = dmap
	call center_dens_map(temp_dmap, box)
	do i=1,temp_dmap%n_dens
	    coords(i,:) = temp_dmap%coord(i,:)
	end do
	dmap_to_pts = new_pts(temp_dmap%n_dens,2,coords)
        return
    end function dmap_to_pts
    
end module simple_dens_map