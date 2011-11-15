program resolve
use simple_fstk
use simple_spidoc
use simple_params
use simple_usupcls
use simple_sll_list
use simple_jiffys
use simple_build
use simple_aligndata
implicit none
save
! MAKE SURE THAT THE PROJECTION DIRECTIONS ARE ASSIGNED
! IMPLEMENT COMMON LINES BASED REFINEMENT OVER DIFFERENT STATEGROUPS

type(build), target :: b
integer            :: file_stat, alloc_stat
type(sll_list)     :: plist
integer            :: i, ncls_here
integer, parameter :: funit=66
integer, allocatable :: eulcls(:)
type(sll_list), allocatable :: eclasses(:)
if( command_argument_count() < 4 )then
    write(*,*) './classify fstk=instk.fim lp=<low-pass limit (in A)> ncls=<nr of classes> outfile=<status report file> nspace=<nr of projection groups> oritab=<input orientations> nthr=<nr of openMP threads> [hp=<high-pass limit (in A)>] [debug=<yes|no>]'
    stop
endif
! Build
b = new_build( 2 ) ! mode=2, hac
! open status report file
open(unit=funit, file=outfile, status='replace', iostat=file_stat, action='write', form='formatted')
call fopen_err( 'In: classify', file_stat )
write(funit,'(A)') "**** UNSUPERVISED CLASSIFICATION PROCEDURE BEGINS ****"
! shift and rotate according to input orientations
call shrot_fstk( b, 'inplalgnstk.fim' )
! set global stack variable
stk = 'inplalgnstk.fim'
write(funit,'(A)') "WROTE 2D ALIGNED TRANSFORMS TO SIMPLE STACK: inplalgnstk.fim"
! Classify within nspace projection direction classes
! build e_ref for the orientation matrices
call kill_eulers(b%e_ref)
b%e_ref = new_eulers(nptcls) 
do i=1,nptcls
    call set_euler( b%e_ref, i, oris(i,1), oris(i,2), oris(i,3) )
end do
allocate( eulcls(nptcls), stat=alloc_stat )
call alloc_err('In: classify', alloc_stat)
! make projection direction classes
call classify_eulers( b%e_ref, nspace, pgrp, eulcls )
! convert to singly linked list representation
call arr_to_sll_cls( eulcls, nptcls, eclasses )
do i=1,nspace
    ! make HAC functionality
    call make_usupcls( b, plist, fstk )
    ! do the classification
    call usupcls_master
    ! kill the HAC functionality
    call kill_usupcls
end do
end program resolve