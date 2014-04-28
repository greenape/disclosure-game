#!/bin/bash
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingBayesianPayoffSignaller,game=CarryingInformationGame,resp=SharingBayesianPayoffResponder mw_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingPayoffProspectSignaller,game=CarryingInformationGame,resp=SharingPayoffProspectResponder mw_proportions.sh

qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingLexicographicSignaller,game=CarryingInformationGame,resp=SharingLexicographicResponder mw_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingProspectSignaller,game=CarryingInformationGame,resp=SharingProspectResponder mw_proportions.sh

qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingSignaller,game=CarryingInformationGame,resp=SharingResponder mw_proportions.sh

qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingBayesianPayoffSignaller,game=CarryingInformationGame,resp=SharingBayesianPayoffResponder women_proportions.sh
#qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingPayoffProspectSignaller,game=CarryingInformationGame,resp=SharingPayoffProspectResponder women_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingLexicographicSignaller,game=CarryingInformationGame,resp=SharingLexicographicResponder women_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingProspectSignaller,game=CarryingInformationGame,resp=SharingProspectResponder women_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=SharingSignaller,game=CarryingInformationGame,resp=SharingResponder women_proportions.sh
