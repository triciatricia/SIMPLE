#!<PERLPATH>
use strict;
use warnings;
use Getopt::Long;
use lib '<SIMPLEPATH>/lib';
use spider;
use cluster_exec;

## command line options ##
my $mode1 = 0;
my $mode2 = 0;

GetOptions( 'classify' => \$mode1, 'hcl' => \$mode2 );

($mode1 == 0) && ($mode2 == 0) && (die "run options:
        --classify      - run PCA, optionally run HCL                       
        --hcl           - run HCL\n");

if ($mode1 == 1) {
  ( @ARGV != 7) && ( die "Give to script:
  1) box size in pixels
  2) mask radius in pixels
  3) stack with rotated particles ( ex. /path/STACK.spi )
  4) number of particles in the above stack
  5) nr of eigenvectors for PCA (20 should be enough, note also that 
      the eig:s used for clustering can be different)
  6) classification on all eigenvectors ( y or n )
  7) local execution or cluster ( l or c )
  NOTE: this mode has to be executed with 'nohup &'\n" );

  my $box     = $ARGV[0];
  my $mask    = $ARGV[1];
  my $stack   = $ARGV[2];
  my $nptcl   = $ARGV[3];
  my $neigs   = $ARGV[4];
  my $hcl     = $ARGV[5]; 
  my $exec    = $ARGV[6];

  pca( $box, $mask, $neigs, $stack, "1-$nptcl", $exec );
  if ( $exec eq 'c' ) {
    sleep(10) until ( finished( "JOBS" ) eq 'true' );
    job_failure_check( glob "errfile*" );
    unlink glob ( "JOBS errfile* outfile*" );
  }
  if ( $hcl eq 'y' ) {
    hcl( "1-$neigs", $exec );
    if ( $exec eq 'c' ) {
      sleep(10) until ( finished( "JOBS" ) eq 'true' );
      job_failure_check( glob "errfile*" );
      unlink glob ( "JOBS errfile* outfile*" );
    }
  }
} 
if ($mode2 == 1) {
  ( @ARGV != 2 ) && die "Give to script:
  1) eigenvectors for hcl ( ex. 1,3-15 )
  2) local execution or cluster ( l or c )\n";
  my $eigens = $ARGV[0];
  my $exec   = $ARGV[1];
  hcl( "1-$eigens", $exec );
  if ( $exec eq 'c' ) {
    sleep(10) until ( finished( "JOBS" ) eq 'true' );
    job_failure_check( glob "errfile*" );
    unlink glob ( "JOBS errfile* outfile*" );
  }
} 
