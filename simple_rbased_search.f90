!==Class simple_rbased_search
!
! The simple_rbased_search singleton encapsulates the orienetation search methods in the _SIMPLE_ library,
! enabling code reuse. Search strategies include exhaustive approaches, Monte Carlo, and directed search via
! differential evolution optimization. The composite object is built from objects responsible for optimization, 
! storing ouput data, generation of random numbers, CPU time checking and calculation of common 
! line correlations. The simple_rbased_search, simple_comlin_corr, and simple_fplanes_corr classes form an entangled triplet
! where the pointers required for calculation of comlin correlations are associated by the simple_comlin_search 
! constructor defined below to variables of the comlin_search type. Therefore, the using unit need only to care 
! about the search itself and methods for modifying required variables (incrementor/setters) are defined here. 
! The code is distributed with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or 
! modification is regulated by the GNU General Public License. *Author:* Hans Elmlund, 2009-06-11.
! 
!==Changes are documented below
!
!* deugged and incorporated in the _SIMPLE_ library, HE 2009-06-25
!* revised the template-based search for multiple states (hopefully the final version), HE 2011-03-29
!
module simple_rbased_search
use simple_eulers
use simple_jiffys
use simple_fgridvol
use simple_rnd
use simple_spidoc
use simple_build
use simple_params
use simple_de_opt
use simple_sa_opt
use simple_aligndata
use simple_comlin_corr
use simple_fplanes_corr
use simple_ran_tabu
use simple_ts_opt
use simple_syscalls
use simple_heapsort
use simple_math
use simple_fplane
use simple_volspi
implicit none
save

public :: make_rbased_search, calc_lowpass_lims, soft_refine, rbased_evol_align ! quick_refine
private

interface de_ori_refinement
    module procedure de_ori_refinement_1
    module procedure de_ori_refinement_2
end interface

type(build), pointer :: bp=>null() ! pointer to builder
type(de_opt)         :: nasty     ! differential evolution object
type(ran_tabu)       :: tab

contains

    subroutine make_rbased_search( b )
    ! initializes the orientation search by setting mode-dependent variables and
    ! associating the pointers in the comlin_corr and fplanes_corr singletons.
    ! Also, the objects required for optimization are built.
        type(build), intent(in), target :: b
        real :: rslask
        ! make the differential evolution optimization obj
        nasty = new_de_opt( 5, optlims(:5,:), nbest, neigh, cyclic=cyclic(:5) )
        ! make fplanes corr obj
        call make_fplanes_corr( b )
        ! Assign ptr to builder in this object
        bp => b
        ! Get the actual and relative cpu-time
        rslask = getabscpu( .true. )
        rslask = getdiffcpu( .true. )
    end subroutine make_rbased_search

    subroutine calc_lowpass_lims
    ! is for calculating the ptcl-dependent lowpass limits used in 
    ! reference-based whole section alignment with spectral self-adaption     
        integer :: i, s
        real    :: e1, e2, e3, x, y, corrspec, lowpass, corr
        write(*,'(A)') '>>> CALCULATING LOW-PASS LIMITS'
        bp%arescorr = 0.
        do i=fromp,top
            bp%rescorr = 0.
            ! read the appropriate transform
            call read_fplane( bp%f(ptcl)%arr, fstk, i )
            ! Get the previously established orientation
            e1 = oris(i,1)
            e2 = oris(i,2)
            e3 = oris(i,3)
            x  = oris(i,4)
            y  = oris(i,5)
            state = int(oris(i,6))
            ! set global state variable
            state=s
            ! Calculate the the spectral correlation and the lowpass limit
            call corrspec_fplanes( e1, e2, e3, x, y, bp%rescorr, corrspec, lowpass )
            ! calculate the ordinary correlation
            corr = corr_fplanes( e1, e2, e3, x, y )
            ! Set the aligndata object accordingly
            call set_aligndata( bp%a, i, q=corrspec, lowpass=lowpass, corr=corr )
            ! check so that all correlations are positive
            where( bp%rescorr < 0. ) bp%rescorr = 0.
            ! Update arescorr (whole array addition)
            bp%arescorr = bp%arescorr+bp%rescorr
            if( mode == 23 ) then ! Print the data
                call print_aligndata( bp%a, i, corr='CORR:', q='Q:', lowpass='HRES:', state='STATE:' )
            endif
        end do
        ! Average arescorr over all ptcls (whole array division)
        bp%arescorr = bp%arescorr/real(top-fromp+1)
        write(*,'(A)') '>>> JOINT SPECTRAL CORRELATION PLOT'
        do i=fromk,tok ! Loop over Fourier indices
            write(*,"(1X,A,1X,F6.2,1X,A9,1X,F8.4)") '>>> RESOLUTION:', dstep/real(i), 'CORRSPEC:', bp%arescorr(i)
        end do
        write(*,"(1X,A,1X,F8.4)") '>>> CORRSPEC_SUM:', sum(bp%arescorr)
        lpmed = get_lowpass_median(bp%a) ! The median lowpass limit
    end subroutine calc_lowpass_lims
    
    subroutine exhaustive_euler_search( x, y )
    ! is for exhaustive angular search
        real, intent(in) :: x, y
        real             :: e1, e2, e3, corr, rsol(6)
        integer          :: j, k, cnt
        cnt = 0
        do j=1,nspace! projection direction loop
            call get_euler( bp%e, j, e1, e2, e3 )
            do k=1,ninpl ! inplane angle loop
                e3 = real(k-1)*angres
                rsol(1) = e1
                rsol(2) = e2
                rsol(3) = e3
                rsol(4) = x
                rsol(5) = y
                rsol(6) = 1 
                corr = corr_fplanes( e1, e2, e3, x, y )
                cnt = cnt+1
                call set_heapsort( bp%hso, cnt, corr, rarr=rsol )
            end do
        end do
        call sort_heapsort( bp%hso )
    end subroutine exhaustive_euler_search
    
    subroutine exhaustive_proj_search_1( e3, x, y )
    ! is for exhaustive projection direction search
        real, intent(in) :: e3, x, y
        real             :: e1, e2, corr, rsol(6), rslask
        integer          :: j
        do j=1,nspace! projection direction loop
            call get_euler( bp%e, j, e1, e2, rslask )
            rsol(1) = e1
            rsol(2) = e2
            rsol(3) = e3
            rsol(4) = x
            rsol(5) = y
            rsol(6) = 1
            corr = corr_fplanes( e1, e2, e3, x, y )
            call set_heapsort( bp%hso, j, corr, rarr=rsol )
        end do
        rsol = 0.
        do j=nspace+1,ninpl*nspace
            call set_heapsort( bp%hso, j, -1., rarr=rsol )
        end do
        call sort_heapsort( bp%hso )
    end subroutine exhaustive_proj_search_1
    
    subroutine exhaustive_proj_search_2( e3, x, y )
    ! is for exhaustive projection direction search
        real, intent(in) :: e3, x, y
        real             :: e1, e2, corr, rsol(6), rslask
        integer          :: j, s
        do j=1,nspace! projection direction loop
            call get_euler( bp%e, j, e1, e2, rslask )
            do s=1,nstates ! state loop
                state = s
                rsol(1) = e1
                rsol(2) = e2
                rsol(3) = e3
                rsol(4) = x
                rsol(5) = y
                rsol(6) = real(s)   
                corr = corr_fplanes( e1, e2, e3, x, y )
                call set_heapsort( bp%hso, j, corr, rarr=rsol )
            end do
        end do
        rsol = 0.
        do j=nspace*nstates+1,ninpl*nspace
            call set_heapsort( bp%hso, j, -1., rarr=rsol )
        end do
        call sort_heapsort( bp%hso )
    end subroutine exhaustive_proj_search_2
    
    subroutine de_ori_refinement_1( e1, e2, e3, x, y, lowpass, init_rsols, cost )
    ! is for global template-based refinement given an input solution population 
        real, intent(out)                              :: e1, e2, e3, x, y
        real, intent(in)                               :: lowpass  
        real, intent(in), dimension(nbest,5), optional :: init_rsols
        real, intent(out), optional                    :: cost
        real                                           :: rsol(5), cost_here
        ! set low-pass limit
        lp_dyn = lowpass
        ! re-initialize the DE-pop
        if( present(init_rsols) )then
            call re_init_de_opt( nasty, optlims(:5,:), init_rsols(:,:5) )
        else
            call re_init_de_opt( nasty, optlims(:5,:) )
        endif
        if( lowpass > 20. .or. spec == 0 )then ! use the unweighted correlation
            call de_cont_min( nasty, cost_fplanes, 200, 0.0001, rsol, cost_here )
        else ! use the weighted one
            call de_cont_min( nasty, wcost_fplanes, 200, 0.0001, rsol, cost_here )
        endif
        e1 = rsol(1) 
        e2 = rsol(2)
        e3 = rsol(3)
        x  = rsol(4)
        y  = rsol(5)
        if( present(cost) )then
            cost = cost_here
        endif
    end subroutine de_ori_refinement_1

    subroutine de_ori_refinement_2( e1, e2, e3, x, y, lowpass, tres, cost )
    ! is for global template-based refinement given an input solution population 
        real, intent(inout) :: e1, e2, e3, x, y
        real, intent(in)    :: lowpass  
        real, intent(in)    :: tres
        real, intent(out)   :: cost
        real                :: rsol(5), cost_here
        lp_dyn = lowpass
        ! determine optimization limits
        call mkoptlims( e1, e2, e3, x, y, tres, optlims )
        ! re-initialize the DE-pop
        call re_init_de_opt( nasty, optlims(:5,:) )
        if( lowpass > 20. )then ! use the unweighted correlation
            call de_cont_min( nasty, cost_fplanes, 200, 0.0001, rsol(:5), cost_here )
        else ! use the weighted one
            call de_cont_min( nasty, wcost_fplanes, 200, 0.0001, rsol(:5), cost_here )
        endif
        e1 = rsol(1) 
        e2 = rsol(2)
        e3 = rsol(3)
        x  = rsol(4)
        y  = rsol(5)
        cost = cost_here
    end subroutine de_ori_refinement_2
    
    subroutine soft_refine( b )
        type(build), intent(inout) :: b
        integer                    :: i, j, s
        character(len=32)          :: dig1, dig2, vnam
        write(*,'(A)') '>>> SOFT ORIENTATION REFINEMENT BY DETERMINISTIC ANNEALING'
        ! Re-direct pointers in fgridvol to the new Fourier volume 
        call set_fgridvol('new')
        nbest = nbest_start
        do j=1,maxits
            write(*,'(A,I2)') '  ITERATION: ', j
            do s=1,nstates
                ! zero the Fourier volumes
                b%s3d(s)%fvol_new = cmplx(0.,0.)
                ! zero the kernels
                b%s3d(s)%kernel = 0.
            end do
            do i=1,nptcls
                call print_bar( i, nptcls, '=' )
                ! read the Fourier plane from stack
                call read_fplane( b%f(ptcl)%arr, fstk, i )
                ! do the weighted search
                call search_weighted
            end do
            ! Divide with the gridded kernel
            call kernel_div
            do s=1,nstates
                write(dig1,*) j
                if( nstates > 1 )then
                    write(dig2,*) s
                    vnam = 'softrec_'//trim(adjustl(dig1))//'_state'//trim(adjustl(dig2))//'.spi'
                else
                    vnam = 'softrec_'//trim(adjustl(dig1))//'.spi'
                endif
                ! Update the Fourier references 
                b%s3d(s)%fvol = b%s3d(s)%fvol_new
                ! low-pass filter
                call lp_fvol( b, s, lp )
                ! Rev FFT
                call fft_rev_fvol( b, s )
                ! mask
                if( msk > 1. ) call mask_volspi( b%s3d(s)%vspi, msk )
                ! write the volume file
                call write_volspi( b%s3d(s)%vspi, vnam )
            end do
            ! update nbest
            nbest = nbest-nint(real(nbest_start-nbest_stop)/real(maxits))
        end do
        
        contains
        
            subroutine search_weighted
                integer :: k
                real    :: sols(6), sump, p(nbest), corr, corrs(nbest), sdev, var, norm, corr_best
                logical :: err
                ! Perfom exhaustive angular search
                ! set winsize to 1 and wchoice to 1 for the alignment
                winsz = 1
                wchoice = 1
                if( nstates > 1 )then
                    call exhaustive_proj_search_2(oris(i,3), oris(i,4), oris(i,5))
                else
                    call exhaustive_proj_search_1(oris(i,3), oris(i,4), oris(i,5))
                endif
                ! fish the correlations to an array
                do k=1,nbest
                    call get_heapsort( b%hso, ninpl*nspace-(k-1), corrs(k) )
                    if( k == 1 ) corr_best = corrs(k)
                end do
                ! calculate the measure of variation around the best value
                call deviation( corrs, corr_best, sdev, var, err )
                ! calculate normalization constant for the Gaussian
                norm = 1./(sqrt(twopi*var))
                ! Calculate weights and grid the Fourier plane
                sump = 0.
                write(*,*) '**************'
                do k=1,nbest      
!                    p(k) = exp(corr-1)
                    p(k) = norm*exp(-((corrs(k)-corr_best)**2)/(2*var))
                    write(*,*) 'CORR:', corr, 'P:', p(k) 
                    sump = sump+p(k)
                end do
                write(*,*) 'SUMP:', sump
                ! set winsize to 2 and wchoice to 2 for the reconstruction
                winsz = 2
                wchoice = 2
                do k=1,nbest
                    call get_heapsort( b%hso, ninpl*nspace-(k-1), corr, rarr=sols )
                    p(k) = p(k)/sump
                    if( nstates > 1 )then
                        call grid_fplane(sols(1), sols(2), sols(3), sols(4), sols(5), int(sols(6)), p(k))
                    else
                        call grid_fplane(sols(1), sols(2), sols(3), sols(4), sols(5), 1, p(k))
                    endif
                end do                
            end subroutine search_weighted
            
    end subroutine soft_refine
    
    subroutine rbased_evol_align( i, fhandle )
    ! template-based refinmenet by differential evolution
        integer, intent(in)           :: i
        integer, intent(in), optional :: fhandle
        real                          :: init_rsols(nbest,5), rsols(nstates,5)
        real                          :: corrs_state(nstates)
        real                          :: lowpass, e1, e2, e3, x, y, corrspec, corrspec_first, rslask
        real                          :: corr, cost, lowpass_first, corr_first
        integer                       :: k, state, s, loc(1), j
        if( spec == 0 )then
            lowpass = lp ! input low-pass limit
            call set_aligndata( bp%a, i, lowpass=lowpass )
            x = 0. ! no previous x,y vec avail
            y = 0.
            corr_first = -1. ! no previous corr avail
        else
            call get_aligndata( bp%a, i, e1=e1, e2=e2, e3=e3, x=x, y=y, state=state,&
            lowpass=lowpass_first, q=corrspec_first, corr=corr_first )
            lowpass = min( lp,lowpass_first ) ! The input lowpass limit is limiting
        endif
        ! select interpolation method based on lowpass
        if( lowpass <= 20. )then
            winsz = 2
            wchoice = 2
        else
            winsz = 1
            wchoice = 1
        endif
        ! set lowpass lim
        lp_dyn = lowpass
        do s=1,nstates
            ! set global state parameter
            state = s
            if( spec == 0 )then
                ! DE restart procedure
                do j=1,nrnds
                    if( j == 1 )then
                        call init_1 ! complete diversification
                    else
                        call init_2 ! previosu best included in pop (restart procedure)
                    endif
                    call de_ori_refinement( e1, e2, e3, x, y, lowpass, init_rsols=init_rsols, cost=cost )
                end do
            else if( spec == 1 )then
                ! DE restart procedure
                do j=1,nrnds
                    call init_3 ! previosu best included in pop (restart procedure)
                    call de_ori_refinement( e1, e2, e3, x, y, lowpass, init_rsols=init_rsols, cost=cost )
                end do
            else
                ! continuous local refinement
                call de_ori_refinement( e1, e2, e3, x, y, lowpass, 7., cost )
            endif
            ! calculate correlation
            corrs_state(s) = corr_fplanes( e1, e2, e3, x, y )
            ! store solution
            rsols(s,1) = e1
            rsols(s,2) = e2
            rsols(s,3) = e3
            rsols(s,4) = x
            rsols(s,5) = y
        end do
        loc   = maxloc(corrs_state)
        state = loc(1)
        corr  = corrs_state(loc(1))
        e1    = rsols(loc(1),1)
        e2    = rsols(loc(1),2)
        e3    = rsols(loc(1),3)
        x     = rsols(loc(1),4)
        y     = rsols(loc(1),5) 
        if( spec >= 2 )then ! orientation keeping mode
            call corrspec_fplanes( e1, e2, e3, x, y, bp%rescorr, corrspec, lowpass )
            ! compare the new orientation to the old one...
            if( corrspec > corrspec_first .and. lowpass <= lowpass_first )then
                ! the new orientation is good and should replace the old one
                call set_aligndata( bp%a, i, e1=e1, e2=e2, e3=e3, x=x, y=y, corr=corr, state=state )
            endif 
        else
            ! always replace the old orientation
            call set_aligndata( bp%a, i, e1=e1, e2=e2, e3=e3, x=x, y=y, corr=corr, state=state )
        endif
        if( present(fhandle) )then
            call print_aligndata( bp%a, i, fhandle, corr='CORR:', q='Q:', lowpass='LP:', state='STATE:' )
            ! Get the actual and relative cpu-time
            rslask = getabscpu( .true. )
            rslask = getdiffcpu( .true. )
        endif
        
        contains
    
            subroutine init_1
                ! make even origin shift population
                call gen_origsh_pop(init_rsols(:,4:))
                do k=1,nbest
                    ! make random eulers
                    init_rsols(k,1) = eullims(1,2)*ran3()
                    init_rsols(k,2) = eullims(2,2)*ran3()
                    init_rsols(k,3) = eullims(3,2)*ran3()
                end do
            end subroutine init_1

            subroutine init_2
                do k=1,nbest
                    ! make random eulers
                    init_rsols(k,1) = eullims(1,2)*ran3()
                    init_rsols(k,2) = eullims(2,2)*ran3()
                    init_rsols(k,3) = eullims(3,2)*ran3()
                    ! randomize the translation parameters uniformly
                    init_rsols(k,4) = 2.*trs*ran3()-trs
                    init_rsols(k,5) = 2.*trs*ran3()-trs
                end do
                ! replace the last one with the previous best
                ! (this puts a lower bound on the correlation)
                init_rsols(nbest,1) = e1
                init_rsols(nbest,2) = e2
                init_rsols(nbest,3) = e3
                init_rsols(nbest,4) = x
                init_rsols(nbest,5) = y
            end subroutine init_2

            subroutine init_3
                do k=1,nbest
                    ! make random eulers
                    init_rsols(k,1) = eullims(1,2)*ran3()
                    init_rsols(k,2) = eullims(2,2)*ran3()
                    init_rsols(k,3) = eullims(3,2)*ran3()
                    ! randomize the translation parameters in a Gaussian distribution around
                    ! the previous origin shifts
                    init_rsols(k,4) = gasdev_lim( x, trs/1.5, (/-trs,trs/) )
                    init_rsols(k,5) = gasdev_lim( y, trs/1.5, (/-trs,trs/) )
                end do
                ! replace the last one with the previous best
                ! (this puts a lower bound on the correlation)
                init_rsols(nbest,1) = e1
                init_rsols(nbest,2) = e2
                init_rsols(nbest,3) = e3
                init_rsols(nbest,4) = x
                init_rsols(nbest,5) = y
            end subroutine init_3

!            subroutine search_exhaust
!                ! Perfom exhaustive search
!                call exhaustive_euler_search( x, y )
!                ! get the best solutions out
!                do k=1,nbest
!                    call get_heapsort( bp%hso, ninpl*nspace-(k-1), rslask, rarr=init_rsols(k,:) )
!                    ! randomize the translation parameters in a Gaussian distribution around
!                    ! the previous origin shifts
!                    init_rsols(k,4) = gasdev_lim( x, trs/1.5, (/-trs,trs/) )
!                    init_rsols(k,5) = gasdev_lim( y, trs/1.5, (/-trs,trs/) )
!                    if( k == nbest )then
!                        ! include the previously established orientation in the initialization
!                        ! (this puts a lower bound on the correlation)
!                        init_rsols(nbest,1) = e1
!                        init_rsols(nbest,2) = e2
!                        init_rsols(nbest,3) = e3
!                        init_rsols(nbest,4) = x
!                        init_rsols(nbest,5) = y
!                    endif
!                end do
!            end subroutine search_exhaust
            
    end subroutine rbased_evol_align

end module simple_rbased_search