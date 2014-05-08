#!/bin/bash -vx
#PBS -l walltime=01:00:00
#PBS -l nodes=2:ppn=16
#PBS -l pmem=1gb

cd disclosure-game/python
ulimit -n 512
module load python
#source /home/jg1g12/hpc/bin/activate
sig=SharingSignaller
resp=SharingResponder
game=CarryingInformationGame
dir=/scratch/jg1g12/${sig}_${resp}
mkdir ${dir}
pypy/bin/pypy -m scoop ScoopTest.py -R 32 -s ${sig} -r ${resp} -f test -i 1000 -d ${dir} -g ${game} 