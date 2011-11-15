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
my ( @volumes, $trs, $box, $smpd, $sym, $fstack, $nptcls, $ampstack, $lpass, $npartitions, $jobname, $nspace, $aligndata, $weight, $nrefs );

if ($mode1 == 1) {
    ( @ARGV != 15 ) && die "\ngive to script:\n
1) spider reference volume(s) (multiple volumes separated with commas 
   ex. vol1.spi,vol2.spi, NO SPACES, '.spi' extension)  
2) shift in pixels (ex. if given 5, then [-5,5] will be searched) 
3) box size in pixels (box/2 cannot be an odd number)
4) sampling distance in Angstroms
5) point-group symmetry (c1/c2/c3/c7/c6/d2/d3/d7)
6) fourier transforms stack (ex. /PATH/fstack.fim)
7) number of images in the above stack
8) amplitudes stack (ex. /PATH/ampstack.rfp)
9) low-pass limit in Angstroms 
10) previous round's aligndata file or 0 
11) linear weight (<0.5 -> lowres upweight >0.5 -> hres upweight) 
12) number of partitions
13) nr of reference central sections
14) jobname
15) population size for DE\n 
This program needs to be run with 'nohup &'\n";

} elsif ( $mode2 == 1 ) {
 print "\nHappy Processing!\n";
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
    $ampstack     = $ARGV[7];
    $lpass        = $ARGV[8];
    $aligndata    = $ARGV[9];
    $weight       = $ARGV[10];
    $npartitions  = $ARGV[11];
    $nrefs        = $ARGV[12];
    $jobname      = $ARGV[13];
    $nspace       = $ARGV[14];
    
    $ampstack =~ s/\.rfp//;
    (`ls $fstack` ne "$fstack\n") && die "FT stack stack $fstack does not exist at given location!\n";
    $fstack      = redirect_path_for_chdir( $fstack);
    $ampstack = redirect_path_for_chdir( $ampstack );
    ($sym !~ /[c1|c2|c3|c6|c7|d2|d3|d7]/) && die "Not a valid symmetry group\n";
    ( ($box/2)%2==1 ) && ( die "Fourier transform dimension cannot be an odd number, change box size so the box/2 is an even numebr !!!\n" );
    ( $aligndata !~ /0/ ) && ( `grep 'AWKSOME' $aligndata | wc -l` != $nptcls ) && ( die "Number of entries in $aligndata does not equal nr of particles" );

    ## global variables ##
    my ( $dir, $e1, $e2, $even, $even_spi, @filetab, $nstates, $ftsize, $fffq, $mode );
    $fffq = ($box-1)*$smpd;
    $ftsize = $box/2;
    $nstates = scalar(@volumes);
    $mode = 25;
    ## make dir ##
    $dir = "MIXED_REFINE_".join('_',split(/\s+/,localtime));
    mkdir( $dir );
    chdir( $dir );
    # generate even eulers
    ( $sym =~ /(\d+)/ ) && ( $e1 = 360./$1 );
    ( $sym =~ /c/ )     && ( $e2 = 180. );
    ( $sym =~ /d/ )     && ( $e2 = 90. );
    $even = spiral_eulers( $nrefs, $e1, $e2, "even_$nrefs.dat" );
    $even_spi = get_spidoc( "even_$nrefs.dat" );
    # project volumes
    mkdir( "refs_fts" );
    my @filetabrefs;
    foreach my $i ( 1 .. @volumes ) {
            mkdir( "./refs_fts/refs_$i" );
            ftsh_projmod( $box, $even_spi, $volumes[$i-1], "./refs_fts/refs_$i/ftshproj", 'l' );
            my @refs = glob( "./refs_fts/refs_$i/ftshproj*" );
            push( @filetabrefs, @refs );
            system ( "cat $even >> aligndata.dat" );
    }
    if ( $aligndata !~ /0/ ) {
          $mode = 26;
          $aligndata = redirect_path_for_chdir( $aligndata );
          system( "grep 'AWKSOME' $aligndata | awk '{print\$1,\$2,\$3,\$4,\$5,\$15}' >> aligndata.dat" );
    } 
    arr_to_file( \@filetabrefs, "filetabrefs.dat" );
    system( "cat filetabrefs.dat > filetable.dat" ); 
    system( "ls $fstack >> filetable.dat" );  
    ## make amp fstacks ##
    stack_rfp_amps( "filetabrefs.dat", scalar(@filetabrefs), $ftsize, $fffq, $lpass, "refs" );
    system( "rm filetabrefs.dat");
    ## run 
    generate_scripts( $mode, $nptcls, scalar(@filetabrefs), $nstates, 0, $sym, $box, $smpd,
                    $lpass, $trs, './filetable.dat', './aligndata.dat', $npartitions,  
                      $jobname, "./", $weight, "refs_amp", $ampstack, $nspace );

}
