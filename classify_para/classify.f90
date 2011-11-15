program classify
use simple_pmatch
use simple_fstk
use simple_spidoc
use simple_params
use simple_sll_list
use simple_jiffys
use simple_build
use simple_ppca
use simple_pair_wtab
use simple_math
use simple_cmdline
implicit none
save

type(build), target         :: b
type(pair_wtab)             :: pw
type(sll_list), allocatable :: classes(:)
real, allocatable           :: feats(:,:)
type(imgspi)                :: img
type(stkspi)                :: stack
character(len=256)          :: stkconv
integer                     :: file_stat
integer                     :: i, err, alloc_stat, nreclust
integer, parameter          :: funit=66
real, pointer               :: ptr(:)
logical                     :: cmderr(13)
if( command_argument_count() < 13 )then
    write(*,*) './classify stk=instk.spi box=100 nptcls=10000 smpd=2.33 msk=<mask radius(in pixels)> lp=<low-pass limit(in A){15-30}> doalign=<yes|no> ncls=<nr of classes> minp=<minimum nr of ptcls in a class{20}> maxp=<maximum nr of ptcls in a class{80}> nvars=<nr of eigenvectors{20-40}> maxits=<maximum nr of pca iterations{100}> nthr=<nr of openMP threads> [hp=<high-pass limit (in A)>] [debug=<yes|no>]'
    stop
endif

! PARSE COMMAND LINE
call parse_cmdline
! check command line args
cmderr(1) = .not. defined_cmd_carg('stk')
cmderr(2) = .not. defined_cmd_rarg('box')
cmderr(3) = .not. defined_cmd_rarg('nptcls')
cmderr(4) = .not. defined_cmd_rarg('smpd')
cmderr(5) = .not. defined_cmd_rarg('msk')
cmderr(6) = .not. defined_cmd_rarg('lp')
cmderr(7) = .not. defined_cmd_carg('doalign')
cmderr(8) = .not. defined_cmd_rarg('ncls')
cmderr(9) = .not. defined_cmd_rarg('minp')
cmderr(10) = .not. defined_cmd_rarg('maxp')
cmderr(11) = .not. defined_cmd_rarg('nvars')
cmderr(12) = .not. defined_cmd_rarg('maxits')
cmderr(13) = .not. defined_cmd_rarg('nthr')
if( any(cmderr) )then
    write(*,*) 'ERROR, not all input variables for classify defined!'
    write(*,*) 'Perhaps there are spelling errors?'
    stop
endif

! BUILD OBJECTS
b = new_build(2) ! mode=2
! set outfile
outfile=trim(adjustl(cwd))//'/classify.log'
! allocate what is needed
allocate( classes(nptcls), feats(nptcls,nvars), stat=alloc_stat )
call alloc_err('In: classify', alloc_stat)
do i=1,nptcls
    classes(i) = new_sll_list() 
    call add_sll_node( classes(i), ival=i )
end do
! open status report file
open(unit=funit, file=outfile, status='replace', iostat=file_stat, action='write', form='formatted')
call fopen_err( 'In: classify', file_stat )
write(funit,'(A)') "**** UNSUPERVISED CLASSIFICATION PROCEDURE BEGINS ****"
! make Fourier stack
call make_fstk( 'stkclassify.fim', 'stkclassify.hed' )
! Set global stack variables
fstk = 'stkclassify.fim'
hed = 'stkclassify.hed'


! ROTATIONAL ALIGNMENT
if( doalign == 'yes' )then
    ! Rotational alignment
    call mcrotalgn( b )
    write(funit,'(A)') "WROTE ALIGNMENT REFERENCES TO SPIDER STACK: rotalgn_refs.spi"
    ! Rotate stack
    call shrot_fstk( b, 'inplalgnstk.fim'  )
    call fstk_mk_stkspi( 'inplalgnstk.fim', 'inplalgnstk.spi' )
    write(funit,'(A)') "WROTE ALIGNED IMAGES TO SPIDER STACK: inplalgnstk.spi"
    ! Set global stack variables
    stk =  'inplalgnstk.spi'
    fstk = 'inplalgnstk.fim'
    hed =  'inplalgnstk.hed'
    write(funit,'(A)') "**** FINISHED ROTATIONAL ALIGNMENT ****"
endif

! PROBABILISTIC PCA
! make stack functionality
stack = new_stkspi(name=stk)
! find endian conversion
call find_stkconv(stack,stk,stkconv)
! make image
img = new_imgspi()
! get nr of components
ncomps = get_npcapix( img, msk )
call make_ppca( nptcls, 0 )
do i=1,nptcls
    ! read image
    call read_imgspi( stack, stk, i, img, stkconv )
    ! normalize
    call norm_imgspi(img)
    ! get pointer to pcavec
    call get_ppca_vec_ptr( i, ptr )
    ! extract pca vec to ppca object
    call extract_pcavec( img, msk, ptr )
end do
err = -1
do while( err == -1 )
    call ppca_master( err )
end do
write(funit,'(A,F8.0)') "GLOBAL NOISE VARIANCE: ", epsilon
! get the amplitude feature vectors
call get_pca_feats( feats )
! kill the ppca singleton
call kill_ppca
write(funit,'(A)') "**** FINISHED PROBABILISTIC PCA ****"

! CLASSIFICATION
! do hierarchical classification
nreclust = nint(0.3*real(nptcls)) ! reclustering fraction
! make pair weight table
pw = new_pair_wtab(nptcls)
call build_pw
! do balanced hierarchical classification
call hac_cls( pw, nptcls, ncls, maxp, classes )
! convert singly linked list structure to array
ncls = 1
call sll_to_arr_cls( classes, nptcls, cls, ncls )
! write classification solution to file
call write_spidoc( 'hcl.spi', cls )
write(funit,'(A)') "WROTE FIRST CLASSIFICATION SOLUTION TO FILE: hcl.spi"
! refine classification solution
call refine_hac_cls( pw, nptcls, ncls, nreclust, cls, maxp )
! convert to singly linked list representation
call arr_to_sll_cls( cls, nptcls, classes )
! convert back and update nr of classes
ncls = 1
call sll_to_arr_cls( classes, nptcls, cls, ncls )
! write classification solution to file
call write_spidoc( 'hcl_refined.spi', cls )
write(funit,'(A)') "WROTE REFINED CLASSIFICATION SOLUTION TO FILE: hcl_refined.spi"
write(funit,'(A)') "**** FINISHED CLASSIFICATION ****"

! MAKE CLASS AVERAGES
call fstk_mk_cavgs( b, 'cavgstk.fim' )
write(funit,'(A)') "WROTE FOURIER CLASS AVERAGES TO SIMPLE FOURIER STACK: cavgstk.fim"
! make spider stack of class averages
call fstk_mk_stkspi( 'cavgstk.fim', 'cavgstk.spi' )
write(funit,'(A)') "WROTE CLASS AVERAGES TO SPIDER STACK: cavgstk.spi"
! end gracefully
write(funit,'(A)') "**** CLASSIFY NORMAL STOP ****"
close(funit)
call haloween( 0 )
write(0,'(A)') "HAVE A GLANCE AT THE classify.log FILE TO SEE WHAT WAS DONE"
write(0,'(A)') "**** CLASSIFY NORMAL STOP ****"

contains

   subroutine build_pw
        integer :: a, b
        real    :: corr
        ! first allocate the table so that we immediately see what the memory usage is
        write(*,'(A)') '>>> ALLOCATING CORRELATION PW TABLE'
        do a=1,nptcls-1 
            !$omp parallel do default(shared) private(b) schedule(static)
            do b=a+1,nptcls
                call alloc_pair_w(pw,a,b)    
            end do
            !$omp end parallel do
            call print_bar( a, nptcls-1, '=' )
        end do
        ! then fill it
        write(*,'(A)') '>>> BUILDING CORRELATION PW TABLE'
        do a=1,nptcls-1
            !$omp parallel do default(shared) private(b,corr) schedule(static)
            do b=a+1,nptcls
                ! calc corr, feature vectors assumed to be normalized
                corr = pearsn(feats(a,:),feats(b,:),nvars)
                call set_pair_w( pw, a, b, corr )
            end do
            !$omp end parallel do
            call print_bar( a, nptcls-1, '=' )
        end do
        write(funit,'(A)') "**** FINISHED BUILDING CORRELATION PW TABLE ****"
    end subroutine build_pw
    
end program classify