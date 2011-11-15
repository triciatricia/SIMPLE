program test_imgspi_mod
! -------------------------------------------------------------------------------------
! I will use this to test the identify_densities_imgspi modifications to simple_imgspi and dens_map_mod by plotting. 
!
! Inputs:
!   - stk = a spider stack of spider images
!   - outstk = a spider stack of binarized spider images
!   - stktyp = the program used to make the images (try eman if images made with Simple)
!   - box = the length of the image in pixels
!   - nptcls is the number of particles that you want to plot. 
! -------------------------------------------------------------------------------------

use simple_params
use simple_dens_map
use simple_imgspi
use simple_stkspi
use tester_mod
implicit none
save

type(stkspi)                    :: stack, binstack
type(imgspi)                    :: img, imgbin
type(dens_map)                  :: img_dens_map
integer                         :: alloc_stat, i
character(len=256)              :: stkconv, binstkconv

if( command_argument_count() < 5 )then
    write(*,*) './test_imgspi_mod stk=inputstk.spi outstk=binarystk.spi stktyp=<spider|eman> box=200 nptcls=5  [debug=<yes|no>]'
    stop
endif

! parse command line args
call make_params

! make stacks
stack = new_stkspi( name=stk )
binstack = new_stkspi( name=outstk )
! determine how to convert the stacks
call find_stkconv( stack, stk, stkconv )
call find_stkconv( stack, stk, binstkconv )

! make image
img = new_imgspi()
imgbin = new_imgspi()

! for each image, identify densities and store information in dens_maps
do i=1,nptcls
    call read_imgspi( stack, stk, i, img, stkconv )
    call read_imgspi( binstack, outstk, i, imgbin, binstkconv )
    call identify_densities_imgspi( imgbin, box, 4, 4, img_dens_map )
    write(*,*) 'image', i
    call write_mass_coord(img_dens_map)
    call plot_dens_map_imgspi(img, img_dens_map)
    call plot_dens_map_imgspi(imgbin, img_dens_map)
end do


end program test_imgspi_mod