#!/bin/bash
#PBS -l walltime=2:00:00
#PBS -l nodes=24:ppn=16
GAME[0]='-g ReferralGame CaseloadReferralGame -f "referral_"'
GAME[1]='-g Game CaseloadGame -f "standard_"'
GAME[2]='-g ReferralGame CaseloadReferralGame -f "referral_nested_" -n'
GAME[3]='-g Game CaseloadGame -f "standard_nested_" -n'
GAME[4]='-g ReferralGame CaseloadReferralGame -f "referral_alspac_" -p 0.85 0.1 0.05'
GAME[5]='-g Game CaseloadGame -f "standard_alspac_" -p 0.85 0.1 0.05'
GAME[6]='-g ReferralGame CaseloadReferralGame -f "referral_alspac_nested_" -n -p 0.85 0.1 0.05'
GAME[7]='-g Game CaseloadGame -f "standard_alpac_nested_" -n -p 0.85 0.1 0.05'

SIGNALLERS='BayesianSignaller BayesianPayoffSignaller RecognitionSignaller LexicographicSignaller'
RESPONDERS='BayesianResponder BayesianPayoffResponder RecognitionResponder LexicographicResponder'

cd disclosure-game/python
module load python
python -m scoop -vvv --tunnel HPCExperiments.py -R 100 ${GAME[$PBS_ARRAYID]} -s $SIGNALLERS -r $RESPONDERS