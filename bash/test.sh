#!/bin/bash
python -m scoop ../python/HPCExperiments.py -R 10 -g Game CaseloadGame -s BayesianPayoffSignaller -r BayesianPayoffResponder  -n -f "../results/payoff_alspac_" -d $PWD -p 0.85 0.1 0.05