module simple_stat
use simple_def_precision
use simple_pair_wtab
use simple_sll_list
use simple_jiffys
use simple_math
use simple_rnd
use simple_params
implicit none
save

interface normalize
    module procedure normalize_1
    module procedure normalize_2
    module procedure normalize_3
end interface

interface moment
    module procedure moment_1
    module procedure moment_2
    module procedure moment_3
end interface

interface convert_to_rank
    module procedure convert_to_rank_1
    module procedure convert_to_rank_2
end interface

contains

	subroutine histogram( arr, bins, sc )
    ! generates a primitive histogram given an array of real data
        real, intent(in)    :: arr(:)
        integer, intent(in) :: bins, sc
        real                :: a(bins), minv, maxv, mean, std, var, binwidth
        integer             :: h(bins), bin, i, j, n
        logical             :: err
        write(*,*) ">>> GENERATING HISTOGRAM <<<"
        n = size(arr,1)
        call moment( arr, mean, std, var, err )
        minv = minval(arr)
        maxv = maxval(arr)
        write(*,*) "Number of values = ", n
        write(*,*) "Minimum value = ", minv
        write(*,*) "Maximum value = ", maxv
        write(*,*) "Mean value = ", mean
        write(*,*) "Standard deviation = ", std
        write(*,*) "Variance = ", var
        h = 0
        binwidth = (maxv-minv)/real(bins)
        do i=1,n 
            bin = nint((arr(i)-minv)/binwidth)  ! int(1.+(arr(i)-minv)/binwidth)
            if( bin < 1 )    bin = 1    ! check for underflows
            if( bin > bins ) bin = bins ! check for overflows
            h(bin) = h(bin)+1
            a(bin) = a(bin)+arr(i)
        end do
        do i=1,bins
            a(i) = a(i)/real(h(i))
            write(*,*) a(i),h(i),"|",('#', j=1,nint(real(h(i))/real(sc)))
        end do
    end subroutine histogram

    subroutine moment_1( data, ave, sdev, var, err )
    ! given a 1D real array of data, this routine returns its mean: _ave_,
    ! standard deviation: _sdev_, and variance: _var_
        real, intent(out)    :: ave, sdev, var
        logical, intent(out) :: err
        real, intent(in)     :: data(:)
        integer              :: n, i
        real                 :: ep, nr, dev
        err = .false.
        n   = size(data,1)
        nr  = n
        if( n <= 1 ) then
            write(*,*) 'ERROR: n must be at least 2'
            write(*,*) 'In: moment_1, module: simple_stat.f90'
            stop
        endif
        ! calc average
        ave = 0.
        do i=1,n
            ave = ave+data(i)
        end do
        ave = ave/nr
        ! calc sum of devs and sum of devs squared
        ep = 0.        
        var = 0.
        do i=1,n
            dev = data(i)-ave
            ep = ep+dev
            var = var+dev*dev
        end do
        var = (var-ep**2./nr)/(nr-1.) ! corrected two-pass formula
        sdev = sqrt(var)
        if( var == 0. ) err = .true.
    end subroutine moment_1
    
    subroutine deviation( data, point, sdev, var, err )
    ! given a 1D real array of data, this routine returns its mean: _point_,
    ! standard deviation: _sdev_, and variance: _var_
        real, intent(out)    :: sdev, var
        logical, intent(out) :: err
        real, intent(in)     :: data(:), point
        integer              :: n, i
        real                 :: ep, nr, dev
        err = .false.
        n   = size(data,1)
        nr  = n
        ! calc sum of devs and sum of devs squared
        ep = 0.        
        var = 0.
        do i=1,n
            dev = data(i)-point
            ep = ep+dev
            var = var+dev*dev
        end do
        var = (var-ep**2./nr)/(nr-1.) ! corrected two-pass formula
        sdev = sqrt(var)
        if( var == 0. ) err = .true.
    end subroutine deviation
    
    subroutine moment_2( data, ave, sdev, var, err )
    ! given a 2D real array of data, this routine returns its mean: _ave_,
    ! standard deviation: _sdev_, and variance: _var_
        real, intent(out)    :: ave, sdev, var
        logical, intent(out) :: err
        real, intent(in)     :: data(:,:)
        integer              :: nx, ny, n, i, j
        real                 :: ep, nr, dev
        err = .false.
        nx = size(data,1)
        ny = size(data,2)
        n  = nx*ny
        nr = n
        if( n <= 1 ) then
            write(*,*) 'ERROR: n must be at least 2'
            write(*,*) 'In: moment_2, module: simple_stat.f90'
            stop
        endif
        ! calc average
        ave = 0.
        do i=1,nx
            do j=1,ny
                ave = ave+data(i,j)
            end do
        end do
        ave = ave/nr
        ! calc sum of devs and sum of devs squared
        ep = 0.        
        var = 0.
        do i=1,nx
            do j=1,ny
                dev = data(i,j)-ave
                ep = ep+dev
                var = var+dev*dev
            end do
        end do
        var = (var-ep**2./nr)/(nr-1.) ! corrected two-pass formula
        sdev = sqrt(var)
        if( var == 0. ) err = .true.
    end subroutine moment_2
    
    subroutine moment_3( data, ave, sdev, var, err )
    ! given a 3D real array of data, this routine returns its mean: _ave_,
    ! standard deviation: _sdev_, and variance: _var_
        real, intent(out)    :: ave, sdev, var
        logical, intent(out) :: err
        real, intent(in)     :: data(:,:,:)
        integer              :: nx, ny, nz, n, i, j, k
        real                 :: ep, nr, dev
        err = .false.
        nx = size(data,1)
        ny = size(data,2)
        nz = size(data,3)
        n  = nx*ny*nz
        nr = n
        if( n <= 1 ) then
            write(*,*) 'ERROR: n must be at least 2'
            write(*,*) 'In: moment_3, module: simple_stat.f90'
            stop
        endif
        ! calc average
        ave = 0.
        do i=1,nx
            do j=1,ny
                do k=1,ny
                    ave = ave+data(i,j,k)
                end do
            end do
        end do
        ave = ave/nr
        ! calc sum of devs and sum of devs squared
        ep = 0.        
        var = 0.
        do i=1,nx
            do j=1,ny
                do k=1,nz
                    dev = data(i,j,k)-ave
                    ep = ep+dev
                    var = var+dev*dev
                end do
            end do
        end do
        var = (var-ep**2./nr)/(nr-1.) ! corrected two-pass formula
        sdev = sqrt(var)
        if( var == 0. ) err = .true.
    end subroutine moment_3
    
    function pearsn( x, y, n ) result( r )
    ! Given two real arrays x(1:n) and y(1:n) this routine calculates their correlation coefficient
        integer, intent(in) :: n
        real                :: x(n),y(n),r,ax,ay,sxx,syy,sxy,xt,yt,sqrtprod
        integer             :: j
        ax  = sum(x)/real(n)
        ay  = sum(y)/real(n)
        sxx = 0.
        syy = 0.
        sxy = 0.
        do j=1,n
            xt  = x(j)-ax
            yt  = y(j)-ay
            sxx = sxx+xt**2
            syy = syy+yt**2
            sxy = sxy+xt*yt
        end do
        sqrtprod = sqrt(sxx*syy) 
        if(sxy == 0. .or. (sxy > 0. .or. sxy < 0.))then
            if( sqrtprod == 0. )then
                r = -1. 
            else
                r = sxy/sqrtprod ! Pearsons corr. coeff
            endif
        else
            r = -1.
        endif
    end function pearsn

    subroutine hac_cls( pw, nobj, ncls, maxp, classes)
    ! Hierachical Agglomerative Classification of a pair-weight table of correlations
    ! the pair weight table is cleared after this operation
    	type(pair_wtab), intent(inout) :: pw
        integer, intent(in)    :: nobj ! number of objects to classify
        integer, intent(inout) :: ncls ! number of classes
        integer, intent(in)    :: maxp ! maximum nr of ptcls 
        type(sll_list)         :: classes(nobj) ! array of linked lists, for storing the cls-info
        real    :: corr
        integer :: i, j, nptcls
        integer :: nclasses, round
        logical :: halt
        ! initialize parameters
        nclasses = nobj
        round    = 0
        ! flush a copy of the pw table before molesting it
        call flush_pair_wtab( pw, pwfile )
        write(*,'(A)') ">>> HA-CLASSIFICATION USING THE GROUP AVERAGE METHOD"
        do while(nclasses > ncls)
            round = round+1
            if( round == 1 .or. mod(round,500) == 0 ) then
                write(*,"(1X,A)", advance="no") 'Iteration:'
                write(*,"(1X,I7)", advance="no") round
                write(*,"(1X,A)", advance="no") 'Nclasses:'
                write(*,"(1X,I7)", advance="no") nclasses
            endif
            ! get the max scoring merge out
            call get_wmax_pair( pw, i, j, corr, halt )
            if( round == 1 .or. mod(round,500) == 0 ) then
                write(*,"(1X,A)", advance="no") 'Corr:'
                write(*,"(1X,F7.4)") corr
            endif 
            if( halt ) exit
            ! predict the resulting nr of ptcls
            nptcls = get_sll_size(classes(i))+get_sll_size(classes(j))
            if( nptcls > maxp )then
                ! remove the entry from the pw-tab
                call remove_pair_w( pw, i, j )
                cycle
            endif
            ! merge the cluster pair
            classes(i) = append_sll_lists(classes(i),classes(j))
            ! merge the entries in the pw-tab
            call merge_pair_w( pw, i, j )
            ! update the number of classes
            nclasses = nclasses-1
        end do
        ncls = nclasses
        call clear_pair_wtab( pw ) 
        write(*,"(1X,A)", advance="no") 'Iteration:'
        write(*,"(1X,I7)", advance="no") round
        write(*,"(1X,A)", advance="no") 'Nclasses:'
        write(*,"(1X,I7)", advance="no") nclasses
        write(*,"(1X,A)", advance="no") 'Corr:'
        write(*,"(1X,F7.4)") corr
    end subroutine hac_cls
    
    subroutine refine_hac_cls( pw, nobjs, ncls, nreclust, cls, lim )
    	type(pair_wtab), intent(in) :: pw
        integer, intent(in) :: nobjs, ncls, nreclust
        integer, intent(out) :: cls(nobjs)
        integer, intent(in) :: lim
        real :: pcorrs(nobjs), corr, corr_prev
        integer :: class, i, it, ptcls(nobjs), worst
        write(*,'(A)') ">>> REFINEMENT BY ADAPTIVE GREEDY LOCAL SEARCH"
        call recover_pair_wtab( pw, pwfile )
        it = 0
        corr = -1.
        do
            it = it+1
            ! calculate all particle scores        
            !$omp parallel do default(shared) private(i) schedule(static)
            do i=1,nobjs
                pcorrs(i) = refine_hac_score( pw, nobjs, cls, i, cls(i) )
            end do
            !$omp end parallel do
            ! order the ptcls
            ptcls = (/(i,i=1,nobjs)/)
            call hpsort(nobjs, pcorrs, ptcls)
            corr_prev = corr
            corr = sum(pcorrs)/real(nobjs)
            if( it == 1 .or. (mod(it,10) == 0 .or. abs(corr-corr_prev) < 0.0005) ) then
                write(*,"(1X,A)", advance="no") 'Iteration:'
                write(*,"(1X,I7)", advance="no") it
                write(*,"(1X,A)", advance="no") 'Corr:'
                write(*,"(1X,F7.4)") corr
                if( abs(corr-corr_prev) < 0.0005 ) exit
            endif
            ! recluster using greedy local search
            do i=1,nreclust
                class = find_best_class( pw, nobjs, ncls, cls, ptcls(i) )
                if( cls(ptcls(i)) == class ) cycle
                ! apply the change
                cls(ptcls(i)) = class
                if( cls_pop(cls,class) > lim )then
                    ! reassign the worst fitting ptcl in class to the best available
                    worst = find_worst_ptcl(pw, nobjs, cls, class)
                    class = find_best_avail_class(pw, nobjs, ncls, cls, worst, lim)
                    cls(worst) = class
                endif
            end do
            if( it >= 30 ) exit
        end do
        ! remove the pwfile
        call del_binfile(pwfile)
    end subroutine refine_hac_cls
    
    function refine_hac_score( pw, nobjs, cls, ptcl, class ) result( ccorr )
        type(pair_wtab), intent(in) :: pw
        integer, intent(in) :: nobjs, ptcl, class
        integer, intent(in) :: cls(nobjs)
        integer :: cnt, i
        real :: ccorr
        ccorr = 0.
        cnt   = 0
        do i=1,nobjs
            if(i /= ptcl .and. cls(i) == class)then
                ccorr = ccorr+get_pair_w( pw, ptcl, i )
                cnt   = cnt+1
            endif   
        end do
        if( cnt /= 0 )then
            ccorr = ccorr/real(cnt)
        else
            ccorr = 0. ! to not penalize lonely ptcls
        endif          
    end function refine_hac_score
    
    function find_best_class( pw, nobjs, ncls, cls, ptcl ) result( class )
        type(pair_wtab), intent(in) :: pw
        integer, intent(in) :: nobjs, ncls, ptcl
        integer, intent(in) :: cls(nobjs)
        integer :: class
        real :: clscorrs(ncls)
        integer :: loc(1), i
        !$omp parallel do default(shared) private(i) schedule(static)
        do i=1,ncls
            clscorrs(i) = refine_hac_score( pw, nobjs, cls, ptcl, i )
        end do
        !$omp end parallel do
        loc   = maxloc(clscorrs)
        class = loc(1)
    end function find_best_class
    
    function find_best_avail_class( pw, nobjs, ncls, cls, ptcl, lim ) result( class )
        type(pair_wtab), intent(in) :: pw
        integer, intent(in) :: nobjs, ncls, ptcl, lim
        integer, intent(in) :: cls(nobjs)
        integer :: class
        real :: clscorrs(ncls)
        integer :: loc(1), i
        !$omp parallel do default(shared) private(i) schedule(static)
        do i=1,ncls
            if( cls_pop(cls,i) > lim )then
                clscorrs(i) = -1.
            else
                clscorrs(i) = refine_hac_score( pw, nobjs, cls, ptcl, i )
            endif
        end do
        !$omp end parallel do
        loc   = maxloc(clscorrs)
        class = loc(1)
    end function find_best_avail_class
    
    function find_worst_ptcl( pw, nobjs, cls, class ) result( ptcl )
        type(pair_wtab), intent(in) :: pw
        integer, intent(in) :: nobjs
        integer, intent(in) :: cls(nobjs)
        integer, intent(in) :: class
        real :: corrs(nobjs)
        integer :: loc(1), i, ptcl
        corrs = 1.
        !$omp parallel do default(shared) private(i) schedule(static)
        do i=1,nobjs
            if( cls(i) == class ) corrs(i) = refine_hac_score( pw, nobjs, cls, i, class )
        end do
        !$omp end parallel do
        loc  = minloc(corrs)
        ptcl = loc(1)
    end function find_worst_ptcl
    
    function cls_pop( cls, class ) result( pop )
         integer, intent(in) :: cls(:), class
         integer             :: i, pop
         pop = 0
         do i=1,size(cls)
             if( cls(i) == class ) pop = pop+1
         end do
     end function cls_pop

    subroutine sll_to_arr_cls( classes, nobj, cls, clsnr )
    ! translate the sll representation of cls to array representation
        integer, intent(in)    :: nobj
        integer, intent(inout) :: clsnr
        type(sll_list)         :: classes(nobj) ! array of linked lists, for storing the cls-info
        integer, intent(out)   :: cls(nobj)
        integer :: i, j, ptcl
        do i=1,nobj
            if( get_sll_size(classes(i)) >= 1 )then
                do j=1,get_sll_size(classes(i))
                    call get_sll_node(classes(i), j, ptcl)
                    cls(ptcl) = clsnr
                end do
                clsnr = clsnr+1             
            endif
        end do       
    end subroutine sll_to_arr_cls
    
    subroutine arr_to_sll_cls( cls, nobj, classes )
    ! translate the arr representation of cls to sll representation
        integer, intent(in) :: nobj, cls(nobj)
        type(sll_list)      :: classes(nobj) ! array of linked lists, for storing the cls-info
        integer :: i, j
        do i=1,nobj
            call kill_sll_list(classes(i))
            classes(i) = new_sll_list()
            call add_sll_node(classes(i), i)
        end do
        do i=1,nobj-1
            do j=i+1,nobj
                if(cls(i) /= 0 .and. cls(j) /= 0 )then
                    if(cls(i) == cls(j))then
                        if(get_sll_size(classes(i)) >= 1)then
                            ! merge the cluster pair
                            classes(i) = append_sll_lists(classes(i),classes(j))
                        else
                            exit
                        endif
                    endif
                endif
            end do
        end do
    end subroutine arr_to_sll_cls
    
    subroutine normalize_1( arr, err )
        real, intent(inout)  :: arr(:)
        real                 :: ave, sdev, var
        logical, intent(out) :: err
        call moment_1( arr, ave, sdev, var, err )
        if( err ) return
        arr = (arr-ave)/sdev ! array op    
    end subroutine normalize_1
    
    subroutine normalize_2( arr, err )
        real, intent(inout)  :: arr(:,:)
        real                 :: ave, sdev, var
        logical, intent(out) :: err
        call moment_2( arr, ave, sdev, var, err )
        if( err ) return
        arr = (arr-ave)/sdev ! array op    
    end subroutine normalize_2
    
    subroutine normalize_3( arr, err )
        real, intent(inout)  :: arr(:,:,:)
        real                 :: ave, sdev, var
        logical, intent(out) :: err
        call moment_3( arr, ave, sdev, var, err )
        if( err ) return
        arr = (arr-ave)/sdev ! array op    
    end subroutine normalize_3
    
    subroutine gen_wvec( arr )
        real, intent(inout) :: arr(:)
        integer :: n, i
        n = size(arr)
        do i=1,n
            arr(i) = ran3()
        end do
        call hpsort(n,arr)
        call reverse_rarr(arr)
        arr = arr/sum(arr)
    end subroutine gen_wvec 
          
    ! integer stuff
    
    subroutine convert_to_rank_1( n, arr, rank )
    ! convert real array to rank array
        integer, intent(in)  :: n
        real, intent(in)     :: arr(n)
        integer, intent(out) :: rank(n)
        integer              :: j
        integer              :: order(n)
        real                 :: arr_copy(n)
        arr_copy = arr
        order = (/(j,j=1,n)/)
        call hpsort(n, arr_copy, order)
        ! convert to rank
        do j=1,n
            rank(order(j)) = j
        end do
    end subroutine convert_to_rank_1
    
    subroutine convert_to_rank_2( n, arr, order, rank )
    ! convert real array to rank array
        integer, intent(in)  :: n
        real, intent(inout)  :: arr(n)
        integer, intent(out) :: rank(n), order(n)
        integer              :: j
        order = (/(j,j=1,n)/)
        call hpsort(n, arr, order)
        ! convert to rank
        do j=1,n
            rank(order(j)) = j
        end do
    end subroutine convert_to_rank_2
    
    function spear( n, pi1, pi2 ) result( corr )
    ! Spearman rank correlation
        integer, intent(in) :: n, pi1(n), pi2(n)
        real                :: corr, sqsum, rn
        integer             :: k
        rn    = real(n)
        sqsum = 0. 
        do k=1,n
            sqsum = sqsum+(pi1(k)-pi2(k))**2.
        end do
        corr = 1.-(6.*sqsum)/(rn**3.-rn)
    end function spear
        
    function avg_dist_table( dist_table, n_cls, n_obj, cls )
    ! returns an avg_dist_table based on a distance table (dist_table) of n_obj objects that are clustered into n_cls clusters as indicated in the cls array. The distance between empty clusters is -1. 
        integer, intent(in)             :: n_cls, n_obj, cls(n_obj)
        real, intent(in)                :: dist_table(n_obj,n_obj)
        real                            :: avg_dist_table(n_cls,n_cls)
        integer                         :: i, j, n, cls_i, cls_j, n_cls_i, n_cls_j
        avg_dist_table = 0.
        do i=1,n_obj-1
            do j=i+1,n_obj
                cls_i = cls(i)
                cls_j = cls(j)
                if (cls_i /= cls_j) then
                    avg_dist_table(cls_i,cls_j) = dist_table(i,j) + avg_dist_table(cls_i,cls_j)
                    avg_dist_table(cls_j,cls_i) = dist_table(i,j) + avg_dist_table(cls_j,cls_i)
                end if
            end do
        end do
        do i=1,n_cls-1
            do j=i+1,n_cls
                n_cls_i = count(cls==i)
                n_cls_j = count(cls==j)
                if (n_cls_i==0 .or. n_cls_j==0.) then
                    avg_dist_table(i,j) = -1.
                    avg_dist_table(j,i) = -1.
                else
                    n =  n_cls_i * n_cls_j
                    avg_dist_table(i,j) = avg_dist_table(i,j)/n
                    avg_dist_table(j,i) = avg_dist_table(i,j)
                end if
            end do
        end do
        do n=1,n_cls
            avg_dist_table(n,n) = 0.
        end do
        return
    end function avg_dist_table
    
    function sil_width( cls, cluster_dist_table, n_obj, n_cls, obj_dist_table )
    ! returns the overall silhouette width. cluster = cls. cls = array indicating which cluster each object is in. cluster_dist_table is the distance table of distances between clusters. n_obj = number of objects. n_cls = number of clusters. 
        integer, intent(in)             :: n_obj, n_cls, cls(n_obj)
        real, intent(in)                :: cluster_dist_table(n_cls,n_cls)
        real, intent(in)                :: obj_dist_table(n_obj,n_obj)
        real                            :: sil_width, sil_width_n(n_obj), dist_self, dist_other
        integer                         :: i, j, n, closest_cluster(n_cls)
        do n=1,n_cls
            closest_cluster(n) = closest_obj(n, cluster_dist_table, n_cls)
        end do
        do n=1,n_obj
            dist_self = avg_dist_to_cluster(obj_dist_table, n_obj, cls, n, cls(n))
            dist_other = avg_dist_to_cluster(obj_dist_table, n_obj, cls, n, closest_cluster(cls(n)))
            sil_width_n(n) = (dist_other - dist_self) / max(dist_other, dist_self)
        end do
        sil_width = sum(sil_width_n)/size(sil_width_n)
        return
    end function sil_width
    
    function sil_width_cls( cls, cluster_dist_table, n_obj, n_cls, obj_dist_table, min_n )
    ! returns the silhouette widths of clusters with at least min_n members. cluster = cls. cls = array indicating which cluster each object is in. cluster_dist_table is the distance table of distances between clusters. n_obj = number of objects. n_cls = number of clusters. 
        integer, intent(in)             :: n_obj, n_cls, cls(n_obj), min_n
        real, intent(in)                :: cluster_dist_table(n_cls,n_cls)
        real, intent(in)                :: obj_dist_table(n_obj,n_obj)
        real                            :: sil_width_cls(n_cls), dist_self, dist_other
        integer                         :: i, j, n, closest_cluster(n_cls), cls_size(n_cls)
        integer                         :: cls_n
        ! Find the closest cluster to each one.
        do n=1,n_cls
            closest_cluster(n) = closest_obj(n, cluster_dist_table, n_cls)
        end do
        sil_width_cls = 0.
        cls_size = 0
        do n=1,n_obj
            cls_size(cls(n)) = cls_size(cls(n)) + 1
        end do
        ! Calculate the sil. width for each object, and sum up for each cluster. 
        do n=1,n_obj
            cls_n = cls(n)
            if (cls_size(cls_n) >= min_n) then
                dist_self = avg_dist_to_cluster(obj_dist_table, n_obj, cls, n, cls_n)
                dist_other = avg_dist_to_cluster(obj_dist_table, n_obj, cls, n, closest_cluster(cls_n))
                sil_width_cls(cls_n) = sil_width_cls(cls_n) + ((dist_other - dist_self) / max(dist_other, dist_self)) / cls_size(cls_n)
	    else 
		sil_width_cls(cls_n) = -1.
            end if
        end do
        return
    end function sil_width_cls
    
    function dist_self( cls, cluster_dist_table, n_obj, n_cls, obj_dist_table )
    ! returns the silhouette width of individual objects. cluster cls. cls = array indicating which cluster each object is in. cluster_dist_table is the distance table of distances between clusters. n_obj = number of objects. n_cls = number of clusters. 
        integer, intent(in)             :: n_obj, n_cls, cls(n_obj)
        real, intent(in)                :: cluster_dist_table(n_cls,n_cls)
        real, intent(in)                :: obj_dist_table(n_obj,n_obj)
        real                            :: dist_self(n_obj)
        integer                         :: i, j, n, closest_cluster(n_cls)
        do n=1,n_cls
            closest_cluster(n) = closest_obj(n, cluster_dist_table, n_cls)
        end do
        do n=1,n_obj
            dist_self(n) = avg_dist_to_cluster(obj_dist_table, n_obj, cls, n, cls(n))
        end do
        return
    end function dist_self
    
    function avg_dist_to_cluster(dist_table, n_obj, cls, obj, cluster)
    ! returns the average distance from the object obj to each object in cluster. Mostly copied from refine_hac_score. 
        integer, intent(in)             :: n_obj, cls(n_obj), obj, cluster
        real, intent(in)                :: dist_table(n_obj, n_obj)
        real                            :: avg_dist_to_cluster
        integer                         :: n, i
        avg_dist_to_cluster = 0.
        n = 0
        do i=1,n_obj
            if(i /= obj .and. cls(i) == cluster)then
                avg_dist_to_cluster = avg_dist_to_cluster + dist_table(obj,i)
                n = n+1
            endif   
        end do
        if( n /= 0 ) avg_dist_to_cluster = avg_dist_to_cluster/real(n)    
        return
    end function avg_dist_to_cluster
    
    function closest_obj(obj, dist_table, n_obj)
    ! returns the closest object to obj that isn't obj in the distance table (dist_table). n_obj = number of objects in the table (= size of the array in one dimension). closest_obj ignores distances that are less than 0. 
        integer, intent(in)             :: obj, n_obj
        real, intent(in)                :: dist_table(n_obj,n_obj)
        integer                         :: closest_obj, n
        real                            :: dist_table_temp(n_obj,n_obj)
        dist_table_temp = dist_table
        do n=1,n_obj
            dist_table_temp(n,n) = -1.
        end do
        closest_obj = 0
        closest_obj = minloc(dist_table_temp(obj,:),1,dist_table_temp(obj,:)>=0.)
        return
    end function closest_obj

end module simple_stat