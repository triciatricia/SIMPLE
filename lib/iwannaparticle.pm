package iwannaparticle;

=head1 NAME

iwannaparticle - reconstruction tool 

=head1 DESCRIPTION

contains subroutines and functions for reconstructing
particles from electron microscopic images, 
supported symmetries : c1, c2, c6, c7, d2, d3, d7

=SYNOPSIS

rock on

=head1 AUTHOR

This perl module was written by Dominika Elmlund -09

=cut

use warnings;
use Exporter;
use lib   '<SIMPLEPATH>/lib';
use parse_aligninfo;
use spider;
use eulers;
my $spider_binary  =     get_spider;
my $proExt      =     "xxx";
@ISA = ('Exporter');
@EXPORT = qw (reconstruct_bp3f reconstruct_bpcg reconstruct_bp32f reconstruct_bpcg_eo ); 

   #### data parser #### 
sub parse_data {                        
  my $algndoc       = shift;
  my $nr_of_states  = shift;
  my $sym           = shift;
  my $free_corr     = shift;
  my $modelq        = shift;
  my $hres          = shift;
  my $scaling       = shift;
  my $nr_of_ptcls   = shift;
  my $eo            = shift;
  # input parameters check 
  (`grep AWKSOME $algndoc | wc -l` != $nr_of_ptcls) && die "Number of entries in aligndoc not equal to nr of ptcls, check aligndoc or number of ptcls!\n";
  (($nr_of_states !~ /^\d+$/) || ($nr_of_states =~ /0/))  && die "Not a valid number of states!\n";
  ($sym !~ /[c1|c2|c3|c6|c7|d2|d3|d7|oct]/) && die "Not a valid symmetry group\n";
  ($scaling !~ /^(\d+)?(\.\d*)?([eE]-?\d+)?$/) && die "Not a valid scaling factor\n";
  ($eo !~ /y|n/) && die "Not a valid shuffling parameter, give 'y' or 'n'\n";
  # create database
  my $nr = parse_aligndata($algndoc);
  # shuffle if eo
  ($eo eq 'y') && (shuffle_db);
  # fix translations
  ($scaling != 1) && (scale_translations($scaling));
  # create symeulers
  my $nr_of_symops;
  my $expeulers = "eulers.dat";
  my $symeulers   = "$sym"."symeulers.dat"; 
  ($sym eq 'c1')  && ($symeulers = 0);
  ($sym ne 'c1')  && (entries_to_euldoc("eulers.dat", "NORM", "0", "EUL1", "EUL2", "EUL3")); 
  ($sym eq 'c1')  && ($nr_of_symops = 1);
  ($sym eq 'c2')  && ($nr_of_symops = 2)  && (c2_symapt($expeulers));
  ($sym eq 'c3')  && ($nr_of_symops = 3)  && (c3_symapt($expeulers));
  ($sym eq 'c6')  && ($nr_of_symops = 6)  && (c6_symapt($expeulers));
  ($sym eq 'c7')  && ($nr_of_symops = 7)  && (c7_symapt($expeulers));
  ($sym eq 'd2')  && ($nr_of_symops = 4)  && (d2_symapt($expeulers));
  ($sym eq 'd3')  && ($nr_of_symops = 6)  && (d3_symapt($expeulers));
  ($sym eq 'd7')  && ($nr_of_symops = 14) && (d7_symapt($expeulers));
  ($sym eq 'oct') && ($nr_of_symops = 24) && (oct_symapt($expeulers)); 
  # nr of objects in database
  ($sym eq 'c1') && ($max = $nr+1);
  ($sym ne 'c1') && ($max=($nr+1)*$nr_of_symops); 
  # info storage
  my @max_and_members_in_states;
  my @max_and_members_in_states_even;
  my @max_and_members_in_states_odd;
  # nr of objects in database stored at the 0th position
  ($eo eq 'n') && (push(@max_and_members_in_states, $max)); 
  ($eo eq 'y') && (push(@max_and_members_in_states_even, $max)) && (push(@max_and_members_in_states_odd, $max));
  # create spidocs
  if ($eo eq 'n') {
    foreach my $i (1 .. $nr_of_states ){
          entries_to_spidoc("fixed_eulers_state$i.spi", "STATE", $i, $free_corr, $modelq, $hres, $nr_of_symops, $symeulers, "EUL3", "EUL2", "EUL1");
          entries_to_spidoc("fixed_trs_state$i.spi", "STATE", $i, $free_corr, $modelq, $hres, $nr_of_symops, $symeulers, "X", "Y");
          entries_to_spidoc( "seldoc_state$i.spi", "STATE", $i, $free_corr, $modelq, $hres, $nr_of_symops, $symeulers, "PTCLNR");
          $members_in_state[$i] = `cat fixed_trs_state$i.spi | wc -l`;  
          chomp($members_in_state[$i]); 
          push(@max_and_members_in_states, $members_in_state[$i]);
    }
  } elsif ($eo eq 'y') {
    foreach my $i (1 .. $nr_of_states ){
          entries_to_spidoc("fixed_eulers_state$i.spi", "EO", $i, $free_corr, $modelq, $hres, $nr_of_symops, $symeulers, "EUL3", "EUL2", "EUL1");
          entries_to_spidoc("fixed_trs_state$i.spi", "EO", $i, $free_corr, $modelq, $hres, $nr_of_symops, $symeulers, "X", "Y");
          entries_to_spidoc("seldoc_state$i.spi", "EO", $i, $free_corr, $modelq, $hres, $nr_of_symops, $symeulers, "PTCLNR");
          $members_in_state_even[$i] = `cat fixed_trs_state$i\_even.spi | wc -l`;
          $members_in_state_odd[$i]  = `cat fixed_trs_state$i\_odd.spi | wc -l`;
          chomp($members_in_state_even[$i]);
          chomp($members_in_state_odd[$i]);
          push(@max_and_members_in_states_even, $members_in_state_even[$i]);
          push(@max_and_members_in_states_odd, $members_in_state_odd[$i]);
    }
  } else {
    print " Wrong arguments to parse_data!\n";
  }
  # returnes references to arrays holding max nr of objects in database at the 0th place, followed by nr of ptcls in states/eo
  ($eo eq 'n') && (return \@max_and_members_in_states);   
  ($eo eq 'y') && (return (\@max_and_members_in_states_even, \@max_and_members_in_states_odd));
}

    #### reconstruction subroutines ####

sub reconstruct_bp3f {
    my $volume          = shift;
    my $algnDoc         = shift;
    my $nr_of_states    = shift;
    my $sym             = shift;
    my $free_corr       = shift;
    my $modelq            = shift;
    my $hres              = shift;
    my $scaling         = shift;
    my $stack           = shift;
    my $nr_of_ptcls     = shift;
    my $exec            = shift;
    my $nnodes          = shift;
    print "volume: $volume\n";
    print "algnDoc: $algnDoc\n";
    print "nr_of_states : $nr_of_states\n";
    print "sym: $sym\n";
    print "free_corr: $free_corr\n";
    print "modelq: $modelq\n";
    print "hres : $hres\n";
    print "scaling: $scaling\n";
    print "stack: $stack\n";
    print "nr_of_ptcls: $nr_of_ptcls\n";
    print "exec: $exec\n";
    print "nnodes: $nnodes\n";
    (`ls $stack` ne "$stack\n") && die "Spider stack does not exist at given location, check path and stack name!\n";
    ($stack !~ /[\w+|d+]\.spi/) && die "Not a valid spider stack name! (Ex. xxxxx.spi)\n";
    ($exec !~ /[l|c]/) && die "Not a valid execution choice!\n";
    ($nr_of_states == 0) && ($nr_of_states = 1);
    $stack =~ s/\.spi//;
    my $max_and_members_in_states = parse_data($algnDoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $nr_of_ptcls, 'n');
    my $max = $$max_and_members_in_states[0];
    my $stars = make_stars(length ($max));
    my $inFile = $stack."@"."{".$stars."x15}";
    foreach my $i (1 .. $nr_of_states ){
        if ( $$max_and_members_in_states[$i] != 0 ) {    
                my $outFile = "nstack".$i."@"."{".$stars."x12}";
                my $inFile2 = "nstack".$i."@".$stars;
                unlink("script$i.$proExt");
                open(MYSCRIPT, "> :encoding(UTF-8)", "script$i.$proExt") or die "Cannot open file: $!\n";
                print MYSCRIPT "do lb1 x12=1,$$max_and_members_in_states[$i]
ud ic,x12,x13,x14
fixed_trs_state$i.spi
ud ic,x12,x15
seldoc_state$i.spi
sh f
$inFile
_1
(x13,x14)
(0)
fi x16,x17
_1
(7,8)
if (x16 .ne. x17) then
ar sca
_1
$outFile
(0,255)
else
cp
_1
$outFile
endif
lb1\n";
if( $nnodes > 1 ){
  print MYSCRIPT "md\nset mp\n$nnodes\n"
}
print MYSCRIPT "bp 3f
$inFile2
1-$$max_and_members_in_states[$i]
fixed_eulers_state$i.spi
*
$volume\_$i
en
";
close(MYSCRIPT);
            ( $exec    eq 'c' ) && ( submit_spider ( "rec$i", "script$i", 20000 ) );
            ( $exec    eq 'l' ) && ( spider ( "script$i" ) );    
        }
    }
    return( "rec" )
}

sub reconstruct_bp32f {
    my $volume           = shift;
    my $algnDoc          = shift;
    my $nr_of_states     = shift;
    my $sym              = shift;
    my $free_corr     = shift;
    my $modelq        = shift;
    my $hres          = shift;
    my $scaling          = shift;
    my $stack            = shift;
    my $nr_of_ptcls      = shift;
    my $exec             = shift;
    my $nnodes           = shift;
    (`ls $stack` ne "$stack\n") && die "Spider stack does not exist at given location, check path and stack name!\n";
    ($stack !~ /[\w+|d+]\.spi/) && die "Not a valid spider stack name! (Ex. xxxxx.spi)\n";
    ($exec !~ /[l|c)]/) && die "Not a valid execution choice!\n";
    ($nr_of_states == 0) && ($nr_of_states = 1);
    $stack =~ s/\.spi//;
    my $max_and_members_in_states = parse_data($algnDoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $nr_of_ptcls, 'n');
    my $max = $$max_and_members_in_states[0];
    my $stars = make_stars(length ($max));
    my $inFile = $stack."@"."{".$stars."x15}";
    foreach my $i (1 .. $nr_of_states ){
        if ( $$max_and_members_in_states[$i] != 0 ) {    
                   my $outFile = "nstack".$i."@"."{".$stars."x12}";
                my $inFile2 = "nstack".$i."@".$stars;
                unlink("script$i.$proExt");
                open(MYSCRIPT, "> :encoding(UTF-8)", "script$i.$proExt") or die "Cannot open file: $!\n";
                print MYSCRIPT "do lb1 x12=1,$$max_and_members_in_states[$i]
ud ic,x12,x13,x14
fixed_trs_state$i.spi
ud ic,x12,x15
seldoc_state$i.spi
sh f
$inFile
_1
(x13,x14)
(0)
fi x16,x17
_1
(7,8)
if (x16 .ne. x17) then
ar sca
_1
$outFile
(0,255)
else
cp
_1
$outFile
endif
lb1\n";
if( $nnodes > 1 ){
  print MYSCRIPT "md\nset mp\n$nnodes\n"
}
print MYSCRIPT "bp 32f
$inFile2
1-$$max_and_members_in_states[$i]
fixed_eulers_state$i.spi
*
$volume\_$i
$volume\_even_$i
$volume\_odd_$i
en
";
            close(MYSCRIPT);
            ( $exec    eq 'c' ) && ( submit_spider ( "rec$i", "script$i", 20000 ) );
            ( $exec    eq 'l' ) && ( spider ( "script$i" ) );            
        }
    }
    return( "rec" )    
}


sub reconstruct_bpcg {
    my $volume          = shift;
    my $algnDoc         = shift;
    my $nr_of_states    = shift;
    my $sym             = shift;
    my $free_corr     = shift;
    my $modelq        = shift;
    my $hres          = shift;
    my $scaling         = shift;
    my $stack           = shift;    
    my $nr_of_ptcls     = shift;
    my $exec            = shift;
    my $mask            = shift;
    my $nnodes          = shift;
    (`ls $stack` ne "$stack\n") && die "Spider stack does not exist at given location, check path and stack name!\n";
    ($stack !~ /[\w+|d+]\.spi/) && die "Not a valid spider stack name! (Ex. xxxxx.spi)\n";
    ($exec !~ /[l|c]/) && die "Not a valid execution choice!\n";
    ($nr_of_states == 0) && ($nr_of_states = 1);
    $stack =~ s/\.spi//;
    my $max_and_members_in_states = parse_data($algnDoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $nr_of_ptcls, 'n');
    my $max = $$max_and_members_in_states[0];
    my $stars = make_stars(length ($max));
    my $inFile = $stack."@"."{".$stars."x15}";
    foreach my $i (1 .. $nr_of_states ){
        if ( $$max_and_members_in_states[$i] != 0 ) {        
                   my $outFile = "nstack".$i."@"."{".$stars."x12}";
                my $inFile2 = "nstack".$i."@".$stars;
                unlink("script$i.$proExt");
                open(MYSCRIPT, "> :encoding(UTF-8)", "script$i.$proExt") or die "Cannot open file: $!\n";
                print MYSCRIPT "do lb1 x12=1,$$max_and_members_in_states[$i]
ud ic,x12,x13,x14
fixed_trs_state$i.spi
ud ic,x12,x15
seldoc_state$i.spi
sh f
$inFile
_1
(x13,x14)
(0)
fi x16,x17
_1
(7,8)
if (x16 .ne. x17) then
ar sca
_1
$outFile
(0,255)
else
cp
_1
$outFile
endif
lb1\n";
if( $nnodes > 1 ){
  print MYSCRIPT "md\nset mp\n$nnodes\n"
}
print MYSCRIPT "bp cg
$inFile2
1-$$max_and_members_in_states[$i]
$mask
fixed_eulers_state$i.spi
n
$volume\_$i
0.000005,0
50,1
2000.
en
";
            close(MYSCRIPT);
            ( $exec    eq 'c' ) && ( submit_spider ( "rec$i", "script$i", 100000 ) );
            ( $exec    eq 'l' ) && ( spider ( "script$i" ) );    
        }
    }
    return( "rec" )
}


sub reconstruct_bpcg_eo {
    my $volume          = shift;
    my $algnDoc         = shift;
    my $nr_of_states    = shift;
    my $sym             = shift;
    my $free_corr     = shift;
    my $modelq        = shift;
    my $hres          = shift;
    my $scaling         = shift;
    my $stack           = shift;    
    my $nr_of_ptcls     = shift;
    my $exec            = shift;
    my $mask            = shift;
    my $nnodes          = shift;
    my @eos = qw/even odd/;
    (`ls $stack` ne "$stack\n") && die "Spider stack does not exist at given location, check path and stack name!\n";
    ($stack !~ /[\w+|d+]\.spi/) && die "Not a valid spider stack name! (Ex. xxxxx.spi)\n";
    ($exec !~ /[l|c]/) && die "Not a valid execution choice!\n";
    ($nr_of_states == 0) && ($nr_of_states = 1);
    $stack =~ s/\.spi//;
    (my $max_and_members_in_states_even, my $max_and_members_in_states_odd) = parse_data($algnDoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, $nr_of_ptcls, 'y');
    my $max = $$max_and_members_in_states_even[0];
    my $stars = make_stars(length ($max));
    my $inFile = $stack."@"."{".$stars."x15}";
    reconstruct_bpcg ($volume, $algnDoc, $nr_of_states, $sym, $free_corr, $modelq, $hres, $scaling, "$stack.spi", $nr_of_ptcls, $exec, $mask);
    foreach my $i (1 .. $nr_of_states ){
        if ( $$max_and_members_in_states_even[$i] != 0 ) {
            foreach my $part ( @eos ) {
                my $outFile = "nstack".$i.$part."@"."{".$stars."x12}";
                my $inFile2 = "nstack".$i.$part."@".$stars;
                my $max;
                ($part eq 'even') && ($max = $$max_and_members_in_states_even[$i]);
                ($part eq 'odd') && ($max = $$max_and_members_in_states_odd[$i]);
                unlink("script$i.$part.$proExt");
                open(MYSCRIPT, "> :encoding(UTF-8)", "script_$part\_$i.$proExt") or die "Cannot open file: $!\n";
                print MYSCRIPT "do lb1 x12=1,$max
ud ic,x12,x13,x14
fixed_trs_state$i\_$part.spi
ud ic,x12,x15
seldoc_state$i\_$part.spi
sh f
$inFile
_1
(x13,x14)
(0)
fi x16,x17
_1
(7,8)
if (x16 .ne. x17) then
ar sca
_1
$outFile
(0,255)
else
cp
_1
$outFile
endif
lb1\n";
if( $nnodes > 1 ){
  print MYSCRIPT "md\nset mp\n$nnodes\n"
}
print MYSCRIPT "bp cg
$inFile2
1-$max
$mask
fixed_eulers_state$i\_$part.spi
n
$volume\_$i\_$part
0.000005,0
50,1
2000.
en
";
                close(MYSCRIPT);
                ( $exec    eq 'c' ) && ( $job_name = submit_spider ( "rec_$part\_$i", "script_$part\_$i", 100000 ) );    
                ( $exec    eq 'l' ) && ( spider ("script_$part\_$i" ) );    
            }
        }
    }
    return( "rec" )
}


sub make_stars{
        my $noStars = shift;
        my $stars = "";
        my $star = "*";

        for (my $i = 0; $i < $noStars; $i++) {
                $stars .= $star;
                }
        return $stars;
}
1;
