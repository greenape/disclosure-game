#!/bin/bash
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsBayesianPayoffSignaller,game=CarryingInformationGame,resp=proportionsBayesianPayoffResponder mw_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsPayoffProspectSignaller,game=CarryingInformationGame,resp=proportionsPayoffProspectResponder mw_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsLexicographicSignaller,game=CarryingInformationGame,resp=proportionsLexicographicResponder mw_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsProspectSignaller,game=CarryingInformationGame,resp=proportionsProspectResponder mw_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsSignaller,game=CarryingInformationGame,resp=proportionsResponder mw_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsBayesianPayoffSignaller,game=CarryingInformationGame,resp=proportionsBayesianPayoffResponder women_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsPayoffProspectSignaller,game=CarryingInformationGame,resp=proportionsPayoffProspectResponder women_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsLexicographicSignaller,game=CarryingInformationGame,resp=proportionsLexicographicResponder women_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsProspectSignaller,game=CarryingInformationGame,resp=proportionsProspectResponder women_proportions.sh
qsub -t 0-198 -vpython=/home/jg1g12/pypy/bin/pypy,sig=proportionsSignaller,game=CarryingInformationGame,resp=proportionsResponder women_proportions.sh
