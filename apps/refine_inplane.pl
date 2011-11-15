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
my $mode3 = 0;
my $mode4 = 0;


GetOptions( 'inplane' => \$mode1, 'hcl' => \$mode2, 'cavgs' => \$mode3, 'help' => \$mode4 );

($mode1 == 0) && ($mode2 == 0) && ($mode3 == 0) && ($mode4 == 0) && (die "run options:
        --inplane       - run rotational alignment using AP SH,
                          run PCA, optionally run HCL
        --hcl           - run HCL
        --cavgs         - make class averages
        --help\n");

## command line arguments ##
my ( @volumes, $box, $trs, $sym, $stack_ptcls, $nptcls, $mask, $dir, $tres, $lim_ptcls_in_class, @e_files, $innerRing, $outerRing, $nr_of_partitions, $hcl, $e1, $e2, $eigs, $eigens );

if ($mode1 == 1) {
        ( @ARGV != 11 ) && die "\ngive to script:\n
1) volume/volumes separated with commas (ex. vol1.spi,vol2.spi NO SPACES)
2) box size ( box/2 cannot be an odd number )
3) shift in pixels (ex. if given 5, then [-5,5] will be searched) 
4) first ring (ex. 5 - the search for rotational alignment will be 
   restricted to pixels with radii in the specified range )
5) last ring (ex. 40, first+last ring < box/2 )
6) point-group symmetry (allowed: c1/c2/c3/c6/d2/d3/d7)
7) spider stack with single particles ( ex. /PATH/stack.spi )
8) number of ptcls in the above stack
9) mask radius for PCA, should match the size of the particle 
10) nr of eigenvectors for PCA (20 should be enough, note also that 
    the eig:s used for clustering can be different)
11) classification on all eigenvectors ( y or n )
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
$mask                   = $ARGV[8];
$eigs                   = $ARGV[9];
$hcl                    = $ARGV[10];
$nr_of_partitions       = ceil( $nptcls/1000 );
( $sym =~ /(\d+)/ )     && ( $e1 = 360./$1 );
( $sym =~ /c/ )         && ( $e2 = 180. );
( $sym =~ /d/ )         && ( $e2 = 90. );

} elsif ( $mode2 == 1 ) {
        ( @ARGV != 2 ) && die "\ngive to script:\n\n1) REFINE_INPLANE directory\n2) eigenvectors for hcl ( ex. 1,3-15 )\nNOTE: this mode has to be executed with 'nohup &'\n";
        $dir    = $ARGV[0];
        $eigens = $ARGV[1];

} elsif ( $mode3 == 1 ) {
        ( @ARGV != 3 ) && die "\ngive to script:\n
1) REFINE_INPLANE directory
1) dendrdoc threshold
2) min nr of ptcls in class
NOTE: this mode has to be executed with 'nohup &'\n";

$dir                    = $ARGV[0];
$tres                   = $ARGV[1];
$lim_ptcls_in_class     = $ARGV[2];

}


if ( $mode1 == 1 ) {
        $dir = "REFINE_INPLANE_".join('_',split(/\s+/,localtime));
        print "\n     ***** REFINE INPLANE START *****\n\n";
        mkdir( $dir );
        chdir( $dir );
        # generate even eulers
        my $even = spiral_eulers( 2000, $e1, $e2, "spiral_eulers.dat" );
        # project volumes
        my $even_spi = get_spidoc( "spiral_eulers.dat" );
        my $m = 1;
        my $n = 2000;
        print "projecting volumes ...\n"; 
        foreach my $i ( 1 .. @volumes ) {
                projmod( $box, $even_spi, $volumes[$i-1], "STACKprojs.spi", 'l', $m, $n );
                $m += 2000;
                $n += 2000;
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
        print "submitting and running apsh jobs ...\n";
        sleep(10) until ( finished( "JOBS" ) eq 'true');
        job_failure_check( glob "errfile*" );
        unlink glob ( "JOBS errfile* outfile*" );
        doc_combine( "PARMFILE", "PARMFILE_ALL" );
        print "rotating and translating particles ...\n";
        rtsq( "PARMFILE_ALL", $stack_ptcls, "STACKout_rtsh.spi", 'c' );
        sleep(10) until ( finished( "JOBS" ) eq 'true' );
        job_failure_check( glob "errfile*" );
        unlink glob ( "JOBS errfile* outfile*" );
                                        ######### PCA #########
        mkdir ( "final_output" );
        system( "mv ./STACKout_rtsh.spi ./final_output" );
        mkdir ( "aligndocs" );
        system( "mv PARM* ./aligndocs" );
        unlink glob( "*" );
        chdir ( "./final_output" );
        pca( $box, $mask, $eigs, "STACKout_rtsh.spi", "1-$nptcls", "c" );
        print "submitting and running pca ...\n";
        sleep(10) until ( finished( "JOBS" ) eq 'true' );
        job_failure_check( glob "errfile*" );
        unlink glob ( "JOBS errfile* outfile*" );
        if ( $hcl eq 'y' ) {
           hcl( "1-$eigs", "c" );
           print "submitting and running hcl ...\n";
           sleep(10) until ( finished( "JOBS" ) eq 'true' );
           job_failure_check( glob "errfile*" );
           unlink glob ( "JOBS errfile* outfile*" );
        }
        chdir( "../../" );
        print "\n        ******** refine_inplane.pl -inplane NORMAL STOP ********\n"
}
                                        ######### HCL #########
if ( $mode2 == 1 ) {
        chdir( $dir."/final_output" );
        hcl( $eigens, "c" );
        print "submitting and running hcl ...\n";
        sleep(10) until ( finished( "JOBS" ) eq 'true' );
        job_failure_check( glob "errfile*" );
        unlink glob ( "JOBS errfile* outfile*" );
        chdir( "../../" );
        print "\n        ******** refine_inplane.pl -hcl NORMAL STOP ********\n"
}

if ( $mode3 == 1 ) {
        chdir( $dir."/final_output" );
#       make_cavgs_lowlim( $tres, "dendrdoc001.spi", 1, "STACKout_rtsh.spi", "docs", "classdoc", "STACKcavgs.spi", 'c' );
        print "running make_cavgs ...\n";
        make_cavgs_lowlim( $tres, "dendrdoc001.spi", $lim_ptcls_in_class, "STACKout_rtsh.spi", "docs_tres", "classdoc", "STACKcavgs_tres.spi", 'l' );
        
        chdir( "../../" );
        print "\n        ******** refine_inplane.pl -cavgs NORMAL STOP ********\n"
}

if ( $mode4 == 1 ) {
        print "\n\t\t>>>>>>>> mode - inplane <<<<<<<<\n 
First, refinement of in-plane parameters (translation and rotation) is done
given the input reconstruction(s) and a spider stack of single-particles. 
Next, the aligned image stack is reconstituted in factor space using 
PCA analysis. Hierarchical ascendant classification and generation of a 
dendrogram is optionally performed if the user selects to use all 
eigenvectors for classification.
 
NOTE:
- the input single particle stack should not have been interpolated,
  i.e. not have been previously rotated or subpixel translated

Output from the program is an aligned stack of single particle images - 
STACKout_rtsh.spi, reconstituted image vectors, eigenimages, and 
optionally a dendrogram, found in the final_output directory. If the 
user did not select to classify on all eigenvectors, the program should be 
executed in '-hcl' mode with custom selection of eigenvalues. 
After the generation of a dendrogram, class averages are generated by
executing the program in '-cavgs' mode.

NOTE:
- you have to determine the threshold of the classification dendrogram 
  manually by running the spider command cl hd for different threshold values, 
  see documentation on the spider web page. After a suitable threshold has been
  found execute this program in '-cavgs' mode.

INPUT - VOLUME(S).spi, STACK_W_SINGLES.spi

OUTPUT - STACKout_rtsh.spi, pcasri**.spi files with eigenimages, dendrogram
         in ./REFINE_INPLANE_XXX/final_output

\t\t>>>>>>>> mode - hcl <<<<<<<<\n
Hierarchical ascendant classification and generation of a dendrogram.

INPUT - ./REFINE_INPLANE_XXX/ directory and selection of eigenvectors
        to be included in the hierarchical clustering using Ward's
        algorithm (Ex. 1,3-20)

OUTPUT - dendrdoc001.spi in ./REFINE_INPLANE_XXX/final_output

NOTE:

- you have to determine the threshold of the dendrogram for
  classification manually (see above) and then go for '-cavgs' mode

\t\t>>>>>>>> mode - cavgs <<<<<<<<\n
Calculates class averages given the input dendrdoc threshold.

NOTE:

- this mode generates a set of 'thresholded' class averages and class docs
  (ie. the user selects a minimum number of particles per class) 

INPUT - ./REFINE_INPLANE_XXX/ directory, min nr of ptcls in class,

OUTPUT -./docs_trs/classdocs****, STACKcavgs_tres.spi 

NOTE:
- now the STACKout_rtsh.spi stack can be removed

The thresholded class averages are used as an input to het_master.pl, which
establishes reconstructions. Selected reconstructions from het_master.pl,
are used as input for the next round of refine_inplane.pl. The same stack 
of single files is used repeatedly, whereas reconstructions change each round.
The combination of refine_inplane.pl with het_master.pl offers a powerful way 
to do ab initio reconstruction and initial refinement from heterogeneous 
single-particle data.\n\n";
}

