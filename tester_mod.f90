! functions and subroutines to help me test things. 
module tester_mod

implicit none
save

interface fuzzy_compare
    module procedure fuzzy_compare_r
    module procedure fuzzy_compare_rarr
    module procedure fuzzy_compare_r2arr
    module procedure fuzzy_compare_i
    module procedure fuzzy_compare_iarr
    module procedure fuzzy_compare_i2arr
end interface fuzzy_compare

contains

function fuzzy_compare_r(a, b, threshold)
! are a and b within threshold?
    real, intent(in)    :: a, b, threshold
    logical             :: fuzzy_compare_r
    fuzzy_compare_r = abs(a - b) <= threshold
    return
end function fuzzy_compare_r

function fuzzy_compare_rarr(a, b, arrsize, threshold)
! are a and b within threshold?
    integer, intent(in) :: arrsize
    real, intent(in)    :: a(arrsize), b(arrsize), threshold
    logical             :: fuzzy_compare_rarr
    fuzzy_compare_rarr = all(abs(a - b) <= threshold)
    return
end function fuzzy_compare_rarr

function fuzzy_compare_r2arr(a, b, arrsize1, arrsize2, threshold)
! are a and b within threshold?
    integer, intent(in) :: arrsize1, arrsize2
    real, intent(in)    :: a(arrsize1,arrsize2), b(arrsize1,arrsize2), threshold
    logical             :: fuzzy_compare_r2arr
    fuzzy_compare_r2arr = all(abs(a - b) <= threshold)
    return
end function fuzzy_compare_r2arr

function fuzzy_compare_i(a, b, threshold)
! are a and b within threshold?
    integer, intent(in) :: a, b, threshold
    logical             :: fuzzy_compare_i
    fuzzy_compare_i = abs(a - b) <= threshold
    return
end function fuzzy_compare_i

function fuzzy_compare_iarr(a, b, arrsize, threshold)
! are a and b within threshold?
    integer, intent(in) :: arrsize
    integer, intent(in) :: a(arrsize), b(arrsize), threshold
    logical             :: fuzzy_compare_iarr
    fuzzy_compare_iarr = all(abs(a - b) <= threshold)
    return
end function fuzzy_compare_iarr

function fuzzy_compare_i2arr(a, b, arrsize1, arrsize2, threshold)
! are a and b within threshold?
    integer, intent(in) :: arrsize1, arrsize2, a(arrsize1,arrsize2), b(arrsize1,arrsize2), threshold
    logical             :: fuzzy_compare_i2arr
    fuzzy_compare_i2arr = all(abs(a - b) <= threshold)
    return
end function fuzzy_compare_i2arr

subroutine report(result, result_size)
! report the results of a test. Result is a logical array that is true if tests are passed. result_size is the size of the result array. 
    integer, intent(in)         :: result_size
    logical, intent(in)         :: result(result_size)
    integer                     :: i
    if (.not. all(result)) then
        if (count(result==.false.) > 3) then
            write(*,*) 'You are illiterate!', count(result==.false.)
        else 
            write(*,*) 'You fail!', count(result==.false.), 'times.'
        end if
        do i = 1,size(result)
            if (.not. (result(i))) write(*,*) i
        end do
    else 
        write(*,*) 'You win!'
    end if
end subroutine report

end module tester_mod