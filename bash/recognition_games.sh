#!/bin/bash
#PBS -l walltime=1:00:00
#PBS -l nodes=32:ppn=16
cd ../python
module load python
python -m scoop -vvv --tunnel --log standard.log HPCExperiments.py -R 100 -g RecognitionGame CaseloadRecognitionGame -s BayesianSignaller RecognitionSignaller -r BayesianResponder RecognitionResponder -f "recognition_"