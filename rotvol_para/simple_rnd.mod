	  o  4   k820309              12.1        ��N                                                                                                           
       ../simple_rnd.f90 SIMPLE_RND              IDUM R8PO_FA #         @                                                     #SEED_RND%CEILING    #SEED_RND%REAL                                                                                                          CEILING                                                 REAL %         @                                                    	       #RAN3%MOD    #RAN3%IABS    #RAN3%REAL                                                    MOD                                                 IABS                                                 REAL %         @                                                     	       #P 	             
                                  	     	      %         @                                
                    	       #MEAN    #STDEV    #LIMITS              
  @                                    	                
  @                                    	                
                                                     	    p          p            p                          %         @                                                    	       #MEAN    #STDEV              
                                       	                
                                       	      %         @                                                    	       #GASDEV3%LOG    #GASDEV3%SQRT                                                    LOG                                                 SQRT %         @                                                          #IRND_UNI%MAX    #IRND_UNI%CEILING    #IRND_UNI%REAL    #NP                                                    MAX                                                 CEILING                                                 REAL           
  @                                          %         @                                                            #NP    #NO              
  @                                                    
                                             %         @                                                            #LLIM    #HLIM              
                                                       
  @                                          #         @                                                     #NP     #IRND !   #JRND "             
  @                                                     D                                 !                      D                                 "            %         @                                 #                          #IRND_GASDEV%NINT $   #IRND_GASDEV%MAX %   #IRND_GASDEV%REAL &   #MEAN '   #STDEV (   #NP )                                              $     NINT                                            %     MAX                                            &     REAL           
  @                               '     	                
  @                               (     	                
  @                               )           #         @                                  *                  #RAN_IARR%SIZE +   #IARR ,   #NP -                                              +     SIZE           D@                               ,                                  &                                                     
  @                               -           (        `                                 .                    
               	    #MNORM_SMP%MATMUL /   #COV 0   #M 1   #MEANS 2   p          5 O p            5 O p                                                                     /     MATMUL          
                                  0                    	      p        5 � p        r 1   p          5 � p        r 1     5 � p        r 1       5 � p        r 1     5 � p        r 1                               
  @                               1                    
                                  2                    	    p          5 � p        r 1       5 � p        r 1                        �   %      fn#fn     �      b   uapp(SIMPLE_RND    �   �       SEED_RND !   �  @      SEED_RND%CEILING    �  =      SEED_RND%REAL      |       RAN3    �  <      RAN3%MOD    �  =      RAN3%IABS    �  =      RAN3%REAL    8  W       BRAN    �  @   a   BRAN%P    �  q       GASDEV_LIM     @  @   a   GASDEV_LIM%MEAN !   �  @   a   GASDEV_LIM%STDEV "   �  �   a   GASDEV_LIM%LIMITS    T  e       GASDEV    �  @   a   GASDEV%MEAN    �  @   a   GASDEV%STDEV    9  s       GASDEV3    �  <      GASDEV3%LOG    �  =      GASDEV3%SQRT    %  �       IRND_UNI    �  <      IRND_UNI%MAX !   �  @      IRND_UNI%CEILING    4  =      IRND_UNI%REAL    q  @   a   IRND_UNI%NP    �  `       IRND_UNI_NOT     	  @   a   IRND_UNI_NOT%NP     Q	  @   a   IRND_UNI_NOT%NO    �	  d       IRND_UNI_LIM "   �	  @   a   IRND_UNI_LIM%LLIM "   5
  @   a   IRND_UNI_LIM%HLIM    u
  d       IRND_UNI_PAIR !   �
  @   a   IRND_UNI_PAIR%NP #     @   a   IRND_UNI_PAIR%IRND #   Y  @   a   IRND_UNI_PAIR%JRND    �  �       IRND_GASDEV !   G  =      IRND_GASDEV%NINT     �  <      IRND_GASDEV%MAX !   �  =      IRND_GASDEV%REAL !   �  @   a   IRND_GASDEV%MEAN "   =  @   a   IRND_GASDEV%STDEV    }  @   a   IRND_GASDEV%NP    �  m       RAN_IARR    *  =      RAN_IARR%SIZE    g  �   a   RAN_IARR%IARR    �  @   a   RAN_IARR%NP    3  �       MNORM_SMP !     ?      MNORM_SMP%MATMUL    W  $  a   MNORM_SMP%COV    {  @   a   MNORM_SMP%M     �  �   a   MNORM_SMP%MEANS 