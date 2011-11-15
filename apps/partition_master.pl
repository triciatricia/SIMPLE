#!<PERLPATH>
use warnings;
use strict;
use Getopt::Long;
use lib '<SIMPLEPATH>/lib'; 
use cluster_exec;
use parse_aligninfo;
use eulers;
use spider;

## command line options ##
my $mode1 = 0;
my $mode2 = 0;


GetOptions( 'refine' => \$mode1, 'readme' => \$mode2 );

($mode1 == 0) && ($mode2 == 0) && (die "run options:
        --refine     
        --readme\n");

## command line arguments ##
my ( @volumes, $trs, $box, $smpd, $sym, $fstack, $nptcls, $boost, $aligndata, $lpass,
     $npartitions, $jobname, $nrefs, $nrefsects, $evobody, $freek);

if ($mode1 == 1) {
    ( @ARGV != 15 ) && die "\ngive to script:\n
1)  spider reference volume(s) (multiple volumes separated with commas 
    ex. vol1.spi,vol2.spi, NO SPACES, '.spi' extension )
2)  shift in pixels (ex. if given 5, then [-5,5] will be searched) 
3)  box size in pixels
4)  sampling distance in Angstroms
5)  point-group symmetry (c1/c2/c3/c7/c6/d2/d3/d7)
6)  stack with fourier transforms
    (ex. /PATH/fstack.fim, where '.fim' denotes a SIMPLE format )
7)  number of transforms in the above stack
8)  low-pass limit in Angstroms
    (note that this will now limit the spectral self-adaption)
9)  free correlation shell in Angstroms
10) previous round's aligndata file or 0
11) filebody of evol-align popstacks
12) use resolution boosting (y or n, note that boosting should be used first 
    after convergence has been achived without boosting)
13) nr of partitions
14) nr of reference central sections
15) jobname\n";

} elsif ( $mode2 == 1 ) {
 print "\nNote the following: Preparation of the .fim Fourier stack required for 
evol-align refinement is done by fixfstack.pl. Resolution boosting \
refers to evol-align with orientation keeping, meaning that exhaustive 
search is still perfomed first, but the newly established orientations
are compared with the old ones and they are enforced togive better 
phase consistency than the old orientations, otherwise they are rejected.
The box size of the volumes must be the same as the box size of the 
particle images used to generate the Fourier stack. The first round 
is perfomed with a fixed lowpass limit (~20 A), and used to establish 
orientations that are used to automatically estimate the lowpass limit.
The resulting alignment documents need to be merged using merge_algndocs.pl 
before reconstruction with rec_master.pl. Do not throw the merged alignment
document. It will be used to initiate the next round of refinement. 
Happy Processing!\n";
}

if ( $mode1 == 1 ) {
    ( $ARGV[0] =~ /,/ ) && ( @volumes = split(/,/,$ARGV[0]) );
    ( $ARGV[0] !~ /,/ ) && ( push @volumes, $ARGV[0] );
    foreach ( @volumes ) {
            (`ls $_` ne "$_\n") && die "Volume $_ does not exist at given location!\n";
            $_ = redirect_path_for_chdir( $_ );
    }
    $trs          = $ARGV[1];
    $box          = $ARGV[2];
    $smpd         = $ARGV[3];
    $sym          = $ARGV[4];
    $fstack       = $ARGV[5];
    $nptcls       = $ARGV[6];
    $lpass        = $ARGV[7];
    $freek        = $ARGV[8];
    $aligndata    = $ARGV[9];
    $evobody      = $ARGV[10];
    $boost        = $ARGV[11];    
    $npartitions  = $ARGV[12];
    $nrefsects    = $ARGV[13];
    $jobname      = $ARGV[14];
    
    (`ls $fstack` ne "$fstack\n") && die "Fourier stack $fstack does not exist at given location!\n";
    $fstack       = redirect_path_for_chdir( $fstack );
    ($sym !~ /[c1|c2|c3|c6|c7|d2|d3|d7]/) && die "Not a valid symmetry group\n";
    ( ($box/2)%2==1 ) && ( die "Fourier transform dimension cannot be an odd number, change box size so the box/2 is an even numebr !!!\n" );
    (-e $aligndata ) && ( `grep 'AWKSOME' $aligndata | wc -l` != $nptcls ) && ( die "Number of entries in $aligndata does not equal nr of particles" );
    ## global variables ##
    my ( $dir, $e1, $e2, $even, $even_spi, @filetab, $align_mode, $nstates );
    $nstates = scalar(@volumes);
    $dir = "EVOL_REFINE_".join('_',split(/\s+/,localtime));
    mkdir( $dir );
    system( "cp $evobody* ./$dir" );
    chdir( $dir );
    $nrefs = $nrefsects * @volumes;
    ( $sym =~ /(\d+)/ ) && ( $e1 = 360./$1 );
    ( $sym =~ /c/ )     && ( $e2 = 180. );
    ( $sym =~ /d/ )     && ( $e2 = 90. );
    # generate even eulers
    $even = spiral_eulers( $nrefsects, $e1, $e2, "even_$nrefsects.dat" );
    $even_spi = get_spidoc( "even_$nrefsects.dat" );
    # project volumes
    mkdir( "refs" );
    foreach my $i ( 1 .. @volumes ) {
            mkdir( "./refs/refs_$i" );
            ftsh_projmod( $box, $even_spi, $volumes[$i-1], "./refs/refs_$i/ftshproj", 'l' );
            my @refs = glob( "./refs/refs_$i/ftshproj*" );
            push( @filetab, @refs );
            system ( "cat $even >> aligndata.dat" );
    }
    push( @filetab, $fstack );
    arr_to_file( \@filetab, "filetable.dat" );
    $aligndata = redirect_path_for_chdir( $aligndata );
    if (-e $aligndata ) {
      system( "grep 'AWKSOME' $aligndata | awk '{print\$1,\$2,\$3,\$4,\$5,\$17}' >> aligndata.dat" );
    } 
    $align_mode = 20;
    if( -e $aligndata ){
        $align_mode = 21;
        ( $boost eq 'y' ) && ( $align_mode = 22 );
        ( $boost eq '3' ) && ( $align_mode = 25 );
    }
    generate_scripts( $align_mode, $nptcls, $nrefs, $nstates, 0, $sym, $box, $smpd, $lpass, $trs, './filetable.dat', './aligndata.dat', $npartitions, $jobname, "./", $freek, 0, 0 );
}
