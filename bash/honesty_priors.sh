#!/bin/bash
#PBS -l walltime=25:00:00
#PBS -l nodes=12:ppn=16
GAME[1]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r BayesianPayoffResponder'

GAME[2]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r BayesianPayoffResponder -n'

GAME[3]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r LexicographicResponder'

GAME[4]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r LexicographicResponder -n'

GAME[5]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r RecognitionLexicographicResponder'

GAME[6]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r RecognitionLexicographicResponder -n'

GAME[7]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r RecognitionBayesianPayoffResponder'

GAME[8]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r RecognitionBayesianPayoffResponder -n'

cd disclosure-game/python
module load python
ulimit -n 512
python -m scoop HPCExperiments.py -R 100 ${GAME[$PBS_ARRAYID]} --pickled-arguments honesty_priors.args -f ${PBS_ARRAYID}_honesty_priors_ --individual-measures -i 1000