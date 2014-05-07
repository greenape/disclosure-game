#!/bin/bash
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingBayesianPayoffSignaller,game=CaseloadSharingGame,resp=SharingBayesianPayoffResponder sensitivity.sh
#qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingPayoffProspectSignaller,game=CaseloadSharingGame,resp=SharingPayoffProspectResponder w_sharing_new.sh
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingLexicographicSignaller,game=CaseloadSharingGame,resp=SharingLexicographicResponder sensitivity.sh
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingProspectSignaller,game=CaseloadSharingGame,resp=SharingProspectResponder sensitivity.sh
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingSignaller,game=CaseloadSharingGame,resp=SharingResponder sensitivity.sh
