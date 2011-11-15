#!<PERLPATH>

use warnings;
use strict;
use Getopt::Long;
use File::Copy;
use POSIX qw/ceil/;
use lib         '<SIMPLEPATH>/lib';  
use spider;
use eulers;
use cluster_exec;
use parse_aligninfo;

## command line options ##
my $mode1 = 0;
my $mode2 = 0;

GetOptions( 'apsh' => \$mode1, 'rtsq' => \$mode2 );

($mode1 == 0) && ($mode2 == 0) && (die "run options:
        --apsh  
        --rtsq\n");

## command line arguments ##
my ( @volumes, $box, $trs, $sym, $stack_ptcls, $nptcls, $mask, $dir, $tres, $lim_ptcls_in_class, @e_files, $innerRing, $outerRing, $nr_of_partitions,  $e1, $e2 );

if ($mode1 == 1) {
        ( @ARGV != 9 ) && die "\ngive to script:\n
1) volume/volumes separated with commas (ex. vol1.spi,vol2.spi NO SPACES)
2) box size ( box/2 cannot be an odd number )
3) shift in pixels (ex. if given 5, then [-5,5] will be searched) 
4) first ring (ex. 5 - the search for rotational alignment will be 
   restricted to pixels with radii in the specified range )
5) last ring (ex. 40, shift+last ring <= box/2-2 )
6) point-group symmetry (allowed: c1/c2/c3/c6/d2/d3/d7)
7) spider stack with single particles ( ex. /PATH/stack.spi )
8) number of ptcls in the above stack
9) number of partitions
NOTE: this mode has to be executed with 'nohup &' \n";

( $ARGV[0] =~ /,/ ) && ( @volumes = split(/,/,$ARGV[0]) );
( $ARGV[0] !~ /,/ ) && ( push @volumes, $ARGV[0] );
foreach ( @volumes ) {
        $_ = redirect_path_for_chdir( $_ );
}
$box                    = $ARGV[1];
$trs                    = $ARGV[2];
$innerRing              = $ARGV[3];
$outerRing              = $ARGV[4];
$sym                    = $ARGV[5];
$stack_ptcls            = redirect_path_for_chdir( $ARGV[6] );
$nptcls                 = $ARGV[7];
$nr_of_partitions       = $ARGV[8];
( $sym =~ /(\d+)/ )     && ( $e1 = 360./$1 );
( $sym =~ /c/ )         && ( $e2 = 180. );
( $sym =~ /d/ )         && ( $e2 = 90. );

} elsif ( $mode2 == 1 ) {
        ( @ARGV != 1 ) && die "\ngive to script:\n\n1) PROJMATCH directory\nNOTE: this mode has to be executed with 'nohup &'\n";
        $dir    = $ARGV[0];
} 

if ( $mode1 == 1 ) {
        ($sym !~ /[c1|c2|c3|c6|c7|d2|d3|d7]/) && die "Not a valid symmetry group\n";
        ($outerRing+$trs > $box/2-2 ) && die "shift+last ring must be <= box/2-2\n";
        $dir = "PROJMATCH_".join('_',split(/\s+/,localtime));
        mkdir( $dir );
        chdir( $dir );
        # generate even eulers
        my $even = spiral_eulers( 350, $e1, $e2, "spiral_eulers.dat" );
        # project volumes
        my $even_spi = get_spidoc( "spiral_eulers.dat" );
        my $m = 1;
        my $n = 350;
        print "projecting volumes ...\n"; 
        foreach my $i ( 1 .. @volumes ) {
                projmod( $box, $even_spi, $volumes[$i-1], "STACKprojs.spi", 'l', $m, $n );
                $m += 350;
                $n += 350;
        }
        # generate scripts
        unlink( 'even_all.dat' );
        my $even_all  = 'even_all.dat';  
        foreach my $i ( @volumes ) {
                system ( "cat $even >> $even_all" );
        }
        my $even_all_spi = get_spidoc( "$even_all" );
        for( my $i=1; $i<=$nr_of_partitions; $i++ ) {
                my $stopptcl = $i*(int($nptcls/$nr_of_partitions)+1);
                my $startptcl = $stopptcl-(int($nptcls/$nr_of_partitions));
                if($stopptcl > $nptcls ){
                        $stopptcl = $nptcls
                }
                apsh( "STACKprojs.spi", $even_all_spi, $stack_ptcls, $startptcl, $stopptcl, $trs, $innerRing, $outerRing, $i, 'c' );
        }
}
if ( $mode2 == 1 ) {
        chdir( $dir );
        doc_combine( "PARMFILE", "PARMFILE_ALL" );
        ( `cat PARMFILE_ALL | wc -l` != $nptcls+1 ) && ( die "Number of entries in PARMFILE_ALL does not equal nr of particles" );
        rtsq( "PARMFILE_ALL", $stack_ptcls, "STACKout_rtsh.spi", 'c' );
}


