!==Program abinirec
!
! _Abinirec_ is a program for ab initio 3D reconstruction from class averages. The algorithm is model-based, uses 
! deterministic annealing to do soft orientation assignment. A low-resolution molecular envelope is reconstructed
! in an iterative fashion (Expectation Maximization). No assumption about the existence of common lines is made.
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_.
! Redistribution and modification is regulated by the GNU General Public License.
! *Author:* Hans Elmlund 2009-05-26.
!
!==References
!
!* NOT PUBLISHED
!
!==Changes are documented below
!
!*
! 
program abinirec
use simple_params
use simple_rnd
use simple_rbased_search
use simple_build
use simple_ran_tabu
use simple_fgridvol
use simple_cmdline
use simple_jiffys
implicit none
save
type(build), target  :: b
real                 :: e1, e2, e3
integer              :: i, j, alloc_stat
type(ran_tabu)       :: rt
logical              :: cmderr(5)
integer, allocatable :: closest(:)
real, allocatable    :: weights(:)
if( command_argument_count() < 5 )then
    write(*,*) './abinirec fstk=cavgstk.fim lp=<low-pass limit(in A){20-30}> msk=<mask radius in pixels> maxits=<maximum nr of iterations{6-10}> nthr=<nr openMP threads> [vol1=<startvol.spi>] [nbest_start=<start neighborhood>] [nbest_stop=<stop neighborhood>] [hp=<high-pass limit (in A){100}>] [debug=<yes|no>]'
    stop
endif
! parse command line
call parse_cmdline
! check command line arguments
cmderr(1) = .not. defined_cmd_carg('fstk')
cmderr(2) = .not. defined_cmd_rarg('lp')
cmderr(3) = .not. defined_cmd_rarg('msk')
cmderr(4) = .not. defined_cmd_rarg('maxits')
cmderr(5) = .not. defined_cmd_rarg('nthr')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for abinirec defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif
! seed the random number generator
call seed_rnd
! build all objects required for reference-free alignment
b = new_build( 10 )
! set nbest to 10
nbest=10
! allocate
allocate( closest(nbest), weights(nbest), stat=alloc_stat )
call alloc_err( 'In: abinirec', alloc_stat )
! make a random start
winsz=2
wchoice=2
call make_fgridvol( b, 'old' )
if( vols(1) == '' )then
    write(*,'(A)') '>>> MAKING A RANDOM STARTING SOLUTION'
    ! zero the Fourier volume
    b%s3d(1)%fvol = cmplx(0.,0.)
    ! zero the kernels
    b%s3d(1)%kernel = 0.
    ! make random nr func
    rt = new_ran_tabu(nspace)
    do i=1,nptcls
        call print_bar( i, nptcls, '=' )
        ! read the Fourier plane from stack
        call read_fplane( b%f(ptcl)%arr, fstk, i )
        ! pick a random projection direction
        b%statearr(i) = irnd_uni_tabu(rt)
        call insert_ran_tabu(rt, b%statearr(i))
        call get_euler(b%e, b%statearr(i), e1, e2, e3)
        ! generate weights for the neighboring directions 
        closest = find_closest_eulers(b%e, e1, e2, nbest)
        call gen_wvec(weights)
        ! grid 
        do j=1,nbest
            call get_euler(b%e, closest(j), e1, e2 )
            call grid_fplane(e1, e2, 0., 0., 0., 1, weights(j))
        end do
    end do
    ! low-pass filter volume
    call lp_fvol( b, 1, lp )
    ! reverse transform volume
    call fft_rev_fvol( b, 1 )
    ! output starting solution
    call write_volspi( b%s3d(1)%vspi, 'rndstart.spi' )
endif
! make rbased refinement functionality
call make_rbased_search( b )
! refine
call soft_refine( b )
! end gracefully
call haloween( 0 )
write(0,'(A)') "**** ABINIREC NORMAL STOP ****"
end program abinirec