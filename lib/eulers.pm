package eulers;

=head1 NAME

eulers

=head1 DESCRIPTION

eulers and vectors handling functions 

=SYNOPSIS

rock on

=head1 AUTHOR

This perl module was written by Dominika Elmlund & Hans Elmlund -10

=cut

##############################################################################################################
##############################################################################################################
#
#    EULERS CONVENTION:
#    eul1 - psi    - rotation around Z on the latitude defined by theta (direction of tilting), 0 - 360
#    eul2 - theta    - roatation around Y, angle between the north and south pole, 0 - 180
#    eul3 - phi    - in-plane rotation around Z´, 0 - 360
#
#    ROTATION MATRICES:
#    |  cos(eul3) sin(eul3) 0 | |  cos(eul2) 0 sin(eul2) | |  cos(eul1) sin(eul1) 0 |
#    | -sin(eul3) cos(eul3) 0 | |      0     1     0     | | -sin(eul1) cos(eul1) 0 |    
#    |      0         0     1 | | -sin(eul2) 0 cos(eul2) | |      0         0     1 |
#
##############################################################################################################
##############################################################################################################

use warnings;
use Exporter;
use lib   '<SIMPLEPATH>/lib';
use parse_aligninfo;
use Math::Trig;
my $m2euler_binary =     '<SIMPLEPATH>/bin/m2euler';
use constant PI => (4.* atan2(1.,1.));
@ISA = ('Exporter');
@EXPORT = qw (  spiral_eulers from_eul_get_mat from_eul_get_vec get_dist get_dist_ang 
                c2_symapt c3_symapt c6_symapt c7_symapt d2_symapt d3_symapt d7_symapt oct_symapt );

sub mmult {
    my($m1,$m2) = @_;
    my($m1rows,$m1cols) = matdim($m1);
    my($m2rows,$m2cols) = matdim($m2);
    unless($m1cols == $m2rows) { # raise exception
        die "IndexError: matrices don't match!\n";
    }
    my$result = [];
    my($i,$j,$k);
    for $i (range($m1rows)) {
        for $j (range($m2cols)) {
            for $k (range($m1cols)) {
                $result->[$i][$j] += $m1->[$i][$k] * $m2->[$k][$j]   
            }   
        }   
    }
    return $result;
}

sub range { 0 .. ($_[0]-1) }

sub veclen {
    my$ary_ref = $_[0];
    my$type    = ref $ary_ref;
    if($type ne "ARRAY") { die "$type is bad array ref for $ary_ref\n" }
    return scalar(@$ary_ref)
}

sub matdim {
    my$matrix = $_[0];
    my$rows = veclen($matrix);
    my$cols = veclen($matrix->[0]);
    return ($rows,$cols);   
}

sub spiral_eulers
{
  my $neulers    = shift;
  my $psi_lim    = shift;
  my $theta_lim  = shift;
  my $fname      = shift;
  $neulers++;
  open( F, ">$fname" ) or die "Cannot open file $fname: $!\n";
  foreach my $i (1 .. $neulers-1) {
    my $acos_arg = ($i/($neulers-1.))*2.-1.;
    my $e1 = $i*(($psi_lim*log($neulers))/$neulers);
    if( $e1 > $psi_lim ){
      my $turns = int($e1/$psi_lim);
      $e1 = $e1-$turns*$psi_lim;
    }
    my $e2 = $theta_lim/PI * acos($acos_arg);
    my $e3 = 0.;
    $e1 = sprintf "%.3f", $e1;
    $e2 = sprintf "%.3f", $e2;
    $e3 = sprintf "%.3f", $e3;
    printf F "%8s%9s%8s\n", $e1, $e2, $e3;
  }
  close( F );
  return( "$fname" );
}

# sub deg2rad 
# {
#     my $degrees = shift;
#     return ( $degrees / 180 ) * PI;
# }
# 
# sub rad2deg
# {
#     my $radians = shift;
#     return ( $radians / PI ) * 180;
# }

sub from_eul_get_mat 
{
    my ( $eul1, $eul2, $eul3 ) = @_;
    
    $eul1 = deg2rad ($eul1);
    $eul2 = deg2rad ($eul2);
    $eul3 = deg2rad ($eul3);
    
    my $transf_mat = [
    [ cos($eul3) * cos($eul2) * cos($eul1) - sin($eul3) * sin($eul1),  sin($eul3) * cos($eul2) * cos($eul1) + cos($eul3) * sin($eul1), -sin($eul2) * cos($eul1)],
    [-cos($eul3) * cos($eul2) * sin($eul1) - sin($eul3) * cos($eul1), -sin($eul3) * cos($eul2) * sin($eul1) + cos($eul3) * cos($eul1),  sin($eul2) * sin($eul1)],
    [ cos($eul3) * sin($eul2), sin($eul3) * sin($eul2), cos($eul2)]
    ];
    
    return $transf_mat;
}

sub from_eul_get_vec
{
    my ( $eul1, $eul2, $eul3 ) = @_;
    
    $eul1 = deg2rad ($eul1);
    $eul2 = deg2rad ($eul2);
    $eul3 = deg2rad ($eul3);
    
    my $transf_mat = [
    [ cos($eul3) * cos($eul2) * cos($eul1) - sin($eul3) * sin($eul1),  sin($eul3) * cos($eul2) * cos($eul1) + cos($eul3) * sin($eul1), -sin($eul2) * cos($eul1)],
    [-cos($eul3) * cos($eul2) * sin($eul1) - sin($eul3) * cos($eul1), -sin($eul3) * cos($eul2) * sin($eul1) + cos($eul3) * cos($eul1),  sin($eul2) * sin($eul1)],
    [ cos($eul3) * sin($eul2), sin($eul3) * sin($eul2), cos($eul2)]
    ];
    my $z_vec = [
        [0],
        [0],
        [1]
    ];
    
    return (mmult($transf_mat,$z_vec));
}

sub get_dist
{
    my ( $vec1, $vec2 ) = @_;
    my $sc_prod = sprintf "%.6f", ( $vec1 * $vec2 )->sum();
    return sprintf "%.5f", acos ( $sc_prod ); 
}

sub get_dist_ang
{
    my ( $vec1, $vec2 ) = @_;
    my $sc_prod = sprintf "%.6f", ( $vec1 * $vec2 )->sum();
    return rad2deg ( sprintf "%.5f", acos ( $sc_prod ) ); 
}

    ## SYMMETRY OPERATIONS ##
    ## apt - Association for the Prevention of Torture ##

sub c2_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "c2angmat.dat";
    # C2-symmetry
    my $unitary = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $c2_1 = [
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000, -1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    
    my @c2apt;
    $c2apt[0] = 2;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $c2apt[0] * @array;
    for my $i (0 .. $#array) 
    {
        my @eulers = split /\s+/, $array[$i]; 
        my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);     
        $c2apt[1] = mmult($unitary,$rotmat);
        $c2apt[2] = mmult($c2_1,$rotmat);
        for my $i (1 .. $c2apt[0]) 
        {    
            my @row;
            $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $c2apt[$i]->[0][0], $c2apt[$i]->[0][1], $c2apt[$i]->[0][2];
            $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $c2apt[$i]->[1][0], $c2apt[$i]->[1][1], $c2apt[$i]->[1][2];
            $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $c2apt[$i]->[2][0], $c2apt[$i]->[2][1], $c2apt[$i]->[2][2];
            for my $i (0 .. 2)
            {
                $row[$i] =~ s/\s-/-/g;
                print ANGMAT $row[$i];
            }
        }
    }
    close(ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > c2symeulers.dat"); 
}

sub c3_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "c3angmat.dat";
    # C3-symmetry
    my $unitary = from_eul_get_mat (0, 0, 0);
    my $c3_1    = from_eul_get_mat (0, 0, 120);
    my $c3_2    = from_eul_get_mat (0, 0, 240);
    my @c3apt;
    $c3apt[0] = 3;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $c3apt[0] * @array;
    for my $i (0 .. $#array)
    {
        my @eulers = split /\s+/, $array[$i]; 
        my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);         
        $c3apt[1] = mmult($unitary,$rotmat);
        $c3apt[2] = mmult($c3_1,$rotmat);
        $c3apt[3] = mmult($c3_2,$rotmat);
        for my $i (1 .. $c3apt[0])
        {    
            my @row;
            $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $c3apt[$i]->[0][0], $c3apt[$i]->[0][1], $c3apt[$i]->[0][2];
            $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $c3apt[$i]->[1][0], $c3apt[$i]->[1][1], $c3apt[$i]->[1][2];
            $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $c3apt[$i]->[2][0], $c3apt[$i]->[2][1], $c3apt[$i]->[2][2];
            for my $i (0 .. 2)
            {
                $row[$i] =~ s/\s-/-/g;
                print ANGMAT $row[$i];
            }
        }
    }
    close (ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > c3symeulers.dat"); 
}

sub c6_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "c6angmat.dat";
    # C6-symmetry
    my $unitary = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $c6_1 = [
        [ 0.5000, -0.8660,  0.0000],
        [ 0.8660,  0.5000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $c6_2 = [
        [-0.5000, -0.8660,  0.0000],
        [ 0.8660, -0.5000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $c6_3 = [
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000, -1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000],
    ];
    my $c6_4 = [
        [-0.5000,  0.8660,  0.0000],
        [-0.8660, -0.5000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $c6_5 = [
        [ 0.5000,  0.8660,  0.0000],
        [-0.8660,  0.5000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my @c6apt;
    $c6apt[0] = 6;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $c6apt[0] * @array;
    for my $i (0 .. $#array) 
    {
        my @eulers = split /\s+/, $array[$i]; 
        my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);         
        $c6apt[1] = mmult($unitary,$rotmat);
        $c6apt[2] = mmult($c6_1,$rotmat);
        $c6apt[3] = mmult($c6_2,$rotmat);
        $c6apt[4] = mmult($c6_3,$rotmat);
        $c6apt[5] = mmult($c6_4,$rotmat);
        $c6apt[6] = mmult($c6_5,$rotmat);
        for my $i (1 .. $c6apt[0])
        {    
            my @row;
            $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $c6apt[$i]->[0][0], $c6apt[$i]->[0][1], $c6apt[$i]->[0][2];
            $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $c6apt[$i]->[1][0], $c6apt[$i]->[1][1], $c6apt[$i]->[1][2];
            $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $c6apt[$i]->[2][0], $c6apt[$i]->[2][1], $c6apt[$i]->[2][2];
            for my $i (0 .. 2)
            {
                $row[$i] =~ s/\s-/-/g;
                print ANGMAT $row[$i];
            }
        }
    }
    close (ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > c6symeulers.dat"); 
}

sub c7_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "c7angmat.dat";
    # C7-symmetry
    my $unitary = from_eul_get_mat (0, 0, 0);
    my $c7_1  = from_eul_get_mat (0, 0, 51.43);
    my $c7_2  = from_eul_get_mat (0, 0, 102.86);
    my $c7_3  = from_eul_get_mat (0, 0, 154.29);
    my $c7_4  = from_eul_get_mat (0, 0, 205.72);
    my $c7_5  = from_eul_get_mat (0, 0, 257.15);
    my $c7_6  = from_eul_get_mat (0, 0, 308.58);
    my @c7apt;
    $c7apt[0] = 7;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $c7apt[0] * @array;
    for my $i (0 .. $#array) 
    {
      my @eulers = split /\s+/, $array[$i]; 
      my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);     
      $c7apt[1] = mmult($unitary,$rotmat);
      $c7apt[2] = mmult($c7_1,$rotmat);
      $c7apt[3] = mmult($c7_2,$rotmat);
      $c7apt[4] = mmult($c7_3,$rotmat);
      $c7apt[5] = mmult($c7_4,$rotmat);
      $c7apt[6] = mmult($c7_5,$rotmat);
      $c7apt[7] = mmult($c7_6,$rotmat);
      for my $i (1 .. $c7apt[0])
      { 
        my @row;
        $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $c7apt[$i]->[0][0], $c7apt[$i]->[0][1], $c7apt[$i]->[0][2];
        $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $c7apt[$i]->[1][0], $c7apt[$i]->[1][1], $c7apt[$i]->[1][2];
        $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $c7apt[$i]->[2][0], $c7apt[$i]->[2][1], $c7apt[$i]->[2][2];
        for my $i (0 .. 2)
        {
          $row[$i] =~ s/\s-/-/g;
          print ANGMAT $row[$i];
        }
      }
    }
    close (ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > c7symeulers.dat"); 
}

sub d2_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "d2angmat.dat";
    #d3-symmetry
    my $unitary = from_eul_get_mat (0, 0, 0);
    my $d2_1    = from_eul_get_mat (0, 0, 180);
    my $d2_2    = from_eul_get_mat (0, 180, 0);
    my $d2_3    = from_eul_get_mat (0, 180, 180);
    my @d2apt;
    $d2apt[0] = 4;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $d2apt[0] *  @array;
    for my $i (0 .. $#array) 
    {
        my @eulers = split /\s+/, $array[$i]; 
        my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);     
        $d2apt[1] = mmult($unitary,$rotmat);
        $d2apt[2] = mmult($d2_1,$rotmat);
        $d2apt[3] = mmult($d2_2,$rotmat);
        $d2apt[4] = mmult($d2_3,$rotmat);
        for my $i (1 .. $d2apt[0])
        {   
            my @row;
            $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $d2apt[$i]->[0][0], $d2apt[$i]->[0][1], $d2apt[$i]->[0][2];
            $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $d2apt[$i]->[1][0], $d2apt[$i]->[1][1], $d2apt[$i]->[1][2];
            $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $d2apt[$i]->[2][0], $d2apt[$i]->[2][1], $d2apt[$i]->[2][2];
            for my $i (0 .. 2)
            {
                $row[$i] =~ s/\s-/-/g;
                print ANGMAT $row[$i];
            }
        }
    }
    close (ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > d2symeulers.dat"); 
}


sub d3_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "d3angmat.dat";
    #d3-symmetry
    my $unitary = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d3_1 = [
        [ -0.5000,  0.8660,  0.0000],
        [ -0.8660, -0.5000,  0.0000],
        [  0.0000,  0.0000,  1.0000]
    ];
    my $d3_2 = [
        [ -0.5000, -0.8660,  0.0000],
        [  0.8660, -0.5000,  0.0000],
        [  0.0000,  0.0000,  1.0000]
    ];
    my $d3_3 = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000, -1.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000],
    ];
    my $d3_4 = [
        [ -0.5000, -0.8660,  0.0000],
        [ -0.8660, -0.5000,  0.0000],
        [  0.0000,  0.0000, -1.0000]
    ];
    my $d3_5 = [
        [ -0.5000, 0.8660,  0.0000],
        [  0.8660, 0.5000,  0.0000],
        [  0.0000, 0.0000, -1.0000]
    ];
    my @d3apt;
    $d3apt[0] = 6;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $d3apt[0] *  @array;
    for my $i (0 .. $#array) 
    {
        my @eulers = split /\s+/, $array[$i]; 
        my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);        
        $d3apt[1]  = mmult($unitary,$rotmat);
        $d3apt[2]  = mmult($d3_1,$rotmat);
        $d3apt[3]  = mmult($d3_2,$rotmat);
        $d3apt[4]  = mmult($d3_3,$rotmat);
        $d3apt[5]  = mmult($d3_4,$rotmat);
        $d3apt[6]  = mmult($d3_5,$rotmat);
        for my $i (1 .. $d3apt[0])
        {    
            my @row;
            $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $d3apt[$i]->[0][0], $d3apt[$i]->[0][1], $d3apt[$i]->[0][2];
            $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $d3apt[$i]->[1][0], $d3apt[$i]->[1][1], $d3apt[$i]->[1][2];
            $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $d3apt[$i]->[2][0], $d3apt[$i]->[2][1], $d3apt[$i]->[2][2];
            for my $i (0 .. 2)
            {
                $row[$i] =~ s/\s-/-/g;
                print ANGMAT $row[$i];
            }
        }
    }
    close (ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > d3symeulers.dat"); 
}

sub d7_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "d7angmat.dat";
    # D7-symmetry
    my $unitary = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_1 = [
        [ 0.6235, -0.7818,  0.0000],
        [ 0.7818,  0.6235,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_2 = [
        [-0.2225, -0.9749,  0.0000],
        [ 0.9749, -0.2225,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_3 = [
        [-0.9010, -0.4339,  0.0000],
        [ 0.4339, -0.9010,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_4 = [
        [-0.9010,  0.4339,  0.0000],
        [-0.4339, -0.9010,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_5 = [
        [-0.2225,  0.9749,  0.0000],
        [-0.9749, -0.2225,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_6 = [
        [ 0.6235,  0.7818,  0.0000],
        [-0.7818,  0.6235,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_7 = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $d7_8 = [
        [ 0.6235, -0.7818,  0.0000],
        [-0.7818, -0.6235,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $d7_9 = [
        [-0.2225, -0.9749,  0.0000],
        [-0.9749,  0.2225,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $d7_10 = [
        [-0.9010, -0.4339,  0.0000],
        [-0.4339,  0.9010,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $d7_11 = [
        [-0.9010,  0.4339,  0.0000],
        [ 0.4339,  0.9010,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $d7_12 = [
        [-0.2225,  0.9749,  0.0000],
        [ 0.9749,  0.2225,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $d7_13 = [
        [ 0.6235,  0.7818,  0.0000],
        [ 0.7818, -0.6235,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $d7_14 = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000, -1.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];

    my @d7apt;
    $d7apt[0] = 14;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $d7apt[0] * @array;
    for my $i (0 .. $#array) 
    {
        my @eulers = split /\s+/, $array[$i]; 
        my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);         
        $d7apt[1] = mmult($d7_1,$rotmat);
        $d7apt[2] = mmult($d7_2,$rotmat);
        $d7apt[3] = mmult($d7_3,$rotmat);
        $d7apt[4] = mmult($d7_4,$rotmat);
        $d7apt[5] = mmult($d7_5,$rotmat);
        $d7apt[6] = mmult($d7_6,$rotmat);
        $d7apt[7] = mmult($d7_7,$rotmat);
        $d7apt[8] = mmult($d7_8,$rotmat);
        $d7apt[9] = mmult($d7_9,$rotmat);
        $d7apt[10] = mmult($d7_10,$rotmat);
        $d7apt[11] = mmult($d7_11,$rotmat);
        $d7apt[12] = mmult($d7_12,$rotmat);
        $d7apt[13] = mmult($d7_13,$rotmat);
        $d7apt[14] = mmult($d7_14,$rotmat);    
        for my $i (1 .. $d7apt[0])
        {    
            my @row;
            $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $d7apt[$i]->[0][0], $d7apt[$i]->[0][1], $d7apt[$i]->[0][2];
            $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $d7apt[$i]->[1][0], $d7apt[$i]->[1][1], $d7apt[$i]->[1][2];
            $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $d7apt[$i]->[2][0], $d7apt[$i]->[2][1], $d7apt[$i]->[2][2];
            for my $i (0 .. 2)
            {
                $row[$i] =~ s/\s-/-/g;
                print ANGMAT $row[$i];
            }
        }
    }
    close (ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > d7symeulers.dat"); 
}

sub oct_symapt {
    my $eulers_file = shift;
    my @array       = file_to_arr("$eulers_file"); 
    my $fname       = "octangmat.dat";
    # oct-symmetry
    my $unitary = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $oct_1 = [
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000, -1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $oct_2 = [
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $oct_3 = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000, -1.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $oct_4 = [
        [ 0.0000,  0.0000,  1.0000],
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  1.0000,  0.0000]
    ];
    my $oct_5 = [
        [ 0.0000,  0.0000, 1.0000],
        [-1.0000,  0.0000, 0.0000],
        [ 0.0000, -1.0000, 0.0000]
    ];
    my $oct_6 = [
        [ 0.0000, 0.0000, -1.0000],
        [-1.0000, 0.0000,  0.0000],
        [ 0.0000, 1.0000,  0.0000]
    ];
    my $oct_7 = [
        [ 0.0000,  0.0000, -1.0000],
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000, -1.0000,  0.0000]
    ];
    my $oct_8 = [
        [ 0.0000,  1.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000],
        [ 1.0000,  0.0000,  0.0000]
    ];
    my $oct_9 = [
        [ 0.0000, -1.0000, 0.0000],
        [ 0.0000,  0.0000, 1.0000],
        [-1.0000,  0.0000, 0.0000]
    ];
    my $oct_10 = [
        [ 0.0000, 1.0000,  0.0000],
        [ 0.0000, 0.0000, -1.0000],
        [-1.0000, 0.0000,  0.0000]
    ];
    my $oct_11 = [
        [ 0.0000, -1.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000],
        [ 1.0000,  0.0000,  0.0000]
    ];
    my $oct_12 = [
        [ 0.0000,  1.0000,  0.0000],
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $oct_13 = [
        [ 0.0000, -1.0000,  0.0000],
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000]
    ];
    my $oct_14 = [
        [ 0.0000,  1.0000,  0.0000],
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $oct_15 = [
        [ 0.0000, -1.0000,  0.0000],
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000]
    ];
    my $oct_16 = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000],
        [ 0.0000, -1.0000,  0.0000]
    ];
    my $oct_17 = [
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000,  1.0000],
        [ 0.0000,  1.0000,  0.0000]
    ];
    my $oct_18 = [
        [-1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000],
        [ 0.0000, -1.0000,  0.0000]
    ];
    my $oct_19 = [
        [ 1.0000,  0.0000,  0.0000],
        [ 0.0000,  0.0000, -1.0000],
        [ 0.0000,  1.0000,  0.0000]
    ];
    my $oct_20 = [
        [ 0.0000,  0.0000,  1.0000],
        [ 0.0000,  1.0000,  0.0000],
        [-1.0000,  0.0000,  0.0000]
    ];
    my $oct_21 = [
        [ 0.0000,  0.0000,  1.0000],
        [ 0.0000, -1.0000,  0.0000],
        [ 1.0000,  0.0000,  0.0000]
    ];
    my $oct_22 = [
        [ 0.0000,  0.0000, -1.0000],
        [ 0.0000,  1.0000,  0.0000],
        [ 1.0000,  0.0000,  0.0000]
    ];
    my $oct_23 = [
        [ 0.0000,  0.0000, -1.0000],
        [ 0.0000, -1.0000,  0.0000],
        [-1.0000,  0.0000,  0.0000]
    ];
    my @octapt;
    $octapt[0] = 24;
    open (ANGMAT, "> :encoding(UTF-8)", "$fname") or die "Cannot open file $fname for writing: $!\n";
    printf ANGMAT " %i\n", $octapt[0] * @array;
    for my $i (0 .. $#array) 
    {
        my @eulers = split /\s+/, $array[$i]; 
        my $rotmat = from_eul_get_mat ($eulers[0], $eulers[1], $eulers[2]);     
        $octapt[1] = mmult($unitary,$rotmat);
        $octapt[2] = mmult($oct_1,$rotmat);
        $octapt[3] = mmult($oct_2,$rotmat);
        $octapt[4] = mmult($oct_3,$rotmat);
        $octapt[5] = mmult($oct_4,$rotmat);
        $octapt[6] = mmult($oct_5,$rotmat);
        $octapt[7] = mmult($oct_6,$rotmat);
        $octapt[8] = mmult($oct_7,$rotmat);
        $octapt[9] = mmult($oct_8,$rotmat);
        $octapt[10] = mmult($oct_9,$rotmat);
        $octapt[11] = mmult($oct_10,$rotmat);
        $octapt[12] = mmult($oct_11,$rotmat);
        $octapt[13] = mmult($oct_12,$rotmat);
        $octapt[14] = mmult($oct_13,$rotmat);
        $octapt[15] = mmult($oct_14,$rotmat);
        $octapt[16] = mmult($oct_15,$rotmat);
        $octapt[17] = mmult($oct_16,$rotmat);
        $octapt[18] = mmult($oct_17,$rotmat);
        $octapt[19] = mmult($oct_18,$rotmat);
        $octapt[20] = mmult($oct_19,$rotmat);
        $octapt[21] = mmult($oct_20,$rotmat);
        $octapt[22] = mmult($oct_21,$rotmat);
        $octapt[23] = mmult($oct_22,$rotmat);
        $octapt[24] = mmult($oct_23,$rotmat);
        for my $i (1 .. $octapt[0])
        {    
            my @row;
            $row[0] = sprintf " %1.4f %1.4f %1.4f\n", $octapt[$i]->[0][0], $octapt[$i]->[0][1], $octapt[$i]->[0][2];
            $row[1] = sprintf " %1.4f %1.4f %1.4f\n", $octapt[$i]->[1][0], $octapt[$i]->[1][1], $octapt[$i]->[1][2];
            $row[2] = sprintf " %1.4f %1.4f %1.4f\n", $octapt[$i]->[2][0], $octapt[$i]->[2][1], $octapt[$i]->[2][2];
            for my $i (0 .. 2)
            {
                $row[$i] =~ s/\s-/-/g;
                print ANGMAT $row[$i];
            }
        }
    }
    close (ANGMAT) or die "Cannot close file $fname: $!\n";
    system("cat $fname | $m2euler_binary | awk '{print\$2,\$3,\$4}' > octsymeulers.dat"); 
}

1;
