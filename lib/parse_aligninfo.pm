package parse_aligninfo;

=head1 NAME

parse_aligninfo 

=head1 DESCRIPTION

conatines various useful and useless
document parsing and handling subroutines

=SYNOPSIS

rock on

=head1 AUTHOR

This perl module was written by Dominika & Hans Elmlund -09

=cut


use Exporter;
use List::Util 'shuffle';
use warnings;
@ISA = ('Exporter');
@EXPORT = qw(    parse_aligndata shuffle_db parse_filenames file_to_arr arr_to_file split_line entries_to_spidoc entries_to_euldoc 
        create_db parse_eultable parse_states get_nr_of_members_in_state double_translations scale_translations    round_translations  );

my @db;


my %self = (
    FILENAME    => undef,
    PTCLNR      => undef,
    EUL1        => undef,
    EUL2        => undef,
    EUL3        => undef,
    X           => undef,
    Y           => undef,
    CORR        => 99.,
    MODELQ      => 99.,
    ALIGNQ      => undef,
    HIGHRES     => 0.,
    STATE       => undef,
);

sub parse_aligndata {
    my $aligndata = shift;
    my $last_db_index = 0;
    open( ALGN, "<$aligndata" ) or die "$aligndata: $!\n";
    while( <ALGN> ){
        chomp( $_ );
        # [$last_db_index] goes from 0 - nrptcl-1 
        my @oneline = split_line( 'AWKSOME', $_ ); 
        if( $oneline[0] ne 'NODATA' ) {    
            $db = {%self}; # putting a copy of the %self hash in each $counter entry of the @db array
            $db[$last_db_index]->{PTCLNR}   = $last_db_index+1;
            $db[$last_db_index]->{EUL1}     = $oneline[0];
            $db[$last_db_index]->{EUL2}     = $oneline[1];
            $db[$last_db_index]->{EUL3}     = $oneline[2];
            $db[$last_db_index]->{X}        = idef($oneline[3]);
            $db[$last_db_index]->{Y}        = idef($oneline[4]);
            $db[$last_db_index]->{CORR}     = idef($oneline[6]);
            $db[$last_db_index]->{FREE_CORR}= idef($oneline[8]);
            $db[$last_db_index]->{MODELQ}   = idef($oneline[10]);
            $db[$last_db_index]->{ALIGNQ}   = idef($oneline[12]);
            $db[$last_db_index]->{HIGHRES}  = idef($oneline[14]);
            $db[$last_db_index]->{STATE}    = idef($oneline[16]);
            if($db[$last_db_index]->{STATE} == 0){
                $db[$last_db_index]->{STATE} = 1
            }
            if($db[$last_db_index]->{FREE_CORR} == -1.){
                $db[$last_db_index]->{FREE_CORR} = 1.
            }
            $last_db_index++; # gives indexing of the db from 0 to $#db
        }
    }
    close( ALGN );
    return $last_db_index-1;
}

sub idef{
    my $var = shift;
    if( defined($var) ){
        return $var
    }else{
        return 0
    }
} 

sub create_db {
    my $nr_of_entries = shift;
    my $last_db_index = 0;
    foreach my $i ( 1 .. $nr_of_entries ) {
        $db[$last_db_index] = {%self};
        $db[$last_db_index]->{PTCLNR}     = $last_db_index+1;
        $last_db_index++; # gives indexing of the db from 0 to $#db
    }
    return $last_db_index-1;
}

sub shuffle_db {     # randomizes the @db - for e/o test 
    @db = shuffle(@db);
    return \@db;
}

sub parse_filenames {
    my $filetable = shift;
    my $counter_files = 0;
    open( FILES, "<$filetable" ) or die "$!\n";
    while( <FILES> ){
        chomp( $_ );
        $db[$counter_files]->{FILENAME} = $_;
        $counter_files++;
    }
    close( FILES );
    return $counter_files-1;
}

sub round_translations
{
    foreach (@db) {
        $_->{X} = int ( $_->{X} + .5 * ($_->{X} <=> 0) );
        $_->{Y} = int ( $_->{Y} + .5 * ($_->{Y} <=> 0) );
    }
}

sub double_translations {
    foreach (@db) {
        $_->{X}=$_->{X}*2.;
        $_->{Y}=$_->{Y}*2.;
    }

}

sub scale_translations {
    my$scale = shift;
    foreach (@db) {
        $_->{X}=$_->{X}*$scale;
        $_->{Y}=$_->{Y}*$scale;
    }

}

sub parse_states {
    my $states = shift;
    my $counter_lines = 0;
    open( STATES, "<$states" ) or die "$!\n";
    while( <STATES> ){    
        chomp( $_ );
        $db[$counter_lines]->{STATE} = $_;
        $counter_lines++;
    }
    close( FILES );
    return $counter_lines-1;
}

sub parse_eultable {
    my $eultable = shift;
    my $counter_eulers = 0;
    open( EULERS, "<$eultable" ) or die "$!\n";
    while( <EULERS> ){
        chomp( $_ );
        my @oneline = split_line( 'EMPTY', $_ );
        if( $oneline[0] ne 'NODATA' ) {    
            $db[$counter_eulers]->{EUL1}     = $oneline[0];
            $db[$counter_eulers]->{EUL2}     = $oneline[1];
            $db[$counter_eulers]->{EUL3}     = $oneline[2];
            $counter_eulers++;
        }
    }
    return $counter_eulers-1;
}

sub file_to_arr {
    my $file = shift;
    open(FOO, "<$file") or die "$!\n";
    my @filearr = <FOO>;
    close(FOO);
    chomp(@filearr);
    return(@filearr);
}

sub arr_to_file {
    my $arr_ref = shift;
    my $fname   = shift;
    open(FOO, ">$fname") or die "$!\n";
    foreach (@$arr_ref) {
        print FOO "$_\n";
    }
    close(FOO);
    return("$fname");
}

sub split_line {
    my $pattern = shift;
    my $line    = shift;
    if( $pattern eq "EMPTY" ) {
        my @splitarr = split(/\s+/, $line);
        if( $splitarr[0] =~ /\d+.+/ ){
        } else {
            shift @splitarr;
        }
        return @splitarr;
    
    } elsif( $line =~ /$pattern/ ){
        my @splitarr = split(/\s+/, $line);
        if( $splitarr[0] =~ /\d+.+/ ){
        } else {
            shift @splitarr;
        }
        return @splitarr;
    } else {
        return 'NODATA';
    }
}

sub entries_to_euldoc {
    my $file    = shift;
    my $mode    = shift;
    my $state     = shift;
    my @entries = @_;    
    open( OUTFILE, ">$file" ) or die "$!\n";
    foreach my $i ( 0 .. $#db ) {
        if ($mode eq "NORM") {
            foreach my $j ( 0 .. $#entries ) {
                print OUTFILE "$db[$i]->{$entries[$j]}\t";
            }
            print OUTFILE "\n";
        } elsif ($mode eq "ROUND") {
            foreach my $j ( 0 .. $#entries ) {
                printf OUTFILE "%3.0f\t", $db[$i]->{$entries[$j]};
            }
            print OUTFILE "\n";
        } elsif ($mode eq "STATE") {
            if( $db[$i]->{STATE} == $state ){
                $counter++;  
                foreach my $j ( 0 .. $#entries ) {
                    print OUTFILE "$db[$i]->{$entries[$j]}\t";
                }
                print OUTFILE "\n";
            }
        } else {
            print OUTFILE "ERROR, Not a valid mode for entries to spidoc!\n";
            die "Not a valid mode for entries to spidoc!\n";
        }
    }
    close (OUTFILE);
}

# NOTE that if you want to use the 'EO' mode you should shuffle the @db before using entries_to_spidoc;
sub entries_to_spidoc {
    my $file      = shift;
    my $mode      = shift;
    my $state     = shift;
    my $free_corr = shift;
    my $modelq    = shift;
    my $hres      = shift;
    my $symops    = shift;
    my $symeulers = shift;
    my @entries   = @_;
    my @eulers;
    my $nr_of_entries = @entries;
    my $counter;
    my $n=0;
    my $cnt1=0;
    my $cnt2=0;
    my $eotest;
    ($state == 0) && ($state = 1);
    ($symops == 0) && ($symops = 1);
    ($symops != 1) && (@eulers = file_to_arr($symeulers));
    if ($mode eq 'EO') {
        $file =~ /(.+)\.spi/;
        my $eofile = $1;
        open ( OUTFILE_EVEN, ">$eofile\_even.spi" ) or die "$!\n";     
        open ( OUTFILE_ODD,  ">$eofile\_odd.spi" ) or die "$!\n";     
    } elsif ($mode eq 'STATE') {
        open( OUTFILE, ">$file" ) or die "$!\n";
    } elsif ($mode eq 'NORM') {
        open( OUTFILE, ">$file" ) or die "$!\n";
    } else  {
        die "Not a valid mode for entries to spidoc!\n";
    }
    if ($symops != 1) {
        ($mode eq "EO") && ($counter = 1) && ($eotest = 1);
        foreach my $i ( 0 .. $#db ) {
            if( $db[$i]->{HIGHRES} <= $hres ){
                if( $db[$i]->{FREE_CORR} >= $free_corr ){
                    if( $db[$i]->{MODELQ} >= $modelq ){
                        foreach (1 .. $symops ) {            
                            my @triplet = split(/\s+/,$eulers[$n]);
                            $n++;            
                            $db[$i]->{EUL1}     = $triplet[0];
                            $db[$i]->{EUL2}     = $triplet[1];
                            $db[$i]->{EUL3}     = $triplet[2];
                            if ($mode eq "STATE") {
                                if( $db[$i]->{STATE} == $state ){
                                    $counter++;          
                                    print OUTFILE "$counter\t$nr_of_entries\t";
                                    foreach my $j ( 0 .. $#entries ) {
                                        print OUTFILE "$db[$i]->{$entries[$j]}\t";
                                    }
                                    print OUTFILE "\n";
                                }    
                            } elsif ($mode eq "EO") {
                                if( $db[$i]->{STATE} == $state ){                            
                                    if ($eotest % 2 != 0) {
                                        $cnt1++;
                                        print OUTFILE_ODD  "$cnt1\t$nr_of_entries\t";
                                        foreach my $j ( 0 .. $#entries ) {
                                            print OUTFILE_ODD  "$db[$i]->{$entries[$j]}\t";
                                        }
                                        print OUTFILE_ODD "\n";
                                    } else { 
                                        $cnt2++;
                                        print OUTFILE_EVEN "$cnt2\t$nr_of_entries\t";
                                        foreach my $j ( 0 .. $#entries ) {
                                            print OUTFILE_EVEN "$db[$i]->{$entries[$j]}\t";
                                        }
                                        print OUTFILE_EVEN  "\n";
                                    }
                                }
                            } elsif ($mode eq "NORM") {
                                $counter++;          
                                print OUTFILE "$counter\t$nr_of_entries\t";
                                foreach my $j ( 0 .. $#entries ) {
                                    print OUTFILE "$db[$i]->{$entries[$j]}\t";
                                }
                                print OUTFILE "\n";    
                            } else {
                                print OUTFILE "ERROR, Not a valid mode for entries to spidoc!\n";
                                print OUTFILE_EVEN "ERROR, Not a valid mode for entries to spidoc!\n";
                                print OUTFILE_ODD "ERROR, Not a valid mode for entries to spidoc!\n";
                                die "Not a valid mode for entries to spidoc!\n";
                            }
                        }
                
                    }
                }
            } 
        ($mode eq "EO") && ($counter += $symops) && ($eotest++) ;
        }
    } elsif ($symops == 1) {
        foreach my $i ( 0 .. $#db ) {    
            if( $db[$i]->{HIGHRES} <= $hres ){
                if( $db[$i]->{FREE_CORR} >= $free_corr ){ 
                    if( $db[$i]->{MODELQ} >= $modelq ){
                        if ($mode eq "STATE") {
                            if( $db[$i]->{STATE} == $state ){
                                $counter++;          
                                print OUTFILE "$counter\t$nr_of_entries\t";
                                foreach my $j ( 0 .. $#entries ) {
                                    print OUTFILE "$db[$i]->{$entries[$j]}\t";
                                }
                                print OUTFILE "\n";
                            }
                        } elsif ($mode eq "EO") {
                            if( $db[$i]->{STATE} == $state ){
                                $counter++;
                                if ($counter % 2 != 0) {
                                    $cnt1++;
                                    print OUTFILE_ODD  "$cnt1\t$nr_of_entries\t";
                                    foreach my $j ( 0 .. $#entries ) {
                                        print OUTFILE_ODD  "$db[$i]->{$entries[$j]}\t";
                                    }
                                    print OUTFILE_ODD "\n";
                                } else { 
                                    $cnt2++;
                                    print OUTFILE_EVEN "$cnt2\t$nr_of_entries\t";
                                    foreach my $j ( 0 .. $#entries ) {
                                        print OUTFILE_EVEN "$db[$i]->{$entries[$j]}\t";
                                    }
                                    print OUTFILE_EVEN  "\n";
                                }
                            }
                        } elsif ($mode eq "NORM") {
                            $counter++;          
                            print OUTFILE "$counter\t$nr_of_entries\t";
                            foreach my $j ( 0 .. $#entries ) {
                                print OUTFILE "$db[$i]->{$entries[$j]}\t";
                            }
                            print OUTFILE "\n";    
                        } else {
                            print OUTFILE "ERROR, Not a valid mode for entries to spidoc!\n";
                            print OUTFILE_EVEN "ERROR, Not a valid mode for entries to spidoc!\n";
                            print OUTFILE_ODD "ERROR, Not a valid mode for entries to spidoc!\n";
                            die "Not a valid mode for entries to spidoc!\n";
                        }
                    }
                }
            }
        }
    }
    close(OUTFILE);
    close(OUTFILE_EVEN);
    close(OUTFILE_ODD);
}

sub get_nr_of_members_in_state {
    my $state     = shift;    
    my $counter;
    foreach my $i ( 0 .. $#db ) {
        if( $db[$i]->{STATE} eq $state ){
            $counter++;
        }
    }
    return $counter;
}
1;
