module simple_usupcls
use simple_sll_list
use simple_params
use simple_jiffys
use simple_stat
use simple_build
use simple_fplanes_corr
use simple_fplane
implicit none

public :: make_usupcls, usupcls_master, kill_usupcls, get_usupncls
private

interface usupcls_master
    module procedure usupcls_master_1
    module procedure usupcls_master_2
end interface

type(sll_list), allocatable  :: classes(:)
type(sll_list)               :: ptcl_list
integer, allocatable         :: cls_here(:)
integer                      :: nclasses, nobjs, target_to, nreclust, clsnr=1
real, allocatable            :: sqsums(:)
character(len=32)            :: fstknam
type(build), pointer         :: bp=>null()
type(pair_wtab)              :: pw


! intended to be able to deal with classification problems not necessarily involving entire particle stacks
! but also subpopulations, for example defined by template-based search. The particle indices should be provided
! as a linked list. To enhance the speed of the correlation calculations, the complex sqsums are first calculated 
! and stored in an array. Next, the table of correlations is built (pw-table) and the first classification solution is
! generated using the group average method. The solution is refined using a greedy adaptive algorithm.


contains

    subroutine make_usupcls( b, ptcl_list_in, fstknam_in )
        type(build), intent(in), target :: b
        type(sll_list), intent(in)      :: ptcl_list_in
        character(len=*)                :: fstknam_in
        integer                         :: alloc_stat, pi, i, maxpind, loc
        ! set parameters
        ptcl_list = clone_sll_list( ptcl_list_in )
        nobjs = get_sll_size(ptcl_list)
        nclasses = nobjs/maxp
        fstknam = fstknam_in
        nreclust = nint(0.3*real(nobjs)) ! reclustering fraction
        bp => b
        target_to = int(dstep/lp)
        ! find maximum particle index
        loc = sll_maxloc( ptcl_list, maxpind )
        ! allocate
        allocate( sqsums(nobjs), classes(nobjs), cls_here(maxpind), stat=alloc_stat )
        call alloc_err("In: make_usupcls, module: simple_usupcls", alloc_stat)
        cls_here = 0
        ! read transforms, prepare classes array & alculate sqsums (for the correlation table generation)
        do i=1,nobjs
            classes(i) = new_sll_list() 
            call get_sll_node( ptcl_list, i, ival=pi )
            call add_sll_node( classes(i), ival=pi )
            call read_fplane( bp%f(i)%arr, fstk, pi ) ! remember that the translation table is encoded the ptcl_list
            sqsums(i) = calc_sqsum( b%f(i)%arr, target_to )
        end do
        ! make pair weight table
        pw = new_pair_wtab( nobjs )
        ! set Fourier index lplim
        target_to = int(dstep/lp)     
    end subroutine make_usupcls
    
    subroutine kill_usupcls
        integer :: i
        call kill_pair_wtab(pw)
        do i=1,nobjs
            call kill_sll_list(classes(i))
        end do
        deallocate( sqsums, cls_here, classes )
    end subroutine kill_usupcls
    
    subroutine build_pw
        integer :: a, b
        real    :: corr
        ! first allocate the table so that we immediately see what the memory usage is
        write(*,'(A)') '>>> ALLOCATING CORRELATION PW TABLE'
        do a=1,nobjs-1 
            do b=a+1,nobjs
                call alloc_pair_w(pw,a,b)    
            end do
            call print_bar( a, nobjs-1, '=' )
        end do
        ! then fill it
        write(*,'(A)') '>>> BUILDING CORRELATION PW TABLE'
        do a=1,nobjs-1
            do b=a+1,nobjs
                corr = corr_fplanes( bp%f(a)%arr, bp%f(b)%arr, sqsums(a), sqsums(b), target_to )
                call set_pair_w( pw, a, b, corr  )
            end do
            call print_bar( a, nobjs-1, '=' )
        end do
    end subroutine build_pw
    
    function get_usupncls( ) result( nclsout )
        integer :: nclsout
        nclsout = nclasses
    end function get_usupncls
    
    subroutine usupcls_master_1
        integer :: foo=1
        ! build table of correlations
        call build_pw
        ! do balanced hierarchical classification
        call hac_cls( pw, nobjs, nclasses, maxp, classes, nclasses )
        ! convert singly linked list structure to array
        call sll_to_arr_cls( classes, nobjs, cls_here, foo )
        ! write classification solution to file
        call write_spidoc( 'scratch_first_hcl.spi', cls_here )
        ! refine classification solution
        call refine_hac_cls( pw, nobjs, nclasses, nreclust, cls_here, maxp )
        ! convert back to singly linked list structure
        call arr_to_sll_cls( cls_here, nobjs, classes )
        ! report classification solution to the global cls array
        call sll_to_arr_cls( classes, nobjs, cls, clsnr )
    end subroutine usupcls_master_1
    
    subroutine usupcls_master_2( classes_in )      
        type(sll_list) :: classes_in(ncls)
        integer :: inds(nobjs), i
        real :: cpops(nobjs)
        ! build table of correlations
        call build_pw
        ! do balanced hierarchical classification
        call hac_cls( pw, nobjs, nclasses, maxp, classes )
        do i=1,nobjs
            inds(i) = i
            cpops(i) = real(get_sll_size(classes(i)))
        end do
        call hpsort(nobjs, cpops, inds)
        classes_in(1) = clone_sll_list(classes(inds(nobjs)))
        classes_in(2) = clone_sll_list(classes(inds(nobjs-1)))
        classes_in(3) = clone_sll_list(classes(inds(nobjs-2)))
    end subroutine usupcls_master_2

end module simple_usupcls