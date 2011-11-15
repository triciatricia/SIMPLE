! -------------------------------------------------------------------------------------
! A module for aligning dens_maps (abbreviated "dmap") using Simple Differential Evolution (Simple DE). 
! See simple_dens_map.f90 for more info about dens_maps, and simple_de_opt.f90 for more 
! information about Simple DE optimization. 
! -------------------------------------------------------------------------------------

module simple_dens_map_align
use simple_dens_map
use simple_de_opt
implicit none
save

! Variables:
! bx = box size of the image in pixels
! center = array of the coordinates of the center of the image x,y
! num_dmap = the number of dens_maps.
! dmap_arr = the array of dens_maps to align. 
! num_params = the number of parameters = num_dmap - 1

integer, private                        :: num_dmap, num_params, bx
type(dens_map), private, allocatable    :: dmap_arr(:)
real, private                           :: center(2)

contains
    
    subroutine init_dmap_align(dmap_arr_in, num_dmap_in, box_in)
    ! Initialize values for optimization alignment. 
        integer, intent(in)             :: num_dmap_in, box_in
        type(dens_map), intent(in)      :: dmap_arr_in(num_dmap_in)
        integer                         :: alloc_stat, n
        ! Set variables bx, num_dmap, dmap_arr, num_params
        bx = box_in
        center = real(bx+1)/2
        num_dmap = num_dmap_in
        num_params = num_dmap - 1
        ! Check if dmap_arr is already allocated from a previous call. 
        if (allocated(dmap_arr)) then
            deallocate(dmap_arr)
        end if
        allocate(dmap_arr(num_dmap), stat=alloc_stat)
        call alloc_err('In: simple_dens_map_align.f90: init_dmap_align', alloc_stat)
        dmap_arr = dmap_arr_in
        ! Center dens_maps based on center of mass. 
        do n=1,num_dmap
            call center_dens_map(dmap_arr(n), bx)
        end do
    end subroutine init_dmap_align
    
    !What the cost function is supposed to look like.
    function cost_dmap(param,param_size)
    ! Cost for aligning dmap. Parameters in param (aka: vec). Size of the vector param = param_size (aka: D). THe parameters are the angles to rotate each dens_map, except for the last one. The last dens_map in the array does not get rotated. 
        real                            :: cost_dmap
        integer, intent(in)             :: param_size
        real, intent(in)                :: param(param_size)
        type(dens_map)                  :: dmap_rot(num_dmap) !array of rotated dens_map
        integer                         :: n, m
        real                            :: dist
        ! Rotate the dens_maps according to the parameter specified. Calculate cost. 
        dmap_rot = dmap_arr
        do n=1,param_size
            call rotate_dens_map(dmap_rot(n), param(n), bx) ! bx is a global variable
        end do
        ! Calculate the Euclidean distances between coordinates of each rotated dens_map.
        dist = 0.
        do n=1, num_dmap-1
            do m=n+1, num_dmap
                dist = dist + dist_btwn_dens_maps(dmap_rot(n),dmap_rot(m))
            end do
        end do
        dist = dist * 2.
        cost_dmap = dist
        return
    end function cost_dmap

end module simple_dens_map_align