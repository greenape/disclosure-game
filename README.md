The Disclosure Game
===============
A method for modelling disclosure behaviour
by treating the interaction as paired signalling games played by decision
theoretic agents using Bayesian inference to reason about probable outcomes.
Two theories of decision making - Bayesian risk
minimisation, and cumulative prospect theory - are implemented.

Suggested runtime if not using a supercomputer is PyPy, and a default experiment can be run like so:

    cd python
    pypy Run.py

Run.py also accepts several arguments to determine combinations of game, signaller, and responder types to simulate and so on.

For example, to run 100 runs of the Recognition game, with all combinations of Ambiguity and Recognition signallers, with Bayesian and Recognition responders:
        
    cd python
    pypy Run.py --runs 100 --games RecognitionGame --signallers AmbiguitySignaller RecognitionSignaller --responders BayesianResponder RecognitionResponder

Game Types
===============
Several game types are available, Game is the simplest, where women play some number of rounds against a randomly allocated midwife. CaseloadGame is similar, but the midwife is selected at the start and played against consistently.

ReferralGame, and CaseloadReferralGame are analagous except that a referral ends the game for the woman, and women's types are only revealed after a referral.

RecognitionGame, and CaseloadRecognitionGame are like the Referral games, but women receive ambiguous information about the type of midwives. Types are narrowed down only so far as can be determined by the social payoff received for a signal.

Agent Types
===============

Several classes of agent are available: two variations on Bayesian Risk and Cumulative Prospect Theory, and a lexicographic heuristic.

Both the Bayesian and CPT agents come in a flavour which uses a relatively sophisticated model of reasoning, where signallers hold beliefs about the distribution of responder player types, and the outcomes of signals. Responders of this type reason based on the likelihood of a given signal being honest.

The lexicographic agents are based only on a presumed signal -> payoff link, and response -> payoff (given a signal) link, and two equivalent agent models (BayesianPayoff, and ProspectPayoff) use this reasoning model as well.


