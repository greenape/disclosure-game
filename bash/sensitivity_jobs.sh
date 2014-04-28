#!/bin/bash
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingBayesianPayoffSignaller,game=CarryingInformationGame,resp=SharingBayesianPayoffResponder sensitivity.sh
#qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingPayoffProspectSignaller,game=CarryingInformationGame,resp=SharingPayoffProspectResponder w_sharing_new.sh
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingLexicographicSignaller,game=CarryingInformationGame,resp=SharingLexicographicResponder sensitivity.sh
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingProspectSignaller,game=CarryingInformationGame,resp=SharingProspectResponder sensitivity.sh
qsub -t 0-25 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingSignaller,game=CarryingInformationGame,resp=SharingResponder sensitivity.sh
