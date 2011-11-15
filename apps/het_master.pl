#!<PERLPATH>
use warnings;
use strict;
use lib '<SIMPLEPATH>/lib';  
use iwannaparticle;
use parse_aligninfo;
use cluster_exec;
use spider;
use Cwd;

## binaries ##
my $align = get_evol_align; 
my $stack_fts = get_stack_ft;

(@ARGV != 9) && die "\ngive to script:\n
1) eulertable to initiate state assignment or 0 for reference free
   alignment followed by state assignment
2) shift in pixels (ex. if given 5, then [-5,5] will be searched) 
3) state groups to test (separated with commas, ex 1,2,3,4)
4) spider stack with class averages (ex. /PATH/stack.spi)
5) number of images in the above stack
6) box size in pixels ( box/2 cannot be an odd number )
7) sampling distance in Angstroms
8) symmetry group ( allowed: c1/c2/c3/c6/c7 )
9) low-pass limit in Angstroms (typically 20)\n
NOTE: final scores for different state groups are written to 
the RESULTS file. In each group there is usually one state with 
a low score to which non-fitting data have been matched. This
reconstruction should be excluded from further analysis. 
This program needs to be run with 'nohup &'\n";

my $eulers       = $ARGV[0];
( $eulers !~ /0/ ) && ( $eulers = redirect_path_for_chdir( $eulers ) ) && ( $eulers = redirect_path_for_chdir( $eulers ) );
my $trs          = $ARGV[1];
($trs == 0) && ($trs = 0.0001);
my @state_groups = split /,/,$ARGV[2];
my $spistack     = $ARGV[3];
my $navgs        = $ARGV[4];
my $box          = $ARGV[5];
my $smpd         = $ARGV[6];
my $sym          = $ARGV[7];
my $lpass        = $ARGV[8];
my $ftsize       = $box/2;
my $filetable    = "filetable.dat";

# no need to record children that have terminated
$SIG{CHLD} = 'IGNORE';

## some error checks ##
(`ls $spistack` ne "$spistack\n") && die "Spider stack does not exist at given location, check path and stack name!\n";
($spistack !~ /[\w+|d+]\.spi/) && die "Not a valid spider stack name! (Ex. xxxxx.spi)\n";
( $ftsize%2==1 ) && ( die "Fourier transform dimension $ftsize cannot be an odd number, change the box size !!!\n" );

######## HET MASTER #########
my $dir = "HET_MASTER_".join('_',split(/\s+/,localtime));
mkdir( $dir );
mkdir "./$dir/fts";
fixfourierfiles( $ftsize, $navgs, "$spistack", "./$dir/fts/ftshavg", 'l' );
unlink glob ("*xxx*" );
chdir( $dir );
open(RESULTS, ">RESULTS") or die "Cannot open file: $!\n";
print RESULTS ("\n     ***** HET MASTER START *****\n\n");
print "\n     ***** HET MASTER START *****\n\n";
my @selected_aligndocs;
if ( $eulers =~ /0/ ) {
        #### RAD x 3 on each state group ####
        foreach my $nstates ( @state_groups ) {
            mkdir( "rad_states_$nstates" );
            chdir( "rad_states_$nstates" );
            my @filetab = glob( "../fts/ftshavg*" );
            arr_to_file( \@filetab, $filetable );
            generate_scripts( 10, $navgs, $navgs, $nstates, 1, $sym, $box, $smpd, $lpass, 0, $filetable, 0, 3, "rad_states_$nstates", "../", 0, 0, 0); ############### ../
            chdir( "../" );
        }
        print "running RADx3 on each states group ... \n";
        sleep(10) until ( finished( "JOBS" ) eq 'true');
        unlink( "JOBS" );
        my @radouts = glob( "./rad_states*/aligndoc_*" );
        my @failed = check_aligndoc( \@radouts, $navgs, "RADSOME" );
        ( @failed != 0 ) && ( print RESULTS "RAD crashed! Check the output files! @failed\n" ) && ( die );
        unlink glob( "./rad_states*/rad_states*" );

        #### calculate scores for rad alignments ####
        foreach my $nstates ( @state_groups ) {
            chdir( "rad_states_$nstates" );
            foreach ( 1 .. 3 ) {
                mkdir( "score_$_" );
                chdir( "score_$_" );
                make_ang_and_filetab_for_scores( "../aligndoc_$_", 1, "../../fts/ftshavg", "RADSOME" );
                generate_scripts( 24, $navgs, $navgs, 1, 0, $sym, $box, $smpd, 0, 0, "filtab1.dat", "aligndata1.dat", 1, "rad_score", "./", 0, 0, 0 );
                chdir( "../" )
            }
            chdir( "../" );
        }
        print "calculating and sorting scores for RAD alignments ...\n";
        unlink glob( "./rad_states*/score_*/rad_score*" );
        unlink glob( "./rad_states*/score_*/*.dat" );

        #### sort and print scores ####
        print RESULTS ("   *** SCORES for RAD alignments ***\n"); 
        foreach my $nstates ( @state_groups ) {
            my%rad_scores;
            foreach my $i ( 1 .. 3 ) {
                my @out = file_to_arr( "./rad_states_$nstates/score_$i/score1" );
                foreach ( @out ) {
                    ( /CORRSPEC_SUM:\s+(\d+\.\d+)/ ) && ( $rad_scores{$i} = $1 );
                }
            }
            print RESULTS ("\n       states $nstates:\n" );
            my @order;
            foreach my $i (sort {$rad_scores{$b} <=> $rad_scores{$a}} keys%rad_scores ) {
                print RESULTS ("\n           RAD $i = $rad_scores{$i}\n");
                push @order, $i;
            }
            push @selected_aligndocs,  "./rad_states_$nstates/aligndoc_".$order[0];
        }
}

#### reference-free state assignment and orientation refinement initiated with the best scorinq RAD alignment ####
my $ang;
foreach my $nstates ( @state_groups ) {
    my $cnt = 0;
    mkdir( "de_states_$nstates" );   
    if ( $eulers =~ /0/ ) {
      system( "grep RADSOME $selected_aligndocs[$cnt] | awk '{print\$1,\$2,\$3}' > ./de_states_$nstates/eulers.dat" );
      $ang = "eulers.dat";
    } else {
      $ang = $eulers;
    }
    chdir( "./de_states_$nstates" );
    my @filetab = glob( "../fts/ftshavg*" );
    arr_to_file( \@filetab, $filetable );
    if( $eulers =~ /0/ ){
        generate_scripts( 12, $navgs, $navgs, $nstates, 1, $sym, $box, $smpd, $lpass, $trs, $filetable, $ang, 1, "de_states_$nstates", "../", 0, 0, 0); ####################
    }else{
        generate_scripts( 14, $navgs, $navgs, $nstates, 1, $sym, $box, $smpd, $lpass, $trs, $filetable, $ang, 1, "de_states_$nstates", "../", 0, 0, 0);
    }
    chdir( "../" );
    $cnt++;
}
print "running state assignment and final orientations refinement ... \n";
sleep(10) until ( finished( "JOBS" ) eq 'true');
my @deouts = glob( "./de_states*/aligndoc_*" );
my @failed2 = check_aligndoc( \@deouts, $navgs, "AWKSOME" ); 
( @failed2 != 0 ) && ( print RESULTS "DE crashed! Check the output files!\n" ) && ( die );
unlink glob( "./de_states*/de_states*" );

#### calculate scores for DE alignments ####
my %de_results;
my %single_scores;
my @divisors;
foreach my $nstates ( @state_groups ) {
    $de_results{$nstates} = {%single_scores}; # unnamed copy of a %single_scores hash as a value of the %de_results hash
    chdir( "de_states_$nstates" );        
    ( my $existing_states, my $nonexisting_states ) = make_ang_and_filetab_for_scores( "./aligndoc_1", $nstates, "../fts/ftshavg", "AWKSOME" );
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
my @count = glob( "./de_states*/calc_score*" );
unlink glob( "./de_states*/de_score*" );
unlink glob( "./de_states*/*dat" );

#### sort scores & reconstruct volumes ####
print RESULTS ("\n\n   *** SCORES for state assignments ***\n"); 
$spistack = redirect_path_for_chdir( $spistack );
$spistack = redirect_path_for_chdir( $spistack );
print "reconstructing volumes ... \n";
my $j=0;
foreach my $nstates ( @state_groups ) {
    mkdir( "volumes_states_$nstates" );
    chdir( "volumes_states_$nstates" );
    reconstruct_bp3f( "volume", "../de_states_$nstates/aligndoc_1", $nstates, $sym, 0, 0, 200, 1, $spistack, $navgs, 'l', 1 );
    unlink glob ("nstack*");
    chdir( "../" );
    my $total = 0;
    my @score_files = glob( "./de_states_$nstates/score*" );
    foreach my $file ( @score_files ) {
        my $i;
        ( $file =~ /score(\d+)/ ) && ( $i = $1 );
        my @out = file_to_arr( "./de_states_$nstates/score$i" );
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
print RESULTS "\n     ***** HET MASTER NORMAL STOP *****\n\n";
print "\n     ***** HET MASTER NORMAL STOP *****\n\n";
close( RESULTS );
