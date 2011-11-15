      PROGRAM CLUS
C-----------------------------------------------------------------------
C  This is a simple program well suited for cluster analysis of
C  variables.  The clustering method used is average-linkage
C  hierarchical cluster analysis.  There are few options, but that
C  provides the advantage of easy use.  All commands are supplied to
C  the program interactively, in response to prompting questions.
C
C     INPUT:   A correlation matrix (or some other similarity or
C              dissimilarity matrix) in a file named MATRIX.DAT
C              This must contain all the elements of a full
C              (n x n), symmetrical matrix.  Any format is
C              allowable, but each number must include a decimal
C              point.
C
C     OUTPUT:  Output consists of a cluster history and a tree
C              diagram (dendogram).
C
C     Two utility files are created by the program:  SORTED.DAT
C     and CLUM.DAT.  These can be deleted after running the program.
C     If they are present from a previous run they will be re-written
C     and so will not affect the results of a current run.
C-----------------------------------------------------------------------
C  Programming Notes:
C
C  1.  This comes from a pre FORTRAN-77 program--please excuse
C      lack of modern command structure.
C
C  2.  The original version was also written as several separate
C      programs--which, for example, explains why files are used
C      to communicate data between subroutines.
C
C  3.  The program will run as-is with RM FORTRAN on personal
C      computers.  It should be compatible with MS, Lahey, or
C      or other PC FORTRANs with little or no changes.
C
C  Author:    John Uebersax
C  Written:   1978
c
C  Revised:    Change(s):
C  ---------   ---------------------------------------------------------
c  10 mar 93   Uploaded to StatLib
c  10 jun 06   1 - changed output file to output.txt
c              2 - accept DIS or dis as command
c              3 - re-compliled with AbSoft Pro Fortran 7.0
C-----------------------------------------------------------------------
C
C  Driver program
C
      CALL CLUSV1
      CALL PRETRE
      CALL TREE
      END


      SUBROUTINE CLUSV1
C
C THIS ROUTINE DOES THE CLUSTER ANALYSIS, TAKING DATA FROM FILE
C <MATRIX.DAT>.  PARAMETERS CONTROLLING THE ANLAYSIS ARE OBTAINED
C INTERACTIVELY.  THE RESULTS ARE STORED IN FILE <OUTPUT.TXT>, AND     
C ALSO IN <CLUM>, WHICH IS USED AS AN INPUT FILE FOR THE ROUTINE
C PRETRE.                        
C
      COMMON/D/X(100,100),NIN(100),NVAR(100),K,L,M,RX
      CHARACTER FMT(20)
      DIMENSION TITLE(20)
      DATA HDIS /3HDIS/
C
      OPEN (UNIT=2, FILE='CLUM.DAT')
      OPEN (UNIT=3, FILE='MATRIX.DAT')
      OPEN (UNIT=7, FILE='OUTPUT.txt')
C
C READ CLUSTERING PARAMETERS
C
      WRITE (*,4000)
 4000 FORMAT(1X,'Interactive cluster analysis')
      WRITE (*,4001) 
 4001 FORMAT(/,1X,'What is the problem title? ')
      READ (*,4002) TITLE
 4002 FORMAT(20A4)
      WRITE (7,6000) TITLE
 6000 FORMAT(20A4)
      WRITE (2,2000) TITLE
 2000 FORMAT(20A4)
      WRITE (*,4003)
 4003 FORMAT(1X,'How many things are to be clustered? ')
      READ (*,*) M
      WRITE (2,2001) M
 2001 FORMAT(I3)
      LIMIT=M-1
      WRITE (*,4006)
 4006 FORMAT(1X,'SIM or DIS data? ')
      READ (*,4007) CRIT
 4007 FORMAT(A3)
      WRITE (2,2002) CRIT
 2002 FORMAT(A3)
C
C INITIALIZE X, NIN, AND NVAR
C
      DO 140 I=1,M
      READ (3,*) (X(I,J),J=1,M)
 140  CONTINUE

      DO 150 I=1,M
      NVAR(I)=I
      NIN(I)=1
  150 CONTINUE
C
C CLUSTER ANALYSIS
C
      ITR=0
  300 ITR=ITR+1
C
C DETERMINE GROUPS TO BE MERGED THIS ITERATION
C

c      IF (CRIT .EQ. HDIS) GO TO 311

      if (crit .eq. hdis .or. crit .eq. 'dis') goto 311

      CALL SCAN
      GO TO 312
 311  CALL BSCAN
 312  CONTINUE
C
C UPDATE INTER-GROUP SIMILARITY/DISSIMILARITY MATRIX TAKIN INTO
C ACCOUNT THE MERGER OCCURRING HIS ITERATION
C
      CALL ARRANGE
C
C OUTPUT
C
      IF (CRIT .EQ. HDIS) GO TO 400
      WRITE (7,6001) NVAR(K),NVAR(L),NIN(K),ITR,RX
      GO TO 410
 400  WRITE (7,6002) NVAR(K), NVAR(L),NIN(K),ITR,RX
 410  CONTINUE
 6001 FORMAT(/, 1X, 'GROUP ', I3, ' IS JOINED BY GROUP ', I3,
     1'.   N IS ', I3, '   ITER = ', I3, '   SIM = ',
     2F10.3)
 6002 FORMAT(/, 1X, 'GROUP ', I3, ' IS JOINED BY GROUP ', I3,
     1'.   N IS ', I3, '   ITER = ', I3, '   DIS = ',
     2F10.3)
      WRITE (2,2003) NVAR(K),NVAR(L),RX
 2003 FORMAT(2I3,1X,F8.3)
      IF (L .EQ. M) GO TO 600
      MN=M-1
      DO 500 I=L,MN
      NVAR(I)=NVAR(I+1)
  500 CONTINUE
  600 M=M-1
      IF (ITR .LT. LIMIT) GO TO 300
 999  CONTINUE
      WRITE (*,4008)
 4008 FORMAT(3X,'OUTPUT STORED ON FILE <OUTPUT.TXT>.')
      CLOSE (2)
      CLOSE (3)
      RETURN
      END

      SUBROUTINE SCAN
      COMMON/D/X(100,100),NIN(100),NVAR(100),K,L,M,RX
      N=1
      RX=-10000.
      MN=M-1
      DO 20 I=1,MN
      N=N+1
      DO 10 J=N,M
      IF (RX-X(I,J)) 5,5,10
   5  K=I
      L=J
      RX=X(I,J)
  10  CONTINUE
  20  CONTINUE
      RETURN
      END

      SUBROUTINE ARRANGE
      COMMON/D/X(100,100),NIN(100),NVAR(100),K,L,M,RX
      MN=M-1
      SAV=X(K,L)
      SAV2=X(K,K)
      DO 10 I=1,M 
      X(I,K)=(X(I,K)*NIN(K)+X(I,L)*NIN(L))/(NIN(K)+NIN(L))
      X(K,I)=X(I,K)
  10  CONTINUE
      X(K,K)=SAV2*NIN(K)*(NIN(K)-1)+X(L,L)*NIN(L)*(NIN(L)-1)
      X(K,K)=X(K,K)+SAV*2*NIN(K)*NIN(L)
      X(K,K)=X(K,K)/((NIN(K)+NIN(L))*(NIN(K)+NIN(L)-1))
      IF (L .EQ. M) GO TO 60
      DO 20 I=1,M
      DO 15 J=L,MN
      X(I,J)=X(I,J+1)
  15  CONTINUE
  20  CONTINUE
      DO 30 I=L,MN
      DO 25 J=1,M
      X(I,J)=X(I+1,J)
  25  CONTINUE
  30  CONTINUE
      NIN(K)=NIN(K)+NIN(L)
      DO 50 I=L,MN
      NIN(I)=NIN(I+1)
  50  CONTINUE
      RETURN
  60  NIN(K)=NIN(K)+NIN(L)
      RETURN
      END

      SUBROUTINE BSCAN
      COMMON/D/X(100,100),NIN(100),NVAR(100),K,L,M,RX
      N=1 
      RRRMIN=1000000.
      MN=M-1
      DO 20 I=1,MN
      N=N+1
      DO 10 J=N,M
      IF (RRRMIN-X(I,J)) 10,5,5
  5   K=I
      L=J
      RRRMIN=X(I,J)
  10  CONTINUE
  20  CONTINUE
      RX=RRRMIN
      RETURN
      END


      SUBROUTINE PRETRE
C
C  THIS PROGRAM DETERMINES THE ORDER IN WHICH OBJECTS APPEAR ON
C  THE DENDOGRAPH
C
      DIMENSION KLUS(2,100),NIN(100),LIST(100),JHOLD(100)
      DIMENSION TITLE(20)
      OPEN (UNIT=2, FILE='SORTED.DAT')
      OPEN (UNIT=3, FILE='CLUM.DAT')
      READ (3,3000) TITLE
 3000 FORMAT (20A4)
      WRITE (2,3000) TITLE
      READ (3,3001) NN
 3001 FORMAT(I3)
      N=NN-1
      WRITE (2,3001) NN
      READ (3,3002) CRIT
 3002 FORMAT(A3)
      WRITE (2,3002) CRIT
      READ (3,3003) ((KLUS(I,J),I=1,2),J=1,N)
 3003 FORMAT(2I3)
      WRITE (2,3003) ((KLUS(I,J),I=1,2),J=1,N)
      DO 10 I=1,NN
      LIST(I)=I
      nin(i)=1
  10  CONTINUE
      DO 100 II=1,N
C NAME TABS
      I=KLUS(1,II)
      J=KLUS(2,II)
      NI=NIN(I)
      NJ=NIN(J)
      L=1
  15  IF (LIST(L) .EQ. I) GO TO 20
      L=L+1
      IF (L .LE. NN) GO TO 15
  20  ICOL=L
      IN=ICOL+NI
      INEND=IN+NJ-1
      L=L+1
  30  IF (LIST(L) .EQ. J) GO TO 40
      L=L+1
      IF (L .LE. NN) GO TO 30
  40  JCOL=L
      JPRE=JCOL-1
      JEND=JCOL+NJ-1
      NHOLD=1
C REMOVE J VECTOR AND STORE IN HOLD
      DO 50 M=JCOL,JEND
      JHOLD(NHOLD)=LIST(M)
      NHOLD=NHOLD+1
  50  CONTINUE
C SHIFT
      MSH=JEND
  55  IF (MSH .EQ. INEND) GO TO 60
      KSH=MSH-NJ
      LIST(MSH)=LIST(KSH)
      MSH=MSH-1
      GO TO 55
  60  CONTINUE
C INSERT HOLD VECTOR
      NHOLD=1 
      DO 70 M=IN,INEND
      LIST(M)=JHOLD(NHOLD)
      NHOLD=NHOLD+1
  70  CONTINUE
      NIN(I)=NI+NJ
  100 CONTINUE
      WRITE (2,2000) (LIST(M),M=1,NN)
 2000 FORMAT(4(20I3,/),20I3)
C     WRITE (*,4210)
C4210 format(3x,'OUTPUT STORED ON FILE <SORTED>.')
      CLOSE (2)
      CLOSE (3)
      RETURN
      END


      SUBROUTINE TREE
C
C THIS PROGRAM PRINTS A DENDOGRAPH
C
      DIMENSION KLUS(2,100),LIST(100),KOL(100),ROW(144),TITLE(20)
      INTEGER LIST1(10),LIST2(100)
      DATA STAR,BLANK/1H*, 1H /
      OPEN (UNIT=3, FILE='SORTED.DAT')
      READ (3,3000) TITLE
 3000 FORMAT(20A4)
      WRITE (7,6000) TITLE
 6000 FORMAT('', //, 20A4)
      READ (3,3001) NN
 3001 FORMAT(I3)
      READ (3,3002) CRIT
 3002 FORMAT(A3)
      N=NN-1
      READ (3,3003) ((KLUS(I,J),I=1,2),J=1,N)
 3003 FORMAT(2I3)             
      READ (3,3004) (LIST(I),I=1,NN)
 3004 FORMAT(4(20I3,/),20I3)
      ISCL=1
         IF (NN .GE. 44 .AND. NN .LE. 65) ISCL=2
         IF (NN .GT. 32 .AND. NN .LT. 44) ISCL=3
         IF (NN .LE. 32) ISCL=4
      LIMIT=(ISCL*NN)+5
  75  DO 760 II=1,3
      I=4-II
      DO 751 JK=1,LIMIT
      ROW(JK)=BLANK
 751  CONTINUE
      M=0
      DO 750 J=1,NN
      L=LIST(J)
      CALL CONV(L,I,A)
      M=M+ISCL
      ROW(M)=A
 750  CONTINUE
      WRITE (7,6001) (ROW(KK),KK=1,LIMIT)
 6001 FORMAT(5X,130A1)
  760 CONTINUE
    8 ISPACE=5
      DO 10 I=1,NN
      ISPACE=ISPACE+ISCL
      LL=LIST(I)
      KOL(LL)=ISPACE
  10  CONTINUE
      DO 20 I=1,5
      ROW(I)=BLANK
  20  CONTINUE
      L=5
      JSCL=ISCL-1
      DO 30 I=1,NN
      IF (JSCL .EQ. 0) GO TO 26
      DO 25 J=1,JSCL
      L=L+1
      ROW(L)=BLANK
 25   CONTINUE
 26   CONTINUE
      L=L+1
      ROW(L)=STAR
 30   CONTINUE
      LIMIT=(ISCL*NN)+5
      DO 500 IT=1,N
      WRITE (7,6002) (ROW(M),M=1,LIMIT)
 6002 FORMAT(135A1)
  100 CONTINUE
      MERGEI=KLUS(1,IT)
      MERGEJ=KLUS(2,IT)
      II=KOL(MERGEI)
      JJ=KOL(MERGEJ)
      DO 110 L=II,JJ
      ROW(L)=STAR
  110 CONTINUE
      WRITE (7,6003) IT,(ROW(M),M=6,LIMIT)
 6003 FORMAT(1X,I3,1X,130A1)
      DO 120 L=II,JJ
      ROW(L)=BLANK
  120 CONTINUE
      RI=II
      RJ=JJ
      RKOL=(.5*(JJ-II)+II)
      KOL(MERGEI)=INT(RKOL)
      KI=KOL(MERGEI)
      ROW(KI)=STAR
  500 CONTINUE
      WRITE (*,4240)
 4240 FORMAT(3X,'DENDOGRAPH PRINTED TO FILE <OUTPUT.TXT>.', /, '')
      CLOSE (3)
      CLOSE (7)
      RETURN
      END

      SUBROUTINE CONV(N1,N2,ALPHA)
      DIMENSION DIGIT(11)
      DATA DIGIT/1H1, 1H2, 1H3, 1H4, 1H5, 1H6, 1H7, 1H8, 1H9, 1H0, 1H /
C N1=THREE DIGIT INTEGER
C N2=DECIMAL PLACE
      SWITCH=0.0
      R=N1/1000.0
      K=4-N2
      DO 100 I=1,K
      X=R*10.0
      J=INT(X)
      R=X-J+.0001
      IF (J .GT. 0) SWITCH=1.0
      IF (J .EQ. 0) J=10
      IF (J .EQ. 10 .AND. SWITCH .EQ. 0.0 .AND. I .NE. 3) J=11
      ALPHA=DIGIT(J)
  100 CONTINUE
      RETURN
      END
