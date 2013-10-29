import random


def random_expectations(depth=0, breadth=3, low=0, high=10):
    initial = [low, high]
    for i in range(breadth - 1):
        initial.append(random.random()*high)
    initial.sort()
    results = []
    for i in range(breadth):
        if depth == 0:
            results.append(float(initial[i + 1] - initial[i]))
        else:
            results.append(random_expectations(depth - 1, breadth))
    return results


def shuffled(target):
    """
    Return a shuffled version of the argument
    """
    a = list(target)
    random.shuffle(a)
    return a


class Agent(object):
    """
    An agent who plays a game, according to their
    type, and some decision rule.
    Players are one of three types.
    0 = low
    1 = middle
    2 = high

    Players have two possible response moves.
    0 = do nothing
    1 = refer
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        self.player_type = player_type
        self.signals = signals
        self.responses = responses
        self.payoff_log = []
        self.signal_log = []
        self.response_log = []
        self.type_log = []
        self.rounds = 0
        self.payoffs = None
        self.social_payoffs = None
        self.baby_payoffs = None
        self.signal_matches = dict([(y, 0.) for y in signals])
        self.finished = 0
        self.is_finished = False


class Signaller(Agent):

    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Given own type, there are always 6 possible payoffs for a given signal.
        # 2 for each of the three midwife types, per signal.
        self.response_belief = self.response_belief_dict(signals, responses)
        self.type_distribution = dict([(signal, []) for signal in signals])
        self.type_matches = dict([(signal, 0.) for signal in signals])
        self.response_signal_matches = self.response_signal_dict(signals, responses)
        super(Signaller, self).__init__(player_type, signals, responses)

    def response_signal_dict(self, signals, responses):
        return dict([(signal, dict([(response, 0.) for response in responses])) for signal in signals])

    def response_belief_dict(self, signals, responses):
        return dict([(signal, dict([(response, []) for response in responses])) for signal in signals])

    def init_payoffs(self, baby_payoffs, social_payoffs, type_weights=[1., 1., 1.], 
                     response_weights=[[1., 1.], [1., 1.], [1., 2.]]):
        # Don't set up twice.
        if self.baby_payoffs is not None:
            return
        #Only interested in payoffs for own type
        self.baby_payoffs = baby_payoffs[self.player_type]
        self.social_payoffs = social_payoffs
        self.type_weights = type_weights
        self.response_weights = response_weights
        #Response per signal per type
        self.update_beliefs(None, None, None)

    def current_response_belief(self):
        """
        Return the most recent set of response beliefs.
        """
        result = {}

        for signal, responses in self.response_belief.items():
            #signal_matches = [x == signal for x in self.signal_log]
            result[signal] = {}
            for response, belief in responses.items():
                result[signal][response] = belief[len(belief) - 1]
        return result

    def current_type_distribution(self):
        """
        Return the most current believed type distribution.
        """
        result = {}
        for signal, record in self.type_distribution.items():
            result[signal] = record[len(record) - 1]
        return result

    def update_beliefs(self, response, midwife, payoff):
        if payoff is not None:
            self.payoff_log.append(payoff)
        rounds = self.rounds

        # Update type beliefs
        if midwife is not None:
            midwife_type = midwife.player_type
            self.type_log.append(midwife_type)
            self.type_matches[midwife_type] += 1

        for player_type, estimate in self.type_distribution.items():
            alpha_k = self.type_weights[player_type]
            n_k = self.type_matches[player_type]
            n = sum(self.type_matches.values())
            alpha_dot = sum(self.type_weights)
            estimate.append((alpha_k + n_k) / float(alpha_dot + n))

        # Update signal-response beliefs

        if response is not None:
            self.response_log.append(response)
            #self.response_matches[response] += 1.
            self.response_signal_matches[self.signal_log[rounds - 1]][response] += 1.

        #response_matches = {}
        #for response in self.responses:
        #    response_matches[response] = [x == response for x in self.response_log]

        for signal, responses in self.response_belief.items():
            #signal_matches = [x == signal for x in self.signal_log]

            for response, belief in responses.items():
                #matched_pairs = zip(response_matches[response], signal_matches)
                #response_signal_matches = [a and b for a, b in matched_pairs]

                n_k = self.response_signal_matches[signal][response]

                # Rounds where we sent this signal
                n = float(self.signal_matches[signal])

                #print "Payoff-Signal matches", signal_payoff_matches

                #P(response) in this state of the world
                alpha_k = self.response_weights[signal][response]
                alpha_dot = sum(self.response_weights[signal])
                prob = (alpha_k + n_k) / float(alpha_dot + n)
               #print "Probability = (%f + %d) / (%d + (%d - 1)) = %f" % (alpha_k, n_k, alpha_dot, n, prob)

                belief.append(prob)

    def log_signal(self, signal, opponent=None):
        self.signal_matches[signal] += 1
        self.signal_log.append(signal)


class BayesianSignaller(Signaller):
    def loss(self, payoff):
        """ Make a loss out of a payoff.
        """
        return -payoff

    def risk(self, signal, appointment, opponent):
        """
        Compute the bayes risk of sending this signal.
        """
        signal_risk = 0.
        for player_type, log in self.type_distribution.items():
            type_belief = log[appointment]
            for response, belief in self.response_belief[signal].items():
                response_belief = belief[appointment]
                payoff = self.baby_payoffs[response] + self.social_payoffs[player_type][signal]
                payoff = self.loss(payoff)
                #print "Believe payoff will be",payoff,"with confidence",payoff_belief
                #print "Risk is",payoff,"*",payoff_belief
                signal_risk += payoff * response_belief * type_belief
       #print "R(%d|x)=%f" % (signal, signal_risk)
        return signal_risk

    def do_signal(self, opponent=None, rounds=None):
        best = (random.randint(0, 2), 9999999)
        if rounds is None:
            rounds = self.rounds
       #print "Type %d woman evaluating signals." % self.player_type
        for signal in shuffled(self.signals):
            signal_risk = self.risk(signal, rounds, opponent)
           #print "Risk for signal %d is %f. Best so far is signal %d at %f." % (signal, signal_risk, best[0], best[1])
            if signal_risk < best[1]:
                best = (signal, signal_risk)
        self.rounds += 1
        self.log_signal(best[0], opponent)
        return best[0]


class BayesianWealthSignaller(BayesianSignaller):
    def loss(self, payoff):
        """ Make a loss out of a payoff including earnings so far.
        """
        return -(payoff + sum(self.payoff_log))


class MiniMaxSignaller(Signaller):
    """ A signaller which uses straight minimax, ignoring the
    risks.
    """

    def get_payoffs(self, signal):
        """
        Return a list of the possible payoffs for a signal.
        """
        payoffs = []
        for i in self.signals:
            for j in self.responses:
                payoffs.append(self.baby_payoffs[signal][j] + self.social_payoffs[i])
        return payoffs

    def do_signal(self, signal):

        worst_case = {}
        for signal in self.signals:
            worst_case[signal] = min(self.get_payoffs(signal))

        best = (0, -99999)
        for signal in self.signals:
            if best[1] < worst_case[signal]:
                best = (signal, worst_case[signal])

        self.rounds += 1
        self.log_signal(best[0])
        return best[0]


class Responder(Agent):

    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
        # Belief that a particular signal means a state
        self.signal_belief = dict([(y, dict([(x, []) for x in signals])) for y in signals])
        self.signal_type_matches = dict([(y, dict([(x, 0.) for x in signals])) for y in signals])

        super(Responder, self).__init__(player_type, signals, responses)

    def init_payoffs(self, payoffs, type_weights=[[10., 2., 1.], [1., 10., 1.], [1., 1., 10.]]):
        self.type_weights = type_weights
        #Only interested in payoffs for own type
        self.payoffs = payoffs
        self.update_beliefs(None, None)

    def update_beliefs(self, payoff, signaller):
        rounds = self.rounds
        if signaller is not None:
            signaller_type = signaller.player_type
            self.type_log.append(signaller_type)
            #self.type_matches[signaller_type] += 1
            self.signal_type_matches[self.signal_log[rounds - 1]][signaller_type] += 1
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
                n = self.signal_matches[signal_i]
               #print "n = %d" % n

                #matched_pairs = zip(type_matches[player_type], signal_matches)
                #signal_type_matches = [a and b for a, b in matched_pairs]
                n_k = self.signal_type_matches[signal_i][player_type]
               #print "n_k = %d" % n_k
                prob = (alpha_k + n_k) / float(alpha_dot + n)
               #print "Probability = (%f + %d) / (%d + (%d - 1)) = %f" % (alpha_k, n_k, alpha_dot, n, prob)
                self.signal_belief[signal_i][player_type].append(prob)

    def current_beliefs(self):
        """ Return the current beliefs about signals.
        """
        current = {}
        for signal, types in self.signal_belief.items():
            current[signal] = {}
            for player_type, log in types.items():
                current[signal][player_type] = log[self.rounds]
        return current


class BayesianResponder(Responder):
    """ Responds based on belief, and the bayes action rule.
    i.e. minimise the expected risk.
    """

    def loss(self, payoff):
        """ Transmute a payoff into a loss value.
        """
        return -payoff

    def risk(self, act, signal, appointment, opponent):
        """
        Return the expected risk of this action given this signal
        was received.
        """
        act_risk = 0.

       #print "Assessing risk for action",act,"given signal",signal
        for player_type, belief in self.signal_belief[signal].items():
            type_belief = belief[appointment]
            payoff = self.loss(self.payoffs[player_type][act])
           #print "Believe true type is",player_type,"with confidence",type_belief
           #print "Risk is",payoff,"*",type_belief
            act_risk += payoff * type_belief
       #print "R(%d|%d)=%f" % (act, signal, act_risk)
        return act_risk

    def respond(self, signal, rounds=None, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent by minimising bayesian risk.
        """
        if rounds is None:
            self.signal_log.append(signal)
            self.signal_matches[signal] += 1.
            rounds = self.rounds
        best = (random.randint(0, 1), 9999999)
        for response in shuffled(self.responses):
            act_risk = self.risk(response, signal, rounds, opponent)
            if act_risk < best[1]:
                best = (response, act_risk)
        self.response_log.append(best[0])
        self.rounds += 1
        return best[0]


class BayesianWealthResponder(BayesianResponder):
    def loss(self, payoff):
        """ Make a loss out of a payoff including earnings so far.
        """
        return -(payoff + sum(self.payoff_log))


class MiniMaxResponder(Responder):

    def get_payoffs(self, response):
        payoffs = []
        for player_type in self.signals:
            payoffs.append(self.payoffs[player_type][response])
        return payoffs

    """ A responder which uses straight minimax, ignoring the
    risks.
    """

    def respond(self, signal, opponent):
        self.rounds += 1
        self.signal_log.append(signal)

        worst_case = {}
        for response in self.responses:
            worst_case[response] = min(self.get_payoffs(response))
        best = (0, -99999)
        for response in self.responses:
            if best[1] < worst_case[response]:
                best = (response, worst_case[response])
        self.response_log.append(best[0])
        return best[0]


class Game(object):
    def __init__(self, num_rounds=1, baby_payoff=2, no_baby_payoff=2, mid_baby_payoff=1,referral_cost=1, harsh_high=2,
     harsh_mid=1, harsh_low=0, mid_high=1, mid_mid=0, mid_low=0, low_high=0,low_mid=0,low_low=0, randomise_payoffs=False):
        """ A multistage game played by two agents.
        """
        self.signal_log = []
        self.act_log = []
        self.disclosure_log = []
        self.woman_baby_payoff = [[0, 0] for x in range(3)]
        self.woman_social_payoff = [[0, 0, 0] for x in range(3)]
        self.midwife_payoff = [[0, 0] for x in range(3)]
        self.num_rounds = num_rounds
        self.payoffs = {}

        if randomise_payoffs:
            self.random_payoffs()
        else:
            self.payoffs["baby_payoff"] = baby_payoff
            self.payoffs["no_baby_payoff"] = -no_baby_payoff
            self.payoffs["mid_baby_payoff"] = -mid_baby_payoff
            self.payoffs["referral_cost"] = -referral_cost

            self.payoffs["harsh_high"] = -harsh_high
            self.payoffs["harsh_mid"] = -harsh_mid
            self.payoffs["harsh_low"] = -harsh_low
            self.payoffs["mid_high"] = -mid_high
            self.payoffs["mid_mid"] = -mid_mid
            self.payoffs["mid_low"] = -mid_low
            self.payoffs["low_high"] = -low_high
            self.payoffs["low_mid"] = -low_mid
            self.payoffs["low_low"] = -low_low

    def random_payoffs(self):

        self.payoffs["baby_payoff"] = random.randint(0, 100)
        self.payoffs["no_baby_payoff"] = random.randint(-100, 0)
        self.payoffs["mid_baby_payoff"] = random.randint(self.payoffs["no_baby_payoff"], 0)
        self.payoffs["referral_cost"] = random.randint(self.payoffs["no_baby_payoff"], 0)

        self.payoffs["harsh_high"] = random.randint(self.payoffs["mid_baby_payoff"], 0)
        self.payoffs["harsh_mid"] = random.randint(self.payoffs["harsh_high"], 0)
        self.payoffs["harsh_low"] = random.randint(self.payoffs["harsh_mid"], 0)
        self.payoffs["mid_high"] = random.randint(self.payoffs["harsh_low"], 0)
        self.payoffs["mid_mid"] = random.randint(self.payoffs["mid_high"], 0)
        self.payoffs["mid_low"] = random.randint(self.payoffs["mid_mid"], 0)
        self.payoffs["low_high"] = random.randint(self.payoffs["mid_low"], 0)
        self.payoffs["low_mid"] = random.randint(self.payoffs["low_high"], 0)
        self.payoffs["low_low"] = random.randint(self.payoffs["low_mid"], 0)

    def init_payoffs(self, type_weights=[[10., 1., 1.], [1., 10., 1.], [1., 1., 10.]]):
        self.type_weights = type_weights
        #Midwife payoffs
        #Light drinker
        self.midwife_payoff[0][0] = self.payoffs["baby_payoff"]
        self.midwife_payoff[0][1] = self.payoffs["baby_payoff"] + self.payoffs["referral_cost"]

        #Moderate drinker
        self.midwife_payoff[1][0] = self.payoffs["mid_baby_payoff"]
        self.midwife_payoff[1][1] = self.payoffs["baby_payoff"] + self.payoffs["referral_cost"]

        #Heavy drinker
        self.midwife_payoff[2][0] = self.payoffs["no_baby_payoff"]
        self.midwife_payoff[2][1] = self.payoffs["baby_payoff"] + self.payoffs["referral_cost"]

        #Woman's payoff
        #[woman type][action]

        self.woman_baby_payoff[0][0] = self.payoffs["baby_payoff"]
        self.woman_baby_payoff[1][0] = self.payoffs["mid_baby_payoff"]
        self.woman_baby_payoff[2][0] = self.payoffs["no_baby_payoff"]

        self.woman_baby_payoff[0][1] = self.payoffs["baby_payoff"]
        self.woman_baby_payoff[1][1] = self.payoffs["baby_payoff"]
        self.woman_baby_payoff[2][1] = self.payoffs["baby_payoff"]

        #[midwife_type][signal]
        self.woman_social_payoff[0][0] = self.payoffs["low_low"]
        self.woman_social_payoff[1][0] = self.payoffs["mid_low"]
        self.woman_social_payoff[2][0] = self.payoffs["harsh_low"]

        self.woman_social_payoff[0][1] = self.payoffs["low_mid"]
        self.woman_social_payoff[1][1] = self.payoffs["mid_mid"]
        self.woman_social_payoff[2][1] = self.payoffs["harsh_mid"]

        self.woman_social_payoff[0][2] = self.payoffs["low_high"]
        self.woman_social_payoff[1][2] = self.payoffs["mid_high"]
        self.woman_social_payoff[2][2] = self.payoffs["harsh_high"]

    def priors(self):
        priors = {}
        for i in range(3):
            for j in range(3):
                priors["prior_%d_%d" % (i, j)] = self.type_weights[i][j]
        return priors

    def play_round(self, signaller, receiver):
        """ Play a round of this game between the
        two players.
        """
        signal = signaller.do_signal(receiver)
        act = receiver.respond(signal)
        signal_payoff = self.woman_baby_payoff[signaller.player_type][act] + self.woman_social_payoff[signal][receiver.player_type]
        receive_payoff = self.midwife_payoff[signaller.player_type][act]
        #self.signal_log.append(signal)
        #self.act_log.append(act)
        signaller.update_beliefs(act, receiver, signal_payoff)
        receiver.update_beliefs(receive_payoff, signaller)
        # Log honesty of signal
        #self.disclosure_log.append(signal == signaller.player_type)

    def play_game(self, signaller, receiver):
        #signaller.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff, random_expectations(), [random_expectations(breadth=2) for x in range(3)])
        #receiver.init_payoffs(self.midwife_payoff, self.type_weights)
        for r in range(self.num_rounds):
            self.play_round(signaller, receiver)
