module simple_acombs


type acombs
    integer :: K ! number of clusters
    integer :: M ! vector dimension
    integer :: L ! number of strata
    real, allocatable :: centers(:,:) ! dim (M,L)
end type


contains





end module simple_acombs