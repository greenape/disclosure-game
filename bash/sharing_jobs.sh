#!/bin/bash
#qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingBayesianPayoffSignaller,game=CarryingInformationGame,resp=SharingBayesianPayoffResponder mw_sharing_new.sh
#qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingPayoffProspectSignaller,game=CarryingInformationGame,resp=SharingPayoffProspectResponder mw_sharing_new.sh
#qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingLexicographicSignaller,game=CarryingInformationGame,resp=SharingLexicographicResponder mw_sharing_new.sh
#qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingProspectSignaller,game=CarryingInformationGame,resp=SharingProspectResponder mw_sharing_new.sh
#qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingSignaller,game=CarryingInformationGame,resp=SharingResponder mw_sharing_new.sh
#qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingBayesianPayoffSignaller,game=CarryingInformationGame,resp=SharingBayesianPayoffResponder w_sharing_new.sh
qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingPayoffProspectSignaller,game=CarryingInformationGame,resp=SharingPayoffProspectResponder w_sharing_new.sh
qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingLexicographicSignaller,game=CarryingInformationGame,resp=SharingLexicographicResponder w_sharing_new.sh
qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingProspectSignaller,game=CarryingInformationGame,resp=SharingProspectResponder w_sharing_new.sh
qsub -t 0-204 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingSignaller,game=CarryingInformationGame,resp=SharingResponder w_sharing_new.sh
