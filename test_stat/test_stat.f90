program test_stat
! -------------------------------------------------------------------------------------
! I am using this to test modifications to simple_stat
! -------------------------------------------------------------------------------------
use simple_stat
use tester_mod
implicit none
save

logical                         :: result(1000)
integer                         :: alloc_stat
integer                         :: i, j, k, n
!integer, allocatable            :: cls(:)
real                            :: r, s, t
real, allocatable               :: cls_table(:,:), obj_table(:,:), cls_table2(:,:), obj_table2(:,:)

result = .true.

! -------------------------------------------------------------------------------------
! 1-9
! function avg_dist_table( dist_table, n_cls, n_obj, cls )
! -------------------------------------------------------------------------------------
! ! returns an avg_dist_table based on a distance table (dist_table) of n_obj objects that are clustered into n_cls clusters as indicated in the cls array. The distance between empty clusters is -1. 
!     integer, intent(in)             :: n_cls, n_obj, cls(n_obj)
!     real, intent(in)                :: dist_table(n_obj,n_obj)
!     real                            :: avg_dist_table(n_cls,n_cls)
allocate(obj_table(5,5), cls(5), cls_table(2,2), cls_table2(2,2))
obj_table = 0.
r = 1.
do i=1,4
    do j=i+1,5
        obj_table(i,j) = r
        obj_table(j,i) = r
        r = r + 1.
    end do
end do
 cls = (/2, 2, 1, 2, 1/)

 cls_table = avg_dist_table( obj_table, 2, 5, cls )
 cls_table2(1,:) = (/0., 6./)
 cls_table2(2,:) = (/6., 0./)
result(1) = fuzzy_compare(cls_table, cls_table2, 2, 2, 0.)
deallocate(cls_table, cls_table2)

! test if a cluster is empty
 cls = (/3, 3, 1, 3, 1/)
allocate(cls_table(3,3), cls_table2(3,3))
 cls_table = avg_dist_table( obj_table, 3, 5, cls )
 cls_table2(1,:) = (/0., -1., 6./)
 cls_table2(2,:) = (/-1., 0., -1./)
 cls_table2(3,:) = (/6., -1., 0./)
result(2) = fuzzy_compare(cls_table, cls_table2, 3, 3, 0.)

! test 3 clusters
 cls = (/2, 3, 1, 3, 1/)
 cls_table = avg_dist_table( obj_table, 3, 5, cls )
 cls_table2(1,:) = (/0., 3., 7.5/)
 cls_table2(2,:) = (/3., 0., 2./)
 cls_table2(3,:) = (/7.5, 2., 0./)
result(3) = fuzzy_compare(cls_table, cls_table2, 3, 3, 0.)
deallocate(obj_table, cls, cls_table, cls_table2)

! -------------------------------------------------------------------------------------
! 10-19
! function closest_obj(obj, dist_table, n_obj)
! -------------------------------------------------------------------------------------
! ! returns the closest object to obj that isn't obj in the distance table (dist_table). n_obj = number of objects in the table (= size of the array in one dimension). closest_obj ignores distances that are less than 0. 
!     integer, intent(in)             :: obj, n_obj
!     real, intent(in)                :: dist_table(n_obj,n_obj)
!     integer                         :: closest_obj
allocate(cls_table(3,3))
 cls_table(1,:) = (/0., -1., 6./)
 cls_table(2,:) = (/-1., 0., -1./)
 cls_table(3,:) = (/6., -1., 0./)
result(10) = fuzzy_compare(closest_obj(1,cls_table,3), 3, 0)
result(11) = fuzzy_compare(closest_obj(3,cls_table,3), 1, 0)

 cls_table(1,:) = (/0., 3., 7.5/)
 cls_table(2,:) = (/3., 0., 2./)
 cls_table(3,:) = (/7.5, 2., 0./)
result(12) = fuzzy_compare(closest_obj(1,cls_table,3), 2, 0)
result(13) = fuzzy_compare(closest_obj(2,cls_table,3), 3, 0)
result(14) = fuzzy_compare(closest_obj(3,cls_table,3), 2, 0)
deallocate(cls_table)

! -------------------------------------------------------------------------------------
! 20-29
! function avg_dist_to_cluster(dist_table, n_obj, cls, obj, cluster)
! -------------------------------------------------------------------------------------
!     ! returns the average distance from the object obj to each object in cluster. Mostly copied from refine_hac_score. 
!         integer, intent(in)             :: n_obj, cls(n_obj), obj, cluster
!         real, intent(in)                :: dist_table(n_obj, n_obj)
!         real                            :: avg_dist_to_cluster
allocate(obj_table(5,5), cls(5))
obj_table = 0.
r = 1.
do i=1,4
    do j=i+1,5
        obj_table(i,j) = r
        obj_table(j,i) = r
        r = r + 1.
    end do
end do
 cls = (/2, 3, 1, 3, 1/)
result(20) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 1, 1), 3., 0.)
result(21) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 1, 2), 0., 0.)
result(22) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 1, 3), 2., 0.)
result(23) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 2, 1), 6., 0.)
result(24) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 2, 2), 1., 0.)
result(25) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 2, 3), 6., 0.)
result(26) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 3, 1), 9., 0.)
result(27) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 3, 2), 2., 0.)
result(28) = fuzzy_compare(avg_dist_to_cluster(obj_table, 5, cls, 3, 3), 6.5, 0.)
deallocate(obj_table, cls)

! -------------------------------------------------------------------------------------
! 30-39
! function sil_width( cls, cluster_dist_table, n_obj, n_cls, obj_dist_table )
! -------------------------------------------------------------------------------------
! ! returns the sillhoutte width of a cluster (cls). cls = array indicating which cluster each object is in. cluster_dist_table is the distance table of distances between clusters. n_obj = number of objects. n_cls = number of clusters. 
!     integer, intent(in)             :: n_obj, n_cls, cls(n_obj)
!     real, intent(in)                :: cluster_dist_table(n_cls,n_cls)
!     real, intent(in)                :: obj_dist_table(n_obj,n_obj)
!     real                            :: sil_width

allocate(obj_table(5,5), cls(5), cls_table(3,3))
obj_table = 0.
r = 1.
do i=1,4
    do j=i+1,5
        obj_table(i,j) = r
        obj_table(j,i) = r
        r = r + 1.
    end do
end do
 cls = (/2, 3, 1, 3, 1/)
 cls_table(1,:) = (/0., 3., 7.5/)
 cls_table(2,:) = (/3., 0., 2./)
 cls_table(3,:) = (/7.5, 2., 0./)
result(30) = fuzzy_compare( sil_width(cls, cls_table, 5, 3, obj_table), (1.-5./6.-7./9.-3./6.-5./9.)/5., 0.)
deallocate(obj_table, cls, cls_table)

! -------------------------------------------------------------------------------------
! Report results of tests
! -------------------------------------------------------------------------------------
call report(result, size(result))

end program test_stat