#!/usr/bin/perl
use warnings;
use strict;
if( @ARGV != 5 ){
    die "Need five command line arg:s\n(1) SIMPLE program name\n(2) compiler (ifort)\n(3) optimized code or not (1 or 0)\n(4) mac or not (1 or 0)\n(5) clean or not (1 or 0)\n";   
}
my$prog     = $ARGV[0];
my$compiler = $ARGV[1];
my$opt      = $ARGV[2];
my$mac      = $ARGV[3];
my$clean    = $ARGV[4];
if($prog eq "all"){
    comp('abinirec',$compiler,$opt,$mac);
    comp('auto_mask',$compiler,$opt,$mac);
    comp('classify',$compiler,$opt,$mac);
    comp('align',$compiler,$opt,$mac);
    comp('mkalgndoc',$compiler,$opt,$mac);
    comp('mkrndcls',$compiler,$opt,$mac);
    comp('mkrndeuls',$compiler,$opt,$mac);
    comp('mkrndinpls',$compiler,$opt,$mac);
    comp('mkrndints',$compiler,$opt,$mac);
    comp('mkrndoris',$compiler,$opt,$mac);
    comp('reconstruct',$compiler,$opt,$mac);
    comp('fim_to_spi',$compiler,$opt,$mac);
    comp('fim_shift',$compiler,$opt,$mac);
    comp('spi_to_fim',$compiler,$opt,$mac);
}elsif($prog eq "clean") {
    clean('abinirec',$compiler,$opt,$mac);
    clean('auto_mask',$compiler,$opt,$mac);
    clean('classify',$compiler,$opt,$mac);
    clean('align',$compiler,$opt,$mac);
    clean('mkalgndoc',$compiler,$opt,$mac);
    clean('mkrndcls',$compiler,$opt,$mac);
    clean('mkrndeuls',$compiler,$opt,$mac);
    clean('mkrndinpls',$compiler,$opt,$mac);
    clean('mkrndints',$compiler,$opt,$mac);
    clean('mkrndoris',$compiler,$opt,$mac);
    clean('reconstruct',$compiler,$opt,$mac);
    clean('fim_to_spi',$compiler,$opt,$mac);
    clean('fim_shift',$compiler,$opt,$mac);
    clean('spi_to_fim',$compiler,$opt,$mac);
}else{
    comp($prog,$compiler,$opt,$mac);
}

sub comp{
    my$prg      = shift;
    my$compiler = shift;
    my$opt      = shift;
    my$mac      = shift;
    my$prg_para = './'.$prg.'_para';
    my$prg_seq = './'.$prg.'_seq';
    my$prg_nolab = './'.$prg;
    $prg = $prg.'.f90';
    if(-d $prg_para ){
        chdir($prg_para);
        system("../fmkmf.pl -f90 $compiler -openmp 1 -opt $opt -mac $mac $prg > makefile");
        ($clean == 1) && (system("make clean"));
        system("make");
        chdir("../");
    }
    if(-d $prg_seq ){
        chdir($prg_seq);
        system("../fmkmf.pl -f90 $compiler -openmp 0 -opt $opt -mac $mac $prg > makefile");
        ($clean == 1) && (system("make clean"));
        system("make");
        chdir("../");
    }
    if(-d $prg_nolab ){
        chdir($prg_nolab);
        system("../fmkmf.pl -f90 $compiler -openmp 0 -opt $opt -mac $mac $prg > makefile");
        ($clean == 1) && (system("make clean"));
        system("make");
        chdir("../");
    }
}

sub clean{
    my$prg      = shift;
    my$compiler = shift;
    my$opt      = shift;
    my$mac      = shift;
    my$prg_para = './'.$prg.'_para';
    my$prg_seq = './'.$prg.'_seq';
    my$prg_nolab = './'.$prg;
    $prg = $prg.'.f90';
    if(-d $prg_para ){
        chdir($prg_para);
        system("rm $prg_nolab");
        system("make clean");
        chdir("../");
    }
    if(-d $prg_seq ){
        chdir($prg_seq);
        system("rm $prg_nolab");
        system("make clean");
        chdir("../");
    }
    if(-d $prg_nolab ){
        chdir($prg_nolab);
        system("rm $prg_nolab"); 
        system("make clean");
        chdir("../");
    }
}