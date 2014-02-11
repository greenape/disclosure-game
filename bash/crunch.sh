#!/bin/bash
#PBS -l walltime=48:00:00
#PBS -l nodes=1:ppn=1
#PBS -l pmem=16gb

cd disclosure-game/r
module load R/3.0.0
Rscript crunch.R "/scratch/jg1g12" "/home/jg1g12/disclosure-game/figures" 999 999 "/home/jg1g12/R/R-packages"