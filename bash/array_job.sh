#!/bin/bash
#PBS -l walltime=01:00:00
#PBS -l nodes=16:ppn=16
GAME[0]='-g ReferralGame CaseloadReferralGame -f referral_low_prior_'
GAME[1]='-g Game CaseloadGame -f standard_low_prior_'
GAME[2]='-g ReferralGame CaseloadReferralGame -f referral_nested_low_prior_-n'
GAME[3]='-g Game CaseloadGame -f standard_nested_low_prior_-n'
GAME[4]='-g ReferralGame CaseloadReferralGame -f referral_alspac_low_prior_-p 0.85 0.1 0.05'
GAME[5]='-g Game CaseloadGame -f standard_alspac_low_prior_-p 0.85 0.1 0.05'
GAME[6]='-g ReferralGame CaseloadReferralGame -f referral_alspac_nested_low_prior_-n -p 0.85 0.1 0.05'
GAME[7]='-g Game CaseloadGame -f standard_alspac_nested_low_prior_-n -p 0.85 0.1 0.05'

SIGNALLERS='BayesianSignaller BayesianPayoffSignaller RecognitionSignaller LexicographicSignaller'
RESPONDERS='BayesianResponder BayesianPayoffResponder RecognitionResponder LexicographicResponder'

cd disclosure-game/python
module load python
python -m scoop HPCExperiments.py -R 100 ${GAME[$PBS_ARRAYID]} -s $SIGNALLERS -r $RESPONDERS