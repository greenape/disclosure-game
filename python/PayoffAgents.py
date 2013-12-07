from HeuristicAgents import *
from RecognitionAgents import *
from SharingAgents import *

class BayesianPayoffSignaller(LexicographicSignaller):

    def __str__(self):
        return "bayes_payoff"


    """
    A class of agent that reasons on a signals -> payoffs basis.
    """

    def update_beliefs(self, response, midwife, payoff, midwife_type=None):
        super(BayesianPayoffSignaller, self).update_beliefs(response, midwife, payoff, midwife_type)
        for signal, payoffs in self.payoff_belief.items():
            for payoff, belief in payoffs.items():
                n_k = self.payoff_count[signal][payoff]
                n = sum(self.payoff_count[signal].values())
                belief.append(n_k / float(n))

    def risk(self, signal, opponent):
        risk = 0.
        for payoff, belief in self.payoff_belief[signal].items():
            belief = belief[len(belief) - 1]
            risk += belief*self.loss(payoff)
        return risk

    def do_signal(self, opponent=None):
        best = (random.randint(0, 2), 9999999)
       #print "Type %d woman evaluating signals." % self.player_type
        for signal in shuffled(self.signals):
            signal_risk = self.risk(signal, opponent)
            self.risk_log[signal].append(signal_risk)
            self.risk_log_general[signal].append(self.risk(signal, None))
            #print "Risk for signal %d is %f. Best so far is signal %d at %f." % (signal, signal_risk, best[0], best[1])
            if signal_risk < best[1]:
                best = (signal, signal_risk)
        self.rounds += 1
        self.log_signal(best[0], opponent)
        return best[0]


class BayesianPayoffResponder(LexicographicResponder):

    def __str__(self):
        return "bayes_payoff"

    def update_beliefs(self, payoff, signaller, signal, signaller_type=None):
        super(BayesianPayoffResponder, self).update_beliefs(
            payoff, signaller, signal, signaller_type)
        for signal, responses in self.payoff_belief.items():
            for response, payoffs in responses.items():
                for payoff, belief in payoffs.items():
                    #print self.payoff_count
                    n_k = self.payoff_count[signal][response][payoff]
                    n = sum(self.payoff_count[signal][response].values())
                    belief.append(n_k / float(n))

    def risk(self, act, signal, opponent):
        """
        Return the expected risk of this action given this signal
        was received.
        """
        act_risk = 0.

       #print "Assessing risk for action",act,"given signal",signal
        for payoff, belief in self.payoff_belief[signal][act].items():
            payoff = self.loss(payoff)
            belief = belief[len(belief) - 1]
           #print "Believe true type is",player_type,"with confidence",type_belief
           #print "Risk is",payoff,"*",type_belief
            act_risk += payoff*belief
        #print "R(%d|%d)=%f" % (act, signal, act_risk)
        return act_risk

    def respond(self, signal, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent by minimising bayesian risk.
        """
        super(BayesianPayoffResponder, self).respond(signal, opponent)
        best = (random.randint(0, 1), 9999999)
        for response in shuffled(self.responses):
            act_risk = self.risk(response, signal, opponent)
            if act_risk < best[1]:
                best = (response, act_risk)
        self.response_log.pop()
        self.response_log.append(best[0])
        return best[0]

class RecognitionBayesianPayoffResponder(RecognitionResponder, BayesianPayoffResponder):
    """
    A payoff reasoner that retrospectively updates.
    """

class SharingBayesianPayoffResponder(SharingResponder, BayesianPayoffResponder):
    """
    A payoff reasoner that shares info updates.
    """

class SharingBayesianPayoffSignaller(SharingSignaller, BayesianPayoffSignaller):
    """
    A payoff reasoner that shares info updates.
    """