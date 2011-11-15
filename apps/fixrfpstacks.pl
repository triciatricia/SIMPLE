#!<PERLPATH>

use warnings;
use strict;
use lib '<SIMPLEPATH>/lib'; 
use spider;
use cluster_exec;
use parse_aligninfo;

( @ARGV != 8 ) && die "\ngive to script:\n
1) spider stack with masked single images (ex. stack.spi)
2) number of images in the above stack
3) box size (in pixels)
4) sampling distance of the images (in A)
5) lowpass filter limit (in A)
6) output stack body name (giving <stackbody>.rfp )
7) local execution or cluster ( l or c )
8) amplitudes only (give 1 of so, else 0)\n
NOTE: this program first fourier transforms the single images 
spider stack using spider, and then stacks the spider fourier files 
into the <stackbody>.rfp SIMPLE stack format. The <stackbody>.hed 
file contains parameters and a list of stacked fourier transforms. 
If the front-end has a different CPU architecture than the back-end
(the cluster nodes) stacking needs to be done on the cluster!
This program has to be executed with 'nohup &'\n";
 
my $stack   = $ARGV[0];
my $nptcls  = $ARGV[1];
my $box     = $ARGV[2];
my $smpd    = $ARGV[3];
my $lowpass = $ARGV[4];
my $body    = $ARGV[5];
my $exec    = $ARGV[6];
my $amp     = $ARGV[7];
my $ftsize  = $box/2;
my $dstep   = ($box-1)*$smpd; 
( ($ftsize)%2==1 ) && ( die "Fourier transform dimension cannot be an odd number, change box size so the box/2 is an even number !!!\n" );
mkdir("temp_fts");
if ( $exec =~ 'l' ) {
    fixfourierfiles( $ftsize, $nptcls, $stack, "./temp_fts/fts", 'l' );
    if( $amp == 1 ){
        stack_rfp_amps("tempfiltab.dat", $nptcls, $ftsize, $dstep, $lowpass, $body );
    }else{
        stack_rfps("tempfiltab.dat", $nptcls, $ftsize, $dstep, $lowpass, $body );
    }
} elsif( $exec =~ 'c' ) {
    fixfourierfiles( $ftsize, $nptcls, $stack, "./temp_fts/fts", 'c' ); 
    sleep(10) until ( finished( "JOBS" ) eq 'true' );
    job_failure_check( glob "errfile*" );
    unlink glob ( "JOBS errfile* outfile* results.xxx.000 LOG.xxx" );
    my @fts = glob( "./temp_fts/fts*");
    arr_to_file( \@fts, "tempfiltab.dat" );
    if( $amp == 1 ){
        stack_rfp_amps("tempfiltab.dat", $nptcls, $ftsize, $dstep, $lowpass, $body );
    }else{
        stack_rfps("tempfiltab.dat", $nptcls, $ftsize, $dstep, $lowpass, $body );
    }
    sleep(10) until ( finished( "JOBS" ) eq 'true');
    unlink( "JOBS" );
} else {
  die "Not a valid exec mode!\n";
}
system( "rm -rf ./temp_fts tempfiltab.dat fixfourier*" );
print " **** FIXRFPSTACKS NORMAL STOP ****\n";