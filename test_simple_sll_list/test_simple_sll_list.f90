! -------------------------------------------------------------------------------------
! The purpose is to test functions and subroutines added to simple_sll_list. 
! -------------------------------------------------------------------------------------
program test_simple_sll_list
use simple_sll_list
use tester_mod
implicit none

logical                         :: result(1000)
type(sll_list)			:: testlist, testlist2, listarr1(3), listarr2(3)
integer				:: n

! Initialize
result = .TRUE.

! -------------------------------------------------------------------------------------
! insert_sll_node
! (1:19)
! -------------------------------------------------------------------------------------
testlist = new_sll_list()

! Insert 1.
call insert_sll_node(testlist, 1, 1)
call get_sll_node(testlist, 1, n)
result(1) = fuzzy_compare(n, 1, 0)

! Insert 2 at position 1.
call insert_sll_node(testlist, 1, 2)
call get_sll_node(testlist, 1, n)
result(2) = fuzzy_compare(n, 2, 0)
call get_sll_node(testlist, 2, n)
result(3) = fuzzy_compare(n, 1, 0)

! Insert 3 at position 2.
call insert_sll_node(testlist, 2, 3)
call get_sll_node(testlist, 1, n)
result(4) = fuzzy_compare(n, 2, 0)
call get_sll_node(testlist, 2, n)
result(5) = fuzzy_compare(n, 3, 0)
call get_sll_node(testlist, 3, n)
result(6) = fuzzy_compare(n, 1, 0)

! Insert 4 at position 4.
call insert_sll_node(testlist, 4, 4)
call get_sll_node(testlist, 1, n)
result(7) = fuzzy_compare(n, 2, 0)
call get_sll_node(testlist, 2, n)
result(8) = fuzzy_compare(n, 3, 0)
call get_sll_node(testlist, 3, n)
result(9) = fuzzy_compare(n, 1, 0)
call get_sll_node(testlist, 4, n)
result(10) = fuzzy_compare(n, 4, 0)

result(11) = fuzzy_compare(get_sll_size(testlist), 4, 0)

! Should error:
! call insert_sll_node(testlist, 6, 6)

call kill_sll_list(testlist)

! -------------------------------------------------------------------------------------
! copy_int_sll_list
! (20:39)
! -------------------------------------------------------------------------------------
testlist = new_sll_list()

! Insert nodes.
call insert_sll_node(testlist, 1, 1)
call insert_sll_node(testlist, 1, 2)
call insert_sll_node(testlist, 2, 3)
call insert_sll_node(testlist, 4, 4)

testlist2 = copy_int_sll_list(testlist)
call get_sll_node(testlist2, 1, n)
result(20) = fuzzy_compare(n, 2, 0)
call get_sll_node(testlist2, 2, n)
result(21) = fuzzy_compare(n, 3, 0)
call get_sll_node(testlist2, 3, n)
result(22) = fuzzy_compare(n, 1, 0)
call get_sll_node(testlist2, 4, n)
result(23) = fuzzy_compare(n, 4, 0)

! This shouldn't error:
call kill_sll_list(testlist)
call get_sll_node(testlist2, 1, n)
result(24) = fuzzy_compare(n, 2, 0)
call get_sll_node(testlist2, 2, n)
result(25) = fuzzy_compare(n, 3, 0)
call get_sll_node(testlist2, 3, n)
result(26) = fuzzy_compare(n, 1, 0)
call get_sll_node(testlist2, 4, n)
result(27) = fuzzy_compare(n, 4, 0)

listarr1(1) = copy_int_sll_list(testlist2)
listarr1(2) = copy_int_sll_list(testlist2)
listarr1(3) = copy_int_sll_list(testlist2)

listarr2 = copy_int_sll_list(listarr1, 3)
do n=1,3
    call kill_sll_list(listarr1(n))
end do
call kill_sll_list(testlist2)
! This shouldn't error:
testlist2 = copy_int_sll_list(listarr2(2))
! This shouldn't error:
call get_sll_node(testlist2, 1, n)
result(28) = fuzzy_compare(n, 2, 0)
call get_sll_node(testlist2, 2, n)
result(29) = fuzzy_compare(n, 3, 0)
call get_sll_node(testlist2, 3, n)
result(30) = fuzzy_compare(n, 1, 0)
call get_sll_node(testlist2, 4, n)
result(31) = fuzzy_compare(n, 4, 0)
do n=1,3
    call kill_sll_list(listarr2(n))
end do
call kill_sll_list(testlist2)

! -------------------------------------------------------------------------------------
! Report results of tests
! -------------------------------------------------------------------------------------
call report(result, size(result))

end program test_simple_sll_list