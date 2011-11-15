program ralph
use simple_ralph
implicit none
integer :: N, i
character(len=3), allocatable :: dnaseq(:)
character(len=1), allocatable :: protseq(:)
read(*,*) N
allocate( dnaseq(N), protseq(N) )
do i=1,N
read(*,'(A)',advance='no') dnaseq(i)
end do
do i=1,N
read(*,'(A)',advance='no') protseq(i)
end do
call make_ralph( N, dnaseq, protseq )
call sample_ralph( N )
end program ralph