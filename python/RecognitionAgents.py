from Model import *

class RecognitionResponder(BayesianResponder):
    """
    Class of responder which remembers the actions of opponents and then retrospectively
    updates beliefs based on that when true information is available.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Memory of a particular agent's signals.
        self.signal_memory = {}
        super(RecognitionResponder, self).__init__(player_type, signals, responses)

    def __str__(self):
        return "recognition_%s" % super(RecognitionResponder, self).__str__()

    def respond(self, signal, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent by minimising bayesian risk.
        """
        response = super(RecognitionResponder, self).respond(signal, opponent)
        self.remember(opponent, signal, response)
        return response

    def remember(self, signaller, signal, response):
        """
        Remember what was done in response to a signal.
        """
        # Nothing to do if we know the type already
        if hash(signaller) not in self.signal_memory:
            self.signal_memory[hash(signaller)] = [(signal, response)]
        else:
            self.signal_memory[hash(signaller)].append((signal, response))

    def update_beliefs(self, payoff, signaller, signal, signaller_type=None, weight=1.):
        """
        Update beliefs, and do so retrospectively for as many signal-response
        pairs as we have for this signaller.
        """
        #print "Updating"
        #print payoff, signaller, signal, signaller_type, weight
        if signaller is None:
            return super(RecognitionResponder, self).update_beliefs(payoff, signaller, signal, weight)
        #Need to work with an artificial response log while bulk updating
        tmp_response_log = self.response_log
        mem = self.signal_memory.pop(hash(signaller), [])
        while len(mem) > 0:
            signal, response = mem.pop()
            payoff = self.payoffs[signaller.player_type][response]
            self.response_log = [response]
            super(RecognitionResponder, self).update_beliefs(payoff, signaller, signal, signaller_type, weight=weight)

        self.response_log = tmp_response_log
