!==Class simple_eulers
!
! simple_eulers handles lists of Euler angle triplets in Spider format. Functionality
! includes generation of evenly distributed angular orientations, angular orientation classification, 
! and composition of rotations. The code is distributed with the hope that it will be useful, but 
! _WITHOUT_ _ANY_ _WARRANTY_. Redistribution or modification is regulated by the GNU General Public 
! License. *Author:* Hans Elmlund, 2009-05-26
!
!==Changes are documented below
!
!* restructured, deugged, documented and incorporated in the _SIMPLE_ library, HE 2009-06-25
!
module simple_eulers
use simple_heapsort
use simple_math
use simple_def_precision
use simple_spidoc
use simple_jiffys
implicit none

private :: euler_triplet, pi, calc_normal, calc_matrix, calc_dist, find_3NN, spiral_eulers_local,&
find_closest_euler_1, find_closest_euler_2
public

type :: euler_triplet
! Type euler_triplet contains the three Euler angles, the three nearest neighbours to each triplet 
! in the object (if calculated) and their physical distances, the Fourier plane normal resulting from
! applying the Euler rotations to (0,0,1), and the composite rotation matrix
    real :: EUL1=0., EUL2=0., EUL3=0.
    real :: dist_NN1=0., dist_NN2=0., dist_NN3=0., dist_avg=0.
    real :: normal(3)=0., rtot(3,3)=0.
    integer :: NN1=0, NN2=0, NN3=0, class
end type euler_triplet

type :: eulers
! Type eulers is an array of _N_eulers_ Euler angle triplets, see euler_triplet below
    private
    type(euler_triplet), allocatable :: eulers(:)
    integer :: N_eulers=0
    logical :: exists=.false.
end type

interface find_closest_euler
    module procedure find_closest_euler_1
    module procedure find_closest_euler_2
end interface

interface set_euler
    module procedure set_euler_1
    module procedure set_euler_2
    module procedure set_euler_3
end interface

interface get_euler
    module procedure get_euler_1
    module procedure get_euler_2
    module procedure get_euler_3
end interface

interface classify_eulers
    module procedure classify_eulers_1
    module procedure classify_eulers_2
end interface

contains

    function new_eulers( numpart ) result( num )
    ! is a constructor
        integer, intent(in) :: numpart
        type(eulers)        :: num
        integer             :: alloc_stat
        allocate( num%eulers( numpart ), stat=alloc_stat )
        call alloc_err( 'In: new_eulers, module: simple_eulers.f90', alloc_stat )
        num%N_eulers = numpart
        num%exists   = .true.
    end function new_eulers
      
    function find_closest_euler_1( num, e1, e2 ) result( closest )
    ! is for finding the projection closest matching input _e1_,_e2_
        integer                  :: closest
        type(eulers), intent(in) :: num
        real, intent(in)         :: e1, e2
        type(eulers)             :: e_one
        real                     :: distances(num%N_eulers)
        integer                  :: loc(1), i
        closest = 0
        e_one = new_eulers(1)
        call set_euler( e_one, 1, e1, e2, 0. )
        do i=1,num%N_eulers
            distances(i) = calc_dist( num, e_one, i, 1 ) 
        end do
        loc = minloc(distances)
        closest = loc(1)
        call kill_eulers( e_one )
    end function find_closest_euler_1
    
    function find_closest_euler_2( num, e1, e2, efrom, eto ) result( closest )
    ! is for finding the projection closest matching input _e1_,_e2_
        integer                  :: closest
        type(eulers), intent(in) :: num
        real, intent(in)         :: e1, e2
        integer, intent(in)      :: efrom, eto
        type(eulers)             :: e_one
        real                     :: distances(eto-efrom+1)
        integer                  :: indices(eto-efrom+1)
        integer                  :: loc(1), i, cnt
        closest = 0
        e_one   = new_eulers(1)
        cnt     = 0
        call set_euler( e_one, 1, e1, e2, 0. )
        do i=efrom,eto
            cnt = cnt+1
            indices(cnt)   = i
            distances(cnt) = calc_dist( num, e_one, i, 1 ) 
        end do
        loc = minloc(distances)
        closest = indices(loc(1))    
        call kill_eulers( e_one )
    end function find_closest_euler_2

    function mirror_or_not( num, i ) result( mirror )
        type(eulers), intent(in) :: num
        integer, intent(in)      :: i
        real                     :: zvec(3), ang
        logical                  :: mirror
        zvec(1) = 0.
        zvec(2) = 0.
        zvec(3) = 1.
        ang = myacos(dot_product(num%eulers(i)%normal,zvec))
        if( ang < pi )then
            mirror = .false.
        else
            mirror = .true.
        endif
    end function mirror_or_not
    
    function find_closest_eulers( num, e1, e2, n ) result( closest )
    ! is for finding the projection closest matching input _e1_,_e2_
        integer, intent(in)      :: n
        type(eulers), intent(in) :: num
        real, intent(in)         :: e1, e2
        type(eulers)             :: e_one
        integer                  :: entries(num%N_eulers), closest(n), i
        real                     :: distances(num%N_eulers)
        closest = 0
        e_one = new_eulers(1)
        call set_euler( e_one, 1, e1, e2, 0. )
        do i=1,num%N_eulers
            distances(i) = calc_dist( num, e_one, i, 1 )
            entries(i)   = i
        end do
        call hpsort(num%N_eulers, distances, entries )
        do i=1,n
            closest(i) = entries(i)
        end do
        call kill_eulers( e_one )
    end function find_closest_eulers

    subroutine kill_eulers( num )
    ! is a destructor
        type(eulers), intent(inout) :: num
        if( num%exists )then
            num%N_eulers = 0     
            deallocate( num%eulers )
            num%exists = .false.
        endif
    end subroutine kill_eulers
    
    subroutine set_euler_1( num, i, eul1, eul2, eul3 )
    ! sets an Euler triplet in position _i_, calculates the normal and
    ! composes the rotation matrix
        type(eulers), intent(inout) :: num
        integer, intent(in)         :: i
        real, intent(in)            :: eul1, eul2, eul3
        num%eulers(i)%EUL1 = eul1
        num%eulers(i)%EUL2 = eul2
        num%eulers(i)%EUL3 = eul3
        call calc_normal(num,i)
        call calc_matrix(num,i)
    end subroutine set_euler_1
    
    subroutine set_euler_2( num, i, eul1, eul2 )
    ! sets a projection direction in position _i_, calculates the normal and
    ! composes the rotation matrix
        type(eulers), intent(inout) :: num
        integer, intent(in)         :: i
        real, intent(in)            :: eul1, eul2
        num%eulers(i)%EUL1 = eul1
        num%eulers(i)%EUL2 = eul2
        call calc_normal(num,i)
        call calc_matrix(num,i)
    end subroutine set_euler_2
    
    subroutine set_euler_3( num, i, eul3 )
    ! sets an in-pane angle in position _i_, calculates the normal and
    ! composes the rotation matrix
        type(eulers), intent(inout) :: num
        integer, intent(in)         :: i
        real, intent(in)            :: eul3
        num%eulers(i)%EUL3 = eul3
        call calc_normal(num,i)
        call calc_matrix(num,i)
    end subroutine set_euler_3
    
    subroutine get_euler_1( num, i, eul1, eul2, eul3 )
    ! is a getter
        type(eulers), intent(in) :: num
        integer, intent( in )    :: i
        real, intent( out )      :: eul1, eul2, eul3
        eul1 = num%eulers(i)%EUL1
        eul2 = num%eulers(i)%EUL2
        eul3 = num%eulers(i)%EUL3 
    end subroutine get_euler_1
    
    subroutine get_euler_2( num, i, eul1, eul2 )
    ! is a getter
        type(eulers), intent(in) :: num
        integer, intent( in )    :: i
        real, intent( out )      :: eul1, eul2
        eul1 = num%eulers(i)%EUL1
        eul2 = num%eulers(i)%EUL2
    end subroutine get_euler_2
    
    subroutine get_euler_3( num, i, eul3 )
    ! is a getter
        type(eulers), intent(in) :: num
        integer, intent( in )    :: i
        real, intent( out )      :: eul3
        eul3 = num%eulers(i)%EUL3
    end subroutine get_euler_3

    subroutine get_euler_normal( num, i, out_normal )
    ! is a getter
        type(eulers) :: num
        integer, intent(in) :: i
        real, intent(out) :: out_normal(3)
        out_normal = num%eulers( i )%normal
    end subroutine get_euler_normal

    subroutine get_euler_mat( num, i, rtot )
    ! is a getter
        type(eulers), intent(in) :: num
        integer, intent(in)      :: i
        real, intent(out)        :: rtot(3,3)
        rtot = num%eulers(i)%rtot
    end subroutine get_euler_mat
    
    pure function get_N_eulers( num ) result( N_eulers )     
    ! is a getter
        type( eulers ), intent(in) :: num
        integer                    :: N_eulers
        N_eulers = num%N_eulers
    end function get_N_eulers

    subroutine print_euler( num, i )
        type(eulers), intent(in) :: num
        integer, intent(in)      :: i
        write(*,*) num%eulers(i)%EUL1, num%eulers(i)%EUL2, num%eulers(i)%EUL3
    end subroutine print_euler

    subroutine spiral_eulers_local( num )
    ! is for generating evenly distributed projection directions
        type(eulers), intent(inout) :: num
        real                        :: h, theta, psi
        integer                     :: k
        do k=1,num%N_eulers
            h = -1.+((2.*(real(k)-1.))/(real(num%N_eulers)-1.))
            theta = myacos(h)
            if( k == 1 .or. k == num%N_eulers )then
                psi = 0.
            else
                psi = psi+3.6/(sqrt(real(num%N_eulers))*sqrt(1.-real(h)**2.))
            endif
            do while( psi > 2.*pi )
                psi = psi-2.*pi
            end do
            num%eulers(k)%EUL1 = rad2deg(psi)
            num%eulers(k)%EUL2 = rad2deg(theta)
            num%eulers(k)%EUL3 = 0.       
            call calc_normal( num, k )
            call calc_matrix( num, k )
        end do
    end subroutine spiral_eulers_local
    
    subroutine classify_spiral_eulers( num )
        type(eulers), intent(inout) :: num
        integer :: k, cnt
        cnt = 1
        num%eulers(1)%class = cnt
        do k=1,num%N_eulers-1
            if(k >= 2)then
                if(num%eulers(k)%EUL1-num%eulers(k-1)%EUL1 < 0) cnt = cnt+1
                num%eulers(k)%class = cnt
            endif
        end do
        num%eulers(num%N_eulers)%class = cnt
    end subroutine classify_spiral_eulers

    subroutine spiral_eulers( num, pgroup )
        type(eulers), intent(inout) :: num
        character(len=*), intent(in), optional :: pgroup
        type(eulers) :: e_temp
        integer :: mul, counter, csym, i, nes, countdown
        real :: p1, p2, t1, t2, e1, e2, e3
        if( present(pgroup) )then
            if( pgroup .eq. 'c1' )then
                call spiral_eulers_local( num )
            else
                call pgroup_to_lim(pgroup, p1, p2, t1, t2, csym)
                if( pgroup(1:1) .eq. 'c' )then     
                    mul = csym
                else
                    mul = 2*csym
                endif
                nes = mul*num%N_eulers
                e_temp = new_eulers(mul*num%N_eulers)
                call spiral_eulers_local(e_temp)
                call set_euler(num, 1, p2, 0., 0.)
                call set_euler(num, 2, 0., t2, 0.)
                counter = 2
                do i=1,mul*num%N_eulers
                    call get_euler(e_temp, i, e1, e2, e3)
                    if( e1 <= p2 .and. e2 <= t2 ) then
                        counter = counter+1
                        if( counter > num%N_eulers ) exit
                        call set_euler(num, counter, e1, e2, 0.)
                    endif
                end do
                ! correct for zero-eulers in the bottom               
                countdown = num%N_eulers
                e1 = 0.
                e2 = 0.
                do while( e1 == 0. .and. e2 == 0. )
                    call get_euler(num, countdown, e1, e2, e3 )
                    countdown = countdown-1
                end do
                do i=countdown,num%N_eulers-1
                    call get_euler(num, i, e1, e2, e3 )
                    call set_euler(num, i+1, e1/2., e2/2., 0. )
                end do
                ! deallocate
                call kill_eulers(e_temp)
            endif
        else 
            call spiral_eulers_local( num )
        endif
    end subroutine spiral_eulers
    
    subroutine classify_eulers_1( num, even, fname )
    ! classifies the Euler triplets in _num_ according to closeness
    ! to the ones in _even_ and returns the class assignments in _cls_arr_. The resulting
    ! array will contain 0 if the triplet did not fit in the class (if angular treshold is used).
        type(eulers), intent(in)     :: num, even
        character(len=*), intent(in) :: fname
        integer                      :: cls_arr(num%N_eulers)
        real                         :: dists(even%N_eulers)
        integer                      :: i, j, loc(1)
        do i=1,num%N_eulers
            ! calculate the distances and fill sort struct
            do j=1,even%N_eulers
                dists(j) = calc_dist( num, even, i, j )
            end do
            ! find class and store in output array
            loc = minloc(dists)
            cls_arr(i) = loc(1)       
        end do
        call write_spidoc( fname, cls_arr )
    end subroutine classify_eulers_1
    
    subroutine classify_eulers_2( num, ncls, pgroup, cls_arr )
    ! classifies the Euler triplets in _num_ according to closeness
    ! to the ones in _even_ and returns the class assignments in _cls_arr_. The resulting
    ! array will contain 0 if the triplet did not fit in the class (if angular treshold is used).
        type(eulers), intent(in)     :: num
        integer, intent(in)          :: ncls
        character(len=*), intent(in) :: pgroup
        integer, intent(out)         :: cls_arr(num%N_eulers)
        real                         :: dists(ncls)
        type(eulers)                 :: even
        integer                      :: i, j, loc(1)
        even = new_eulers(ncls)
        call spiral_eulers( even, pgroup )
        do i=1,num%N_eulers
            ! calculate the distances and fill sort struct
            do j=1,ncls
                dists(j) = calc_dist( num, even, i, j )
            end do
            ! find class and store in output array
            loc = minloc(dists)
            cls_arr(i) = loc(1)       
        end do
        call kill_eulers(even)
    end subroutine classify_eulers_2
    
    subroutine eulers2spidoc( num, fname )
        type(eulers), intent(in)     :: num
        character(len=*), intent(in) :: fname 
        integer                      :: i, file_stat
        open(unit=5, file=fname, status='REPLACE', action='WRITE', iostat=file_stat)
        if( file_stat /= 0 ) then
            write(*,*) 'ERROR, cannot write to file: ', fname
            write(*,*) 'In: eulers2spidoc, class: simple_spidoc.f90'
            stop
        else
            do i=1,num%N_eulers
                write(5,'(I7,1XI)',advance='no') i, '3'
                write(5,'(1XI7)',advance='no') num%eulers%EUL1
                write(5,'(1XI7)',advance='no') num%eulers%EUL2
                write(5,'(1XI7)') num%eulers%EUL3     
            end do                
            close(5)
        endif
    end subroutine eulers2spidoc

    subroutine angular_tres( num, avgdist, maxdist )
    ! returns the average and maximum distance between 
    ! the projection directions in _num_
        type(eulers)      :: num
        real, intent(out) :: avgdist, maxdist
        type(heapsort)    :: ind_dist
        integer           :: i
        real              :: radians
        ! calculate the distances
        call find_3NN( num )
        ! allocate the sort struct
        ind_dist = new_heapsort( num%N_eulers )
        radians = 0.
        do i=1,num%N_eulers
            call set_heapsort( ind_dist, i, num%eulers(i)%dist_avg )
            radians = radians+num%eulers(i)%dist_avg
        end do
        avgdist = rad2deg(radians/real(num%N_eulers))
        call sort_heapsort(ind_dist)
        call get_heapsort_max(ind_dist, maxdist)
        maxdist = rad2deg(maxdist)
        call kill_heapsort(ind_dist)
    end subroutine angular_tres
   
    subroutine compeuler( phi, theta, psi, i, num )
    ! rotates the triplets in _num_ 
        real, intent(in) :: phi, theta, psi
        integer, intent(in) :: i
        type( eulers ) :: num
        real, dimension( 3,3 ) :: r, s, c
        ! setup the matrices r and s
        r = euler2m( phi, theta, psi )
        s = euler2m( num%eulers( i )%EUL1,&
        num%eulers( i )%EUL2, num%eulers( i )%EUL3 ) 
        ! multiply s with r
        c = matmul( r,s ) ! order is assumingly not important
        ! the composed rotation matrix is constructed
        ! retrieve the euler angles      
        call m2euler( c, num%eulers(i)%EUL1, num%eulers(i)%EUL2, num%eulers(i)%EUL3 )
    end subroutine compeuler

    subroutine calc_normal( num, i )
        type(eulers), intent(inout) :: num
        integer, intent(in)         :: i                
        num%eulers(i)%normal = euler2vec( num%eulers(i)%EUL1,&
        num%eulers(i)%EUL2, num%eulers(i)%EUL3 )
    end subroutine calc_normal

    subroutine calc_matrix( num, i )
        type(eulers), intent(inout) :: num
        integer, intent(in)         :: i
        num%eulers(i)%rtot = euler2m( num%eulers(i)%EUL1,&
        num%eulers(i)%EUL2, num%eulers(i)%EUL3 )
    end subroutine calc_matrix

    function calc_dist( num1, num2, ind1, ind2 ) result( dist )
        real                     :: dist
        type(eulers), intent(in) :: num1, num2
        integer, intent(in)      :: ind1, ind2
        dist = myacos( dot_product(num1%eulers(ind1)%normal,num2%eulers(ind2)%normal) )
    end function calc_dist

    subroutine find_3NN( num )
    ! is for mapping the three nearest neighbours of all triplets in _num_
        type(eulers), intent(inout) :: num
        type(heapsort)              :: ind_dist
        real                        :: dist
        integer                     :: i, j
        do i=1,num%N_eulers
            ind_dist = new_heapsort( num%N_eulers )
            do j=1,num%N_eulers
                if( j == i ) then
                    call set_heapsort( ind_dist, j, 999., ival=j )
                else
                    dist = calc_dist( num, num, i, j )
                    call set_heapsort( ind_dist, j, dist, ival=j )
                endif
            end do
            call sort_heapsort( ind_dist )
            call get_heapsort( ind_dist, 1, num%eulers(i)%dist_NN1, ival=num%eulers(i)%NN1 )
            call get_heapsort( ind_dist, 2, num%eulers(i)%dist_NN2, ival=num%eulers(i)%NN2 )
            call get_heapsort( ind_dist, 3, num%eulers(i)%dist_NN3, ival=num%eulers(i)%NN3 )
            num%eulers(i)%dist_avg = ( num%eulers(i)%dist_NN1+num%eulers(i)%dist_NN2+&
            num%eulers(i)%dist_NN3 )/3.
            call kill_heapsort( ind_dist )
        end do
    end subroutine find_3NN
    
end module simple_eulers
