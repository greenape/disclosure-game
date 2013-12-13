#!/bin/bash
#PBS -l walltime=14:00:00
#PBS -l nodes=1:ppn=16
#PBS -l pmem=1gb
GAME[1]='-g CarryingInformationGame CaseloadSharingGame -s SharingBayesianPayoffSignaller -r SharingBayesianPayoffResponder'

GAME[2]='-g CarryingInformationGame CaseloadSharingGame -s SharingLexicographicSignaller -r SharingLexicographicResponder'

GAME[3]='-g CarryingInformationGame CaseloadSharingGame -s SharingPayoffProspectSignaller -r SharingPayoffProspectResponder'

cd disclosure-game/python
ulimit -n 512
module load python
source /home/jg1g12/hpc/bin/activate
pypy Experiments.py -R 25 ${GAME[$PBS_ARRAYID]}  --pickled-arguments mw_sharing.args -f ${PBS_ARRAYID}_mw_sharing --individual-measures -i 1000 -d /scratch/jg1g12