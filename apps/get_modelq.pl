#!<PERLPATH>
use warnings;
use strict;
use Getopt::Long;
use lib '<SIMPLEPATH>/lib'; 
use cluster_exec;
use parse_aligninfo;
use eulers;
use spider;


## command line arguments ##
my ( @volumes, $box, $smpd, $sym, $fstack, $nptcls, $aligndata, $nstates );

( @ARGV != 7 ) && die "\ngive to script:\n
1) spider reference volumes separated with commas (ex. vol1.spi,vol2.spi,
   NO SPACES, '.spi' extension )
2) box size in pixels
3) sampling distance in Angstroms
4) point-group symmetry (c1/c2/c3/c7/c6/d2/d3/d7)
5) stack with fourier transforms (ex. ./fstack.fim, where '.fim' denotes 
   a SIMPLE format )
6) number of transforms in the above stack
7) previous round's aligndata file\n";


( $ARGV[0] =~ /,/ ) && ( @volumes = split(/,/,$ARGV[0]) );
( $ARGV[0] !~ /,/ ) && ( push @volumes, $ARGV[0] );
foreach ( @volumes ) {
        (`ls $_` ne "$_\n") && die "Volume $_ does not exist at given location!\n";
        $_ = redirect_path_for_chdir( $_ );
}
$box          = $ARGV[1];
$smpd         = $ARGV[2];
$sym          = $ARGV[3];
$fstack       = $ARGV[4];
$nptcls       = $ARGV[5];
$aligndata    = $ARGV[6];
$nstates      = scalar( @volumes );   
    
(`ls $fstack` ne "$fstack\n") && die "Fourier stack $fstack does not exist at given location!\n";
$fstack       = redirect_path_for_chdir( $fstack );
($sym !~ /[c1|c2|c3|c6|c7|d2|d3|d7]/) && die "Not a valid symmetry group\n";
( ($box/2)%2==1 ) && ( die "Fourier transform dimension cannot be an odd number, change box size so the box/2 is an even numebr !!!\n" );
( `grep 'AWKSOME' $aligndata | wc -l` != $nptcls ) && ( die "Number of entries in $aligndata does not equal nr of particles" );
    
    ## global variables ##
    my ( $dir, $e1, $e2, $even, $even_spi, @filetab, $align_mode, $nrefs );
    
$dir = "GET_MODELQ_".join('_',split(/\s+/,localtime));
mkdir( $dir );
chdir( $dir );
$nrefs = 64 * @volumes;
( $sym =~ /(\d+)/ ) && ( $e1 = 360./$1 );
( $sym =~ /c/ )     && ( $e2 = 180. );
( $sym =~ /d/ )     && ( $e2 = 90. );
# generate even eulers
$even = spiral_eulers( 64, $e1, $e2, "even_64.dat" );
$even_spi = get_spidoc( "even_64.dat" );
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
system( "grep 'AWKSOME' $aligndata | awk '{print\$1,\$2,\$3,\$4,\$5,\$15}' >> aligndata.dat" );
( $nstates == 1 ) && ( $align_mode = 23 );
( $nstates != 1 ) && ( $align_mode = 36 );
    
generate_scripts( $align_mode, $nptcls, $nrefs, scalar(@volumes), 0, $sym, $box, $smpd, 0, 0, './filetable.dat', './aligndata.dat', 1, '', "./", 0, 0, 0, 0, 0 );







