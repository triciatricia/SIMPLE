package spider;

=head1 NAME

spider

=head1 DESCRIPTION

subroutines for controlling spider

=SYNOPSIS

rock on

=head1 AUTHOR

This perl module was written by Dominika Elmlund -09

=cut


use Exporter;
use warnings;
use Cwd;
use lib '<SIMPLEPATH>/lib';
use parse_aligninfo;
my $spider_binary = '<SIMPLEPATH>/bin/spider'; 

########### cluster specific variables #################
my $cores_per_node; 
my $system = '<SYSTEM>';                                    
my $submit;
my $submit2 = '';                                
( $system eq 'LUNARC' ) && ( $submit = 'qsub' );
( $system eq 'HOPPER' )  && ( $submit = 'qsub' ) && ( $cores_per_node = 24 );
( $system eq 'LOCAL' )  && ( $submit = 'nohup' ) && ( $submit2 = '&' ); 
########################################################    

@ISA = ( 'Exporter' );
@EXPORT = qw(   get_spider get_spidoc get_nr_of_spilines spider submit_spider 
                projmod ftsh_projmod ftsh_projmod_from_file fixfourierfiles 
                apply_trs apply_trs_from_avgs_align apply_rt rtsq apsh
                rotalgn pca hcl dendr_findtres print_classdocs make_cavgs_lowlim
                stack reorder_ptcls_in_stack cp_ptcls_from_docs doc_combine
                convert_classdat_to_ptcldat get_nr_ptcls_docs print_new_old_ptcl_nr
                parse_classdoc  make_spidoc_from_array_refs  );


sub get_spider
{
        return ( "$spider_binary" );
}

sub get_spidoc 
{
        my $infile = shift;
        my @arr = split/\./,$infile;
        my $outfile = $arr[0].".spi";
        my @data = file_to_arr( "$infile" );
        my $count = 0;
        open(SPI, ">$outfile") or die "Cannot open: $outfile, for writing: $!\n";
        foreach my $line ( @data ) {
                ( $line =~ /;/ ) && ( next );
                $line =~ s/^\s+//;
                my @row = split( /\s+/,$line );
                my $scalar = scalar( @row );
                chomp @row;
                $count++;
                print SPI " $count\t$scalar\t";
                foreach ( @row ) {
                        print SPI "$_\t";
                }
                print SPI "\n";
        }
        close( SPI );
        return( "$outfile" );
}

sub get_nr_of_spilines
{
        my $file = shift;
        my @arr = file_to_arr( "$file" );
        my $cnt = 0;
        foreach ( @arr ) {
                ( $_ =~ /;/ ) && ( next );
                $cnt++;
        }
        return( $cnt );
}

sub spider
{
        my $script = shift;
        my $out = `$spider_binary xxx/spi \@$script 2>&1`;
        if ( !( $out =~ /\*\*\*\* SPIDER NORMAL STOP \*\*\*\*/ ) ) {
                open( MYSCRIPT, ">SPIDER_FAILURE" );
                print MYSCRIPT "ERROR, there is something fishy with the spider-script $script.xxx\n";
                print MYSCRIPT "Check latest spider results file!\n";
                close( MYSCRIPT );
                die;
        }
}

sub submit_spider
{
        my $jobname = shift;
        my $script = shift;
        my $walltime = shift;
        my $pwd = &Cwd::cwd();
        my $foo = "\@$script";
        open( MYSCRIPT, ">submit_$jobname" ) or die "Cannot open submit_$jobname for writing: $!\n";
        if ( $system eq 'LUNARC' ) {
          print MYSCRIPT "\#!/bin/sh -x
#PBS -N $jobname
#PBS -l nodes=1
#PBS -l walltime=$walltime
#PBS -o outfile.\$PBS_JOBID
#PBS -e errfile.\$PBS_JOBID\n";
        }
        if ( $system eq 'HOPPER' ) {
            my $mppw = $cores_per_node;
            my $hours = int($walltime/3600);
            my $min   = (($walltime)/60)%60;
            my $wtime = $hours.':'.$min.':00';
            print MYSCRIPT "#!/bin/sh -x
#PBS -N $jobname
#PBS -l mppwidth=$mppw
#PBS -l walltime=$wtime
#PBS -o outfile.\$PBS_JOBID
#PBS -e errfile.\$PBS_JOBID
#PBS -q regular\n";
        }
        if ( $system eq 'HOPPER' ) {
            my $apruncmd = "aprun -n 1 -d 24";
            print MYSCRIPT "setenv OMP_NUM_THREADS $cores_per_node\n";
            print MYSCRIPT "cd $pwd\n$apruncmd $spider_binary xxx/spi $foo\nexit\n";          
        }else{
            print MYSCRIPT "cd $pwd\n $spider_binary xxx/spi $foo\nexit\n";
        }
        close( MYSCRIPT );
        system( "chmod u+x submit_$jobname" );
        if ( $system eq 'LUNARC' ) { 
            system( "$submit submit_$jobname >> JOBS" );
        } elsif ( $system eq 'LOCAL' ) {
            system( "$submit submit_$jobname $submit2 >> JOBS" );
        } elsif ( $system eq 'HOPPER' ) {
            system( "$submit submit_$jobname $submit2 >> JOBS" );
        }
        return( "$jobname" );
}

sub projmod
{
        my $box         = shift;
        my $spiangles   = shift;
        my $vol         = shift;
        my $outstack    = shift;
        my $exec        = shift;
        my @numbering    = @_;
        my $nangles     = get_nr_of_spilines( "$spiangles" );
        $spiangles      =~ s/\.spi//;
        $outstack    =~ s/\.spi//;
        my $nr        = scalar @numbering; 
        open( MYSCRIPT, ">projmod.xxx" ) or die "Cannot open file: $!\n";
        if ( scalar $nr ==  0 ) {
            print MYSCRIPT "x15=$box\nud n,x10\n$spiangles\ndo lb1 x11=1,x10\nud s x11,x12,x13,x14\n";
        } elsif ( $nr == 2 ) {
        print MYSCRIPT "x88=0\nx15=$box\ndo lb1 x11=$numbering[0],$numbering[1]\nx88=x88+1\n";
        print MYSCRIPT "ud s x88,x12,x13,x14\n";
        }
        print MYSCRIPT "$spiangles\npj 3\n$vol\nx15,x15\n$outstack","\@{*******","x11}\nx12,x13\nx14\n";
        print MYSCRIPT "lb1\nen\n";
        close(MYSCRIPT);
        ( $exec eq 'c' ) && ( submit_spider( "projmod", "projmod", 20000 ) );
        ( $exec eq 'l' ) && ( spider( "projmod" ) );
        return( "projmod" );
}


sub ftsh_projmod
{
        my $box         = shift;
        my $spiangles   = shift;
        my $vol         = shift;
        my $projname    = shift;
        my $exec        = shift;
        my $fdim        = $box/2;
        my $nangles     = get_nr_of_spilines( "$spiangles" );
        my $stars       = "*" x length($nangles);
        open( MYSCRIPT, ">ftsh_projmod.xxx" ) or die "Cannot open file: $!\n";
        print MYSCRIPT "x15=$box\nx17=$fdim\ndo lb1 x10=1,$nangles\nud s x10,x11,x12,x13\n";
        print MYSCRIPT "$spiangles\npj 3\n$vol\nx15,x15\n_1\nx11,x12\nx13\nsh f\n_1 \n_3\n(x17,x17)\n(0)\nft\n_3\n_4\n";
        print MYSCRIPT "cp to opend\n_4\n$projname";
        print MYSCRIPT "{$stars","x10}\nlb1\nen\n";
        close(MYSCRIPT);
        ( $exec eq 'c' ) && ( submit_spider( "ftsh_projmod", "ftsh_projmod", 20000 ) );
        ( $exec eq 'l' ) && ( spider( "ftsh_projmod" ) );
        return( "ftsh_projmod" );
}

sub ftsh_projmod_from_file 
{
        my $box                 = shift;
        my $fixed_projdata      = shift;
        my $state               = shift;
        my $vol                 = shift;
        my $projname            = shift;
        my $exec                = shift;
        my $fdim                = $box/2;
        open( MYSCRIPT, ">ftsh_projmod_from_file$state.xxx" ) or die "Cannot open file ftsh_projmod_from_file$state.xxx for writing: $!\n";
        print MYSCRIPT "x25=$box\nx17=$fdim\nud n,x66\n$fixed_projdata\ndo lb1 x10=1,x66\nud ic,x10,x11,x12,x13\n";
        print MYSCRIPT "$fixed_projdata\nif (x13.eq.$state) then\npj 3\n$vol\nx25,x25\n_1\nx11,x12\n(0)\nsh f\n_1\n";
        print MYSCRIPT "_3\n(x17,x17)\n(0)\nft\n_3\n_4\ncp to opend\n_4\n$projname","{*******x10}\nendif\nlb1\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "ftsh_projmod_from_file", "ftsh_projmod_from_file$state", 10000 ) );
        ( $exec eq 'l' ) && ( spider( "ftsh_projmod_from_file$state" ) );
        return( "ftsh_projmod_from_file" );
}

sub fixfourierfiles
{
        my $fdim        = shift;
        my $nptcls      = shift;
        my $stack       = shift;
        my $out         = shift;
        my $exec        = shift;
        my $stars       = "*" x length($nptcls);
        $stack          =~ s/\.spi//;
        open(MYSCRIPT, "> :encoding(UTF-8)", "fixfourierfiles.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "x20=$fdim\ndo lb1 x10=1,$nptcls\nsh f\n$stack","\@{","$stars","x10}\n_1\n";
        print MYSCRIPT "(x20,x20)\n(0)\nft\n_1\n_2\ncp to opend\n_2\n$out","{$stars","x10}\nlb1\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "fixfourierfiles", "fixfourierfiles", 40000 ) );
        ( $exec eq 'l' ) && ( spider( "fixfourierfiles" ) );
        return( "fixfourierfiles" );
}

sub apply_trs
{
        my $algndoc     = shift;
        my $instack     = shift;
        my $outstack    = shift;
        my $exec        = shift;
        $algndoc        =~ s/\.spi//;
        $instack        =~ s/\.spi//;
        $outstack       =~ s/\.spi//;
        open(MYSCRIPT, "> :encoding(UTF-8)", "apply_trs.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "ud n,x20\n$algndoc\ndo lb2 x12=1,x20\nud ic,x12,x13,x14\n$algndoc\n";
        print MYSCRIPT "sh f\n$instack","\@{********x12}\n$outstack","\@{********x12}\n(x13,x14)\n(0)\n";
        print MYSCRIPT "lb2\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "apply_trs", "apply_trs", 20000 ) );
        ( $exec eq 'l' ) && ( spider( "apply_trs" ) );
        return( "apply_trs" );
}

sub apply_trs_from_avgs_align
{
        my $algndoc     = shift;
        my $docs        = shift;
        my $instack     = shift;
        my $outstack    = shift;
        my $exec        = shift;
        my @arr         = glob( "$docs*" );
        my $navgs       = @arr;
        $algndoc        =~ s/\.spi//;
        $instack        =~ s/\.spi//;
        $outstack       =~ s/\.spi//;
        my $stars       = "*" x length($navgs);
        open(MYSCRIPT, "> :encoding(UTF-8)", "apply_trs_from_avgs_align.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "x88=0\ndo lb1 x10=1,$navgs\nud n,x66\n$docs","{$stars","x10}\nud ic,x10,x11,x12\n";
        print MYSCRIPT "$algndoc\ndo lb2 x20=1,x66\nx88=x88+1\nud x20,x21\n$docs","{$stars","x10}\n";
        print MYSCRIPT "sh f\n$instack","\@{********x21}\n$outstack","\@{********x88}\n(x11,x12)\n(0)\nlb2\nlb1\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "apply_trs_from_avgs_align", "apply_trs_from_avgs_align", 20000 ) );
        ( $exec eq 'l' ) && ( spider( "apply_trs_from_avgs_align" ) );
        return( "apply_trs_from_avgs_align" );
}

sub apply_rt
{
        my $algndoc     = shift;
        my $instack     = shift;
        my $outstack    = shift;
        my $sign        = shift;
        my $exec        = shift;
        $algndoc        =~ s/\.spi//;
        $instack        =~ s/\.spi//;
        $outstack       =~ s/\.spi//;
        open(MYSCRIPT, "> :encoding(UTF-8)", "apply_rt.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "ud n,x20\n$algndoc\ndo lb2 x12=1,x20\nud ic,x12,x13\n$algndoc\n";
        if( $sign eq '+' ) {
                print MYSCRIPT "rt sq\n$instack","\@{********x12}\n$outstack","\@{********x12}\n(x13,1.0)\n";
        } else {
                print MYSCRIPT "rt sq\n$instack","\@{********x12}\n$outstack","\@{********x12}\n($sign","x13,1.0)\n";
        }
        print MYSCRIPT "(0,0)\nlb2\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "apply_rt", "apply_rt", 20000 ) );
        ( $exec eq 'l' ) && ( spider( "apply_rt" ) );
        return( "apply_rt" );
}


sub rtsq
{
        my $algndoc     = shift;     # output from ap sh only !
        my $instack     = shift;
        my $outstack    = shift;
        my $exec        = shift;
        $algndoc        =~ s/\.spi//;
        $instack        =~ s/\.spi//;
        $outstack       =~ s/\.spi//;
        open(MYSCRIPT, "> :encoding(UTF-8)", "rtsq.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "ud n,x20\n$algndoc\ndo lb2 x12=1,x20\nud ic,x12,x13,x14,x15,x16,x17,x18,x19,x20\n$algndoc\n";
        print MYSCRIPT "rt sq\n$instack","\@{*******x12}\n$outstack","\@{*******x12}\n(x18,1.0)\n";
        print MYSCRIPT "(x19,x20)\nlb2\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "rtsq", "rtsq", 30000 ) );
        ( $exec eq 'l' ) && ( spider( "rtsq" ) );
        return( "rtsq" );
}

sub apsh
{
        my $projsStack   = shift;
        my $even_eulers  = shift;
        my $ptclsStack   = shift;
        my $startPtcl    = shift;
        my $stopPtcl     = shift;
        my $trs          = shift;
        my $inRing       = shift;
        my $outRing      = shift;
        my $i            = shift; # partition
        my $exec         = shift;
        $projsStack      =~ s/\.spi//;
        $ptclsStack      =~ s/\.spi//;
        open(MYSCRIPT, "> :encoding(UTF-8)", "apsh$i.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "x66=$i\nud n,x12\n$even_eulers\nap sh\n$projsStack","\@*********\n1-x12\n$trs,1\n";
        print MYSCRIPT "$inRing,$outRing\n$even_eulers\n$ptclsStack","\@*********\n$startPtcl-$stopPtcl\n";
        print MYSCRIPT "*\n0.0\n0\nPARMFILE{******x66}\nen\n";
        close( MYSCRIPT );
            ( $exec eq 'c' ) && ( submit_spider( "apsh$i", "apsh$i", 60000 ) );
            ( $exec eq 'l' ) && ( spider( "apsh$i" ) );
            return( "apsh$i" );

}


sub rotalgn
{
        my $stack_bp    = shift;
        my $sel         = shift;
        my $rings       = shift;
        my $outdoc      = shift;
        my $exec        = shift;
        $stack_bp       =~ s/\.spi//;
        my $nfiles;
        ( $sel =~ /\d+-(\d+)/ ) && ( $nfiles = $1 );
        ( $sel =~ /\w+\.spi/ ) && ( $nfiles = get_nr_of_spilines( "$sel" ) );
        my $stars       = "*" x length( $nfiles );
        open(MYSCRIPT, "> :encoding(UTF-8)", "rotalgn.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "ap ra\n$stack_bp","\@$stars\n$rings\n0\nf\n$outdoc\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "rotalgn", "rotalgn", 50000 ) );
        ( $exec eq 'l' ) && ( spider( "rotalgn" ) );
        return( "rotalgn" );
}

sub pca
{
        my $box         = shift;
        my $mask        = shift;
        my $eigs        = shift;
        my $instack     = shift;
        my $sel_ptcl    = shift;
        my $exec        = shift;
        $instack        =~ s/\.spi//;
        open(MYSCRIPT, "> :encoding(UTF-8)", "pca.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "x10=$box\nmo\nmsk001\n(x10,x10)\nc\n($mask)\nca s\n$instack";
        print MYSCRIPT "\@*******\n$sel_ptcl\nmsk001\n$eigs\np\npca\ndo lb1 x11=1,$eigs\nca sre\n";
        print MYSCRIPT "pca\ny\n(x11)\nEIGS\@{****x11}\nlb1\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "pca", "pca", 60000 ) );
        ( $exec eq 'l' ) && ( spider( "pca" ) );
        return( "pca" );
}

sub hcl
{
        my $eigens      = shift;
        my $exec        = shift;
        open(MYSCRIPT, "> :encoding(UTF-8)", "hcl.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "cl hc\npca_IMC\n$eigens\n(0)\n(5)\ny\ndendrmap001\ny\ndendrdoc001\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "hcl", "hcl", 70000 ) );
        ( $exec eq 'l' ) && ( spider( "hcl" ) );
        return( "hcl" );
}

sub dendr_findtres  
{
        my $dendrdoc    = shift;
        open(MYSCRIPT, "> :encoding(UTF-8)", "findtreshold.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "x20=0\ndo lb1 x10=1,101\ncl hd\nx20\n$dendrdoc\ntmp{*****x10}\nud n x30\n";
        print MYSCRIPT "tmp{*****x10}\nsd x10,x20,x30\nclasstresholds\nx20=x10*0.01\nlb1\nvm\nrm tmp*\nen\n";
        close( MYSCRIPT );
        spider( "dendr_findtres" );
        return( "dendr_findtres" );
}

sub print_classdocs
{
        my $tres        = shift;
        my $dendrdoc    = shift;
        my $dir_name    = shift;
        my $doc_name    = shift;
        $dendrdoc       =~ s/\.spi//;
        mkdir( $dir_name );
        open(MYSCRIPT, "> :encoding(UTF-8)", "getclassdocs.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "cl hd\n$tres\n$dendrdoc\n$dir_name/$doc_name\ncl he\n$tres\n$dendrdoc\n$dir_name/$doc_name\_nolim****\nen\n";
        close( MYSCRIPT );
        spider( "getclassdocs" );
        return( "getclassdocs" );
}

sub make_cavgs_lowlim 
{
        my $tres        = shift;
        my $dendrdoc    = shift;
        my $llim        = shift;
        my $stack_ptcls = shift;
        my $dir_name    = shift;
        my $doc_name    = shift;
        my $stack_cavgs    = shift;
        my $exec    = shift;
        my $lim         = $llim-1;
        $stack_ptcls    =~ s/\.spi//;
        $stack_cavgs    =~ s/\.spi//;
        print_classdocs( $tres, $dendrdoc, $dir_name, $doc_name );
        my $nptcls      = get_nr_ptcls_docs( "$dir_name/$doc_name" );
        my $stars       = "*" x length($nptcls);
        open(MYSCRIPT, "> :encoding(UTF-8)", "make_classavgs_lowlim$llim.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "ud n,x40\n$dir_name/$doc_name\nx13=0\ndo lb1 x10=1,x40\ndoc ren\n$dir_name/$doc_name\_nolim{****x10}\n";
        print MYSCRIPT "$dir_name/$doc_name\_ren{****x10}\nud n,x11\n$dir_name/$doc_name\_ren{****x10}\nif(x11.GT.$lim) then\n";
        print MYSCRIPT "x13=x13+1\ndo lb2 x12=1,x11\nud ic x12,x14\n$dir_name/$doc_name\_ren{****x10}\nsd x12,x14\n";
        print MYSCRIPT "$dir_name/$doc_name","{****x13}\nud ice\n$dir_name/$doc_name\_ren{****x10}\nlb2\nendif\nlb1\n";
        print MYSCRIPT "do lb3 x20=1,x13\nud n,x21\n$dir_name/$doc_name","{****x20}\nsd x20,x21\n$doc_name\_map001\n";
        print MYSCRIPT "as r\n$stack_ptcls\@$stars\n$dir_name/$doc_name","{****x20}\na\n$stack_cavgs","\@{****x20}\n$dir_name/varifile{****x20}\n";
        print MYSCRIPT "lb3\nvm\nrm $dir_name/$doc_name\_ren*\nvm\nrm $dir_name/$doc_name\_nolim*\nvm\nrm $dir_name/varifile*\nvm\nrm $dir_name/$doc_name.spi\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "make_classavgs_lowlim$llim", "make_classavgs_lowlim$llim", 30000 ) );
        ( $exec eq 'l' ) && ( spider( "make_classavgs_lowlim$llim" ) );
        return( "make_classavgs_lowlim$llim" );
}

sub stack 
{
        my $ss          = shift;
        my $outStack    = shift;
        my $exec        = shift;
        my @arr         = glob( "$ss*" );
        my $nss         = scalar( @arr );
        my $stars       = "*" x length( $nss );
        $outStack       =~ s/\.spi//;
        open( MYSCRIPT, "> :encoding(UTF-8)", "stack.xxx" ) or die "Cannot open file: $!\n";
        print MYSCRIPT "do lb1 x10=1,$nss\ncp\n$ss","{$stars","x10}\n$outStack","\@{$stars";
        print MYSCRIPT "x10}\nlb1\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "stack", "stack", 20000 ) );
        ( $exec eq 'l' ) && ( spider( "stack" ) );
        return( "stack" );
}

sub reorder_ptcls_in_stack
{
        my $instack     = shift;
        my $outstack    = shift;
        my $doc         = shift;
        my $exec        = shift;
        $instack        =~ s/\.spi//;
        $outstack       =~ s/\.spi//;
        open(MYSCRIPT, "> :encoding(UTF-8)", "renumber.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "ud n,x66\n$doc\ndo lb1 x10=1,x66\nud s x10,x11,x12\n$doc\ncp\n$instack";
        print MYSCRIPT "\@{*****x12}\n$outstack","\@{*****x11}\nlb1\nen\n";
        close( MYSCRIPT );
        ( $exec eq 'c' ) && ( submit_spider( "renumber", "renumber", 50000 ) );
        ( $exec eq 'l' ) && ( spider( "renumber" ) );
        return( "renumber" );
}

sub make_spidoc_from_array_refs
{
        my$fname        = shift;
        my$entries      = scalar(@_);
        open( SPIDOC, ">$fname") or die "Cannot open $fname for writing: $!\n";
        foreach my$i  ( 1 .. scalar(@{$_[0]}) ) {
                print SPIDOC "$i\t$entries\t";
                foreach (@_) {
                        print SPIDOC "$_->[$i-1]\t";
                }
                print SPIDOC "\n";
        }
        close(SPIDOC);
}

sub convert_classdat_to_ptcldat
{
        my $projdata    = shift; # psi, theta, state, doc nr
        my $docs        = shift;
        my $navgs       = shift; # remove
        $projdata       =~ s/\.spi//;
        my $stars       = "*" x length($navgs);
        open(MYSCRIPT, "> :encoding(UTF-8)", "fix_projdoc.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "do lb1 x10=1,$navgs\nud x10,x11,x12,x13,x14\n$projdata\nud n,x66\n";
        print MYSCRIPT "$docs","{$stars","x10}\ndo lb2 x20=1,x66\nud x20,x21\n$docs","{$stars";
        print MYSCRIPT "x10}\nsd x21,x11,x12,x13\n_1\nlb2\nlb1\ndoc sort\n_1\nfixed_projdata\n0\nN\nen\n";
        close( MYSCRIPT );
        spider( "fix_projdoc" );
        return( "fix_projdoc" );
}

sub cp_ptcls_from_docs
{
        my $docs        = shift;
        my $inStack     = shift;
        my $outStack    = shift;
        $inStack        =~ s/\.spi//;
        $outStack       =~ s/\.spi//;
        my @arr         = glob( "$docs*" );
        my $navgs       = @arr;
        my $stars       = "*" x length($navgs);
        open(MYSCRIPT, "> :encoding(UTF-8)", "cp_ptcls_from_docs.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "x88=0\ndo lb1 x10=1,$navgs\nud n,x66\n$docs","{$stars","x10}\ndo lb2 x20=1,x66\n";
        print MYSCRIPT "x88=x88+1\nud x20,x21\n$docs","{$stars","x10}\ncp\n$inStack","\@{*******x21}\n";
        print MYSCRIPT "$outStack","\@{*******x88}\nlb2\nlb1\nen\n";
        close( MYSCRIPT );
        spider( "cp_ptcls_from_docs" );
        return( "cp_ptcls_from_docs" );
}

sub doc_combine
{
        my $docs    = shift;
        my $outdoc    = shift;
        my @arr         = glob( "$docs*" );
        my $ndocs       = @arr;
        open(MYSCRIPT, "> :encoding(UTF-8)", "doc_combine.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "doc combine\n$docs","******\n1-$ndocs\n$outdoc\nen\n";
        close( MYSCRIPT );
        spider( "doc_combine" );
        return( "doc_combine" );
}

sub get_nr_ptcls_docs
{
        my $docs        = shift;
        my @docs        = glob( "$docs*" );
        my $cnt         = 0;
        foreach my $doc ( @docs ) {
                my @arr = file_to_arr( "$doc" );
                foreach ( @arr ) {
                        ( $_ =~ /\d+\s+\d+\s+\d+/ ) && ( $_ !~ /;/ ) && ( $cnt++);
                }
        }
        return ( $cnt );
}

sub print_new_old_ptcl_nr
{
        my $docs        = shift;
        my $navgs       = shift;
        my $stars       = "*" x length($navgs);
        open(MYSCRIPT, "> :encoding(UTF-8)", "ptcl_nrs.xxx") or die "Cannot open file: $!\n";
        print MYSCRIPT "x88=0\ndo lb1 x10=1,$navgs\nud n,x66\n$docs","{$stars","x10}\n";
        print MYSCRIPT "do lb2 x20=1,x66\nx88=x88+1\nud x20,x21\ndocs/classdoc{$stars","x10}\n";
        print MYSCRIPT "sd x88,x21,x88 ; old ptcl nr, new ptcl nr\nptcl_nrs\nlb2\nlb1\nen\n";
        close( MYSCRIPT );
        spider( "ptcl_nrs" );
        return( "ptcl_nrs" );
}

sub parse_classdoc
{
        my$fname = shift;
        my@ptcls;

        open( CLS, "<$fname" ) or die " Cannot open $fname for reading: $!\n";
        while(my$dat =<CLS>)
        {
                chomp $dat; 
                if( $dat =~ /;/ ){
                        next
                }else{
                        if( $dat =~ /^\s+\d+\s+\d+\s+(\d+)\.0*/  ){
                                push @ptcls, $1;
                        }
                }
        }
        close( CLS );

        return @ptcls;
}
1;
