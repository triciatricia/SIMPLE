#!<PERLPATH>
if( @ARGV < 4 ) {
    die "Input to script: merged_doc FREE_CORR MODELQ HRES STATE\n";
}
open( IN, $ARGV[0] ) or die;
while(<IN>){
    if($_ =~ /AWK/){
        $counter++;
        if($_ =~ /FREE_CORR[:]*\s+([-]*\d+\.\d+)/){
                $free_corr = $1
        }
        if($_ =~ /MODELQ[:]*\s+([-]*\d+\.\d+)/){
                $modelq = $1
        }
        if($_ =~ /HRES[:]*\s+([-]*\d+\.\d+)/){
                $hres = $1
        }
        if( $free_corr >= $ARGV[1] ) {
            if( $modelq >= $ARGV[2] ){
                if( $hres <= $ARGV[3] ){
                    if( defined($ARGV[4]) ){
                        if($_ =~ /STATE[:]*\s+(\d)/){
                                    $state = $1
                        }
                        if( $state == $ARGV[4] ){
                            print $counter, "\n";
                        }
                    }else{
                           print $counter, "\n";
                    }
                }
            }
        }
    }
}