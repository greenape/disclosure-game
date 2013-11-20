#!/bin/bash
#PBS -l walltime=25:00:00
#PBS -l nodes=16:ppn=16
GAME[0]='-g ReferralGame CaseloadReferralGame -f referral_honesty_priors_'
GAME[1]='-g Game CaseloadGame -f standard_honesty_priors_'

SIGNALLERS='BayesianSignaller BayesianPayoffSignaller RecognitionSignaller LexicographicSignaller'
RESPONDERS='BayesianResponder BayesianPayoffResponder RecognitionResponder LexicographicResponder'

cd disclosure-game/python
module load python
ulimit -n 512
python -m scoop HPCExperiments.py -R 100 ${GAME[$PBS_ARRAYID]} -s $SIGNALLERS -r $RESPONDERS --pickled-arguments honesty_priors.args