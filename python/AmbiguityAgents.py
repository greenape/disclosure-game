from RecognitionAgents import *


class AmbiguitySignaller(FuzzySignaller):
    """
    A class of signaller that uses the Fryer model for resolving ambiguity
    in observations. i.e. confirmation bias.

    Fryer Jr., R.G., Harms, P. & Jackson, M., 2013. 
    Updating Beliefs with Ambiguous Evidence: Implications for Polarization., 02138(July), pp.1-22.
    """

    def __str__(self):
        return "ambiguity"

    def fuzzy_update_beliefs(self, response, midwife, payoff, possible_types):
        """
        This class of agent uses their existing beliefs to resolve
        the ambiguity of the possible types by finding the maximum
        likelihood and assuming this is the truth.
        """

        max_type = random.choice(possible_types)
        current = self.individual_current_type_distribution(midwife)
        likelihood = current[max_type]
        for t in possible_types:
            if current[t] > likelihood:
                likelihood = current[t]
                max_type = t
        #print "Possible types were", possible_types,"resolved to",max_type,"with p", likelihood
        super(AmbiguitySignaller, self).update_beliefs(response, midwife, payoff, midwife_type=max_type)


class AmbiguityResponder(RecognitionResponder):
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        self.individual_signal_belief = {}
        self.individual_signal_type_matches = {}
        self.individual_weights = {}
        self.individual_signal_matches = {}

        super(AmbiguityResponder, self).__init__(player_type, signals, responses)

    def __str__(self):
        return "ambiguity"

    def fuzzy_update_beliefs(self, signaller, signal):
        max_type = random.choice(self.signals)
        current = self.individual_current_type_distribution(signaller)
        likelihood = current[max_type]
        for t in self.signals:
            if current[t] > likelihood:
                likelihood = current[t]
                max_type = t

        self.update_beliefs(None, signaller, signal, signaller_type=max_type)

    def update_beliefs(self, payoff, signaller, signal, signaller_type=None):
        if signaller_type is None:
            return super(AmbiguityResponder, self).update_beliefs(payoff, signaller, signal)
        if signaller is not None:
            if signaller not in self.individual_signal_belief:
                self.individual_signal_belief[signaller] = dict([(y, dict([(x, []) for x in self.signals])) for y in self.signals])
                self.individual_signal_type_matches[signaller] = dict([(y, dict([(x, 0.) for x in self.signals])) for y in self.signals])
                self.individual_signal_matches[signaller] = dict([(y, 0.) for y in self.signals])
                self.individual_weights[signaller] = list(self.type_weights)
                # This is wrong because you were treating it like a dict.
                for signal in self.individual_weights[signaller]:
                    for player_type in self.individual_weights[signaller][signal]:
                        self.individual_weights[signaller][signal][player_type] += self.signal_type_matches[signal][player_type]

            else:
                self.individual_signal_type_matches[signaller][signal][signaller_type] += 1.
                self.individual_signal_matches[signaller][signal] += 1.
        if payoff is not None:
            self.payoff_log.append(payoff)

        #type_matches = {}
        #for player_type in self.signals:
        #    type_matches[player_type] = [x == player_type for x in self.type_log]

        for signal_i, types in self.individual_signal_belief[signaller].items():
            for player_type, belief in types.items():
                #signal_matches = [x == signal_i for x in self.signal_log]
               #print "Updating P(%d|%d).." % (player_type, signal_i)
                alpha_k = self.individual_type_weights[signaller][signal_i][player_type]
               #print "alpha_k = %f" % alpha_k
                alpha_dot = sum(self.individual_type_weights[signaller][signal_i])
               #print "Num alternatives = %d" % alpha_dot
                n = self.individual_signal_matches[signaller][signal_i]
               #print "n = %d" % n

                #matched_pairs = zip(type_matches[player_type], signal_matches)
                #signal_type_matches = [a and b for a, b in matched_pairs]
                n_k = self.individual_signal_matches[signaller][signal_i][player_type]
               #print "n_k = %d" % n_k
                prob = (alpha_k + n_k) / float(alpha_dot + n)
               #print "Probability = (%f + %d) / (%d + (%d - 1)) = %f" % (alpha_k, n_k, alpha_dot, n, prob)
                belief.append(prob)

    def risk(self, act, signal, opponent):
        """
        Return the expected risk of this action given this signal
        was received.
        """
        act_risk = 0.

       #print "Assessing risk for action",act,"given signal",signal
        for player_type, type_belief in self.individual_current_type_distribution(opponent)[signal].items():
            payoff = self.loss(self.payoffs[player_type][act])
           #print "Believe true type is",player_type,"with confidence",type_belief
           #print "Risk is",payoff,"*",type_belief
            act_risk += payoff * type_belief
       #print "R(%d|%d)=%f" % (act, signal, act_risk)
        return act_risk

    def individual_current_type_distribution(self, signaller):
        """ Return the current beliefs about signals.
        """
        if signaller not in self.individual_signal_belief:
            return self.current_beliefs()
        current = {}
        for signal, types in self.individual_signal_belief[signaller].items():
            current[signal] = {}
            for player_type, log in types.items():
                current[signal][player_type] = log[len(log) - 1]
        return current
