#!/bin/bash
#PBS -l walltime=2:00:00
#PBS -l nodes=24:ppn=16
GAME[0]='-g ReferralGame CaseloadReferralGame -f "referral_"'
GAME[1]='-g Game CaseloadGame -f "standard_"'
GAME[2]='-g ReferralGame CaseloadReferralGame -f "referral_nested_" -n'
GAME[3]='-g Game CaseloadGame -f "standard_nested_" -n'

SIGNALLERS='BayesianSignaller BayesianPayoffSignaller RecognitionSignaller LexicographicSignaller'
RESPONDERS='BayesianResponder BayesianPayoffResponder RecognitionResponder LexicographicResponder'

cd ../python
module load python
python -m scoop -vvv --tunnel HPCExperiments.py -R 100 ${GAME[$PBS_ARRAYID]} -s $SIGNALLERS -r $RESPONDERS