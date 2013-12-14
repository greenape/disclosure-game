from Model import *

class RecognitionSignaller(BayesianSignaller):
    """
    A signalling agent which recognises and remembers opponents.

    After observing the true type of an individual, the belief on
    this immediately goes to 1 since it is certain.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Midwife type memory
        self.type_memory = {}

        super(RecognitionSignaller, self).__init__(player_type, signals, responses)

    def __str__(self):
        return "recognition_%s" % super(RecognitionSignaller, self).__str__()

    def update_beliefs(self, response, midwife, payoff, midwife_type=None):
        """
        This remembers types if revealed.
        """
        #print "Updating beliefs with known type."
        #Update general beliefs first
        super(RecognitionSignaller, self).update_beliefs(response, midwife, payoff, midwife_type)

        #Exit early if there's no midwife
        if midwife is None:
            return

        #Then update beliefs about *this* opponent
        #Known type
        if midwife_type is None:
            self.type_memory[hash(midwife)] = midwife.player_type

    def risk(self, signal, opponent):
        """
        If the opponent's type is known, then use modified risk
        that treats it as having probability 1.
        """
        if hash(opponent) in self.type_memory:
            #print "Known type."
            signal_risk = self.known_type_risk(signal, opponent)
        else:
            signal_risk = super(RecognitionSignaller, self).risk(signal, opponent)
        #print "R(%d|x)=%f" % (signal, signal_risk)
        return signal_risk

    def known_type_risk(self, signal, opponent):
        """
        Risk for a known type.
        """
        signal_risk = 0.
        for response, response_belief in self.current_response_belief()[signal].items():
            payoff = self.baby_payoffs[response] + self.social_payoffs[opponent.player_type][signal]
            payoff = self.loss(payoff)
                #print "Believe payoff will be",payoff,"with confidence",payoff_belief
                #print "Risk is",payoff,"*",payoff_belief
            signal_risk += payoff * response_belief
       #print "R(%d|x)=%f" % (signal, signal_risk)
        return signal_risk


class FuzzySignaller(RecognitionSignaller):
    """
    A signalling agent that remembers types and can deal with
    ambiguous information about them.
    """

    def __str__(self):
        return "fuzzy"

    def fuzzy_update_beliefs(self, response, midwife, payoff, possible_types):
        """
        A fuzzy update of type beliefs. Updates based on the possible types
        for this payoff.
        """
        print "Called with possible types", possible_types
        # If we've already learned the true type, then this is moot
        if hash(midwife) in self.type_memory:
            self.update_beliefs(response, midwife, payoff)
            return
        else:
            # Update general response beliefs
            super(RecognitionSignaller, self).update_beliefs(response, None, payoff)
            self.update_type_distribution(possible_types)

    def update_type_distribution(self, possible_types):
        """
        Update beliefs on distributions for a number of possible
        types.
        """
        for midwife_type in possible_types:
            self.type_matches[midwife_type] += 1.

        for player_type, estimate in self.type_distribution.items():
            alpha_k = self.type_weights[player_type]
            n_k = self.type_matches[player_type]
            n = sum(self.type_matches.values())
            alpha_dot = sum(self.type_weights)
            estimate.append((alpha_k + n_k) / float(alpha_dot + n))

    def risk(self, signal, opponent):
        """
        Risk here is based on the belief about a specific opponent rather
        than the general case. If the opponent has not been encountered
        before, then the decision is based on the general beliefs.
        """
        if hash(opponent) in self.type_memory:
            #print "Known type."
            signal_risk = self.known_type_risk(signal, opponent)
        else:
            signal_risk = super(RecognitionSignaller, self).risk(signal, opponent)
        #print "R(%d|x)=%f" % (signal, signal_risk)
        return signal_risk

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

    def update_beliefs(self, payoff, signaller, signal, signaller_type=None):
        """
        Update beliefs, and do so retrospectively for as many signal-response
        pairs as we have for this signaller.
        """
        if signaller is None:
            return super(RecognitionResponder, self).update_beliefs(payoff, signaller, signal)
        #Need to work with an artificial response log while bulk updating
        tmp_response_log = self.response_log
        mem = self.signal_memory.pop(hash(signaller), [])
        while len(mem) > 0:
            signal, response = mem.pop()
            payoff = self.payoffs[signaller.player_type][response]
            self.response_log = [response]
            super(RecognitionResponder, self).update_beliefs(payoff, signaller, signal)

        self.response_log = tmp_response_log
