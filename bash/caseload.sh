#!/bin/bash
#PBS -l walltime=01:00:00
#PBS -l nodes=12:ppn=16

cd disclosure-game/python
module load python

python -m scoop HPCExperiments.py -R 100 --pickled-arguments caseload.args -s BayesianSignaller BayesianPayoffSignaller RecognitionSignaller LexicographicSignaller -r BayesianResponder BayesianPayoffResponder RecognitionResponder LexicographicResponder -g ReferralGame Game -f "caseload_low_prior_"