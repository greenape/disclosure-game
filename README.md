The Disclosure Game
===============
A method for modelling disclosure behaviour
by treating the interaction as paired signalling games played by decision
theoretic agents using Bayesian inference to reason about probable outcomes.
Two theories of decision making - Bayesian risk
minimisation, and cumulative prospect theory - are implemented.

The code is designed to run on home computers, and any HPC environment where [SCOOP](https://code.google.com/p/scoop/) is available.

Suggested runtime if not using a supercomputer is PyPy, and a default experiment can be run like so:

    cd python
    pypy Experiments.py

Experiments.py also accepts several arguments to determine combinations of game, signaller, and responder types to simulate and so on.

Game Types
===============
Several game types are available, Game is the simplest, where women play some number of rounds against a randomly allocated midwife. CaseloadGame is similar, but the midwife is selected at the start and played against consistently.

ReferralGame, and CaseloadReferralGame are analagous except that a referral ends the game for the woman, and women's types are only revealed after a referral.

RecognitionGame, and CaseloadRecognitionGame are like the Referral games, but women receive ambiguous information about the type of midwives. Types are narrowed down only so far as can be determined by the social payoff received for a signal. BayesianSignaller, and ProspectTheorySignaller agents cannot play the recognition games.

Agent Types
===============

Four types of signaller - Bayesian, Prospect, Recognition, and Ambiguity.

RecognitionSignaller remembers opponents and maintains beliefs about them specifically, dealing with ambiguous evidence by simply assuming an observation of the possible types.
AmbiguitySignaller is similar, but assumes it has seen the most probable of the possible types.

Three types of responder - Bayesian, Prospect, and Recognition.
RecognitionResponder performs retrospective updates, so if it gets to observe a true type after lots of interactions, it then updates with those observations.


