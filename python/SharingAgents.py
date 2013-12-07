from RecognitionAgents import RecognitionResponder
from Model import BayesianSignaller

class SharingResponder(RecognitionResponder):
    """
    Class of responder which remembers the actions of opponents and then retrospectively
    updates beliefs based on that when true information is available.
    Makes the most recent referral available to be shared.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Memory available for sharing
        self.shareable = None
        super(SharingResponder, self).__init__(player_type, signals, responses)

    def __str__(self):
        return "sharing_%s" % super(SharingResponder, self).__str__()

    def remember(self, signaller, signal, response):
        """
        Remember what was done in response to a signal.
        """
        super(SharingResponder, self).remember(signaller, signal, response)
        if response == 1 or signaller.is_finished:
            payoff_sum = sum(map(lambda x: self.payoffs[signaller.player_type][x[1]], self.signal_memory[hash(signaller)]))
            self.shareable = (hash(self), payoff_sum, (signaller.player_type, list(self.signal_memory[hash(signaller)])))

class SharingSignaller(BayesianSignaller):
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Exogenous memories
        self.exogenous = []
        super(SharingSignaller, self).__init__(player_type, signals, responses)

    def __str__(self):
        return "sharing_%s" % super(SharingSignaller, self).__str__()

    def exogenous_update(self, signal, response, tmp_signaller, payoff, midwife_type=None):
        self.log_signal(signal, tmp_signaller)
        self.exogenous.append((tmp_signaller.player_type, signal, response, payoff))
        self.update_beliefs(response, tmp_signaller, payoff, midwife_type)

    def get_memory(self):
        memories = zip(self.type_log, self.signal_log, self.response_log, self.payoff_log)
        for memory in self.exogenous:
            memories.remove(memory)
        payoff_sum = sum(map(lambda x: x[3], memories))
        return (payoff_sum, memories)
