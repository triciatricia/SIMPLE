package cluster_exec;

=head1 NAME

cluster_exec - script generation tool 

=head1 DESCRIPTION

contains subroutines and functions for partitioning
and executing software developed in the Elmlund group,
can be configured for LUNARC and NERSC cluster environments

=SYNOPSIS

rock on

=head1 AUTHOR

This perl module was written by Dominika Elmlund -09

=cut

use warnings;
use Exporter;
use IPC::Open2;
use Cwd;
use lib '<SIMPLEPATH>/lib';                                        
use parse_aligninfo;

########### cluster specific variables #################
my $system = '<SYSTEM>';                                    
my $submit;   
my $submit2 = '';
my $cores_per_node;                                
( $system eq 'LUNARC' ) && ( $submit = 'qsub' );
( $system eq 'HOPPER' )  && ( $submit = 'qsub' ) && ( $cores_per_node = 24 );
( $system eq 'LOCAL' )  && ( $submit = 'nohup' ) && ( $submit2 = "\&\n" ); 
########################################################    

my $evol_align_para = '<SIMPLEPATH>/bin/evol_align_para';
my $evol_align      = '<SIMPLEPATH>/bin/evol_align'; 
my $stack_ft        = '<SIMPLEPATH>/bin/stack_fouriers';
my $stack_rfps      = '<SIMPLEPATH>/bin/stack_rfps';
my $stack_rfp_amps  = '<SIMPLEPATH>/bin/stack_rfp_amps';  

@ISA = ('Exporter');
@EXPORT = qw ( get_evol_align get_evol_align_para get_stack_ft generate_scripts stack_fouriers stack_fouriers_local 
               finished job_failure_check merge_algndocs redirect_path_for_chdir check_aligndoc get_stack_rfps
               make_ang_and_filetab_for_scores get_stack_rfp_amps stack_rfps stack_rfps_local stack_rfp_amps 
               stack_rfp_amps_local );
               
sub get_evol_align
{
  return ( "$evol_align" );
}

sub get_evol_align_para
{
  return ( "$evol_align_para" );
}

sub get_stack_ft
{
  return ( "$stack_ft" );
}

sub get_stack_rfps
{
  return ( "$stack_rfps" );
}

sub get_stack_rfp_amps
{
  return ( "$stack_rfp_amps" );
}

#! *Available* *modes* *are:*
#!* *mode* *10* rad - reference-free 3D alignment
#!* *mode* *11* reference-free state assignment
#!* *mode* *12* -"- & reference-free orientation refinement
#!* *mode* *13* reference-free projection direction assignment by the CE method
#!* *mode* *14* reference-free projection direction assignment by the CE-VNLS method
#!* *mode* *20* alignment with fixed lowpass limit, followed by *21*
#!* *mode* *21* alignment with spectral self-adaptation
#!* *mode* *22* alignment with spectral self-adaptation and orientation keeping
#!* *mode* *23* for finding filtering treshold or do spectral sorting
#!* *mode* *24* for calculating spectral score for a set of aligned projections
#!* *mode* *30* multireference alignment with fixed lowpass limit, docked reconstructions, followed by *31*
#!* *mode* *31* -"- with spectral self-adaptation, docked reconstructions
#!* *mode* *32* -"- with spectral self-adaptation and orientation keeping, docked reconstructions
#!* *mode* *36* for finding the filtering treshold or do spectral sorting
#! *Available* *flags* *are:*
#!* *flag* *0* no effect
#!* *flag* *1* turn off exhaustive search and first DE round, should be run with modes 21,22,31,32,33,34,35
#!* *flag* *2* only alignment with fixed lowpass limit, should be run with modes 20,30,33
#!* *flag* *3* run spectral=1 style refinement, but with fixed resolution limit

# Variables global to the module
my $binary;
my $nptcls;
my $nrefs;
my $nstates;
my $boot;
my $sym;
my $stack_opt;
my $box;
my $smpd;
my $ftsize;  # 1/2 box size;
my $ffreq;   # box size-1*smpd
my $lpass;
my $trs;
my $path_jobs;
my $filetable;
my $aligndata;
my $pwd;
my $nodes = 1;
my $npartitions;
my $jobname;
my%scriptdata = (
  SCRIPTNAME  => undef,
  WALLTIME    => undef,
  FROM_PTCL   => undef,
  TO_PTCL     => undef,
);
my @scripts;
my $mode;
my $freek;
my $refamps;
my $refamps_hed;
my $cavgamps;
my $cavgamps_hed;

# SCRIPT GENERATOR

sub generate_scripts 
{
  $mode         = shift;
  $nptcls       = shift;
  $nrefs        = shift;
  $nstates      = shift;
  $boot         = shift;
  $sym          = shift;
  $box          = shift;
  $smpd         = shift;
  $lpass        = shift;
  $trs          = shift;
  $filetable    = shift;
  $aligndata    = shift;
  $npartitions  = shift; # or number 'of runs for rad
  $jobname      = shift;
  $path_jobs    = shift;
  $freek        = shift; # added, pad with zeroes in relevant modules
  $refamps_body = shift; 
  $cavgamps_body = shift; 
  $pwd          = &Cwd::cwd();
  $ftsize       = $box/2; 
  $ffreq        = ($box-1)*$smpd;
  if ( $system eq 'HOPPER' ) {
      $binary = $evol_align_para;
  } else {
      $binary = $evol_align;
  }
  if ( $mode =~ /10|11|12|14/ ) {
    $stack_opt = 0;
    ( $mode == 10 ) && ( $doc = 'run_rad' );
    ( $mode == 11 ) && ( $doc = 'run_state_assign' );
    ( $mode == 12 ) && ( $doc = 'run_de' );
    ( $mode == 14 ) && ( $doc = 'run_de' );
    foreach ( 1 .. $npartitions ) {
      ( $mode == 10 ) && ( $scripts[$_]->{WALLTIME} = 100000 );
      ( $mode == 11 ) && ( $scripts[$_]->{WALLTIME} = 40000 );
      ( $mode == 12 ) && ( $scripts[$_]->{WALLTIME} = 40000 );
      ( $mode == 14 ) && ( $scripts[$_]->{WALLTIME} = 100000 );
      $scripts[$_]->{SCRIPTNAME} = "$doc$_";
      $scripts[$_]->{FROM_PTCL}  = 1;
      $scripts[$_]->{TO_PTCL}    = $nptcls;
      my $handle;
      open( $handle, ">$scripts[$_]->{SCRIPTNAME}" ) or die
      "Cannot open $scripts[$_]->{SCRIPTNAME} for writing\n";
      generate_header($_, $handle);
      generate_core($_, $handle, 'aligndoc_');
      close($handle);
      #Now submit script:
      system("chmod u+x $scripts[$_]->{SCRIPTNAME}");
      if( $system eq 'LOCAL' ){
          my $pid;
          defined($pid=fork()) or die "unable to fork: $!\n";
          if($pid == 0){ # child
              exec("$scripts[$_]->{SCRIPTNAME}");
              die "unable to exec: $!\n";
          }
          open( FOO, ">>$path_jobs/JOBS" ) or die "Cannot append to $path_jobs/JOBS: $!\n";
          print FOO "$pid\n";
          close( FOO );
      }else{
          system("$submit $scripts[$_]->{SCRIPTNAME} $submit2 >> $path_jobs/JOBS");
      } 
    }
    return $doc;
  }
  if ( $mode =~ /20|21|22|25/ ) {
    $stack_opt = 1;
    $doc       = 'submitscript';
    ( $nstates == 1 ) && ( $time_per_image = 60 );
    ( $nstates > 1 ) && ( $time_per_image = $nstates*60 );
    ( $system eq 'HOPPER' ) && ( $time_per_image = $time_per_image/10. );
    for( my $i=1; $i<=$npartitions; $i++ ) {
      fix_range_walltime_and_name( $i, $nptcls );
      my $handle;
      open( $handle, ">$scripts[$i]->{SCRIPTNAME}" ) or die
      "Cannot open $scripts[$i]->{SCRIPTNAME} for writing\n";
      generate_header($i, $handle);
      generate_core($i, $handle, 'aligndoc_');
      close( $handle );
      #Now submit script:
      my $sub = $path_jobs.$scripts[$i]->{SCRIPTNAME};
      system("chmod u+x $sub");
      system("$submit $sub $submit2");
    }
    return "$doc";  
  }
  if ( $mode =~ /24/ ) {
    $stack_opt = 0;
    $doc       = "calc_score";
    $scripts[$npartitions]->{SCRIPTNAME} = "$doc$npartitions";
    $scripts[$npartitions]->{WALLTIME}   = 10000;
    $scripts[$npartitions]->{FROM_PTCL}  = 1;
    $scripts[$npartitions]->{TO_PTCL}    = $nptcls;
    my $handle;
    open( $handle, ">$scripts[$npartitions]->{SCRIPTNAME}" ) or die
    "Cannot open $scripts[$npartitions]->{SCRIPTNAME} for writing\n";
    generate_core($npartitions, $handle, "score");
    close( $handle );
    #Now run script:
    system("chmod u+x $scripts[$npartitions]->{SCRIPTNAME}");
    system( "./$scripts[$npartitions]->{SCRIPTNAME}" ); # local execution
    return "$doc";
  } 
  if ( $mode =~ /23|36/ ) {
    $stack_opt = 1;
    $doc       = "get_MODELQ";
    $scripts[$npartitions]->{SCRIPTNAME} = "$doc";
    $scripts[$npartitions]->{FROM_PTCL}  = 1;
    $scripts[$npartitions]->{TO_PTCL}    = $nptcls;
    my $handle;
    open( $handle, ">$scripts[$npartitions]->{SCRIPTNAME}" ) or die
    "Cannot open $scripts[$npartitions]->{SCRIPTNAME} for writing\n";
    generate_core(1, $handle, "MODELQ");
    close( $handle );
    #Now run script:
    system("chmod u+x $scripts[$npartitions]->{SCRIPTNAME}");
    system( "./$scripts[$npartitions]->{SCRIPTNAME}" ); # local execution
    return "$doc";
  }
}

sub fix_range_walltime_and_name
{
    my $i  = shift; # index in @scripts
    my $n  = shift; # nr of objects to be partitioned
    $scripts[$i]                = {%scriptdata};
    $scripts[$i]->{TO_PTCL}     = $i*(int($n/$npartitions)+1);
    $scripts[$i]->{FROM_PTCL}   = $scripts[$i]->{TO_PTCL}-(int($n/$npartitions));
    if ($scripts[$i]->{TO_PTCL} > $n) {
      $scripts[$i]->{TO_PTCL}   = $n 
    }
    $scripts[$i]->{WALLTIME}    = $time_per_image*($scripts[$i]->{TO_PTCL}-$scripts[$i]->{FROM_PTCL}+1);
    if($scripts[$i]->{WALLTIME} > 600000){
      $scripts[$i]->{WALLTIME}  = 600000
    }
    if($scripts[$i]->{WALLTIME} < 10000){
      $scripts[$i]->{WALLTIME}  = 10000
    }
    $scripts[$i]->{SCRIPTNAME}    = 'submitscript'.$i;    
}

sub generate_header
{
  my $i = shift;
  my $handle = shift;
  if ( $system eq 'LUNARC' ) {
    print $handle "#!/bin/sh -x\n#PBS -N $jobname\n#PBS -l nodes=$nodes\n";
    print $handle "#PBS -l walltime=$scripts[$i]->{WALLTIME}\n";
    print $handle "#PBS -o outfile.\$PBS_JOBID\n";
    print $handle "#PBS -e errfile.\$PBS_JOBID\n";
  }
  if ( $system eq 'HOPPER' ) {
    my $mppw = $nodes*$cores_per_node;
    print $handle "#!/bin/sh -x\n#PBS -N $jobname\n#PBS -l mppwidth=$mppw\n";
    my $hours = int($scripts[$i]->{WALLTIME}/3600);
    my $min   = (($scripts[$i]->{WALLTIME})/60)%60;
    my $wtime = $hours.':'.$min.':00';
    print $handle "#PBS -l walltime=$wtime\n";
    print $handle "#PBS -o outfile.\$PBS_JOBID\n";
    print $handle "#PBS -e errfile.\$PBS_JOBID\n";
    print $handle "#PBS -q regular\n";
  }
  if ( $system eq 'LOCAL' ) {
    return;
  }
}

sub generate_core
{
  my $i      = shift;
  my $handle = shift;
  my $out    = shift;
  if ( $system eq 'HOPPER' ) {
      my $apruncmd = "aprun -n 1 -d 24";
      print $handle "setenv OMP_NUM_THREADS $cores_per_node\n";
      print $handle "cd $pwd\n$apruncmd $evol_align_para <<eot> $out$i\n"; 
      print $handle "$nptcls $nrefs $nstates $boot 4\n";
      print $handle "$sym $stack_opt $scripts[$i]->{FROM_PTCL} $scripts[$i]->{TO_PTCL} $mode $cores_per_node\n";
      print $handle "$ftsize $ffreq $lpass $trs $freek\n";
      print $handle "$filetable\n$aligndata\neot\nexit\n";
  } else {
      print $handle "cd $pwd\n$binary <<eot> $out$i\n";
      print $handle "$nptcls $nrefs $nstates $boot 0\n";
      print $handle "$sym $stack_opt $scripts[$i]->{FROM_PTCL} $scripts[$i]->{TO_PTCL} $mode\n";
      print $handle "$ftsize $ffreq $lpass $trs $freek\n";
      print $handle "$filetable\n$aligndata\neot\nexit\n";
  }
}

sub stack_fouriers
{
  my $filetab = shift;
  my $nptcls  = shift;
  my $fdim    = shift;
  my $fstack  = shift;
  my $pwd   = &Cwd::cwd();
  open( MYSCRIPT, ">run_stack_fourier_files" ) or die
  "Cannot open run_stack_fourier_files for writing\n";
  if ( $system eq 'LUNARC' ) {
    print MYSCRIPT "#!/bin/sh -x
#PBS -N stack_ft
#PBS -l nodes=1
#PBS -l walltime=20000\n";
  }
  print MYSCRIPT "cd $pwd
$stack_ft<<eot
$filetab
$nptcls $fdim
$fstack.fim $fstack.hed
eot
exit\n";
  close(MYSCRIPT);
  system ("chmod 700 run_stack_fourier_files" );
  system ("$submit run_stack_fourier_files >> JOBS" );
  return "run_stack_fourier_files";
}

sub stack_rfps
{
  my $filetab  = shift;
  my $nptcls   = shift;
  my $fdim     = shift;
  my $dstep    = shift;
  my $lowpass  = shift;
  my $rfpstack = shift;
  my $pwd      = &Cwd::cwd();
  open( MYSCRIPT, ">run_stack_rfps" ) or die
  "Cannot open run_stack_rfps for writing\n";
  if ( $system eq 'LUNARC' ) {
    print MYSCRIPT "#!/bin/sh -x
#PBS -N stack_rfps
#PBS -l nodes=1
#PBS -l walltime=20000\n";
  }
  print MYSCRIPT "cd $pwd
$stack_rfps<<eot
$filetab
$nptcls $fdim $dstep $lowpass 0
$rfpstack.rfp $rfpstack.hed
eot
exit\n";
  close(MYSCRIPT);
  system ("chmod 700 run_stack_rfps" );
  system ("$submit run_stack_rfps >> JOBS" );
  return "run_stack_rfps";
}

sub stack_rfp_amps
{
  my $filetab  = shift;
  my $nptcls   = shift;
  my $fdim     = shift;
  my $dstep    = shift;
  my $lowpass  = shift;
  my $rfpstack = shift; 
  my $pwd      = &Cwd::cwd();
  $rfpstack = $rfpstack."_amp";
  open( MYSCRIPT, ">run_stack_rfp_amps" ) or die
  "Cannot open run_stack_rfp_amps for writing\n";
  if ( $system eq 'LUNARC' ) {
    print MYSCRIPT "#!/bin/sh -x
#PBS -N stack_rfp_amps
#PBS -l nodes=1
#PBS -l walltime=20000\n";
  }
  print MYSCRIPT "cd $pwd
$stack_rfp_amps<<eot
$filetab
$nptcls $fdim $dstep $lowpass 1
$rfpstack.rfp $rfpstack.hed
eot
exit\n";
  close(MYSCRIPT);
  system ("chmod 700 run_stack_rfp_amps" );
  system ("$submit run_stack_rfp_amps >> JOBS" );
  return "run_stack_rfp_amps";
}

sub finished
{
    my $jobs_file = shift;
    my @arr = file_to_arr( $jobs_file );
    my @pids;
    foreach (@arr) {
        (/(\d+)/) && (push @pids, $1);
    }
    my $cnt=0;
    foreach my $pid ( @pids ) { 
      if ( $system eq 'LUNARC' ) {
        ( `qstat | grep $pid` =~ /$pid/ ) && ( $cnt++ );             
      }
      if ( $system eq 'LOCAL' ) {
        ( kill 0, $pid ) && ( $cnt++ )
      }
    }
    ( $cnt == 0 ) && ( return 'true' );
    ( $cnt != 0 ) && ( return 'false' );
}  

sub job_failure_check
{
    my @errfiles    = @_;
    my @failed;
    foreach my $e ( @errfiles ) {
      (  `cat $e` !~ /\*\*\*\* (SPIDER|EVOL_ALIGN) NORMAL STOP \*\*\*\*/ ) && ( push @failed, $e );  
    }
    if ( scalar @failed != 0 ) {
        open( MYSCRIPT, ">JOB_FAILURE" ) or die "Cannot open JOB_FAILURE for writing: $!\n";
        print MYSCRIPT "Check @failed files for more info.\n";
        close( MYSCRIPT );
        die;     
    }
}

sub merge_algndocs 
{
  my $docname = shift;
  my $merged  = shift;
  my @algndocs = glob("$docname*");
  chomp @algndocs;
  foreach my $j (1 .. scalar(@algndocs)) {
    my $doc = $docname.$j;
    system("cat $doc >> $merged");
  }
}

sub redirect_path_for_chdir
{
  my $path = shift;
    if( $path =~ /^\.\// ) {
        $path =~ s/^\.\//\.\.\//;
    } elsif ( $path =~ /^\.\.\// ) {
    $path = '../'.$path;
    } elsif ( $path =~ /^\// ) {
        # No substitution needed, $path sould be the absolute path
    } else {
        $path = '../'.$path;
    }
    return "$path";
}

sub check_aligndoc
{
    my $files  = shift;
    my $nptcls = shift;
    my $match  = shift;
    my @failed;
    foreach (@$files) {
        my $awk = `grep $match $_ |  wc -l`;
        chomp $awk;
        ($nptcls != $awk) && ( push @failed, $_ );
    }
    return ( @failed );
}

sub make_ang_and_filetab_for_scores 
{
  my $aligndoc  = shift;
  my $nstates   = shift;
  my $ftspath   = shift;
  my $match     = shift;
  my @fts       = glob( "$ftspath*" );
  system( "grep $match $aligndoc > temp.dat" );
  my @doc = file_to_arr( "temp.dat" ); 
  my @existing_states; ## some states may be empty
  my @nonexisting_states;
  foreach my $state ( 1 .. $nstates ) {
      my $cnt = 0;
      open( FH1, ">temptab$state.dat" ) or die "Cannot open file temptab$state.dat for writing";
      open( FH2, ">aligndata$state.dat" ) or die "Cannot open file aligndata$state,dat for writing";
      open( FH3, ">foo$state.dat" ) or die "Cannot open file foo$state.dat for writing";
      foreach my $j ( 0 .. $#doc ) {
          if ( ( $doc[$j] =~ /STATE:\s+$state/ ) or ($doc[$j] =~ /RADSOME/ ) ) {
              $cnt++;
              $doc[$j] =~ s/^\s+//;
              print FH1 "$fts[$j]\n";
              my @line = split( /\s+/, $doc[$j] );
              print FH2 "$line[0] $line[1] $line[2]\n";
              print FH3 "$line[0] $line[1] $line[2] $line[3] $line[4] 1\n";    
          }
      } 
      ( $cnt > 0 ) && ( push @existing_states, $state );
      ( $cnt == 0 ) && ( push @nonexisting_states, $state );
      close( FH1 );
      close( FH2 );
      close( FH3 );
      system( "cat foo$state.dat >> aligndata$state.dat" );
      system( "cat temptab$state.dat > filtab$state.dat" );
      system( "cat temptab$state.dat >> filtab$state.dat" );
      unlink( "foo$state.dat" );
      unlink( "temptab*.dat" );
  }
  unlink( "temp.dat" );
  return( \@existing_states, \@nonexisting_states );
}
1;