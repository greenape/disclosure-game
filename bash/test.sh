#!/bin/bash
pypy ../python/Experiments.py -R 2 -g Game CaseloadGame -s BayesianSignaller RecognitionSignaller -r BayesianResponder RecognitionResponder  -f "../results/standard_"
pypy ../python/Experiments.py -R 2 -g ReferralGame CaseloadReferralGame -s BayesianSignaller RecognitionSignaller -r BayesianResponder RecognitionResponder  -f "../results/referral_"