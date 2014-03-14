#!/bin/bash
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingLexicographicSignaller_SharingLexicographicResponder -f "*_w_*_women.db" -t "w_lexic_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingLexicographicSignaller_SharingLexicographicResponder -f "*_w_*_mw.db" -t "w_lexic_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingSignaller_SharingResponder -f "*_w_*_women.db" -t "w_sharing_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingSignaller_SharingResponder -f "*_w_*_mw.db" -t "w_sharing_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingPayoffProspectSignaller_SharingPayoffProspectResponder -f "*_w_*_women.db" -t "w_payoff_prospect_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingPayoffProspectSignaller_SharingPayoffProspectResponder -f "*_w_*_mw.db" -t "w_payoff_prospect_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingBayesianPayoffSignaller_SharingBayesianPayoffResponder -f "*_w_*_women.db" -t "w_payoff_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingBayesianPayoffSignaller_SharingBayesianPayoffResponder -f "*_w_*_mw.db" -t "w_payoff_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectSignaller_SharingProspectResponder -f "*_w_*_women.db" -t "w_prospect_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectSignaller_SharingProspectResponder -f "*_w_*_mw.db" -t "w_prospect_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingLexicographicSignaller_SharingLexicographicResponder -f "*_mw_*_women.db" -t "lexic_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingLexicographicSignaller_SharingLexicographicResponder -f "*_mw_*_mw.db" -t "lexic_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingSignaller_SharingResponder -f "*_mw_*_women.db" -t "sharing_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingSignaller_SharingResponder -f "*_mw_*_mw.db" -t "sharing_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingPayoffProspectSignaller_SharingPayoffProspectResponder -f "*_mw_*_women.db" -t "payoff_prospect_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingPayoffProspectSignaller_SharingPayoffProspectResponder -f "*_mw_*_mw.db" -t "payoff_prospect_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingBayesianPayoffSignaller_SharingBayesianPayoffResponder -f "*_mw_*_women.db" -t "payoff_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingBayesianPayoffSignaller_SharingBayesianPayoffResponder -f "*_mw_*_mw.db" -t "payoff_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectSignaller_SharingProspectResponder -f "*_mw_*_women.db" -t "prospect_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectSignaller_SharingProspectResponder -f "*_mw_*_mw.db" -t "prospect_mw.db"