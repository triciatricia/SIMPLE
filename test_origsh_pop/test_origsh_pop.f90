program test_origsh_pop
use simple_math
implicit none
real    :: opop(98,2)
integer :: i
call gen_origsh_pop( opop )
do i=1,98
    write(*,*) opop(i,1), opop(i,2)
end do
end program test_origsh_pop