!==Program resolve
!
! _resolve_ is a program for heterogeneity analysis of a spider stack given 3D alignment parameters (obtained by program align).  
! The stack is in-plane rotated and classified before applying to the class averages a model-based refinement procedure based on 
! deterministic annealing for soft parameter assignment. Low-resolution molecular envelopes of the different states are reconstructed
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
program resolve
use simple_params
use simple_rnd
use simple_rbased_search
use simple_build
use simple_ran_tabu
use simple_fgridvol
use simple_cmdline
use simple_jiffys
use simple_fstk
implicit none
save
type(build), target  :: b
integer              :: alloc_stat, i, j, k
logical              :: cmderr(6)
real                 :: e1, e2, e3
type(ran_tabu)       :: rt
integer, allocatable :: closest(:)
real, allocatable    :: weights(:), stateweights(:)
character(len=32)    :: dig, vnam
if( command_argument_count() < 6 )then
    write(*,*) './resolve fstk=cavgstk.fim nstates=<nr of states to resolve> lp=<low-pass limit(in A){15-30}> msk=<mask radius in pixels> maxits=<maximum nr of iterations{6-10}> nthr=<nr openMP threads> [vol1=<startvol.spi>] [nbest_start=<start neighborhood>] [nbest_stop=<stop neighborhood>] [hp=<high-pass limit (in A){100}>] [debug=<yes|no>]'
    stop
endif
call parse_cmdline
! check command line args
cmderr(1) = .not. defined_cmd_carg('fstk')
cmderr(2) = .not. defined_cmd_rarg('nstates')
cmderr(3) = .not. defined_cmd_rarg('lp')
cmderr(4) = .not. defined_cmd_rarg('msk')
cmderr(5) = .not. defined_cmd_rarg('maxits')
cmderr(6) = .not. defined_cmd_rarg('nthr')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for resolve defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif

! introduce two modes, one without starting volume and one with

b = new_build(10) ! mode=10 & mode=2, check this
! seed the random number generator
call seed_rnd
! set nbest to 10
nbest=10
! allocate what is needed
allocate( closest(nbest), weights(nbest), stateweights(nstates), stat=alloc_stat )
call alloc_err('In: resolve', alloc_stat)
! make a random start
call make_fgridvol( b, 'old' )
if( vols(1) == '' )then
    write(*,'(A)') '>>> MAKING RANDOM STARTING SOLUTIONS'
    ! zero the Fourier volumes
    do k=1,nstates
        b%s3d(k)%fvol = cmplx(0.,0.)
        ! zero the kernels
        b%s3d(k)%kernel = 0.
    end do
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
        call gen_wvec(stateweights)  
        ! grid
        do k=1,nstates
            do j=1,nbest
                call get_euler( b%e, closest(j), e1, e2 )
                call grid_fplane( e1, e2, 0., 0., 0., k, stateweights(k)*weights(j) )
            end do
        end do
    end do
    ! low-pass filter volumes
    do k=1,nstates
        write(dig,*) k
        vnam = 'rndstart_state'//trim(adjustl(dig))//'.spi'
        call lp_fvol( b, k, lp )
        ! reverse transform volume
        call fft_rev_fvol( b, k )
        ! output starting solution
        call write_volspi( b%s3d(k)%vspi, vnam )
    end do
endif
! make rbased refinement functionality
call make_rbased_search( b )
! refine
call soft_refine( b )
! end gracefully
call haloween( 0 )
write(0,'(A)') "**** RESOLVE NORMAL STOP ****"
end program resolve