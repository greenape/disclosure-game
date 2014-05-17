from heuristic import *
from recognition import *
from sharing import *

class BayesianPayoffSignaller(LexicographicSignaller):

    def __str__(self):
        return "bayes_payoff"


    """
    A class of agent that reasons on a signals -> payoffs basis.
    """
    #@profile
    def update_beliefs(self):
        #super(BayesianPayoffSignaller, self).update_beliefs(response, midwife, payoff, midwife_type, weight)
        for signal, payoffs in self.payoff_belief.iteritems():
            n = float(sum(self.payoff_count[signal].values()))
            for payoff, belief in payoffs.iteritems():
                n_k = self.payoff_count[signal][payoff]
                #el belief[:]
                #belief.append(n_k / float(n))
                self.payoff_belief[signal][payoff] = 0.
                if n > 0:
                    self.payoff_belief[signal][payoff] = n_k / n


    def risk(self, signal, opponent):
        risk = 0.
        for payoff, belief in self.payoff_belief[signal].iteritems():
            #belief = belief[len(belief) - 1]
            risk += belief*self.loss(payoff)
        return risk

    def do_signal(self, opponent=None):
        best = (self.random.randint(0, 2), 9999999)
       #print "Type %d woman evaluating signals." % self.player_type
        for signal in shuffled(self.signals, self.random):
            signal_risk = self.risk(signal, opponent)
            #self.risk_log[signal].append(signal_risk)
            #self.risk_log_general[signal].append(self.risk(signal, None))
            #print "Risk for signal %d is %f. Best so far is signal %d at %f." % (signal, signal_risk, best[0], best[1])
            if signal_risk < best[1]:
                best = (signal, signal_risk)
        self.rounds += 1
        self.log_signal(best[0], opponent)
        return best[0]


class BayesianPayoffResponder(LexicographicResponder):
    """
    Class of responder that reasons based on a straight responses imply payoffs
    basis.
    """

    def __str__(self):
        return "bayes_payoff"

    #@profile
    def update_beliefs(self, payoff, signaller, signal, signaller_type=None, weight=1.):
        super(BayesianPayoffResponder, self).update_beliefs(
            payoff, signaller, signal, signaller_type, weight)
        for signal, responses in self.payoff_belief.iteritems():
            for response, payoffs in responses.iteritems():
                n = float(sum(self.payoff_count[signal][response].values()))
                for payoff, belief in payoffs.iteritems():
                    #print self.payoff_count
                    n_k = self.payoff_count[signal][response][payoff]
                    #del belief[:]
                    #belief.append(n_k / float(n))
                    self.payoff_belief[signal][response][payoff] = n_k / n

    def risk(self, act, signal, opponent):
        """
        Return the expected risk of this action given this signal
        was received.
        """
        act_risk = 0.

       #print "Assessing risk for action",act,"given signal",signal
        for payoff, belief in self.payoff_belief[signal][act].iteritems():
            payoff = self.loss(payoff)
            #belief = belief[len(belief) - 1]
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
        best = (self.random.randint(0, 1), 9999999)
        for response in shuffled(self.responses, self.random):
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