#!/usr/bin/perl
$count;
while(<>){
    @row=split(/\s+/,$_);
    $scalar=scalar(@row);
    chomp @row;
    $count++;
    print "  $count\t$scalar\t";
    foreach $i (1 .. $scalar){
	print "$row[$i-1]\t";
    }
    print "\n";
}
