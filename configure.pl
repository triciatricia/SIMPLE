#!/usr/bin/perl
use warnings;
use strict;
use Cwd;
use Tie::File;

print "\nInstallation on lunarc/hopper/local ?\n\n";
my $system = <STDIN>;
chomp( $system );
$system =~ tr/a-z/A-Z/;
my $pwd = &Cwd::cwd();
my @all = glob("./apps/*.pl ./lib/*.pm source_bash source_tcsh");
chomp(@all);
foreach ( @all ) {
	tie my @array, 'Tie::File', $_ or die "Can't open $_: $!";
	foreach (@array) {
            s/<PERLPATH>/\/usr\/bin\/perl/;
            s/<SIMPLEPATH>/$pwd/;
            s/<SYSTEM>/$system/;
	}
	untie @array;
}
unlink glob( "./apps/*~" );
unlink glob( "./lib/*~" );
