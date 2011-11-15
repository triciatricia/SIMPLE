#!<PERLPATH>
use strict;
use warnings;
use lib '<SIMPLEPATH>/lib';
use spider;

( @ARGV != 8 ) && ( die "Give to script:
1) dendrdoc threshold
2) dendrdoc ( ex. /path/dendrdoc001.spi )
3) min nr of ptcls in class
4) stack with rotated particles ( ex. /path/STACK.spi )
5) name of output directory for classdocs
6) name of classdocs file body
7) output stack with class averages ( ex. /path/STACKout.spi )
8) local execution or cluster ( l or c )\n" );

make_cavgs_lowlim( $ARGV[0], $ARGV[1], $ARGV[2], $ARGV[3], $ARGV[4], $ARGV[5], $ARGV[6], $ARGV[7] );

