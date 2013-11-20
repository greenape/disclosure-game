#!/bin/bash
#PBS -l walltime=50:00:00
#PBS -l nodes=16:ppn=16
GAME[0]='-g ReferralGame CaseloadReferralGame -f referral_priors_sweep_'
GAME[1]='-g Game CaseloadGame -f standard_priors_sweep_'
GAME[2]='-g ReferralGame CaseloadReferralGame -f referral_nested_priors_sweep_ -n'
GAME[3]='-g Game CaseloadGame -f standard_nested_priors_sweep_ -n'

SIGNALLERS='BayesianSignaller BayesianPayoffSignaller RecognitionSignaller LexicographicSignaller'
RESPONDERS='BayesianResponder BayesianPayoffResponder RecognitionResponder LexicographicResponder'

cd disclosure-game/python
module load python
ulimit -n 512
python -m scoop HPCExperiments.py -R 10 ${GAME[$PBS_ARRAYID]} -s $SIGNALLERS -r $RESPONDERS --pickled-arguments priors.args