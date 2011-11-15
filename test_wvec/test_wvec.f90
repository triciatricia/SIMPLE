program test_wvec
use simple_stat
implicit none
real :: arr(10)
call gen_wvec(arr)
write(*,*) arr
end program test_wvec