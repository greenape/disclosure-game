#!/bin/bash
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingLexicographicSignaller_SharingLexicographicResponder -f "*_women.db" -t "lexic_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingLexicographicSignaller_SharingLexicographicResponder -f "*_mw.db" -t "lexic_mw.db"

#python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingSignaller_SharingResponder -f "*_women.db" -t "sharing_w.db"
#python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingSignaller_SharingResponder -f "*_mw.db" -t "sharing_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectPayoffSignaller_SharingProspectPayoffResponder -f "*_women.db" -t "payoff_prospect_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectPayoffSignaller_SharingProspectPayoffResponder -f "*_mw.db" -t "payoff_prospect_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingBayesianPayoffSignaller_SharingBayesianPayoffResponder -f "*_women.db" -t "payoff_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingBayesianPayoffSignaller_SharingBayesianPayoffResponder -f "*_mw.db" -t "payoff_mw.db"

python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectSignaller_SharingProspectResponder -f "*_women.db" -t "prospect_w.db"
python sqlite_merge.py -d /Users/jg1g12/Downloads/SharingProspectSignaller_SharingProspectResponder -f "*_mw.db" -t "prospect_mw.db"