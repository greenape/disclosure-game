#!/bin/bash
#PBS -l walltime=60:00:00
#PBS -l nodes=16:ppn=16

GAME[1]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r BayesianPayoffResponder -p 0.85 0.1 0.05'
GAME[2]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r BayesianPayoffResponder -n -p 0.85 0.1 0.05'
GAME[3]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r LexicographicResponder -p 0.85 0.1 0.05'
GAME[4]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r LexicographicResponder -n -p 0.85 0.1 0.05'
GAME[5]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r RecognitionLexicographicResponder -p 0.85 0.1 0.05'
GAME[6]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r RecognitionLexicographicResponder -n -p 0.85 0.1 0.05'
GAME[7]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r RecognitionBayesianPayoffResponder -p 0.85 0.1 0.05'
GAME[8]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r RecognitionBayesianPayoffResponder -n -p 0.85 0.1 0.05'

cd disclosure-game/python
module load python
python -m scoop HPCExperiments.py -R 100 ${GAME[$PBS_ARRAYID]} -f ${PBS_ARRAYID}_alspac_ --individual-measures -i 1000