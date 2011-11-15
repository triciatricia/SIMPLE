module simple_ralph
use simple_jiffys
use simple_random_nrs
implicit none
save

public :: make_ralph, sample_ralph
private

type dnaseq
    character(len=1) :: a=''
    integer :: ns
    character(len=3), dimension(6) :: s
    integer :: tabu
end type dnaseq

type(dnaseq), allocatable, dimension(:) :: space

contains

    subroutine make_ralph( N, dnaseq, protseq )
        integer, intent(in) :: N
        character(len=1)    :: protseq(N)
        character(len=3)    :: dnaseq(N)
        integer             :: alloc_stat, i  
        ! make the search space
        allocate( space(N), stat=alloc_stat )
        call alloc_err( 'In: make_ralph, module: simple_ralph', alloc_stat )
        do i=1,N
            ! fill in the protein sequence info and 
            if( protseq(i) == 'Y' )then
                call make_Y( space(i) )
            endif
            if( protseq(i) == 'S' )then
                call make_S( space(i) )
            endif
            if( protseq(i) == 'P' )then
                call make_P( space(i) )
            endif
            if( protseq(i) == 'T' )then
                call make_T( space(i) )
            endif
            if( protseq(i) == 'A' )then
                call make_A( space(i) )
            endif
            if( space(i)%a == '' )then
                write(*,*) 'ERROR, amino acid residue in sequence not implemented!'
                stop
            endif
            ! fill in the tabus from the DNA sequence
            call set_dna_tabu( space(i), dnaseq(i) )
        end do
    end subroutine make_ralph
    
    subroutine sample_ralph( N )
        integer, intent(in) :: N
        integer :: i, j
        do j=1,1000
            do i=1,N
                write(*,'(A)',advance='no') space%s(irnd_uni_not(space(i)%ns,space(i)%tabu))                
            end do
            write(*,*) ''
            write(*,*) ''
        end do
    end subroutine sample_ralph
    
    subroutine make_Y( dnaobj )
        type(dnaseq) :: dnaobj
        dnaobj%a  = 'Y'
        dnaobj%ns = 2
        dnaobj%s  = (/'TAT','TAC','000','000','000','000'/)
    end subroutine make_Y
    
    subroutine make_S( dnaobj )
        type(dnaseq) :: dnaobj
        dnaobj%a  = 'S'
        dnaobj%ns = 6
        dnaobj%s  = (/'TCG','TCA','TCT','TCC','AGT','AGC'/)
    end subroutine make_S
    
    subroutine make_P( dnaobj )
        type(dnaseq) :: dnaobj
        dnaobj%a  = 'P'
        dnaobj%ns = 4
        dnaobj%s  = (/'CCG','CCA','CCT','CCC','000','000'/)
    end subroutine make_P
    
    subroutine make_T( dnaobj )
        type(dnaseq) :: dnaobj
        dnaobj%a  = 'T'
        dnaobj%ns = 4
        dnaobj%s  = (/'ACG','ACA','ACT','ACC','000','000'/)
    end subroutine make_T
    
    subroutine make_A( dnaobj )
        type(dnaseq) :: dnaobj
        dnaobj%a  = 'A'
        dnaobj%ns = 4
        dnaobj%s  = (/'GCG','GCA','GCT','GCC','000','000'/)
    end subroutine make_A
    
    subroutine set_dna_tabu( dnaobj, inseq )
        type(dnaseq) :: dnaobj
        character(len=3), intent(in) :: inseq
        integer :: i
        logical :: did_set
        did_set = .false.
        do i=1,dnaobj%ns
            if( dnaobj%s(i) == inseq )then
                dnaobj%tabu = i
                did_set = .true.
            endif
        end do
        if( did_set )then
        else
            write(*,*) 'ERROR, no matching DNA sequence for:', inseq
            stop
        endif
    end subroutine set_dna_tabu

end module simple_ralph