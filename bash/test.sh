#!/bin/bash
#pypy ../python/Experiments.py -R 2 -g Game CaseloadGame -s BayesianSignaller RecognitionSignaller -r BayesianResponder RecognitionResponder  -f "../results/standard_"
#pypy ../python/Experiments.py -R 2 -g ReferralGame CaseloadReferralGame -s BayesianSignaller RecognitionSignaller -r BayesianResponder RecognitionResponder  -f "../results/referral_"
#pypy ../python/Experiments.py -R 2 -g RecognitionGame CaseloadRecognitionGame -s RecognitionSignaller -r RecognitionResponder  -f "../results/recognition_"
#pypy ../python/Experiments.py -R 2 -g RecognitionGame CaseloadRecognitionGame -s AmbiguitySignaller -r RecognitionResponder  -f "../results/ambiguity_"
#pypy ../python/Experiments.py -R 2 -g RecognitionGame CaseloadRecognitionGame -s AmbiguitySignaller -r BayesianResponder  -f "../results/ambiguity_bayes_"
#pypy ../python/Experiments.py -R 2 -g RecognitionGame CaseloadRecognitionGame -s AmbiguitySignaller -r AmbiguityResponder  -f "../results/ambiguity_ambiguity_"
pypy ../python/Experiments.py -R 2 -g Game CaseloadGame -s LexicographicSignaller -r LexicographicResponder  -f "../results/heuristic_"
pypy ../python/Experiments.py -R 2 -g Game CaseloadGame -s BayesianPayoffSignaller -r BayesianPayoffResponder  -f "../results/payoff_"