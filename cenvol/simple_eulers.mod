	  e  �   k820309              12.1        �N                                                                                                           
       ../simple_eulers.f90 SIMPLE_EULERS       	       EULER_TRIPLET PI CALC_NORMAL CALC_MATRIX CALC_DIST FIND_3NN SPIRAL_EULERS_LOCAL FIND_CLOSEST_EULER_1 FIND_CLOSEST_EULER_2                                                    
                        �                                 
                        �                                 
                            @                             
                        �                                 
                                                              u #FIND_CLOSEST_EULER_1    #FIND_CLOSEST_EULER_2    %         @    @X                                                      #FIND_CLOSEST_EULER_1%MINLOC    #NUM    #E1 
   #E2                                                    MINLOC          
  @                                    P              #EULERS 	             
@ @                               
     	                
@ @                                    	      %         @    @X                                                      #FIND_CLOSEST_EULER_2%MINLOC    #NUM    #E1    #E2    #EFROM    #ETO                                                    MINLOC           
  @                                    P              #EULERS 	             
@ @                                    	                
@ @                                    	                
                                                       
                                                                                                   u #SET_EULER_1    #SET_EULER_2    #SET_EULER_3                                                          u #GET_EULER_1    #GET_EULER_2    #GET_EULER_3                                                           u #CLASSIFY_EULERS_1    #CLASSIFY_EULERS_2                   �  @               �                '�                    #SCORES    #INDICES    #SLLS    #N B   #SORTED C   #EXISTS D              � D                                                            	            &                                                      � D                                          H                             &                                                      �                                           �                    #SLL_LIST              &                                                          �  @               �                '                    #LIST_SIZE     #HEAD !               � D                                                                        _�                                                    0                 �                              !     @                    #SLL_NODE "                 @  @               �           "     '@                   #CONTENT #   #NEXT A               �                               #     8                     #LIST_OBJECT $                  �  @               �           $     '8                   #IVAL %   #RVAL (   #DVAL +   #IARR .   #RARR 2   #DARR 6   #PT_TO_IVAL :   #PT_TO_RVAL ;   #PT_TO_DVAL <   #PT_TO_IARR =   #PT_TO_RARR >   #PT_TO_DARR ?   #EXISTS @                �                               %                           #I_SCALAR &                  �  @                          &     '                    #I '               � D                              '                                                                                                 0                 �                               (                          #R_SCALAR )                  �  @                          )     '                    #R *               � D                              *               	                                                 	                                 0.                 �                               +                          #D_SCALAR ,                  �  @                          ,     '                    #R -               � D                             -               
                                                 
                                 0.                 �                               .     P                     #I_ARRAY /                  �  @               A           /     'P                    #N 0   #IARR 1              � D                             0                                                                                                 0               � D                             1                                         &                                                        �                               2     P       `              #R_ARRAY 3                  �  @               @           3     'P                    #N 4   #RARR 5               � D                             4                              � D                             5                             	            &                                                        �                               6     P       �              #D_ARRAY 7                  �  @               @           7     'P                    #N 8   #DARR 9               � D                             8                              � D                            9                             
            &                                                       �                             :                         #I_SCALAR &                                          y#I_SCALAR &                                                              �                             ;                        #R_SCALAR )                                          y#R_SCALAR )                                                              �                             <                  	      #D_SCALAR ,                                          y#D_SCALAR ,                                                              �                             =     P             
      #I_ARRAY /                                          y#I_ARRAY /                                                              �                             >     P                    #R_ARRAY 3                                          y#R_ARRAY 3                                                              �                             ?     P       (            #D_ARRAY 7                                          y#D_ARRAY 7                                                              � D                              @     0                                                                                     �                     �                             A     @      8            #SLL_NODE "                                          y#SLL_NODE "                                                              � D                              B     �                                                                                           0                � D                              C     �                                                                                      �                      � D                              D     �                                                                                      �                        @  @               �           E     '@                   #CONTENT F   #NEXT G               �                               F     8                     #LIST_OBJECT $              �                             G     @      8            #SLL_NODE E                                          y#SLL_NODE E                                                  #         @                                 H                   #MESSAGE I   #ALLOC_STAT J             
                                 I                    1           
                                  J           %         @                                K                   	       #MYACOS%MIN L   #MYACOS%ABS M   #MYACOS%SIGN N   #MYACOS%ACOS O   #ARG P                                               L     MIN                                             M     ABS                                             N     SIGN                                             O     ACOS           
                                  P     	      %         @                                Q                    	       #RAD R             
                                  R     	      #         @                                 S                  #PGROUP_TO_LIM%REAL T   #PGROUP U   #P1 V   #P2 W   #T1 X   #T2 Y   #CSYM Z                                               T     REAL           
                                 U                    1                                            V     	                                                  W     	                                                  X     	                                                  Y     	                                                  Z            %         @                                 [                          #EVEN%REAL \   #EVEN%NINT ]   #EVEN%MOD ^   #VAL _                                               \     REAL                                             ]     NINT                                             ^     MOD           
                                  _     	      &         @                                `     �                      #N a   #HEAPSORT              
                                  a           #         @                                 b                   #NUM c   #I d   #SCORE e   #IVAL f   #RVAL g   #IARR h   #RARR i                                              c     �               #HEAPSORT              
                                  d                     
                                  e     	                
                                 f                     
                                 g     	                
                                 h                                 &                                                     
                                 i                   	              &                                           #         @                                 j                   #NUM k                                              k     �               #HEAPSORT    #         @                                 l                   #NUM m   #SCORE n   #IVAL o   #RVAL p   #IARR q   #RARR r                                              m     �               #HEAPSORT                                               n     	                                                  o                                                       p     	                                                  q                                  &                                                                                      r                   	 	              &                                           #         @                                 s                   #NUM t                                              t     �               #HEAPSORT    (         `                                u     	              A               	    #EULER2M%MATMUL v   #E1 w   #E2 x   #E3 y   p          p          p            p          p                                                                      v     MATMUL           
                                  w     	                
                                  x     	                
                                  y     	      #         @                                 z                  #M2EULER%SQRT {   #M2EULER%MATMUL |   #MAT }   #CEUL1 ~   #CEUL2    #CEUL3 �                                               {     SQRT                                             |     MATMUL           
                                  }     	              	 F   p          p          p            p          p                                                                     ~     	                                                       	                                                  �     	       (         `                                �                   C               	    #EULER2VEC%MATMUL �   #PHI �   #THETA �   #PSI �   p          p            p                                                                      �     MATMUL           
                                  �     	                
                                  �     	                
                                  �     	      #         @                                 �                   #NUM �   #WHICH �   #SCORE �   #IVAL �   #RVAL �   #IARR �   #RARR �                                              �     �               #HEAPSORT              
                                  �                                                      �     	                                                  �                                                       �     	                                                  �                    
              &                                                                                      �                   	               &                                           %         @                                 �                   	       #ARG%SQRT �   #ARG%SUM �   #VEC �                                               �     SQRT                                             �     SUM           
                                  �                   	 *             &                                           #         @                                  �                  #WRITE_SPIDOC_1%SIZE �   #FNAME �   #ARR �                                               �     SIZE           
                                 �                    1           
                                 �                   	              &                                           #         @                                 �                  #WRITE_SPIDOC_2%REAL �   #WRITE_SPIDOC_2%SIZE �   #FNAME �   #ARR �                                               �     REAL                                             �     SIZE           
                                 �                    1           
                                 �                                 &                                           #         @                                  �                  #WRITE_SPIDOC_3%SIZE �   #FNAME �   #ARR �                                               �     SIZE           
                                 �                    1           
                                 �                                 &                   &                                                          �  @               A           	     'P                    #EULERS �   #N_EULERS �   #EXISTS �              �                               �                    \             #EULER_TRIPLET �             &                                                          @  @                          �     '\                    #EUL1 �   #EUL2 �   #EUL3 �   #DIST_NN1 �   #DIST_NN2 �   #DIST_NN3 �   #DIST_AVG �   #NORMAL �   #RTOT �   #NN1 �   #NN2 �   #NN3 �   #CLASS �               �                               �               	                                                	                                 0.                �                               �              	                                                	                                 0.                �                               �              	                                                	                                 0.                �                               �              	                                                	                                 0.                �                               �              	                                                	                                 0.                �                               �              	                                                	                                 0.                �                               �              	                                                	                                 0.                �                               �                            	  p          p            p                                                                           	                                 0.            �                               �     	       (              	  	  p          p          p            p          p                                         	             	                     	                                 0.            �                               �     L       
                                                                                    0                �                               �     P                                                                                           0                �                               �     T                                                                                           0                 �                               �     X                        � D                              �     H                                                                                           0                � D                              �     L                                                                                      �          #         @      X                                              #NUM �   #I �   #EUL1 �   #EUL2 �   #EUL3 �             
D @                               �     P               #EULERS 	             
  @                               �                     
                                  �     	                
                                  �     	                
                                  �     	      #         @      X                                               #NUM �   #I �   #EUL1 �   #EUL2 �             
D @                               �     P               #EULERS 	             
  @                               �                     
                                  �     	                
                                  �     	      #         @      X                                               #NUM �   #I �   #EUL3 �             
D @                               �     P               #EULERS 	             
  @                               �                     
                                  �     	      #         @      X                                              #NUM �   #I �   #EUL1 �   #EUL2 �   #EUL3 �             
                                  �     P              #EULERS 	             
                                  �                     D                                 �     	                 D                                 �     	                 D                                 �     	       #         @      X                                               #NUM �   #I �   #EUL1 �   #EUL2 �             
                                  �     P              #EULERS 	             
                                  �                     D                                 �     	                 D                                 �     	       #         @      X                                               #NUM �   #I �   #EUL3 �             
                                  �     P              #EULERS 	             
                                  �                     D                                 �     	       #         @      X                                              #CLASSIFY_EULERS_1%MINLOC �   #NUM �   #EVEN �   #FNAME �                                              �     MINLOC          
  @                               �     P              #EULERS 	            
  @                               �     P              #EULERS 	             
@ @                              �                    1 #         @      X                                              #CLASSIFY_EULERS_2%MINLOC �   #NUM �   #NCLS �   #PGROUP �   #CLS_ARR �                                              �     MINLOC          
  @                               �     P              #EULERS 	             
  @                               �                     
  @                              �                    1          D                                 �                         p          5 8 � p        r#EULERS 	    �   U  	   �       5 8 � p        r#EULERS 	    �   U  	   �                     &         @                                �     P                      #NUMPART �   #EULERS 	             
                                  �           #         @                                 �                   #NUM �             
D                                 �     P               #EULERS 	   #         @                                  �                   #NUM �   #I �   #OUT_NORMAL �                                              �     P               #EULERS 	             
                                  �                     D                                 �                   	 	    p          p            p                          #         @                                  �                   #NUM �   #I �   #RTOT �             
                                  �     P              #EULERS 	             
                                  �                     D                                 �     	              	 
    p          p          p            p          p                          %         @                                �                           #NUM �             
                                  �     P              #EULERS 	   #         @                                  �                   #NUM �   #I �             
                                  �     P              #EULERS 	             
                                  �           #         @                                  �                   #NUM �             
D                                 �     P               #EULERS 	   #         @                                 �                  #SPIRAL_EULERS%PRESENT �   #NUM �   #PGROUP �                                              �     PRESENT           
D @                               �     P               #EULERS 	             
 @                              �                    1 #         @                                  �                   #NUM �   #FNAME �             
                                  �     P              #EULERS 	             
                                 �                    1 #         @                                  �                  #ANGULAR_TRES%REAL �   #NUM �   #AVGDIST �   #MAXDIST �                                              �     REAL           D @                               �     P               #EULERS 	             D                                 �     	                 D @                               �     	       #         @                                  �                  #COMPEULER%MATMUL �   #PHI �   #THETA �   #PSI �   #I �   #NUM �                                              �     MATMUL           
  @                               �     	                
  @                               �     	                
  @                               �     	                
                                  �                     D @                               �     P               #EULERS 	      �   +      fn#fn #   �   �   b   uapp(SIMPLE_EULERS     U  @   J   SIMPLE_HEAPSORT    �  @   J   SIMPLE_MATH %   �  @   J   SIMPLE_DEF_PRECISION      @   J   SIMPLE_SPIDOC    U  @   J   SIMPLE_JIFFYS '   �  t       gen@FIND_CLOSEST_EULER %   	  �      FIND_CLOSEST_EULER_1 ,   �  ?      FIND_CLOSEST_EULER_1%MINLOC )   �  T   a   FIND_CLOSEST_EULER_1%NUM (   &  @   a   FIND_CLOSEST_EULER_1%E1 (   f  @   a   FIND_CLOSEST_EULER_1%E2 %   �  �      FIND_CLOSEST_EULER_2 ,   D  ?      FIND_CLOSEST_EULER_2%MINLOC )   �  T   a   FIND_CLOSEST_EULER_2%NUM (   �  @   a   FIND_CLOSEST_EULER_2%E1 (     @   a   FIND_CLOSEST_EULER_2%E2 +   W  @   a   FIND_CLOSEST_EULER_2%EFROM )   �  @   a   FIND_CLOSEST_EULER_2%ETO    �  s       gen@SET_EULER    J  s       gen@GET_EULER $   �  n       gen@CLASSIFY_EULERS )   +  �       HEAPSORT+SIMPLE_HEAPSORT 0   �  �   %   HEAPSORT%SCORES+SIMPLE_HEAPSORT 1   Q	  �   %   HEAPSORT%INDICES+SIMPLE_HEAPSORT .   �	  �   a   HEAPSORT%SLLS+SIMPLE_HEAPSORT )   �
  i       SLL_LIST+SIMPLE_SLL_LIST =   �
  �   %   SLL_LIST%LIST_SIZE+SIMPLE_SLL_LIST=LIST_SIZE .   �  ^   a   SLL_LIST%HEAD+SIMPLE_SLL_LIST )   �  g      SLL_NODE+SIMPLE_SLL_LIST 1   Z  a   a   SLL_NODE%CONTENT+SIMPLE_SLL_LIST /   �  �       LIST_OBJECT+SIMPLE_LIST_OBJECT 4   �  ^   a   LIST_OBJECT%IVAL+SIMPLE_LIST_OBJECT )     W       I_SCALAR+SIMPLE_I_SCALAR +   h  �   %   I_SCALAR%I+SIMPLE_I_SCALAR 4     ^   a   LIST_OBJECT%RVAL+SIMPLE_LIST_OBJECT )   k  W       R_SCALAR+SIMPLE_R_SCALAR +   �  �   %   R_SCALAR%R+SIMPLE_R_SCALAR 4   h  ^   a   LIST_OBJECT%DVAL+SIMPLE_LIST_OBJECT )   �  W       D_SCALAR+SIMPLE_D_SCALAR +     �   %   D_SCALAR%R+SIMPLE_D_SCALAR 4   �  ]   a   LIST_OBJECT%IARR+SIMPLE_LIST_OBJECT '      a       I_ARRAY+SIMPLE_I_ARRAY +   �  �   %   I_ARRAY%N+SIMPLE_I_ARRAY=N 1   &  �   %   I_ARRAY%IARR+SIMPLE_I_ARRAY=IARR 4   �  ]   a   LIST_OBJECT%RARR+SIMPLE_LIST_OBJECT '     a       R_ARRAY+SIMPLE_R_ARRAY +   x  H   %   R_ARRAY%N+SIMPLE_R_ARRAY=N 1   �  �   %   R_ARRAY%RARR+SIMPLE_R_ARRAY=RARR 4   T  ]   a   LIST_OBJECT%DARR+SIMPLE_LIST_OBJECT '   �  a       D_ARRAY+SIMPLE_D_ARRAY +     H   %   D_ARRAY%N+SIMPLE_D_ARRAY=N 1   Z  �   %   D_ARRAY%DARR+SIMPLE_D_ARRAY=DARR :   �  �   a   LIST_OBJECT%PT_TO_IVAL+SIMPLE_LIST_OBJECT :   �  �   a   LIST_OBJECT%PT_TO_RVAL+SIMPLE_LIST_OBJECT :   �  �   a   LIST_OBJECT%PT_TO_DVAL+SIMPLE_LIST_OBJECT :   R  �   a   LIST_OBJECT%PT_TO_IARR+SIMPLE_LIST_OBJECT :     �   a   LIST_OBJECT%PT_TO_RARR+SIMPLE_LIST_OBJECT :   �  �   a   LIST_OBJECT%PT_TO_DARR+SIMPLE_LIST_OBJECT 6   �  �   %   LIST_OBJECT%EXISTS+SIMPLE_LIST_OBJECT .   T  �   a   SLL_NODE%NEXT+SIMPLE_SLL_LIST +      �   %   HEAPSORT%N+SIMPLE_HEAPSORT 0   �  �   %   HEAPSORT%SORTED+SIMPLE_HEAPSORT 0   i  �   %   HEAPSORT%EXISTS+SIMPLE_HEAPSORT )     g      SLL_NODE+SIMPLE_SLL_LIST 1   t  a   a   SLL_NODE%CONTENT+SIMPLE_SLL_LIST .   �  �   a   SLL_NODE%NEXT+SIMPLE_SLL_LIST (   �   e       ALLOC_ERR+SIMPLE_JIFFYS 0   !  L   a   ALLOC_ERR%MESSAGE+SIMPLE_JIFFYS 3   R!  @   a   ALLOC_ERR%ALLOC_STAT+SIMPLE_JIFFYS #   �!  �       MYACOS+SIMPLE_MATH '   -"  <      MYACOS%MIN+SIMPLE_MATH '   i"  <      MYACOS%ABS+SIMPLE_MATH (   �"  =      MYACOS%SIGN+SIMPLE_MATH (   �"  =      MYACOS%ACOS+SIMPLE_MATH '   #  @   a   MYACOS%ARG+SIMPLE_MATH $   _#  Y       RAD2DEG+SIMPLE_MATH (   �#  @   a   RAD2DEG%RAD+SIMPLE_MATH *   �#  �       PGROUP_TO_LIM+SIMPLE_MATH /   �$  =      PGROUP_TO_LIM%REAL+SIMPLE_MATH 1   �$  L   a   PGROUP_TO_LIM%PGROUP+SIMPLE_MATH -   %  @   a   PGROUP_TO_LIM%P1+SIMPLE_MATH -   W%  @   a   PGROUP_TO_LIM%P2+SIMPLE_MATH -   �%  @   a   PGROUP_TO_LIM%T1+SIMPLE_MATH -   �%  @   a   PGROUP_TO_LIM%T2+SIMPLE_MATH /   &  @   a   PGROUP_TO_LIM%CSYM+SIMPLE_MATH !   W&  �       EVEN+SIMPLE_MATH &   �&  =      EVEN%REAL+SIMPLE_MATH &   '  =      EVEN%NINT+SIMPLE_MATH %   V'  <      EVEN%MOD+SIMPLE_MATH %   �'  @   a   EVEN%VAL+SIMPLE_MATH -   �'  e       NEW_HEAPSORT+SIMPLE_HEAPSORT /   7(  @   a   NEW_HEAPSORT%N+SIMPLE_HEAPSORT -   w(  �       SET_HEAPSORT+SIMPLE_HEAPSORT 1   )  V   a   SET_HEAPSORT%NUM+SIMPLE_HEAPSORT /   X)  @   a   SET_HEAPSORT%I+SIMPLE_HEAPSORT 3   �)  @   a   SET_HEAPSORT%SCORE+SIMPLE_HEAPSORT 2   �)  @   a   SET_HEAPSORT%IVAL+SIMPLE_HEAPSORT 2   *  @   a   SET_HEAPSORT%RVAL+SIMPLE_HEAPSORT 2   X*  �   a   SET_HEAPSORT%IARR+SIMPLE_HEAPSORT 2   �*  �   a   SET_HEAPSORT%RARR+SIMPLE_HEAPSORT .   p+  Q       SORT_HEAPSORT+SIMPLE_HEAPSORT 2   �+  V   a   SORT_HEAPSORT%NUM+SIMPLE_HEAPSORT 1   ,  �       GET_HEAPSORT_MAX+SIMPLE_HEAPSORT 5   �,  V   a   GET_HEAPSORT_MAX%NUM+SIMPLE_HEAPSORT 7   �,  @   a   GET_HEAPSORT_MAX%SCORE+SIMPLE_HEAPSORT 6   1-  @   a   GET_HEAPSORT_MAX%IVAL+SIMPLE_HEAPSORT 6   q-  @   a   GET_HEAPSORT_MAX%RVAL+SIMPLE_HEAPSORT 6   �-  �   a   GET_HEAPSORT_MAX%IARR+SIMPLE_HEAPSORT 6   =.  �   a   GET_HEAPSORT_MAX%RARR+SIMPLE_HEAPSORT .   �.  Q       KILL_HEAPSORT+SIMPLE_HEAPSORT 2   /  V   a   KILL_HEAPSORT%NUM+SIMPLE_HEAPSORT $   p/  �       EULER2M+SIMPLE_MATH +   `0  ?      EULER2M%MATMUL+SIMPLE_MATH '   �0  @   a   EULER2M%E1+SIMPLE_MATH '   �0  @   a   EULER2M%E2+SIMPLE_MATH '   1  @   a   EULER2M%E3+SIMPLE_MATH $   _1  �       M2EULER+SIMPLE_MATH )   �1  =      M2EULER%SQRT+SIMPLE_MATH +   42  ?      M2EULER%MATMUL+SIMPLE_MATH (   s2  �   a   M2EULER%MAT+SIMPLE_MATH *   '3  @   a   M2EULER%CEUL1+SIMPLE_MATH *   g3  @   a   M2EULER%CEUL2+SIMPLE_MATH *   �3  @   a   M2EULER%CEUL3+SIMPLE_MATH &   �3  �       EULER2VEC+SIMPLE_MATH -   �4  ?      EULER2VEC%MATMUL+SIMPLE_MATH *   �4  @   a   EULER2VEC%PHI+SIMPLE_MATH ,   =5  @   a   EULER2VEC%THETA+SIMPLE_MATH *   }5  @   a   EULER2VEC%PSI+SIMPLE_MATH -   �5  �       GET_HEAPSORT+SIMPLE_HEAPSORT 1   L6  V   a   GET_HEAPSORT%NUM+SIMPLE_HEAPSORT 3   �6  @   a   GET_HEAPSORT%WHICH+SIMPLE_HEAPSORT 3   �6  @   a   GET_HEAPSORT%SCORE+SIMPLE_HEAPSORT 2   "7  @   a   GET_HEAPSORT%IVAL+SIMPLE_HEAPSORT 2   b7  @   a   GET_HEAPSORT%RVAL+SIMPLE_HEAPSORT 2   �7  �   a   GET_HEAPSORT%IARR+SIMPLE_HEAPSORT 2   .8  �   a   GET_HEAPSORT%RARR+SIMPLE_HEAPSORT     �8  t       ARG+SIMPLE_MATH %   .9  =      ARG%SQRT+SIMPLE_MATH $   k9  <      ARG%SUM+SIMPLE_MATH $   �9  �   a   ARG%VEC+SIMPLE_MATH -   3:  u       WRITE_SPIDOC_1+SIMPLE_SPIDOC 2   �:  =      WRITE_SPIDOC_1%SIZE+SIMPLE_SPIDOC 3   �:  L   a   WRITE_SPIDOC_1%FNAME+SIMPLE_SPIDOC 1   1;  �   a   WRITE_SPIDOC_1%ARR+SIMPLE_SPIDOC -   �;  �       WRITE_SPIDOC_2+SIMPLE_SPIDOC 2   K<  =      WRITE_SPIDOC_2%REAL+SIMPLE_SPIDOC 2   �<  =      WRITE_SPIDOC_2%SIZE+SIMPLE_SPIDOC 3   �<  L   a   WRITE_SPIDOC_2%FNAME+SIMPLE_SPIDOC 1   =  �   a   WRITE_SPIDOC_2%ARR+SIMPLE_SPIDOC -   �=  u       WRITE_SPIDOC_3+SIMPLE_SPIDOC 2   >  =      WRITE_SPIDOC_3%SIZE+SIMPLE_SPIDOC 3   O>  L   a   WRITE_SPIDOC_3%FNAME+SIMPLE_SPIDOC 1   �>  �   a   WRITE_SPIDOC_3%ARR+SIMPLE_SPIDOC    ??  v       EULERS    �?  �   a   EULERS%EULERS    \@  �      EULER_TRIPLET #   >A  �   a   EULER_TRIPLET%EUL1 #   �A  �   a   EULER_TRIPLET%EUL2 #   �B  �   a   EULER_TRIPLET%EUL3 '   0C  �   a   EULER_TRIPLET%DIST_NN1 '   �C  �   a   EULER_TRIPLET%DIST_NN2 '   |D  �   a   EULER_TRIPLET%DIST_NN3 '   "E  �   a   EULER_TRIPLET%DIST_AVG %   �E  �   a   EULER_TRIPLET%NORMAL #   �F    a   EULER_TRIPLET%RTOT "   �G  �   a   EULER_TRIPLET%NN1 "   �H  �   a   EULER_TRIPLET%NN2 "   &I  �   a   EULER_TRIPLET%NN3 $   �I  H   a   EULER_TRIPLET%CLASS     J  �   !   EULERS%N_EULERS    �J  �   !   EULERS%EXISTS    \K  v       SET_EULER_1     �K  T   a   SET_EULER_1%NUM    &L  @   a   SET_EULER_1%I !   fL  @   a   SET_EULER_1%EUL1 !   �L  @   a   SET_EULER_1%EUL2 !   �L  @   a   SET_EULER_1%EUL3    &M  l       SET_EULER_2     �M  T   a   SET_EULER_2%NUM    �M  @   a   SET_EULER_2%I !   &N  @   a   SET_EULER_2%EUL1 !   fN  @   a   SET_EULER_2%EUL2    �N  b       SET_EULER_3     O  T   a   SET_EULER_3%NUM    \O  @   a   SET_EULER_3%I !   �O  @   a   SET_EULER_3%EUL3    �O  v       GET_EULER_1     RP  T   a   GET_EULER_1%NUM    �P  @   a   GET_EULER_1%I !   �P  @   a   GET_EULER_1%EUL1 !   &Q  @   a   GET_EULER_1%EUL2 !   fQ  @   a   GET_EULER_1%EUL3    �Q  l       GET_EULER_2     R  T   a   GET_EULER_2%NUM    fR  @   a   GET_EULER_2%I !   �R  @   a   GET_EULER_2%EUL1 !   �R  @   a   GET_EULER_2%EUL2    &S  b       GET_EULER_3     �S  T   a   GET_EULER_3%NUM    �S  @   a   GET_EULER_3%I !   T  @   a   GET_EULER_3%EUL3 "   \T  �       CLASSIFY_EULERS_1 )   �T  ?      CLASSIFY_EULERS_1%MINLOC &   U  T   a   CLASSIFY_EULERS_1%NUM '   sU  T   a   CLASSIFY_EULERS_1%EVEN (   �U  L   a   CLASSIFY_EULERS_1%FNAME "   V  �       CLASSIFY_EULERS_2 )   �V  ?      CLASSIFY_EULERS_2%MINLOC &   �V  T   a   CLASSIFY_EULERS_2%NUM '   8W  @   a   CLASSIFY_EULERS_2%NCLS )   xW  L   a   CLASSIFY_EULERS_2%PGROUP *   �W  �   a   CLASSIFY_EULERS_2%CLS_ARR    �X  i       NEW_EULERS #   Y  @   a   NEW_EULERS%NUMPART    ]Y  Q       KILL_EULERS     �Y  T   a   KILL_EULERS%NUM !   Z  h       GET_EULER_NORMAL %   jZ  T   a   GET_EULER_NORMAL%NUM #   �Z  @   a   GET_EULER_NORMAL%I ,   �Z  �   a   GET_EULER_NORMAL%OUT_NORMAL    �[  b       GET_EULER_MAT "   �[  T   a   GET_EULER_MAT%NUM     H\  @   a   GET_EULER_MAT%I #   �\  �   a   GET_EULER_MAT%RTOT    <]  Y       GET_N_EULERS !   �]  T   a   GET_N_EULERS%NUM    �]  X       PRINT_EULER     A^  T   a   PRINT_EULER%NUM    �^  @   a   PRINT_EULER%I '   �^  Q       CLASSIFY_SPIRAL_EULERS +   &_  T   a   CLASSIFY_SPIRAL_EULERS%NUM    z_  x       SPIRAL_EULERS &   �_  @      SPIRAL_EULERS%PRESENT "   2`  T   a   SPIRAL_EULERS%NUM %   �`  L   a   SPIRAL_EULERS%PGROUP    �`  \       EULERS2SPIDOC "   .a  T   a   EULERS2SPIDOC%NUM $   �a  L   a   EULERS2SPIDOC%FNAME    �a  �       ANGULAR_TRES "   Pb  =      ANGULAR_TRES%REAL !   �b  T   a   ANGULAR_TRES%NUM %   �b  @   a   ANGULAR_TRES%AVGDIST %   !c  @   a   ANGULAR_TRES%MAXDIST    ac  �       COMPEULER !   �c  ?      COMPEULER%MATMUL    +d  @   a   COMPEULER%PHI     kd  @   a   COMPEULER%THETA    �d  @   a   COMPEULER%PSI    �d  @   a   COMPEULER%I    +e  T   a   COMPEULER%NUM 