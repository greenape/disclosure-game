import Model
import math
import random
from PayoffAgents import *
from RecognitionAgents import *

class ProspectTheorySignaller(Model.BayesianSignaller):
    """
    A responder which makes decision using cumulative prospect theory.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1], 
        alpha=.94, beta=.86, l=2.25, gamma=.99, delta=.93):
        self.alpha = alpha
        self.gamma = gamma
        self.l = l
        self.delta = delta
        self.beta = beta
        super(ProspectTheorySignaller, self).__init__(player_type, signals, responses)

    def weighting(self, probability, power):
        return pow(probability, power) / pow(pow(probability, power) + pow(1. - probability, power), 1. / power)


    def value(self, outcome):
        """
        Return the relative value of an outcome.
        """
        if outcome > 0:
            return self.gain_value(outcome)
        elif outcome < 0:
            return self.l * self.loss_value(outcome)
        return 0

    def gain_value(self, payoff):
        if self.alpha > 0:
            payoff = pow(payoff, self.alpha)
        elif self.alpha < 0:
            payoff = math.log(payoff)
        else:
            payoff = 1 - pow(1 + payoff, self.alpha)
        return payoff

    def loss_value(self, payoff):
        if self.beta > 0:
            payoff = -pow(-payoff, self.beta)
        elif self.beta < 0:
            payoff = pow(1 - payoff, self.beta) - 1
        else:
            payoff = -math.log(-payoff)
        return payoff

    def collect_prospects(self, signal):
        """
        Compute the cumulative prospect theory value of this signal
        based on the estimated probalities at this appointment.
        """
        prospects = []
        for player_type, type_belief in self.current_type_distribution().items():
            for response, response_belief in self.current_response_belief()[signal].items():
                total_belief = response_belief*type_belief
                payoff = self.baby_payoffs[response] + self.social_payoffs[player_type][signal]
                prospects.append((payoff, total_belief))
        prospects.sort()
        prospects.reverse()
        return prospects

    def cpt_value(self, prospects):
        """
        Compute the cumulative prospect theory value of this set of
        prospects.
        """
        payoffs, probs = zip(*prospects)
        signal_risk = 0.
        for i in range(len(prospects)):
            type_belief = probs[i]
            payoff = payoffs[i]
            power = self.gamma
            if payoff < 0:
                power = self.delta
            if i == 0 and payoff < 0 or i == (len(prospects) - 1) and payoff >= 0:
                weight =  (1 - self.weighting(1 - type_belief, power))
                #print "1 - w(1 - ", type_belief,")"
            elif payoff < 0:
                #print "sum(",probs[i:],"-sum(",probs[i + 1:],")"
                weight = self.weighting(sum(probs[i:]), power) - self.weighting(sum(probs[i + 1:]), power)
            else:
                weight = self.weighting(sum(probs[:i + 1]), power) - self.weighting(sum(probs[:i]), power)
                #print "sum(",probs[:i+1],"-sum(",probs[:i],")"
            #print "Weighting for outcome %f: %f" % (payoff, weight)
            signal_risk += self.value(payoff) * weight
        return signal_risk

    def do_signal(self, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent based on expe
        """
        super(LexicographicSignaller, self).do_signal(opponent)
        best = (random.randint(0, 2), -9999999)
        for signal in Model.shuffled(self.signals):
            act_risk = self.cpt_value(self.collect_prospects(signal))
            self.risk_log[signal].append(act_risk)
            self.risk_log_general[signal].append(act_risk)
            if act_risk > best[1]:
                best = (signal, act_risk)
        self.signal_log.pop()
        self.signal_log.append(best[0])
        return best[0]

    def __str__(self):
        return "prospect"

class PayoffProspectSignaller(ProspectTheorySignaller, BayesianPayoffSignaller):
    def __str__(self):
        return "cpt_payoff"

    def collect_prospects(self, signal):
        """
        Compute the cumulative prospect theory value of this signal
        based on the estimated probalities at this appointment.
        """
        prospects = []
        for payoff, belief in self.payoff_belief[signal].items():
            belief = belief[len(belief) - 1]
            prospects.append((payoff, belief))
        prospects.sort()
        prospects.reverse()
        return prospects

class ProspectTheoryResponder(Model.BayesianResponder):
    """
    A responder which makes decision using prospect theory.
    Reference may take value 0 (total losses so far), 1 (losses last round), or 3
    (worst case losses this round)
    Weighting is some function that takes the probability p and returns a weighted version of it.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1],
        alpha=.94, beta=.86, l=2.25, gamma=.99, delta=.93):
        self.alpha = alpha
        self.gamma = gamma
        self.l = l
        self.delta = delta
        self.beta = beta
        super(ProspectTheoryResponder, self).__init__(player_type, signals, responses)

    def weighting(self, probability, power):
        return pow(probability, power) / pow(pow(probability, power) + pow(1. - probability, power), 1. / power)


    def value(self, outcome):
        """
        Return the relative value of an outcome.
        """
        if outcome > 0:
            return self.gain_value(outcome)
        elif outcome < 0:
            return self.l * self.loss_value(outcome)
        return 0

    def gain_value(self, payoff):
        if self.alpha > 0:
            payoff = pow(payoff, self.alpha)
        elif self.alpha < 0:
            payoff = math.log(payoff)
        else:
            payoff = 1 - pow(1 + payoff, self.alpha)
        return payoff

    def loss_value(self, payoff):
        if self.beta > 0:
            payoff = -pow(-payoff, self.beta)
        elif self.beta < 0:
            payoff = pow(1 - payoff, self.beta) - 1
        else:
            payoff = -math.log(-payoff)
        return payoff

    def collect_prospects(self, response, signal):
        """
        Collate the prospects for this response given the signal,
        and sort them in descending order of payoff.
        """
        prospects = []
        for player_type, type_belief in self.current_beliefs()[signal].items():
            payoff = self.payoffs[player_type][response]
            prospects.append((payoff, type_belief))
        prospects.sort()
        prospects.reverse()
        return prospects

    def cpt_value(self, prospects):
        """
        Compute the cumulative prospect theory value of this set of
        prospects.
        """
        payoffs, probs = zip(*prospects)
        signal_risk = 0.
        for i in range(len(prospects)):
            type_belief = probs[i]
            payoff = payoffs[i]
            power = self.gamma
            if payoff < 0:
                power = self.delta
            if i == 0 and payoff < 0 or i == (len(prospects) - 1) and payoff >= 0:
                weight =  (1 - self.weighting(1 - type_belief, power))
            elif payoff < 0:
                weight = self.weighting(sum(probs[i:]), power) - self.weighting(sum(probs[i + 1:]), power)
            else:
                weight = self.weighting(sum(probs[:i + 1]), power) - self.weighting(sum(probs[:i]), power)
            #print "Weighting for outcome %f: %f" % (payoff, weight)
            signal_risk += self.value(payoff) * weight
       #print "U(%d|x)=%f" % (signal, signal_risk)
        return signal_risk

    def respond(self, signal, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent based on expe
        """
        super(ProspectTheoryResponder, self).respond(signal, opponent)

        best = (random.randint(0, 1), -9999999)
        for response in Model.shuffled(self.responses):
            act_risk = self.cpt_value(self.collect_prospects(response, signal))
            if act_risk > best[1]:
                best = (response, act_risk)
        self.response_log.pop()
        self.response_log.append(best[0])
        return best[0]

    def __str__(self):
        return "prospect"

class PayoffProspectResponder(ProspectTheoryResponder, BayesianPayoffResponder):
    def __str__(self):
        return "cpt_payoff"

    def collect_prospects(self, response, signal):
        """
        Compute the cumulative prospect theory value of this signal
        based on the estimated probalities at this appointment.
        """
        prospects = []
        for payoff, belief in self.payoff_belief[signal][response].items():
            belief = belief[len(belief) - 1]
            prospects.append((payoff, belief))
        prospects.sort()
        prospects.reverse()
        return prospects