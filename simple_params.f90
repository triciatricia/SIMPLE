!==Class simple_params
!
! simple_params provides global distribution of common variables used in the SIMPLE library. The code is distributed 
! with the hope that it will be useful, but _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated
! by the GNU General Public License. *Author:* Hans Elmlund, 2011-08-18.
! 
!==Changes are documented below
!
module simple_params
!$ use omp_lib
!$ use omp_lib_kinds
use simple_jiffys
use simple_cmdline
implicit none

private :: check_file, check_carg, check_iarg, check_rarg
public

type fp
    complex, allocatable, dimension(:,:) :: arr 
end type fp

integer, parameter :: MAXS=10 ! maximum number of states
integer, allocatable, target :: cls(:)
real, allocatable  :: oris(:,:), lplims(:), mqs(:) 
character(len=256) :: clsfile='', cwd='', debug='no', doalign='yes', fstk='', pcastk='', pcahed='', hed=''
character(len=256) :: inpltab='', infile='', oritab='', outfile='', outfstk='', outstk='', outbdy='', pgrp='c1'
character(len=256) :: pwfile='', stk='', depopstks(MAXS), dapopstks(MAXS), masks(MAXS)
character(len=256) :: vols(MAXS)='', vols_msk(MAXS)
integer            :: box=0, clip, clsnr=1, fildim, freek, fromc=1, fromk=2, fromp=1, fromr=1, ftsz=0, GENMAX=200, hrecsz=0
integer            :: ivsct=2, mode=0, maxits=1, maxp=0, minp=20, navgs=1, nbest=98, ncls=0, ncomps=0, nrnds
integer            :: nbest_start=30, nbest_stop=10, ncsym=1, nfpl=1, nfrefs, ninpl, noris=0, notref=0, nout=0
integer            :: nptcls, nrestart=1, nspace=100, nstates=1
integer            :: nthr=1, nvars=6, ori=1, ptcl=1, pcasz=0, sep=1, spec=0, state=1, toc, tofny, tok, top, tor
integer            :: winsz=1, wchoice=1, xdim, ydim
real               :: amsklp=0., angtres=7., diam=140., dstep, epsilon, eullims(3,2), fny, freesh=20.
real               :: hp, lp=20., lp_dyn, lp2, lplim=200., lpmed=20., mw, msk=0., mqlim=3.5, neigh=0.2
real               :: optlims(6,2), smpd=0., tres, trs=0.
logical            :: cyclic(6)=.false.

contains

    subroutine make_params( md )
    ! *Available* *modes* *are:*
    !* *mode* *01* reference-free 2D shift alignment
    !* *mode* *02* unsupervised agglomerative hierachical 2D classification with greedy adaptive refinement
    !* *mode* *03* probabilistic pca
    !* *mode* *10* RAD by simulated annealing - reference-free projection direction assignment
    !* *mode* *11* state assignment by GRASP
    !* *mode* *12* -"- & reference-free continuous orientation refinement by DE
    !* *mode* *13* RAD by tabu search - reference-free projection direction assignment
    !* *mode* *14* <empty>
    ! *Available* *modes* *are:*
    !* *mode* *20* multireference EvolAlign alignment with fixed lowpass limit
    !* *mode* *21* multireference EvolAlign alignment with spectral self-adaptation
    !* *mode* *22* multireference EvolAlign alignment with spectral self-adaptation, neighborhood refinment, and orientation keeping
    !* *mode* *23* filtering tresholding/spectral scoring
    !* *mode* *30* reconstruction of volumes by Fourier gridding
    !* *mode* *31* solvent flattening of a spider volume
    !* *mode* *32* center of mass centering of a spider volume (no interpolation errors)
    !* *mode* *33* rotation of a spider volume (using gridding-based interpolation)
    !* *mode* *34* docking of spider volumes
        integer, intent(in), optional :: md
        interface
            integer function getcwd(dir)
                character(len=*) :: dir
            end function getcwd
        end interface
        character(len=32) :: cval1, cval2, cval3, cval4, cval5, cval6
        real :: rval1, rval2, rval4
        integer :: alloc_stat, s, file_stat, i, pos, hrecsz
        real :: rval
        character(len=120) :: dig
        logical :: here
        ! get cwd
        file_stat = getcwd(cwd)
        if( file_stat /= 0 )then
            write(*,*) 'ERROR, in call to getcwd'
            write(*,*) 'In: make_params, module: simple_params'
            stop
        endif
        ! set pwfile
        pwfile = trim(adjustl(cwd))//'/pwfile.bin'
        if( present(md) ) mode = md
        ! ...and store them as global variables
        call check_file( 'clsfile', '.spi', clsfile )
        if( defined_cmd_carg(clsfile) ) call file_exists(clsfile)
        call check_carg( 'debug', debug )
        call check_carg( 'doalign', doalign )    
        call check_file( 'fstk', '.fim', fstk )
        if( defined_cmd_carg(fstk) ) call file_exists(fstk)
        call check_file( 'pcastk', '.fim', pcastk )
        if( defined_cmd_carg(pcastk) ) call file_exists(pcastk)
        call check_file( 'hed', '.hed', hed )
        if( defined_cmd_carg('fstk') .and. .not. defined_cmd_carg('hed') )then
            ! make .hed file
            hed = fstk
            pos = index(hed, '.fim') ! position of '.fim'
            hed(pos:pos+3) = '.hed'  ! replacing .fim with .hed
            if( debug == 'yes' ) write(*,*) 'hed: ', hed
        endif
        if( defined_cmd_carg('pcastk') .and. .not. defined_cmd_carg('pcahed') )then
            ! make .hed file
            pcahed = pcastk
            pos = index(pcahed, '.fim') ! position of '.fim'
            pcahed(pos:pos+3) = '.hed'  ! replacing .fim with .hed
            if( debug == 'yes' ) write(*,*) 'pcahed: ', pcahed
        endif 
        call check_file( 'inpltab', '.spi', inpltab )
        if( defined_cmd_carg(inpltab) ) call file_exists(inpltab)
        call check_carg( 'infile', infile )
        call check_file( 'oritab', '.dat', oritab )
        if( defined_cmd_carg(oritab) ) call file_exists(oritab)
        call check_carg( 'outfile', outfile )
        call check_file( 'outfstk', '.fim', outfstk )
        call check_carg( 'outbdy', outbdy )
        call check_file( 'outstk', '.spi', outstk )
        call check_carg( 'pgrp', pgrp )
        call check_file( 'stk', '.spi', stk )
        if( defined_cmd_carg(stk) ) call file_exists(stk)       
        if( defined_cmd_carg('vol1') )then
            vols(1) = get_cmd_carg('vol1')
            call check_file_kind( vols(1), '.spi' )
            vols_msk(1) = add_to_fbody( vols(1), '.spi', 'msk' )
            vols_msk(1) = trim(adjustl(cwd))//'/'//trim(vols_msk(1))
            masks(1) = trim(adjustl(cwd))//'/automask_1.spi'
            nstates = 1
            if( debug == 'yes' ) write(*,*) 'vol1= ', vols(1)
        endif
        if( defined_cmd_carg('vol2') )then
            vols(2) = get_cmd_carg('vol2')
            call check_file_kind( vols(2), '.spi' )
            vols_msk(2) = add_to_fbody( vols(2), '.spi', 'msk' )
            vols_msk(2) = trim(adjustl(cwd))//'/'//trim(vols_msk(2))
            masks(2) = trim(adjustl(cwd))//'/automask_2.spi'
            nstates = 2
            if( debug == 'yes' ) write(*,*) 'vol2= ', vols(2)
        endif
        if( defined_cmd_carg('vol3') )then
            vols(3) = get_cmd_carg('vol3')
            call check_file_kind( vols(3), '.spi' )
            vols_msk(3) = add_to_fbody( vols(3), '.spi', 'msk' )
            vols_msk(3) = trim(adjustl(cwd))//'/'//trim(vols_msk(3))
            masks(3) = trim(adjustl(cwd))//'/automask_3.spi'
            nstates = 3
            if( debug == 'yes' ) write(*,*) 'vol3=', vols(3)
        endif
        if( defined_cmd_carg('vol4') )then
            vols(4) = get_cmd_carg('vol4')
            call check_file_kind( vols(4), '.spi' )
            vols_msk(4) = add_to_fbody( vols(4), '.spi', 'msk' )
            vols_msk(4) = trim(adjustl(cwd))//'/'//trim(vols_msk(4))
            masks(4) = trim(adjustl(cwd))//'/automask_4.spi'
            nstates = 4
            if( debug == 'yes' ) write(*,*) 'vol4= ', vols(4)
        endif
        if( defined_cmd_carg('vol5') )then
            vols(5) = get_cmd_carg('vol5')
            call check_file_kind( vols(5), '.spi' )
            vols_msk(5) = add_to_fbody( vols(5), '.spi', 'msk' )
            vols_msk(5) = trim(adjustl(cwd))//'/'//trim(vols_msk(5))
            masks(5) = trim(adjustl(cwd))//'/automask_5.spi'
            nstates = 5
            if( debug == 'yes' ) write(*,*) 'vol5= ', vols(5)
        endif
        if( defined_cmd_carg('vol6') )then
            vols(6) = get_cmd_carg('vol6')
            call check_file_kind( vols(6), '.spi' )
            vols_msk(6) = add_to_fbody( vols(6), '.spi', 'msk' )
            vols_msk(6) = trim(adjustl(cwd))//'/'//trim(vols_msk(6))
            masks(6) = trim(adjustl(cwd))//'/automask_6.spi'
            nstates = 6
            if( debug == 'yes' ) write(*,*) 'vol6= ', vols(6)
        endif
        if( defined_cmd_carg('vol7') )then
            vols(7) = get_cmd_carg('vol7')
            call check_file_kind( vols(7), '.spi' )
            vols_msk(7) = add_to_fbody( vols(7), '.spi', 'msk' )
            vols_msk(7) = trim(adjustl(cwd))//'/'//trim(vols_msk(7))
            masks(7) = trim(adjustl(cwd))//'/automask_7.spi'
            nstates = 7
            if( debug == 'yes' ) write(*,*) 'vol7= ', vols(7)
        endif
        if( defined_cmd_carg('vol8') )then
            vols(8) = get_cmd_carg('vol8')
            call check_file_kind( vols(8), '.spi' )
            vols_msk(8) = add_to_fbody( vols(8), '.spi', 'msk' )
            vols_msk(8) = trim(adjustl(cwd))//'/'//trim(vols_msk(8))
            masks(8) = trim(adjustl(cwd))//'/automask_8.spi'
            nstates = 8
            if( debug == 'yes' ) write(*,*) 'vol8= ', vols(8)
        endif
        if( defined_cmd_carg('vol9') )then
            vols(9) = get_cmd_carg('vol9')
            call check_file_kind( vols(9), '.spi' )
            vols_msk(9) = add_to_fbody( vols(9), '.spi', 'msk' )
            vols_msk(9) = trim(adjustl(cwd))//'/'//trim(vols_msk(9))
            masks(9) = trim(adjustl(cwd))//'/automask_9.spi'
            nstates = 9
            if( debug == 'yes' ) write(*,*) 'vol9= ', vols(9)
        endif
        if( defined_cmd_carg('vol10') )then
            vols(10) = get_cmd_carg('vol10')
            call check_file_kind( vols(10), '.spi' )
            vols_msk(10) = add_to_fbody( vols(10), '.spi', 'msk' )
            vols_msk(10) = trim(adjustl(cwd))//'/'//trim(vols_msk(10))
            masks(10) = trim(adjustl(cwd))//'/automask_10.spi'
            nstates = 10
            if( debug == 'yes' ) write(*,*) 'vol10= ', vols(10)
        endif
        call check_iarg('box', box)
        call check_iarg('clsnr', clsnr)
        call check_iarg('fromc', fromc)
        call check_iarg('fromk', fromk)
        call check_iarg('fromp', fromp)
        call check_iarg('fromr', fromr)
        call check_iarg('GENMAX', GENMAX)
        call check_iarg('mode', mode)
        call check_iarg('maxits', maxits)
        call check_iarg('maxp', maxp)
        call check_iarg('minp', minp)
        call check_iarg('navgs', navgs)
        call check_iarg('nbest', nbest)
        call check_iarg('nbest_start', nbest_start)
        call check_iarg('nbest_stop', nbest_stop)
        call check_iarg('ncls', ncls)
        call check_iarg('ninpl', ninpl)
        call check_iarg('nrnds', nrnds)
        call check_iarg('nspace', nspace)
        call check_iarg('nstates', nstates)
        if( defined_cmd_rarg('nstates') )then
            nstates = int(get_cmd_rarg('nstates'))
            if( nstates > MAXS )then
                write(*,*) 'ERROR, the number of states is limited to 10!'
                write(*,*) 'In: make_params, module: simple_params.f90'
                stop
            endif
        endif
        call check_iarg('nout', nout)
        call check_iarg('nptcls', nptcls)
        call check_iarg('nrestart', nrestart)
        call check_iarg('nthr', nthr)
        call check_iarg('nvars', nvars)
        call check_iarg('sep', sep)
        call check_iarg('toc', toc)
        call check_iarg('tok', tok)
        call check_iarg('top', top)
        call check_iarg('tor', tor)
        call check_iarg('winsz', winsz)
        call check_iarg('wchoice', wchoice)
        call check_rarg('amsklp', amsklp)
        call check_rarg('angtres', angtres)
        call check_rarg('diam', diam)
        call check_rarg('epsilon', epsilon)
        call check_rarg('freesh', freesh)
        call check_rarg('hp', hp)
        call check_rarg('lp', lp)
        call check_rarg('lplim', lplim)
        call check_rarg('msk', msk)
        call check_rarg('mw', mw)
        call check_rarg('mqlim', mqlim)
        call check_rarg('neigh', neigh)
        call check_rarg('smpd', smpd)
        call check_rarg('tres', tres)
        call check_rarg('trs', trs)
!$      call omp_set_num_threads(nthr)
        if( defined_cmd_carg('fstk') )then
            ! read variables from stack header
            inquire(iolength=hrecsz) rval
            open(unit=19, file=hed, status='old', iostat=file_stat,&
            access='direct', action='read', form='unformatted', recl=hrecsz)
            call fopen_err( 'In: make_params, module: simple_params.f90', file_stat )
            read(19,rec=1) rval
            nptcls = int(rval)  ! number of transforms
            read(19,rec=2) rval 
            xdim = int(rval)    ! Fourier dim
            read(19,rec=3) smpd ! sampling distance
            read(19,rec=4) rval
            ftsz = int(rval)    ! transform size                             
            close(19)
            box = 2*xdim
        else
            xdim = box/2
        endif
        ! set derived Fourier related variables   
        dstep = real(box-1)*smpd                          ! first wavelength of FT
        if( .not. defined_cmd_rarg('hp') ) hp = 0.7*dstep ! high-pass limit
        fromk = max(2,int(dstep/hp))                      ! high-pass Fourier index
        fny = 2.*smpd                                     ! Nyqvist limit
        tofny = int(dstep/fny)                            ! Nyqvist Fourier index
        freek = int(dstep/freesh)                         ! resolution band excluded (for free corr calc)
        lp = max(fny,lp)                                  ! lowpass limit
        lp_dyn = lp                                       ! dynamic lowpass limit
        lpmed = lp                                        ! median lp
        lp2 = fny                                         ! second lp
        tok = int(dstep/fny)                              ! Nyqvist Fourier index
        ydim = xdim                                       ! square box assumed
        fildim = 2*xdim+2                                 ! spider FT fildim
        if( mode == 10 ) ncls = 3                         ! for the angular reconstitution
        ! set balancing constraint for classification
        if( .not. defined_cmd_rarg('maxp') )then
            if( ncls /= 0 ) maxp = max(maxp,nint(2.*(real(nptcls)/real(ncls))))
        endif
        ! set nr of in-plane rots
        ninpl = int(360./angtres) ! default value of angtres is 7.
        ! define clipped box if not given
        if( .not. defined_cmd_rarg('clip') )then
            clip = box
        endif
        ! error check box
        if( box == 0 )then
            write(*,*) 'ERROR, box size cannot be 0'
            write(*,*) 'In: make_params, module: simple_params.f90'
            stop
        endif
        ! error check Fourier transform size
        if( mod(xdim,2) /= 0 .and. mode /= 0 )then
            write(*,*) 'ERROR, the Fourier transform size must be even!'
            write(*,*) 'In: make_params, module: simple_params.f90'
            stop
        endif
        ! set window size
        if( .not. defined_cmd_rarg('winsz')) then
            if( mode >= 30 )then
                winsz = 2
            else
                winsz = 1
            endif
        endif
        ! set window choice
        if( .not. defined_cmd_rarg('wchoice')) then
            if( mode >= 30 )then
                wchoice = 2 ! sinc w pre-weighted Gaussian window
            else
                wchoice = 1 ! direct sinc
            endif
        endif
        ! set nr of restarts
        nrestart = 10
        if( mode == 10 ) nrestart = 1
        ! set to particle index if not defined in cmdlin
        if( .not. defined_cmd_rarg('top') ) top = nptcls
        if( mode == 34 ) top = nrnds
        ! set the number of input orientations
        noris = nptcls
        if(mode == 20.or.mode == 25) noris = 0
        ! Take care of the space and bootstrap sample size heuristics
        if(mode < 20 .and. mode >= 10 ) then ! reference-free analysis
            ! set constants
            notref = 0 ! none excluded
            fromr = 1 ! first ref is 1
            tor = nptcls ! last ref is last ptcl
            fromc = 1 ! first cavg is 1
            toc = nptcls ! last cavg is last ptcl
            ori = 1 ! only one orientation evaluated at the time
            if( .not. defined_cmd_rarg('nspace') )then
                nspace = 5*nptcls
                if(nspace > 2000)then
                    nspace = 2*nptcls
                endif
            endif
        else if(mode < 40 .and. (.not. defined_cmd_rarg('nspace')))then
             nspace = 240 ! nr of projection directions in exhaustive search
        endif     
        ! set nr of Fourier planes 
        if( defined_cmd_rarg('nfpl') )then
        else if( mode == 1 )then
            nfpl = 1
        else if( mode == 2 )then
            nfpl = nptcls
        else if( mode < 20 .and. mode >= 10 )then
            nfpl = nptcls
        else
            nfpl = 1
        endif
        ! Set spectral alignment indicator
        spec = 0
        if(mode==21.or.(mode==23.or.mode==24))then
            spec = 1
        else if(mode==22)then
            spec = 2
        endif
        ! make sure that oritab is inputted for spectral > 0
        if( spec > 0 .and. oritab == '' )then
            write(*,*) 'ERROR, input orientations are required for spectrally self-adaptive refinement!'
            write(*,*) 'In: make_params, module: simple_params.f90'
            stop
        endif
        ! fix translation param
        trs = abs(trs)
        if( trs < 0.01 ) trs = 0.00001
        ! set nfrefs
        nfrefs = max(maxits*navgs,359)
        nfrefs = max(nfrefs,ncls+500)
        if( mode == 1 ) nfrefs = max(nfrefs,(2*int(trs)+1)**2)
        ! Transform the pointgroup into euler angle limits and store the number of csym ops in ncsym
        eullims(3,1) = 0.
        eullims(3,2) = 359.9999
        if(pgrp(1:1).eq.'c')then
            eullims(2,1) = 0.
            eullims(2,2) = 180.
        else if(pgrp(1:1).eq.'d')then
            eullims(2,1) = 0.
            eullims(2,2) = 90.
        else
            write(*,*) 'ERROR, presently only c and d symmetries are supported!'
            write(*,*) 'In: make_params, module: simple_params.f90'
            stop
        endif
        read(pgrp(2:),'(I2)') ncsym
        eullims(1,1) = 0.
        eullims(1,2) = 359.9999/real(ncsym)
        eullims(1,2) = 180./real(ncsym)
        ! set optlims
        optlims(:3,:) = eullims
        optlims(4,1) = -trs
        optlims(4,2) = trs
        optlims(5,1) = -trs
        optlims(5,2) = trs
        if( nstates > 1 )then ! multi-conformation search
            optlims(6,1) = 1.
            optlims(6,2) = real(nstates)+0.9999
        endif
        ! Set first three in cyclic true, to enable cycling of Euler angles in DE
        cyclic(1) = .true.
        cyclic(2) = .true.
        cyclic(3) = .true.
        ! allocate orientations array
        if( noris > 0 )then
            allocate( oris(noris,6), lplims(noris), mqs(noris), stat=alloc_stat )
            call alloc_err( 'In: make_params, module: simple_params.f90, alloc 1', alloc_stat )
            oris = 0. ! zero the Euler angles & translations
            oris(:,6) = 1. ! set the state params to one
        endif
        ! allocate class array
        if( mode == 2 .or. mode == 10 )then
            allocate( cls(nptcls), stat=alloc_stat )
            call alloc_err( 'In: make_params, module: simple_params.f90, alloc 2', alloc_stat )
            cls = 0
        endif
        ! make stack names for the de population files
        do s=1,nstates
            write(dig,*) s
            depopstks(s) = 'EVOL_ALIGN_POPSTK_'//trim(adjustl(dig))//'.bin'
        end do
        ! make stack names for the discrete angular search populations
        do s=1,nstates
            write(dig,*) s
            dapopstks(s) = 'DISCR_ALIGN_POPSTK_'//trim(adjustl(dig))//'.bin'
        end do
        ! read data into the orientations array
        here = .false.
        if( defined_cmd_carg('oritab') ) call file_exists(oritab, here)
        if(noris > 0 .and. here )then
            open(22, FILE=oritab, STATUS='OLD', action='READ', iostat=file_stat)
            call fopen_err( 'In: make_params, module: simple_params.f90', file_stat )
            ! fill in orientations, states, and lowpass limits
            do i=1,noris
                read(22,*) oris(i,1), oris(i,2), oris(i,3), oris(i,4), oris(i,5),&
                cval1, rval1, cval2, rval2, cval3, mqs(i), cval4, rval4, cval5, lplims(i),&
                cval6, oris(i,6)
            end do
            close(22)
        endif
        write(*,'(A)') '>>> DONE PROCESSING PARAMETERS'
    end subroutine make_params
    
    subroutine kill_params
        if( allocated(oris) )   deallocate( oris )
        if( allocated(lplims) ) deallocate( lplims )
        if( allocated(mqs) )    deallocate( mqs )
        if( allocated(cls) )    deallocate( cls )
    end subroutine kill_params
    
    subroutine check_file( file, ext, var )
        character(len=*), intent(in)  :: file, ext
        character(len=*), intent(out) :: var
        if( defined_cmd_carg(file) )then
            var = get_cmd_carg(file)
            call check_file_kind( var, ext )
            var = trim(adjustl(cwd))//'/'//trim(var)
            if( debug == 'yes' ) write(*,*) file, '=', var
        endif
    end subroutine check_file
    
    subroutine check_carg( carg, var )
        character(len=*), intent(in)  :: carg
        character(len=*), intent(out) :: var
        if( defined_cmd_carg(carg) )then
            var = get_cmd_carg(carg) 
            if( debug == 'yes' ) write(*,*) carg, '=', var
        endif
    end subroutine check_carg
    
    subroutine check_iarg( iarg, var )
        character(len=*), intent(in)  :: iarg
        integer, intent(out) :: var
        if( defined_cmd_rarg(iarg) )then
            var = int(get_cmd_rarg(iarg))
            if( debug == 'yes' ) write(*,*) iarg, '=', var
        endif
    end subroutine check_iarg
    
    subroutine check_rarg( rarg, var )
        character(len=*), intent(in)  :: rarg
        real, intent(out) :: var
        if( defined_cmd_rarg(rarg) )then
            var = get_cmd_rarg(rarg) 
            if( debug == 'yes' ) write(*,*) rarg, '=', var
        endif
    end subroutine check_rarg
    
    subroutine mkoptlims( e1, e2, e3, x, y, atres, opt_limits )
        real, intent(in)  :: e1, e2, e3, x, y, atres
        real, intent(out) :: opt_limits(6,2)
        opt_limits(1,1) = e1-atres
        opt_limits(1,2) = e1+atres
        opt_limits(2,1) = e2-atres
        opt_limits(2,2) = e2+atres
        opt_limits(3,1) = e3-atres
        opt_limits(3,2) = e3+atres
        opt_limits(4,1) = x-trs/2.
        opt_limits(4,2) = x+trs/2.
        opt_limits(5,1) = y-trs/2.
        opt_limits(5,2) = y+trs/2.
        if( opt_limits(4,1) < -trs ) then
            opt_limits(4,1) = -trs
        endif
        if( opt_limits(4,2) > trs ) then
            opt_limits(4,2) = trs
        endif
        if( opt_limits(5,1) < -trs ) then
            opt_limits(5,1) = -trs
        endif
        if( opt_limits(5,2) > trs ) then
            opt_limits(5,2) = trs
        endif
        if( nstates > 1 )then ! multi-conformation refinement
            opt_limits(6,1) = 1.
            opt_limits(6,2) = real(nstates)+0.9999
        endif
    end subroutine mkoptlims
    
end module simple_params