#!/bin/bash
#PBS -l walltime=00:30:00
#PBS -l nodes=12:ppn=16

cd disclosure-game/python
module load python

python -m scoop HPCExperiments.py -R 100 --pickled-arguments caseload.args -s BayesianSignaller BayesianPayoffSignaller RecognitionSignaller LexicographicSignaller -r BayesianResponder BayesianPayoffResponder RecognitionResponder LexicographicResponder -g ReferralGame CaseloadReferralGame Game CaseloadGame -f "caseload_"