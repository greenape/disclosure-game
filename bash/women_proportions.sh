#!/bin/bash
#PBS -l walltime=01:30:00
#PBS -l nodes=1:ppn=16
GAME[1]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r BayesianPayoffResponder'

GAME[2]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r BayesianPayoffResponder -n'

GAME[3]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r LexicographicResponder'

GAME[4]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r LexicographicResponder -n'

GAME[5]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r RecognitionLexicographicResponder'

GAME[6]='-g CarryingReferralGame CarryingGame -s LexicographicSignaller -r RecognitionLexicographicResponder -n'

GAME[7]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r RecognitionBayesianPayoffResponder'

GAME[8]='-g CarryingReferralGame CarryingGame -s BayesianPayoffSignaller -r RecognitionBayesianPayoffResponder -n'

GAME[9]='-g CarryingReferralGame CarryingGame -s PayoffProspectSignaller -r PayoffProspectResponder'

GAME[10]='-g CarryingReferralGame CarryingGame -s PayoffProspectSignaller -r PayoffProspectResponder -n'

GAME[11]='-g CarryingReferralGame CarryingGame -s PayoffProspectSignaller -r RecognitionPayoffProspectResponder'

GAME[12]='-g CarryingReferralGame CarryingGame -s PayoffProspectSignaller -r RecognitionPayoffProspectResponder -n'

GAME[13]='-g CarryingReferralGame CarryingGame -s BayesianSignaller -r BayesianResponder'

GAME[14]='-g CarryingReferralGame CarryingGame -s BayesianSignaller -r BayesianResponder'

cd disclosure-game/python
ulimit -n 512
module load python
source /home/jg1g12/hpc/bin/activate
pypy -m scoop -v HPCExperiments.py -R 10 ${GAME[$PBS_ARRAYID]}  --pickled-arguments women_proportions.args -f ${PBS_ARRAYID}_women_proportions_ --individual-measures -i 1000 -d ${HOME}/results