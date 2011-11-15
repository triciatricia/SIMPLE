module simple_hcubsmp
use simple_jiffys
use simple_math
use simple_stat
implicit none

!TARGETS FOR PARALELLIZATION: GEN_ACOMBS, gridcls_fvecs

public :: make_hcubsmp, hcub_lsz, get_hcubsmp_stat
private

integer :: K        ! number of clusters
integer :: M        ! vector dimension
integer :: N        ! number of feature vectors
integer :: L        ! number of strata
integer :: hcub_lsz ! number of combinations
real, pointer        :: fvecs(:,:)=>null() ! dim (N,M)
real, allocatable    :: centers(:,:)       ! dim (M,L)
real, allocatable    :: hcub_lattice(:,:)  ! dim (L**M,M)
integer, allocatable :: hcub_rank(:)       ! dim (L**M)
integer, allocatable :: fvecs_cls(:)       ! dim (N)

contains

    subroutine make_hcubsmp( K_in, M_in, N_in, fvecs_in )
        integer, intent(in)      :: K_in, M_in, N_in
        real, intent(in), target :: fvecs_in(N_in,M_in)
        real                     :: chunk, low, high, dist
        integer                  :: alloc_stat, i, j
        ! set constants
        K = K_in
        M = M_in
        N = N_in
        L = max(2,ceiling(exp(log(real(K_in))/real(M_in))))
        hcub_lsz = L**M
        fvecs => fvecs_in
        ! allocate centers
        allocate( centers(M,L), hcub_lattice(hcub_lsz,M),&
        fvecs_cls(N), hcub_rank(hcub_lsz), stat=alloc_stat )
        call alloc_err('In: make_acombs, module: simple_acombs', alloc_stat)
        ! define centers
        do i=1,M
            low = minval(fvecs(:,i))
            high = maxval(fvecs(:,i))
            chunk = abs(high-low)/real(L+1)
            centers(i,1) = low+chunk
            do j=2,L
                centers(i,j) = centers(i,j-1)+chunk
            end do
        end do
        write(*,'(A)') '>>> MAKING A HYPER LATTICE'
        call gen_hcub_lattice
        call gridcls_fvecs( dist )
        call gridcls_rank
    end subroutine make_hcubsmp
    
    subroutine kill_hcubsmp
        deallocate( centers, hcub_lattice, fvecs_cls, hcub_rank )
    end subroutine kill_hcubsmp
    
    subroutine get_hcubsmp_stat( class_in, mean, cov, fracpop )
        integer, intent(in) :: class_in
        real, intent(inout) :: mean(M)
        real, intent(inout) :: cov(M,M)
        real, intent(out)   :: fracpop
        real :: diffvec(M,1), cov_det
        integer :: i, class
        real :: div
        ! set class according to rank
        class = hcub_rank(class_in)
        if( cls_pop(fvecs_cls, class) < 3 )then
            fracpop = 0.
            return
        endif
        ! first, calc ML estimate of mean
        div = 0.
        mean = 0.
        do i=1,N
            if( fvecs_cls(i) == class )then
                mean = mean+fvecs(i,:)
                div = div+1.
            endif
        end do
        mean = mean/div
        ! then, calc ML estimate of covariance matrix
        cov = 0.
        do i=1,N
            if( fvecs_cls(i) == class )then
                diffvec(:,1) = fvecs(i,:)-mean
                cov = cov+matmul(diffvec,transpose(diffvec))
            endif
        end do
        cov = cov/div
        fracpop = real(cls_pop(fvecs_cls, class))/real(N)
    end subroutine get_hcubsmp_stat
    
    subroutine gen_hcub_lattice
        select case (M)
         case(2)
             call gen_acombs_2
         case(3)
             call gen_acombs_3
         case(4)
             call gen_acombs_4
         case(5)
             call gen_acombs_5
         case(6)
             call gen_acombs_6
         case(7)
             call gen_acombs_7
         case(8)
             call gen_acombs_8
         case(9)
             call gen_acombs_9
         case(10)
             call gen_acombs_10
         case(11)
             call gen_acombs_11
         case(12)
             call gen_acombs_12
         case default
             write(*,*) 'The number of dimensions is not supported!'
             write(*,*) 'In: gen_hcub_lattice, module: simple_hcubsmp'
             stop
        end select
    end subroutine gen_hcub_lattice
    
    subroutine gridcls_fvecs( dist )
    ! para
        real, intent(out) :: dist
        real              :: dists(hcub_lsz)
        integer           :: loc(1),i,j
        dist = 0.
        do i=1,N
            do j=1,hcub_lsz
                dists(j) = euclid(fvecs(i,:),hcub_lattice(j,:))
            end do
            loc = minloc(dists)
            dist = dist+dists(loc(1))
            fvecs_cls(i) = loc(1)
        end do
        dist = dist/real(N)
    end subroutine gridcls_fvecs

    subroutine gridcls_rank
        real :: hcub_pop(hcub_lsz)
        integer :: j, new_lsz
        do j=1,hcub_lsz
            hcub_pop(j) = cls_pop(fvecs_cls, j)
            hcub_rank(j) = j
        end do
        call hpsort(hcub_lsz, hcub_pop, hcub_rank)
        call reverse_iarr(hcub_rank)
    end subroutine gridcls_rank
    
    subroutine gen_acombs_2
    ! M = 2
        integer :: a1,a2
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
        end do ; end do
    end subroutine gen_acombs_2

    subroutine gen_acombs_3
    ! M = 3
        integer :: a1,a2,a3
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
        end do ; end do ; end do
    end subroutine gen_acombs_3
    
    subroutine gen_acombs_4
    ! M = 4
        integer :: a1,a2,a3,a4
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
        end do ; end do ; end do ; end do
    end subroutine gen_acombs_4
    
    subroutine gen_acombs_5
    ! M = 5
        integer :: a1,a2,a3,a4,a5
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
        end do ; end do ; end do ; end do ; end do
    end subroutine gen_acombs_5
    
    subroutine gen_acombs_6
    ! M = 6
        integer :: a1,a2,a3,a4,a5,a6
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
        do a6=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
            hcub_lattice(cnt,6) = centers(6,a6)
        end do ; end do ; end do ; end do ; end do
        end do
    end subroutine gen_acombs_6
    
    subroutine gen_acombs_7
    ! M = 7
        integer :: a1,a2,a3,a4,a5,a6,a7
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
        do a6=1,L ; do a7=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
            hcub_lattice(cnt,6) = centers(6,a6)
            hcub_lattice(cnt,7) = centers(7,a7)
        end do ; end do ; end do ; end do ; end do
        end do ; end do
    end subroutine gen_acombs_7
    
    subroutine gen_acombs_8
    ! M = 8
        integer :: a1,a2,a3,a4,a5,a6,a7,a8
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
        do a6=1,L ; do a7=1,L ; do a8=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
            hcub_lattice(cnt,6) = centers(6,a6)
            hcub_lattice(cnt,7) = centers(7,a7)
            hcub_lattice(cnt,8) = centers(8,a8)
        end do ; end do ; end do ; end do ; end do
        end do ; end do ; end do
    end subroutine gen_acombs_8
    
    subroutine gen_acombs_9
    ! M = 9
        integer :: a1,a2,a3,a4,a5,a6,a7,a8,a9
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
        do a6=1,L ; do a7=1,L ; do a8=1,L ; do a9=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
            hcub_lattice(cnt,6) = centers(6,a6)
            hcub_lattice(cnt,7) = centers(7,a7)
            hcub_lattice(cnt,8) = centers(8,a8)
            hcub_lattice(cnt,9) = centers(9,a9)
        end do ; end do ; end do ; end do ; end do
        end do ; end do ; end do ; end do
    end subroutine gen_acombs_9
    
    subroutine gen_acombs_10
    ! M = 10
        integer :: a1,a2,a3,a4,a5,a6,a7,a8,a9,a10
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
        do a6=1,L ; do a7=1,L ; do a8=1,L ; do a9=1,L ; do a10=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
            hcub_lattice(cnt,6) = centers(6,a6)
            hcub_lattice(cnt,7) = centers(7,a7)
            hcub_lattice(cnt,8) = centers(8,a8)
            hcub_lattice(cnt,9) = centers(9,a9)
            hcub_lattice(cnt,10) = centers(10,a10)
        end do ; end do ; end do ; end do ; end do
        end do ; end do ; end do ; end do ; end do
    end subroutine gen_acombs_10
    
    subroutine gen_acombs_11
    ! M = 11
        integer :: a1,a2,a3,a4,a5,a6,a7,a8,a9,a10
        integer :: a11
        integer :: cnt
        cnt = 0
        do a1=1,L ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
        do a6=1,L ; do a7=1,L ; do a8=1,L ; do a9=1,L ; do a10=1,L
        do a11=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
            hcub_lattice(cnt,6) = centers(6,a6)
            hcub_lattice(cnt,7) = centers(7,a7)
            hcub_lattice(cnt,8) = centers(8,a8)
            hcub_lattice(cnt,9) = centers(9,a9)
            hcub_lattice(cnt,10) = centers(10,a10)
            hcub_lattice(cnt,11) = centers(11,a11)
        end do ; end do ; end do ; end do ; end do
        end do ; end do ; end do ; end do ; end do
        end do
    end subroutine gen_acombs_11
    
    subroutine gen_acombs_12
    ! M = 12
        integer :: a1,a2,a3,a4,a5,a6,a7,a8,a9,a10
        integer :: a11,a12
        integer :: cnt
        cnt = 0
        do a1=1,L  ; do a2=1,L ; do a3=1,L ; do a4=1,L ; do a5=1,L
        do a6=1,L  ; do a7=1,L ; do a8=1,L ; do a9=1,L ; do a10=1,L
        do a11=1,L ; do a12=1,L
            cnt = cnt+1           
            hcub_lattice(cnt,1) = centers(1,a1)
            hcub_lattice(cnt,2) = centers(2,a2)
            hcub_lattice(cnt,3) = centers(3,a3)
            hcub_lattice(cnt,4) = centers(4,a4)
            hcub_lattice(cnt,5) = centers(5,a5)
            hcub_lattice(cnt,6) = centers(6,a6)
            hcub_lattice(cnt,7) = centers(7,a7)
            hcub_lattice(cnt,8) = centers(8,a8)
            hcub_lattice(cnt,9) = centers(9,a9)
            hcub_lattice(cnt,10) = centers(10,a10)
            hcub_lattice(cnt,11) = centers(11,a11)
            hcub_lattice(cnt,12) = centers(12,a12)
        end do ; end do ; end do ; end do ; end do
        end do ; end do ; end do ; end do ; end do
        end do ; end do
    end subroutine gen_acombs_12
        
end module simple_hcubsmp