module simple_pmatch
use simple_fplanes_corr
use simple_math
use simple_build
use simple_params
use simple_rnd
use simple_stkspi
use simple_imgspi
use simple_jiffys
use simple_ran_tabu
use simple_fplane
implicit none

contains

    subroutine mcrotalgn( b )    
        type(build), intent(inout) :: b
        integer :: r, h, k, j, target_to, i, ip, ntoavg, irnd, jrnd, isel, jsel, maxr, cnt, nits
        real :: maxcorr, maxcorr2, theta, corr, div, mat(2,2), sqsum
        complex :: fsum(-xdim:xdim,-xdim:xdim)
        integer, parameter :: MITS=20, NBOOT=100
        type(imgspi) :: img
        type(stkspi) :: stack
        type(ran_tabu) :: rt
        write(*,'(A)') '>>> ROTATIONAL ALIGNMENT'
        call seed_rnd
        nits = 2*NBOOT+nint(0.2*real(nptcls))
        ! make reference image
        img = new_imgspi( )
        ! make stack of reference images
        stack = new_stkspi( nimgs=MITS )
        call write_stk_hed( stack, 'mcrotalgn_refs.spi' )
        ! make fplanes corr functionality
        call make_fplanes_corr( b )
        ! make random number generation functionality
        rt = new_ran_tabu( nptcls )
        ! determine the low-pass Fourier index
        target_to = int(dstep/lp) 
        ! sample pairs
        write(*,'(A)') '>>> 2D FOURIER REFERENCE GENERATION'
        maxcorr2 = -1.
        cnt = 0
        do i=1,2*NBOOT
            call print_bar( cnt, nits, '=' )
            cnt = cnt+1
            call irnd_uni_pair_tabu( rt, irnd, jrnd )
            call read_fplane(b%frefs(0)%arr, fstk, irnd) 
            call rot_ref
            sqsum = calc_sqsum( b%frefs(0)%arr, target_to )
            call read_fplane( b%f(ptcl)%arr, fstk, jrnd )
            call find_best_rot(jrnd)
            if( maxcorr > maxcorr2 )then
                maxcorr2 = maxcorr
                isel = irnd
                jsel = jrnd
            endif
        end do
        ! select the best pair
        call insert_ran_tabu(rt,isel)
        call insert_ran_tabu(rt,jsel)
        ! prepare for making first average
        call read_fplane(b%frefs(0)%arr, fstk, isel)
        call rot_ref
        sqsum = calc_sqsum( b%frefs(0)%arr, target_to )
        call read_fplane( b%f(ptcl)%arr, fstk, jsel )     
        call find_best_rot(jsel)
        call rot_fplane( b%frefs(0)%arr, theta )
        fsum = cmplx(0.,0.)
        fsum = fsum+b%f(ptcl)%arr
        fsum = fsum+b%frefs(0)%arr
        div = 2.
        ! generate initial reference
        do while( div < 0.2*real(nptcls) ) ! until 20 % of the images are included
            call print_bar( cnt, nits, '=' )
            cnt = cnt+1
            ! make reference average
            b%frefs(0)%arr = cmplx(real(fsum)/div,aimag(fsum)/div)
            call rot_ref
            sqsum = calc_sqsum( b%frefs(0)%arr, target_to )
            maxcorr2 = -1.
            ! randomly sample NBOOT projections and match to avg
            do i=1,NBOOT
                jrnd = irnd_uni_tabu(rt)
                call read_fplane( b%f(ptcl)%arr, fstk, jrnd )               
                call find_best_rot(jrnd)
                if( maxcorr > maxcorr2 )then
                    maxcorr2 = maxcorr
                    jsel = jrnd
                endif
            end do
            ! select the best match
            call insert_ran_tabu(rt,jsel)
            ! prepare for making the reference average
            call read_fplane( b%f(ptcl)%arr, fstk, jsel )
            call find_best_rot(jsel)
            call rot_fplane(b%f(ptcl)%arr, oris(jsel,3))
            fsum = fsum+b%f(ptcl)%arr
            div = div+1.
        end do
        call print_bar( nits, nits, '=' )
        write(*,'(A)') '>>> REFINEMENT'
        do j=1,MITS
            call print_bar( j, MITS, '=' )
            ! write the reference to spider stack
            call fft_rev_fplane( b%frefs(0)%arr, img )
            call write_imgspi( stack, 'mcrotalgn_refs.spi', j, img )
            call rot_ref
            sqsum = calc_sqsum( b%frefs(0)%arr, target_to )
            do i=1,nptcls
                ! read the Fourier plane from stack
                call read_fplane( b%f(ptcl)%arr, fstk, i )
                call find_best_rot(i)
            end do
            ! sort the correlations
            call sort_heapsort( b%hso )
            ! generate the average from the 20% best correlating ptcls
            fsum = cmplx(0.,0.)
            ntoavg = nint(0.2*real(nptcls))
            do i=1,ntoavg
                call get_heapsort(b%hso, nptcls-(i-1), corr, ival=ip)
                ! read the Fourier plane from stack
                call read_fplane( b%f(ptcl)%arr, fstk, ip )
                ! rotate and shift the Fourier plane
                call rot_fplane(b%f(ptcl)%arr, oris(ip,3))
                ! add it to fsum
                fsum(:,:) = fsum(:,:)+b%f(ptcl)%arr
            end do
            div = real(ntoavg)
            b%frefs(0)%arr = cmplx(real(fsum)/div,aimag(fsum)/div)
        end do
        call kill_fplanes_corr
        call kill_stkspi(stack)
        call kill_imgspi(img)
        
        contains
        
            subroutine rot_ref
                do r=1,71
                    ! rotate
                    theta = real(r)*5.
                    mat = rotmat2d(theta)
                    !$omp parallel do default(shared) private(h,k) schedule(static)
                    do h=fromk,target_to
                        do k=fromk,target_to
                            b%frefs(r)%arr(h,k) = extr_fcomp(b%frefs(0)%arr,xdim,1,1,h,k,mat)
                        end do
                    end do
                    !$omp end parallel do
                end do
            end subroutine rot_ref
            
            subroutine find_best_rot( pind )
                integer, intent(in) :: pind
                maxcorr = -1.
                do r=0,71
                    theta = real(r)*5.
                    ! correlate
                    corr = corr_fplanes( b%f(ptcl)%arr, b%frefs(r)%arr, sqsum, target_to )
                    if(corr >= maxcorr)then
                        maxcorr = corr
                        oris(pind,3) = -theta
                        maxr = r
                        call set_heapsort( b%hso, pind, corr, ival=pind )
                    endif
                end do
            end subroutine find_best_rot
        
    end subroutine mcrotalgn

end module simple_pmatch