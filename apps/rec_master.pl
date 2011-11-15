#!<PERLPATH>

use warnings;
use strict;
use lib '<SIMPLEPATH>/lib'; 
use iwannaparticle;

(@ARGV != 15) && die "give to script:
1) mode:
    1 - Back Projection, Interpolated in Fourier Space
    2 - Back Projection, Interpolated in Fourier Space with e/o test
    3 - Back Projection, Conjugate Gradients
    4 - Back Projection, Conjugate Gradients with e/o test    
2) aligndoc ( output from align, het or rad )
3) nr of states 
4) symmetry group ( c1, c2, c3, c6, c7, d2, d3, d7, oct ) 
5) sampling distance of files used for alignment
6) sampling distance of files used for reconstruction
7) mask radius in pixels ( doesn't matter if mode 1 or 2 )
8) free correlation limit
9) modelq limit
10) low-pass limit
11) spider stack with single images ( ex. /PATH/stack.spi )
12) number of images in the stack
13) reconstructed volume name
14) local execution or cluster ( l or c )
15) number of nodes per script\n";

my $mode            = $ARGV[0];
my $algndoc         = $ARGV[1];
my $nr_of_states    = $ARGV[2];
my $sym             = $ARGV[3];
my $smpd1           = $ARGV[4];
my $smpd2           = $ARGV[5];
my $mask            = $ARGV[6];
my $free_corr       = $ARGV[7];
my $modelq          = $ARGV[8];
my $hres            = $ARGV[9];
my $spistack        = $ARGV[10];
my $nr_of_ptcls     = $ARGV[11];
my $volume          = $ARGV[12];
my $exec            = $ARGV[13];
my $nnodes          = $ARGV[14];

(($smpd1 !~ /^(\d+)?(\.\d*)?([eE]-?\d+)?$/) || ($smpd2 !~ /^(\d+)?(\.\d*)?([eE]-?\d+)?$/)) && die "Not a valid scaling factor, check sampling distances\n";
my $scaling = $smpd1/$smpd2;

if ($mode == 1) {
    reconstruct_bp3f    ($volume, $algndoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $spistack, $nr_of_ptcls, $exec, $nnodes );
} elsif ($mode == 2) {
    reconstruct_bp32f   ($volume, $algndoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $spistack, $nr_of_ptcls, $exec, $nnodes );
} elsif ($mode == 3) {
    reconstruct_bpcg    ($volume, $algndoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $spistack, $nr_of_ptcls, $exec, $mask, $nnodes );    
} elsif ($mode == 4) {
    reconstruct_bpcg_eo ($volume, $algndoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $spistack, $nr_of_ptcls, $exec, $mask, $nnodes );
}
