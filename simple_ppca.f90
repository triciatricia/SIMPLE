module simple_ppca
use simple_params
use simple_jiffys
use simple_rnd
use simple_math
use simple_fplane
use simple_def_precision
implicit none
save

public :: make_ppca, ppca_master

real, allocatable :: W(:,:), W_1(:,:), W_2(:,:), W_3(:,:), Wt(:,:), M(:,:), Minv(:,:), MinvWt(:,:)
real, allocatable :: AVG(:), tmp1(:,:), tmp2(:,:), Imat(:,:), E_znzn(:,:,:), alphas(:), A(:,:)
real, allocatable, target :: X(:,:,:)
real, allocatable, target :: E_zn(:,:,:)
integer :: N, pca_mode

contains

    subroutine make_ppca( N_in, pca_mode_in )
    ! pca_mode_in=0 iterative PCA, pca_mode=1 Bayesian pca
        integer, intent(in) :: N_in, pca_mode_in
        integer :: alloc_stat, i
        pca_mode = pca_mode_in
        N = N_in
        ! allocate matrices
        allocate( W(ncomps,nvars), W_1(ncomps,nvars), W_2(nvars,nvars), W_3(nvars,nvars),&
        Wt(nvars,ncomps), M(nvars,nvars), Minv(nvars,nvars), MinvWt(nvars,ncomps),&
        AVG(ncomps), X(N,ncomps,1), Imat(nvars,nvars), E_zn(N,nvars,1), alphas(nvars),&
        E_znzn(N,nvars,nvars), tmp1(1,ncomps), tmp2(ncomps,1), A(nvars,nvars), stat=alloc_stat )
        call alloc_err( 'In: make_ppca, module: simple_ppca', alloc_stat )
        ! make identity matrix
        Imat=0.; do i=1,nvars ; Imat(i,i)=1. ; end do
    end subroutine make_ppca
    
    subroutine get_ppca_vec_ptr( i, ptr )
    ! read pcaplane amplitudes
        integer, intent(in) :: i
        real, pointer       :: ptr(:)
        ptr => X(i,:,1)
    end subroutine get_ppca_vec_ptr

    subroutine kill_ppca
        deallocate(  W, W_1, W_2, W_3, Wt, M, Minv, MinvWt, X, AVG, tmp1, tmp2, Imat, E_znzn, E_zn )
    end subroutine kill_ppca
    
    subroutine get_pca_feats( feats )
        real, intent(out) :: feats(N,nvars)
        feats = E_zn(:,:,1)
    end subroutine get_pca_feats
    
    subroutine init_ppca
        real :: meanv(nvars), tmp2mat(1,1)
        integer :: i, j
        write(*,'(A)') '>>> SUBTRACTING THE GLOBAL AVERAGE FROM THE DATA VECTORS'
        AVG = 0.
        do i=1,N
            AVG = AVG+X(i,:,1)
        end do
        AVG = AVG/real(N)
        do i=1,N
            X(i,:,1) = X(i,:,1)-AVG
        end do
        write(*,'(A)') '>>> INITIALIZING LATENT VARIABLES'
        meanv = 0.
        ! initialize latent variables by zero mean gaussians with unit variance
        do i=1,N
            E_zn(i,:,1) = mnorm_smp(Imat, nvars, meanv)
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
        ! set variance to 0.     
        epsilon = 0.
        ! set alphas
        do i=1,nvars
            tmp2(:,1) = W(:,i)
            tmp2mat = matmul(transpose(tmp2),tmp2)
            alphas(i) = real(ncomps)/tmp2mat(1,1)
        end do
    end subroutine init_ppca
    
    function eval_square_err( ) result( p )
    ! evaluate the square error
        integer :: i
        real    :: p
        p = 0.
        do i=1,N
            tmp2 = matmul(W,E_zn(i,:,:))
            p = p+sqrt(sum((X(i,:,1)-tmp2(:,1))**2.))
        end do
    end function eval_square_err
    
    subroutine ppca_e_step( err )    
        integer, intent(inout) :: err
        integer :: i
        M = matmul(Wt,W)+epsilon*Imat
        call matinv(M, Minv, nvars, err)
        if( err == -1 ) return
        MinvWt = matmul(Minv,Wt)
        ! loop over data
        W_1 = 0.
        W_2 = 0.
        ! make A
        A = epsilon*diag(alphas, nvars)
        do i=1,N
            ! Expectation step (calculate expectations using the old W)
            E_zn(i,:,:) = matmul(MinvWt,X(i,:,:))
            E_znzn(i,:,:) = epsilon*Minv+matmul(E_zn(i,:,:),transpose(E_zn(i,:,:)))
            ! Prepare for update of W (M-step)
            W_1 = W_1+matmul(X(i,:,:),transpose(E_zn(i,:,:)))
            W_2 = W_2+E_znzn(i,:,:)+A
        end do
    end subroutine ppca_e_step
    
    subroutine ppca_m_step( err )
        integer, intent(inout) :: err
        integer :: i
        real    :: tmp1mat(1,1), tmp2mat(1,1)
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
        if( pca_mode == 0 )then
            epsilon=0.
        else
            epsilon=0.
            do i=1,N
                tmp1    = matmul(transpose(E_zn(i,:,:)),Wt)
                tmp1mat = matmul(tmp1(:,:),X(i,:,:))
                tmp2mat = matmul(transpose(X(i,:,:)),X(i,:,:))
                epsilon = epsilon+tmp2mat(1,1)-2.*tmp1mat(1,1)+tr(matmul(E_znzn(i,:,:),W_2),nvars)
            end do
            epsilon = epsilon/real(N*nvars)
        endif
    end subroutine ppca_m_step
    
    subroutine ppca_master( err, maxpcaits )
        integer, intent(inout) :: err
        integer, intent(in)    :: maxpcaits
        integer :: k
        real :: p, p_prev
        call init_ppca
        if( pca_mode /= 0 )then
            write(*,'(A)') '>>> BAYESIAN PCA'
        else
            write(*,'(A)') '>>> ITERATIVE PCA'
        endif
        ! do the Expectation-Maximization
        p = 0.
        do k=1,maxpcaits
            p_prev = p
            p = eval_square_err()
            if( abs(p-p_prev) < 0.1 ) exit
            if( k == 1 .or. mod(k,5) == 0 ) write(*,"(1XA,1XI2,1XA,1XF10.0)") 'Iteration:', k, 'Square error:', p
            call ppca_e_step(err)
            if( err == -1 ) return
            call ppca_m_step(err)
            if( err == -1 ) return
        end do
    end subroutine ppca_master
    
end module simple_ppca