#!/bin/bash -vx
#PBS -l walltime=60:00:00
#PBS -l nodes=1:ppn=16
#PBS -l pmem=1gb
GAME[1]='-g CarryingInformationGame CaseloadSharingGame -s SharingBayesianPayoffSignaller -r SharingBayesianPayoffResponder'

GAME[2]='-g CarryingInformationGame CaseloadSharingGame -s SharingLexicographicSignaller -r SharingLexicographicResponder'

GAME[3]='-g CarryingInformationGame CaseloadSharingGame -s SharingPayoffProspectSignaller -r SharingPayoffProspectResponder'

GAME[4]='-g CarryingInformationGame CaseloadSharingGame -s SharingBayesianPayoffSignaller -r SharingBayesianPayoffResponder -p 0.85 0.1 0.05'

GAME[5]='-g CarryingInformationGame CaseloadSharingGame -s SharingLexicographicSignaller -r SharingLexicographicResponder -p 0.85 0.1 0.05'

GAME[6]='-g CarryingInformationGame CaseloadSharingGame -s SharingPayoffProspectSignaller -r SharingPayoffProspectResponder -p 0.85 0.1 0.05'

GAME[7]='-g CarryingInformationGame CaseloadSharingGame -s SharingSignaller -r SharingResponder'
GAME[8]='-g CarryingInformationGame CaseloadSharingGame -s SharingSignaller -r SharingResponder -p 0.85 0.1 0.05'


cd disclosure-game/python
ulimit -n 512
module load python
#source /home/jg1g12/hpc/bin/activate
#python Run.py -R 25 ${GAME[$PBS_ARRAYID]} --pickled-arguments mw_proportions.args -f ${PBS_ARRAYID}_mw_proportions -i 1000 -d /scratch/jg1g12
dir=/scratch/jg1g12/${sig}_${resp}
mkdir ${dir}
${python} Run.py -R 100 -s ${sig} -r ${resp} --pickled-arguments ../experiment_args/women_proportions_${PBS_ARRAYID}.args -f ${PBS_ARRAYID}_women_proportions -i 1000 -d ${dir} -g ${game} 
#python Run.py -R 25 ${GAME[$PBS_ARRAYID]} --pickled-arguments women_proportions.args -f ${PBS_ARRAYID}_women_proportions -i 1000 -d /scratch/jg1g12