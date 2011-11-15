#!<PERLPATH>

use warnings;
use strict;
(@ARGV != 2) && die "Give to script:
1) aligndocs body and path (ex. ./EVOL_REFINE/aligndoc_ )
2) output merged document name ( ex. merged_1.dat )\n";

my $algndoc = $ARGV[0];
my $final_algndoc = $ARGV[1];
my @algndocs = glob("$algndoc*");
my $nr_of_algndocs = scalar(@algndocs);
foreach my $i (1 .. $nr_of_algndocs) {
    my $doc = $algndoc.$i;
    system("cat $doc >> $final_algndoc");
}
