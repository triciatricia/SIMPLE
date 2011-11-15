#!<PERLPATH>
$counter;
$index;
$sum = 0;
$cnt = 0;
while(<>){
    if($_ =~ /AWK/){
        $counter++;
        if($_ =~ /FREE_CORR[:]*\s+([-]*\d+\.\d+)/){
            $sum = $sum+$1;
	    $cnt = $cnt+1;
        }
    }
}
print $sum/$cnt, "\n";
