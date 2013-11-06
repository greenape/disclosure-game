from Model import *


class RecognitionSignaller(BayesianSignaller):
    """
    A signalling agent which recognises and remembers opponents.
    The general belief about types of opponent is used as the
    prior for subsequent updates about individuals.
    After observing the true type of an individual, the belief on
    this immediately goes to 1 since it is certain.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Per midwife response -> referral beliefs
        self.individual_response_belief = {}
        # Midwife type memory
        self.type_memory = {}
        # Per midwife response -> signal matches
        self.individual_response_signal_matches = {}
        # Per midwife signals
        self.individual_signal_matches = {}
        # Mapping from all appointments to those with an individual
        self.appointment_memory = {}
        # Individual type distributions
        self.individual_type_distribution = {}
        self.individual_type_matches = {}

        super(RecognitionSignaller, self).__init__(player_type, signals, responses)

    def individual_current_type_distribution(self, midwife):
        """
        Return the most current believed type distribution
        for a midwife.
        """
        if midwife not in self.individual_type_distribution:
            return self.current_type_distribution()
        result = {}
        for signal, record in self.individual_type_distribution[midwife].items():
            result[signal] = record[len(record) - 1]
        return result

    def update_beliefs(self, response, midwife, payoff, midwife_type=None):
        """
        This class of agent maintains two sets of beliefs. Beliefs about
        the general world, and about particular opponents.
        New information about an opponent updates the beliefs about both
        that player, and the general class of opponents.
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
            self.type_memory[midwife] = midwife.player_type
        # Individual specific reponse beliefs
        # Update signal-response beliefs
        self.update_signal_response_beliefs(midwife, response)

    def update_signal_response_beliefs(self, midwife, response):
        """
        Update the set of individual beliefs held about this midwife.
        """
        current = self.current_response_belief()
        if not midwife in self.individual_response_signal_matches:
            self.individual_response_signal_matches[midwife] = self.response_signal_dict(self.signals, self.responses)
            self.individual_response_belief[midwife] = self.response_belief_dict(self.signals, self.responses)


        self.individual_response_signal_matches[midwife][self.signal_log[self.rounds - 1]][response] += 1.

        for signal, responses in self.individual_response_belief[midwife].items():
            #signal_matches = [x == signal for x in self.signal_log]

            for response, belief in responses.items():
                #matched_pairs = zip(response_matches[response], signal_matches)
                #response_signal_matches = [a and b for a, b in matched_pairs]

                n_k = self.individual_response_signal_matches[midwife][signal][response]

                # Rounds where we sent this signal to this midwife
                n = float(self.individual_signal_matches[midwife][signal])

                #print "Payoff-Signal matches", signal_payoff_matches

                #P(response) in this state of the world
                alpha_k = current[signal][response]
                alpha_dot = sum(current[signal])
                prob = (alpha_k + n_k) / float(alpha_dot + n)
               #print "Probability = (%f + %d) / (%d + (%d - 1)) = %f" % (alpha_k, n_k, alpha_dot, n, prob)

                belief.append(prob)

    def fuzzy_update_beliefs(self, response, midwife, payoff, possible_types):
        """
        A fuzzy update of type beliefs. Updates based on the possible types
        for this payoff.
        """
        #print "Called with possible types", possible_types
        # If we've already learned the true type, then this is moot
        if midwife in self.type_memory:
            self.update_beliefs(response, midwife, payoff)
            return
        else:
            # Update general response beliefs
            super(RecognitionSignaller, self).update_beliefs(response, None, payoff)
            self.update_type_distribution(possible_types)
            # Update individual type distribution
            current = self.current_type_distribution()
            if not midwife in self.individual_type_matches:
                self.individual_type_matches[midwife] = dict([(signal, 0.) for signal in self.signals])
                self.individual_type_distribution[midwife] = dict([(signal, []) for signal in self.signals])

            # Update type beliefs
            if midwife is not None:
                self.type_log.append(midwife.player_type)

                for midwife_type in possible_types:
                    #self.type_matches[midwife_type] += 1. / len(possible_types)
                    self.individual_type_matches[midwife][midwife_type] += 1.

            for player_type, estimate in self.individual_type_distribution[midwife].items():
                alpha_k = current[player_type]
                n_k = self.individual_type_matches[midwife][player_type]
                n = sum(self.individual_type_matches[midwife].values())
                alpha_dot = sum(current.values())
                estimate.append((alpha_k + n_k) / float(alpha_dot + n))

        # Update individual response beliefs
        self.update_signal_response_beliefs(midwife, response)

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
        #if opponent in self.type_memory:
        #    signal_risk = self.known_type_risk(signal, opponent)
        if opponent in self.individual_type_distribution:
            signal_risk = self.type_risk(signal, opponent)
        else:
            signal_risk = super(RecognitionSignaller, self).risk(signal, opponent)
       #print "R(%d|x)=%f" % (signal, signal_risk)
        return signal_risk

    def known_type_risk(self, signal, opponent):
        """
        Risk for a known type.
        """
        signal_risk = 0.
        for response, belief in self.individual_response_belief[opponent][signal].items():
                response_belief = belief[len(belief) - 1]
                payoff = self.baby_payoffs[response] + self.social_payoffs[self.type_memory[opponent]][signal]
                payoff = self.loss(payoff)
                #print "Believe payoff will be",payoff,"with confidence",payoff_belief
                #print "Risk is",payoff,"*",payoff_belief
                signal_risk += payoff * response_belief
        return signal_risk

    def type_risk(self, signal, opponent):
        """
        Risk for an unknown type individual encountered before.
        """
        signal_risk = 0.
        for player_type, type_belief in self.individual_current_type_distribution(opponent).items():
                #type_belief = log[len(log) - 1]
                for response, belief in self.individual_response_belief[opponent][signal].items():
                    response_belief = belief[len(belief) - 1]
                    payoff = self.baby_payoffs[response] + self.social_payoffs[player_type][signal]
                    payoff = self.loss(payoff)
                    #print "Believe payoff will be",payoff,"with confidence",payoff_belief
                    #print "Risk is",payoff,"*",payoff_belief
                    signal_risk += payoff * response_belief * type_belief
        return signal_risk

    def log_signal(self, signal, opponent):
        super(RecognitionSignaller, self).log_signal(signal, opponent)
        if not opponent in self.individual_signal_matches:
            self.individual_signal_matches[opponent] = dict([(y, 0.) for y in self.signals])
        self.individual_signal_matches[opponent][signal] += 1


class RecognitionResponder(BayesianResponder):
    """
    Class of responder which remembers the actions of opponents and then retrospectively
    updates beliefs based on that when true information is available.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Memory of a particular agent's signals.
        self.signal_memory = {}
        self.type_memory = {}

        super(RecognitionResponder, self).__init__(player_type, signals, responses)

    def respond(self, signal, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent by minimising bayesian risk.
        """
        self.fuzzy_update_beliefs(opponent, signal)
        return super(RecognitionResponder, self).respond(signal, opponent)

    def fuzzy_update_beliefs(self, signaller, signal):
        # Nothing to do if we know the type already
        if signaller in self.type_memory:
            return super(RecognitionResponder, self).update_beliefs(None, signaller)
        if not signaller in self.signal_memory:
            self.signal_memory[signaller] = [signal]
            return
        self.signal_memory[signaller].append(signal)

    def update_beliefs(self, payoff, signaller):
        if signaller is None:
            return super(RecognitionResponder, self).update_beliefs(payoff, signaller)
        self.type_memory[signaller] = signaller.player_type

        rounds = self.rounds
        signaller_type = signaller.player_type
        self.type_log.append(signaller_type)
        
        for signal in self.signals:
            sent = len(filter(lambda x: x == signal, self.signal_memory[signaller]))
            self.signal_type_matches[signal][signaller_type] += sent
        self.signal_memory[signaller] = []
        
        if payoff is not None:
            self.payoff_log.append(payoff)

        #type_matches = {}
        #for player_type in self.signals:
        #    type_matches[player_type] = [x == player_type for x in self.type_log]

        for signal_i, types in self.signal_belief.items():
            for player_type, belief in types.items():
                #signal_matches = [x == signal_i for x in self.signal_log]
                #print "Updating P(%d|%d).." % (player_type, signal_i)
                alpha_k = self.type_weights[signal_i][player_type]
                #print "alpha_k = %f" % alpha_k
                alpha_dot = sum(self.type_weights[signal_i])
                #print "Num alternatives = %d" % alpha_dot
                #n = self.signal_matches[signal_i]
                n = sum(self.signal_type_matches[signal_i].values())
                #print "n = %d" % n

                #matched_pairs = zip(type_matches[player_type], signal_matches)
                #signal_type_matches = [a and b for a, b in matched_pairs]
                n_k = self.signal_type_matches[signal_i][player_type]
                #print "n_k = %d" % n_k
                prob = (alpha_k + n_k) / float(alpha_dot + n)
                #print "Probability = (%f + %d) / (%d + (%d - 1)) = %f" % (alpha_k, n_k, alpha_dot, n, prob)
                self.signal_belief[signal_i][player_type].append(prob)
