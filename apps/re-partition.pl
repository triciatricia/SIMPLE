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
     $npartitions, $jobname, $nrefs, $nrefsects, $weight );

if ($mode1 == 1) {
    ( @ARGV != 14 ) && die "\ngive to script:\n
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
9)  previous round's aligndata file or 0
10) linear weight (<0.5 -> lowres upweight >0.5 -> hres upweight)
11) use resolution boosting (y or n, note that boosting should be used first 
    after convergence has been achived without boosting)
12) nr of partitions
13) nr of reference central sections
14) jobname\n";

} elsif ( $mode2 == 1 ) {
 print "\nResubmits crashed jobs, run in the EVOL_ALIGN folder using the same command as for partition_master.pl!\n";
}

if ( $mode1 == 1 ) {
    ( $ARGV[0] =~ /,/ ) && ( @volumes = split(/,/,$ARGV[0]) );
    ( $ARGV[0] !~ /,/ ) && ( push @volumes, $ARGV[0] );
    foreach ( @volumes ) {
    $trs          = $ARGV[1];
    $box          = $ARGV[2];
    $smpd         = $ARGV[3];
    $sym          = $ARGV[4];
    $fstack       = $ARGV[5];
    $nptcls       = $ARGV[6];
    $lpass        = $ARGV[7];
    $aligndata   = $ARGV[8];
    $weight       = $ARGV[9];
    $boost        = $ARGV[10];    
    $npartitions  = $ARGV[11];
    $nrefsects    = $ARGV[12];
    $jobname      = $ARGV[13];
    
    ## global variables ##
    my ( $dir, $e1, $e2, $even, $even_spi, @filetab, $align_mode, $nstates );

    $nstates = scalar(@volumes);
    $nrefs = $nrefsects * @volumes;
    ( $sym =~ /(\d+)/ ) && ( $e1 = 360./$1 );
    ( $sym =~ /c/ )     && ( $e2 = 180. );
    ( $sym =~ /d/ )     && ( $e2 = 90. );
    
    $align_mode = 20;
    if( -e $aligndata ){
        $align_mode = 21;
        ( $boost eq 'y' ) && ( $align_mode = 22 );
    }

  my $ffreq = ($box-1)*$smpd;
  my $fdim  = $box/2;
  
  for( my $i=1; $i<=$npartitions; $i++ ) {
          my $stopptcl = $i*(int($nptcls/$npartitions)+1);
          my $startptcl = $stopptcl-(int($nptcls/$npartitions));
          if($stopptcl > $nptcls ){
                  $stopptcl = $nptcls
          }
          my $awk = (`grep "AWKSOME" aligndoc_$i | wc -l`);
          my $new_startptcl = $startptcl + $awk;
          my $time_per_image;
          ( $nstates == 1 ) && ( $time_per_image = 30 );
          ( $nstates > 1 ) && ( $time_per_image =$nstates*30 );
          if( $new_startptcl < $stopptcl ) {
                  my $walltime = $time_per_image*($stopptcl-$new_startptcl+1);
                  if( $walltime > 600000 ){
                          $walltime=600000
                  } elsif( $walltime < 10000 ){
                          $walltime=10000
                  }
          my $pwd = `pwd`;
          chomp $pwd;
          open( MYSCRIPT, ">resubmit_$i" ) or die
                "Cannot open resubmit_$i for writing\n";
                print MYSCRIPT "#!/bin/sh -x
#PBS -N $jobname
#PBS -l nodes=1
#PBS -l walltime=$walltime
#end of batch stuff
cd $pwd
<SIMPLEPATH>/bin/evol_align <<eot>> aligndoc_$i
$nptcls $nrefs $nstates 0 0
$sym 1 $new_startptcl $stopptcl $align_mode
$fdim $ffreq $lpass $trs $weight
filetable.dat
aligndata.dat
eot
exit\n";
                close( MYSCRIPT );
                #Now submit script:
                system("chmod u+x resubmit_$i");
                system("qsub resubmit_$i");
        }
  }
}
}

