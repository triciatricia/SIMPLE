! -------------------------------------------------------------------------------------
! center_densities centers images based on center of mass. 
!
! Command Arguments
!   - stk = file name of input stack of images that you are centering
!   - outstk = file name of the output stack of centered images
!   - box = length of a side of the image in pixels (image is square shaped)
!   - nptcls = number of particles
! 
! Requires the following files to be present: 
!   - dens_maps.txt
!     A direct access text file containing the four masses, four x-coordinates, four y-coordinates
!     and number of densities for each image. If an image has fewer than 4 densities, the
!     extra values will be 0. (Format: "(4I5, 8F9.4, I2)")
! 
! Creates the following file: 
!   - <stkout>
!     Spider image stack of centered images. 
! -------------------------------------------------------------------------------------

program center_densities
use simple_stkspi
use simple_imgspi
use simple_math
use simple_cmdline
use simple_params
use simple_dens_map
implicit none

integer                                 :: i, n, shift(2)
integer                                 :: file_stat, alloc_stat
real					:: center, cmass(2)
type(stkspi)                            :: stack, stack_out
type(imgspi)                            :: img
type(dens_map), allocatable             :: dens_maps(:)
character(len=256)                      :: stkconv

if( command_argument_count() < 4 )then
    write(*,*) './center_densities stk=inputstk.spi outstk=outputstk.spi box=200 nptcls=10329 [debug=<yes|no>]'
    stop
endif

! parse command line args
call parse_cmdline
call make_params() 

! allocate
allocate(dens_maps(nptcls), stat=alloc_stat)
call alloc_err('In program: center_densities', alloc_stat)

! -------------------------------------------------------------------------------------
! Recover Data from File
! -------------------------------------------------------------------------------------
! read dens_maps from file
write(*,*) 'Reading dens_maps from file.'
call get_dens_maps(dens_maps, nptcls)

! -------------------------------------------------------------------------------------
! Shift Images and Output to File
! -------------------------------------------------------------------------------------
write(*,*) 'Shifting images and writing to file.'
img = new_imgspi(box)
stack = new_stkspi( name=stk )
stack_out = new_stkspi()
call write_stk_hed( stack_out, outstk )
! determine how to convert the stack
call find_stkconv( stack, stk, stkconv )

 center = (box+1.)/2.
do i=1,nptcls
    call read_imgspi(stack, stk, i, img, stkconv) 
    cmass = cenmass_dens_map(dens_maps(i))
    shift = nint(center - cmass)
    call shift_imgspi_3( img, shift )
    call write_imgspi( stack_out, outstk, i, img )
end do

end program center_densities