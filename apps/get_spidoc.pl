#!<PERLPATH>

use warnings;
use strict;
use lib         '<SIMPLEPATH>/lib'; 
use spider;

( @ARGV != 1 ) && die "\nGive input file!\n\n";

get_spidoc( $ARGV[0] ); 