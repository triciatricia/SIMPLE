module simple_bpca
use simple_params
use simple_jiffys
use simple_rnd
use simple_math
use simple_fplane
use simple_def_precision
implicit none
save


public :: make_bpca, bpca_master

real, allocatable :: W(:,:), W_1(:,:), W_2(:,:), W_3(:,:), Wt(:,:), M(:,:), Minv(:,:), MinvWt(:,:)
real, allocatable :: X(:,:,:), AVG(:), tmp1(:,:), tmp2(:,:), Imat(:,:), E_znzn(:,:,:)
real, allocatable, target :: E_zn(:,:,:)
integer :: N

contains

    subroutine make_bpca
        integer :: alloc_stat, hrecsz, file_stat, i
        real    :: rval
        logical :: overflow
        ! read variables from pca stack header
        inquire(iolength=hrecsz) rval
        open(unit=19, file=pcahed, status='old', iostat=file_stat,&
        access='direct', action='read', form='unformatted', recl=hrecsz)
        call fopen_err('In: init_bpca, module: simple_bpca.f90', file_stat)
        read(19,rec=1) rval
        N = int(rval)        ! number of vectors to compress
        read(19,rec=2) rval 
        ncomps = int(rval)   ! nr of vector components (D)
        read(19,rec=3) rval 
        pcasz = int(rval)    ! file-rec size                 
        close(19)
        ! allocate matrices
        allocate( W(ncomps,nvars), W_1(ncomps,nvars), W_2(nvars,nvars), W_3(nvars,nvars),&
        Wt(nvars,ncomps), M(nvars,nvars), Minv(nvars,nvars), MinvWt(nvars,ncomps),&
        AVG(ncomps), X(N,ncomps,1), Imat(nvars,nvars), E_zn(N,nvars,1), eps(N),&
        E_znzn(N,nvars,nvars), tmp1(1,ncomps), tmp2(ncomps,1), stat=alloc_stat )
        call alloc_err( 'In: make_bpca, module: simple_bpca', alloc_stat )
        ! make identity matrix
        Imat=0.; do i=1,nvars ; Imat(i,i)=1. ; end do
        ! read pca planes
        AVG = 0.
        do i=1,N
            call read_pcaplane(X(i,:,1), pcastk, i)
            AVG = AVG+X(i,:,1)
        end do
        AVG = AVG/real(N)
        ! subtract the average from all planes
        do i=1,N
            X(i,:,1) = X(i,:,1)-AVG
        end do
    end subroutine make_bpca
    
    subroutine kill_bpca
        deallocate( W_1, W_2, W_3, Wt, M, Minv, MinvWt, AVG, X, Imat, E_znzn, tmp1, tmp2 )
    end subroutine kill_bpca
    
    subroutine get_pca_feats( p )
        real, pointer :: p(:,:)
        p => E_zn(:,:,1)
    end subroutine get_pca_feats
    
    subroutine init_bpca
        real :: meanv(nvars)
        meanv = 0.
        ! initialize latent variables by zero mean gaussians with unit variance
        do i=1,N
            do j=1,nvars
                E_zn(i,:,1) = mnorm_smp(Imat, nvars, meanv)
            end do
        end do
        ! initialize weight matrix with uniform random nrs, normalize over j
        do i=1,ncomps
            do j=1,nvars
                W(i,j) = ran3()
            end do
            W(i,:) = W(i,:)/sum(W(i,:)) ! vector operation
        end do
        ! transpose W
        Wt = transpose(W)
        ! set W_2 to WtW
        W_2 = matmul(Wt,W)
        ! set variance to 1     
        epsilon = 1.
    end subroutine init_bpca
    
    function eval_bpca_lhood( ) result( p )
    ! evaluate the log likelihood
        integer :: i
        real    :: p
        real    :: cons1, const2, const3 
        const1 = (real(ncomps)/2.)*log(twopi*epsilon)
        const2 = 1./(2*epsilon)
        const3 = 1./epsilon
        p = 0.
        do i=1,N
            p = p+const1+0.5*tr(E_znzn(i,:,:),nvars)+const2*arg(X(i,:,1))**2.-&
            const3*matmul(matmul(transpose(E_zn(i,:,:)),Wt),X(i,:,:))+
            const2*tr(matmul(E_znzn(i,:,:),W_2),nvars)
        end do
        ! signshift
        p = -p
    end function eval_bpca_lhood
    
    subroutine bpca_e_step( err )    
        integer, intent(inout) :: err
        M = matmul(Wt,W)+epsilon*Imat
        call matinv(M, Minv, nvars, err)
        if( err == -1 ) return
        MinvWt = matmul(Minv,Wt)
        ! loop over data
        W_1 = 0.
        W_2 = 0.
        do i=1,N
            ! Expectation step (calculate expectations using the old W)
            E_zn(i,:,:) = matmul(MinvWt,X(i,:,:))
            E_znzn(i,:,:) = epsilon*Minv+matmul(E_zn(i,:,:),transpose(E_zn(i,:,:)))
            ! Prepare for update of W (M-step)
            W_1 = W_1+matmul(X(i,:,:),transpose(E_zn(i,:,:)))
            W_2 = W_2+E_znzn(i,:,:)
        end do
    end subroutine bpca_e_step
    
    subroutine bpca_m_step( err )
        integer, intent(inout) :: err
        ! prepare for W update
        call matinv(W_2, W_3, nvars, err)
        if( err == -1 ) return
        ! update W
        W = matmul(W_1,W_3)
        ! update Wt
        Wt = transpose(W)
        ! set W_2 to WtW
        W_2 = matmul(Wt,W)
        ! determine the noise variance
        do i=1,N           
            epsilon = epsilon+(arg(X(i,:,1))**2.-2.*dot_product(tmp1(1,:),X(i,:,1))+tr(matmul(E_znzn(i,:,:),W_2),nvars))/real(nvars)
        end do
        epsilon = epsilon/real(N)
    end subroutine bpca_m_step
    
    subroutine bpca_master( err )
        integer, intent(inout) :: err
        integer :: k
        ! do the Expectation-Maximiztion
        write(*,'(A)') '>>> BAYESIAN PCA'
        call init_bpca
        do k=1,maxits
            P = eval_bpca_lhood( )
            if( k == 1 .or. mod(k,5) == 0 ) write(*,"(1XA,1XI2,1XA,1XF7.4)") 'Iteration:', k, 'Log-likelihood:', p
            call bpca_e_step(err)
            if( err == -1 ) return
            call bpca_m_step(err)
            if( err == -1 ) return
        end do
    end subroutine bpca_master
    
end module simple_bpca