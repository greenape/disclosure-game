#!/bin/bash -vx
#PBS -l walltime=30:00:00
#PBS -l nodes=1:ppn=16
#PBS -l pmem=1gb

cd disclosure-game/python
ulimit -n 512
module load python
#source /home/jg1g12/hpc/bin/activate
dir=/scratch/jg1g12/${sig}_${resp}
mkdir ${dir}
${python} Run.py -R 100 -s ${sig} -r ${resp} --pickled-arguments ../experiment_args/sensitivity_${PBS_ARRAYID}.args -f ${PBS_ARRAYID}_sensitivity -i 1000 -d ${dir} -g ${game} 