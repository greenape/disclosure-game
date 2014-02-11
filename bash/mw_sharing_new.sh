#!/bin/bash -vx
#PBS -l walltime=60:00:00
#PBS -l nodes=1:ppn=16
#PBS -l pmem=1gb
GAME[1]='-s SharingBayesianPayoffSignaller -r SharingBayesianPayoffResponder'

GAME[2]='-s SharingLexicographicSignaller -r SharingLexicographicResponder'

GAME[3]='-s SharingPayoffProspectSignaller -r SharingPayoffProspectResponder'

GAME[4]='-s SharingBayesianPayoffSignaller -r SharingBayesianPayoffResponder -p 0.85 0.1 0.05'

GAME[5]='-s SharingLexicographicSignaller -r SharingLexicographicResponder -p 0.85 0.1 0.05'

GAME[6]='-s SharingPayoffProspectSignaller -r SharingPayoffProspectResponder -p 0.85 0.1 0.05'

GAME[7]='-s SharingSignaller -r SharingResponder'
GAME[8]='-s SharingSignaller -r SharingResponder -p 0.85 0.1 0.05'

GAME[9]='-s SharingProspectSignaller -r SharingProspectResponder'
GAME[10]='-s SharingProspectSignaller -r SharingProspectResponder -p 0.85 0.1 0.05'

cd disclosure-game/python
ulimit -n 512
module load python
#source /home/jg1g12/hpc/bin/activate
dir=/scratch/jg1g12/${sig}_${resp}
mkdir ${dir}
python Run.py -R 100 -s ${sig} -r ${resp} --pickled-arguments ../experiment_args/mw_sharing_${PBS_ARRAYID}.args -f ${PBS_ARRAYID}_mw_sharing -i 1000 -d ${dir} -g CarryingInformationGame 