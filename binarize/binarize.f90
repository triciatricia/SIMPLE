! -------------------------------------------------------------------------------------
! binarize takes a stack of 2D spider images (stk) and applies a low pass filter with low pass limit (lp), binarizes using a threshold intensity (tres), and sets pixels beyond a mask radius (msk) from the center to the background intensity. 
! 
! Input:
!   - stk = stack of spider images to binarize
!   - lp = low pass limit for the low pass filter
!   - stktyp = image created using spider or eman (try eman if image made in Simple)
!   - box = length of an edge of the image in pixels (images are square shaped)
!   - nptcls = number of images in the stack
!   - smpd = sampling distance in Angstroms per pixel
!   - msk = mask radius in pixels (useful if your image size is larger than the particle
!     that you are imaging and want to ignore anything beyond a radius)
!   - outstk = the output spider stack file name for the binarized images
!   - tres = threshold intensity for the binarizing. Pixels with values above tres 
!     will be set to the foreground value, and pixels below or equal to tres will be 
!     set to the background value. 
! -------------------------------------------------------------------------------------

program binarize
use simple_stkspi
use simple_imgspi
use simple_math
use simple_params
use simple_jiffys
use simple_ffts
use simple_fplane
! use gnufor2
implicit none
save
type(imgspi)  :: img
type(stkspi)  :: stack, stack_out
integer       :: alloc_stat, i
real, pointer :: img_pointer(:,:)=>null()
complex, allocatable :: ft(:,:)
character(len=256) :: stkconv

if( command_argument_count() < 8 )then
    write(*,*) './binarize stk=inputstk.spi lp=40 box=100 nptcls=10000 smpd=2.33 msk=40 outstk=ouputstk.spi tres=0.5 [debug=<yes|no>]'
    stop
endif

! parse command line args
call make_params

! make image
img = new_imgspi()

! make stacks
stack = new_stkspi( name=stk )
stack_out = new_stkspi()

! determine how to convert the stack
call find_stkconv( stack, stk, stkconv )

! allocate
allocate( ft(-xdim:xdim,-xdim:xdim) )

! read images
do i=1,nptcls  
    call read_imgspi( stack, stk, i, img, stkconv )
!    call plot_imgspi( img )
    call shift_imgspi( img )
    call get_imgspi_ptr( img, img_pointer ) !returns a pointer img_pointer to volume data (rmat)
    call simple_2dfft( img_pointer, box, ft )
    call lp_fplane( ft, lp )
!    call lp_ft( ft, xdim, lplim, dstep, lp )
    call simple_2dfft_rev( ft, box, img_pointer )
    call shift_imgspi( img ) !Assume that an image shifted twice is the same as the original.
!    call plot_imgspi( img )
    call bin_imgspi( img, tres,  msk )
!    call plot_imgspi( img )
    call write_stk_hed( stack_out, outstk )
    call write_imgspi( stack_out, outstk, i, img )
end do

end program binarize