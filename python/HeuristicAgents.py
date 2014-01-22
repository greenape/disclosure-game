from Model import *
from RecognitionAgents import RecognitionResponder
from SharingAgents import *
import operator
import random

class LexicographicSignaller(BayesianSignaller):
    """
    A signaller that uses the Lexicographic heuristic to make decisions.
    """

    def __str__(self):
        return "lexicographic"

    def init_payoffs(self, baby_payoffs, social_payoffs, type_weights=[1., 1., 1.],
                     response_weights=[[1., 1.], [1., 1.], [1., 2.]]):
        #Payoff counter
        self.payoff_count = dict([(signal, {}) for signal in self.signals])
        self.payoff_belief = dict([(signal, {}) for signal in self.signals])
        for signal in self.signals:
            for payoff in social_payoffs[signal]:
                for baby_payoff in baby_payoffs[self.player_type]:
                    self.payoff_count[signal][payoff + baby_payoff] = 0
                    self.payoff_belief[signal][payoff + baby_payoff] = []
        self.depth = 0
        for signal, payoffs in self.payoff_count.items():
            self.depth = max(len(payoffs), self.depth)
        # Psuedocounts go in
        for signal in self.signals:
            breadth = len(self.payoff_count[signal])
            weights = random_expectations(breadth=breadth, high=random.randint(breadth, 10))
            i = 0
            for payoff in self.payoff_count[signal].keys():
                self.payoff_count[signal][payoff] = weights[i]
                i += 1
            #for player_type in self.signals:
            #    for response in self.responses:
            #        payoff = baby_payoffs[self.player_type][response] + social_payoffs[signal][player_type]
            #        self.payoff_count[signal][payoff] += type_weights[player_type] + response_weights[signal][response]
        super(LexicographicSignaller, self).init_payoffs(baby_payoffs, social_payoffs, type_weights,
            response_weights)

    def frequent(self, signal, n, responder=None):
        """
        Return the nth most frequently experienced outcome from
        this signal.
        """
        sorted_dict = sorted(self.payoff_count[signal].items(), key=operator.itemgetter(1), reverse=True)
        return sorted_dict[min(n, len(sorted_dict) - 1)][0]

    def update_beliefs(self, response, midwife, payoff, midwife_type=None):
        #super(LexicographicSignaller, self).update_beliefs(response, midwife, payoff, midwife_type)
        if payoff is not None:
            try:
                self.payoff_count[self.signal_log[len(self.signal_log) - 1]][payoff] += 1
            except KeyError:
                # Must be an impossible payoff add it anyway?
                self.payoff_count[self.signal_log[len(self.signal_log) - 1]][payoff] = 1
        if response is not None:
            self.response_log.append(response)

    def do_signal(self, opponent=None):
        #super(LexicographicSignaller, self).do_signal(opponent)
        signals = shuffled(self.signals)
        n = 0
        # Reduce to possible
        while n < self.depth:
            mappings = {}
            # N most frequent outcome of each signal
            for signal in signals:
                payoff = self.frequent(signal, n, opponent)
                mappings[signal] = payoff
            n += 1
            # Choose the highest unless there's a tie
            sorted_mappings = sorted(mappings.items(), key=operator.itemgetter(1), reverse=True)
            # Is there a best option?
            best = sorted_mappings[0][0]
            try:
                if sorted_mappings[0][1] > sorted_mappings[1][1]:
                    break
                # Remove any worse than the tied pair.
                #if sorted_mappings[1][1] > sorted_mappings[2][1]:
                #    print "removing", sorted_mappings[2][0]
                #    signals.remove(sorted_mappings[2][0])
            except IndexError:
                pass
        # No advantage found so take the first
        self.rounds += 1
        self.log_signal(best, opponent)
        return best


class LexicographicResponder(BayesianResponder):

    def __str__(self):
        return "lexicographic"

    def init_payoffs(self, payoffs, type_weights=[[10., 2., 1.], [1., 10., 1.], [1., 1., 10.]]):
        self.payoff_count = dict([(y, dict([(x, {}) for x in self.responses])) for y in self.signals])
        self.payoff_belief = dict([(y, dict([(x, {}) for x in self.responses])) for y in self.signals])
        #This is a bit more fiddly. Psuedo counts are for meanings..
        for signal in self.signals:
            #total = sum(type_weights[signal])
            for player_type in self.signals:
                #freq = type_weights[signal][player_type] / float(total)
                for response in self.responses:
                    payoff = payoffs[player_type][response]
                    if payoff not in self.payoff_count[signal][response]:
                        self.payoff_count[signal][response][payoff] = type_weights[signal][player_type]
                        self.payoff_belief[signal][response][payoff] = []
                    else:
                        #print self.payoff_count
                        self.payoff_count[signal][response][payoff] += type_weights[signal][player_type]
        self.depth = 0
        for signal, responses in self.payoff_count.items():
            for response, payoff in responses.items():
                self.depth = max(len(payoff), self.depth)
        super(LexicographicResponder, self).init_payoffs(payoffs, type_weights)


    def update_beliefs(self, payoff, signaller, signal, signaller_type=None):
        if payoff is not None:
            #print self.payoff_count, signal, payoff, self.response_log[len(self.response_log) - 1]
            self.payoff_count[signal][self.response_log[len(self.response_log) - 1]][payoff] += 1
        #super(LexicographicResponder, self).update_beliefs(payoff, signaller, signal, signaller_type)

    def frequent(self, signal, response, n, signaller=None):
        """
        Return the nth most frequently experienced outcome from
        this response to the signal.
        """
        sorted_dict = sorted(self.payoff_count[signal][response].items(), key=operator.itemgetter(1), reverse=True)
        return sorted_dict[min(n, len(sorted_dict) - 1)][0]

    def respond(self, signal, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent by minimising bayesian risk.
        """
        #super(LexicographicResponder, self).respond(signal, opponent)
        if opponent is not None:
            self.type_log.append(opponent.player_type)
        self.signal_log.append(signal)
        self.signal_matches[signal] += 1.
        n = 0
        while n < self.depth:
            mappings = {}
            for response in self.responses:
                payoff = self.frequent(signal, response, n, opponent)
                mappings[response] = payoff
            sorted_mappings = sorted(mappings.items(), key=operator.itemgetter(1), reverse=True)
                # Is there a best option?
            best = sorted_mappings[0][0]
            try:
                if sorted_mappings[0][1] > sorted_mappings[1][1]:
                    break
            except IndexError:
                    #Only one payoff
                pass
            n += 1
        #self.response_log.pop()
        self.rounds += 1
        self.response_log.append(best)
        return best

class RecognitionLexicographicResponder(RecognitionResponder, LexicographicResponder):
    """
    A class of lexicographic responder that retrospectively updates when it learns a True
    type.
    """

class SharingLexicographicResponder(SharingResponder, LexicographicResponder):
    """
    A lexicographic reasoner that shares info updates.
    """

class SharingLexicographicSignaller(SharingSignaller, LexicographicSignaller):
    """
    A lexicographic reasoner that shares info updates.
    """