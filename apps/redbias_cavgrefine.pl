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
my ( @volumes, $trs, @state_groups, $spistack, $box, $smpd, $weight, $sym, $cavgs, $ncavgs, $aligndata, $lpass, $jobname );

if ($mode1 == 1) {
    ( @ARGV != 12 ) && die "\ngive to script:\n
1) spider reference volume(s) (multiple volumes separated with commas 
   ex. vol1.spi,vol2.spi, NO SPACES, '.spi' extension)  
2) shift in pixels (ex. if given 5, then [-5,5] will be searched)
3) state groups to test (separated with commas, ex 1,2,3,4)
4) box size in pixels (box/2 cannot be an odd number)
5) sampling distance in Angstroms
6) weight between unbiased and biased correlation
   (>0.5 means that more weight is given to the unbiased measures)
7) point-group symmetry (c1/c2/c3/c7/c6/d2/d3/d7)
8) class averages spider stack (ex. /PATH/stack.spi)
9) number of images in the above stack
10) low pass limit in Angstroms
11 aligndata file from the previous round
12) jobname\n 
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
    @state_groups = split /,/,$ARGV[2];
    $box          = $ARGV[3];
    $smpd         = $ARGV[4];
    $weight       = $ARGV[5];  
    $sym          = $ARGV[6];
    $cavgs        = $ARGV[7];
    $ncavgs       = $ARGV[8];
    $lpass        = $ARGV[9];
    $aligndata    = $ARGV[10];  
    $jobname      = $ARGV[11];
    $spistack     = $cavgs;
    
    (`ls $cavgs` ne "$cavgs\n") && die "Cavgs stack $cavgs does not exist at given location!\n";
    $cavgs = redirect_path_for_chdir( $cavgs);
    ($sym !~ /[c1|c2|c3|c6|c7|d2|d3|d7]/) && die "Not a valid symmetry group\n";
    ( ($box/2)%2==1 ) && ( die "Fourier transform dimension cannot be an odd number, change box size so the box/2 is an even numebr !!!\n" );
    ( `grep 'AWKSOME' $aligndata | wc -l` != $ncavgs ) && ( die "Number of entries in $aligndata does not equal nr of particles" );
    
    ## global variables ##
    my ( $dir, $e1, $e2, $even, $even_spi, @filetab, $nrefs, $ftsize, $fffq );
    $fffq = ($box-1)*$smpd;
    $ftsize = $box/2;
    ## make dir ##
    $dir = "REDBIAS_REFINE_".join('_',split(/\s+/,localtime));
    mkdir( $dir );
    chdir( $dir );
    # generate aligndata
    $aligndata = redirect_path_for_chdir( $aligndata );
    system( "grep 'AWKSOME' $aligndata | awk '{print\$1,\$2,\$3,\$4,\$5,\$15}' > aligndata.dat" );
    # generate even eulers
    $nrefs = 64 * @volumes;
    ( $sym =~ /(\d+)/ ) && ( $e1 = 360./$1 );
    ( $sym =~ /c/ )     && ( $e2 = 180. );
    ( $sym =~ /d/ )     && ( $e2 = 90. );
    $even = spiral_eulers( 64, $e1, $e2, "even_64.dat" );
    $even_spi = get_spidoc( "even_64.dat" );
    # ft cavgs
    mkdir( "cavgs_fts" );
    fixfourierfiles( $ftsize, $ncavgs, $cavgs, "./cavgs_fts/fts", 'l' ); 
    my @filetabcavgs = glob( "./cavgs_fts/fts*");
    arr_to_file( \@filetabcavgs, "filetabcavgs.dat" );
    system( "cat filetabcavgs.dat > filetable.dat" );
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
    arr_to_file( \@filetabrefs, "filetabrefs.dat" );
    system( "cat filetabrefs.dat >> filetable.dat" );  
    ## make amp fstacks ##
    stack_rfp_amps_local( "filetabrefs.dat", scalar(@filetabrefs), $ftsize, $fffq, $lpass, "refs" );
    stack_rfp_amps_local( "filetabcavgs.dat", $ncavgs, $ftsize, $fffq, $lpass, "cavgs" );
    system( "rm filetabrefs.dat filetabcavgs.dat");
    ## run
    my$ang = './aligndata.dat';
    my$awk = '{sub(".",".."); print}';
    foreach my$nstates ( @state_groups ) {
	mkdir( "redbias_states_$nstates" );
	chdir( "redbias_states_$nstates" );
    	system( "cat ../filetable.dat | awk $awk > filetable.dat" );
        generate_scripts( 50, $ncavgs, scalar(@filetabrefs), $nstates, 0, $sym,
        $box, $smpd, $lpass, $trs, './filetable.dat', $ang, 0, $jobname, "./",
        $weight, "../refs_amp", "../cavgs_amp" );
        chdir("../");   
    }
    print "running state assignment and final orientations refinement ... \n";
    ######################################
    foreach my $nstates ( @state_groups ) {
          chdir( "./redbias_states_$nstates" );
          sleep(10) until ( finished( "JOBS" ) eq 'true');
          chdir( "../" );
    }
    my @deouts = glob( "./redbias_states*/aligndoc_*" );
    my @failed2 = check_aligndoc( \@deouts, $ncavgs, "AWKSOME" ); 
    ( @failed2 != 0 ) && ( print RESULTS "DE crashed! Check the output files!\n" ) && ( die );
    unlink glob( "./redbias_states*/*" );
#### calculate scores for DE alignments ####
my %de_results;
my %single_scores;
my @divisors;
foreach my $nstates ( @state_groups ) {
    $de_results{$nstates} = {%single_scores}; # unnamed copy of a %single_scores hash as a value of the %de_results hash
    chdir( "redbias_states_$nstates" );
    ( my $existing_states, my $nonexisting_states ) = make_ang_and_filetab_for_scores( "./aligndoc_1", $nstates, "../cavgs_fts/fts", "AWKSOME" );
    push( @divisors, scalar( @$existing_states ) );
    foreach ( @$existing_states ) { # dereference 
        my $cnt = ( `cat filtab$_.dat | wc -l` )/2;
        generate_scripts( 24, $cnt, $cnt, 1, 0, $sym, $box, $smpd, 0, 0, "filtab$_.dat", "aligndata$_.dat", $_, "de_score$_", "./", 0, 0, 0 );
    }
    foreach ( @$nonexisting_states ) {
        $de_results{$nstates}->{"VOLUME_$_"} = 0.0; # assign 0's to empty states
    }
    chdir( "../" );
}
my @count = glob( "./redbias_states*/calc_score*" );
unlink glob( "./redbias_states*/de_score*" );
unlink glob( "./redbias_states*/*dat" );

#### sort scores & reconstruct volumes ####
print RESULTS ("\n\n   *** SCORES for state assignments ***\n"); 
$spistack = redirect_path_for_chdir( $spistack );
$spistack = redirect_path_for_chdir( $spistack );
print "reconstructing volumes ... \n";
my $j=0;
foreach my $nstates ( @state_groups ) {
    mkdir( "volumes_states_$nstates" );
    chdir( "volumes_states_$nstates" );
    reconstruct_bp3f( "volume", "../redbias_states_$nstates/aligndoc_1", $nstates, $sym, 'NONE', 0, 1, $spistack, $ncavgs, 'l' );
    unlink glob ("nstack*");
    chdir( "../" );
    my $total = 0;
    my @score_files = glob( "./redbias_states_$nstates/score*" );
    foreach my $file ( @score_files ) {
        my $i;
        ( $file =~ /score(\d+)/ ) && ( $i = $1 );
        my @out = file_to_arr( "./redbias_states_$nstates/score$i" );
        foreach ( @out ) {
            ( /CORRSPEC_SUM:\s+(\d+\.\d+)/ ) && ( $de_results{$nstates}->{"VOLUME_$i"} = $1 ) && ( $total += $1 ); # single volume score
        }
    }
    $de_results{$nstates}->{TOTAL} = $total/$divisors[$j]; # total score for the group, only for existing states
    $j++;
}
print "calculating and sorting scores for final alignments ...\n";
foreach my $group (sort {$de_results{$b}->{TOTAL} <=> $de_results{$a}->{TOTAL}} keys%de_results) {
        print  RESULTS "\n           $group states:\n";
        printf RESULTS "\n           \t    TOTAL = %.3f\n", $de_results{$group}->{TOTAL};
        foreach my $volume (1 .. $group) {
                my $key = "VOLUME_$volume";
                printf RESULTS "\n           \t volume $volume = %.3f\n", $de_results{$group}->{$key};
        }
}
print RESULTS "\n     ***** REDBIAS CAVGREFINE NORMAL STOP *****\n\n";
print "\n     ***** REDBIAS CAVGREFINE NORMAL STOP *****\n\n";
close( RESULTS );

}





