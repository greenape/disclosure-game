#!/bin/bash
#PBS -l walltime=12:00:00
#PBS -l nodes=1:ppn=16
#PBS -l mem=16gb
GAME[1]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r BayesianPayoffResponder'

GAME[2]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r LexicographicResponder'

GAME[3]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r RecognitionLexicographicResponder -n'

GAME[4]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r RecognitionBayesianPayoffResponder -n'

GAME[5]='-g CarryingReferralGame CarryingGame -s PayoffProspectSignaller -r PayoffProspectResponder'

GAME[6]='-g CarryingReferralGame CarryingGame -s PayoffProspectSignaller -r RecognitionPayoffProspectResponder -n'

GAME[7]='-g CarryingReferralGame CarryingGame -s BayesianSignaller -r BayesianResponder'

GAME[8]='-g CarryingReferralGame CarryingGame -s BayesianSignaller -r RecognitionResponder -n'

cd disclosure-game/python
module load python
ulimit -n 512
python -m scoop HPCExperiments.py -R 100 ${GAME[$PBS_ARRAYID]} --pickled-arguments priors.args -f ${PBS_ARRAYID}_honesty_priors --individual-measures -i 1000