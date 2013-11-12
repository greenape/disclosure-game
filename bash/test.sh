#!/bin/bash
pypy ../python/Experiments.py -R 2 -g Game CaseloadGame -s LexicographicSignaller -r LexicographicResponder  -f "../results/alspac/heuristic_" -p 0.85 0.1 0.05
pypy ../python/Experiments.py -R 2 -g Game CaseloadGame -s BayesianPayoffSignaller -r BayesianPayoffResponder  -f "../results/alspac/payoff_" -p 0.85 0.1 0.05
pypy ../python/Experiments.py -R 2 -g ReferralGame CaseloadReferralGame -s LexicographicSignaller -r LexicographicResponder  -f "../results/alspac/heuristic_ref_" -p 0.85 0.1 0.05
pypy ../python/Experiments.py -R 2 -g ReferralGame CaseloadReferralGame -s BayesianPayoffSignaller -r BayesianPayoffResponder  -f "../results/alspac/payoff__ref" -p 0.85 0.1 0.05