from random import Random
from Measures import measures_midwives, measures_women
from collections import OrderedDict
from itertools import count
from copy import deepcopy

try:
    import scoop
    scoop.worker
    scoop_on = True
    LOG = scoop.logger
except:
    scoop_on = False
    import multiprocessing
    LOG = multiprocessing.get_logger()
    pass

def random_expectations(depth=0, breadth=3, low=1, high=10, random=Random()):
    """
    Generate depth x breadth array of random numbers where each row sums to
    high, with a minimum of low.
    """
    result = []
    if depth == 0:
        initial = high + 1
        for i in range(breadth - 1):
            n = random.randint(low, initial - (low * (breadth - i)))
            initial -= n
            result.append(n)
        result.append(initial - low)
        random.shuffle(result)
    else:
        result = [random_expectations(depth - 1, breadth, low, high, random) for x in range(breadth)]
    return result

def weighted_random_choice(choices, weights, random=Random()):
    population = [val for val, cnt in zip(choices, weights) for i in range(int(cnt))]
    return random.choice(population)

def shuffled(target, random=Random()):
    """
    Return a shuffled version of the argument
    """
    a = list(target)
    random.shuffle(a)
    return a


class Agent(object):
    id_generator = count()
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
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1], seed=None):
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
        self.signal_matches = dict.fromkeys(signals, 0.)#dict([(y, 0.) for y in signals])
        self.finished = 0
        self.started = 0
        self.is_finished = False
        self.accrued_payoffs = 0
        self.random = Random(seed)
        self.ident = Agent.id_generator.next()

    def __hash__(self):
        return self.ident

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        result.ident = Agent.id_generator.next()
        return result


class Signaller(Agent):

    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1], seed=None):
        # Given own type, there are always 6 possible payoffs for a given signal.
        # 2 for each of the three midwife types, per signal.
        self.response_belief = self.response_signal_dict(signals, responses)
        self.type_distribution = {s:[] for s in signals}#dict([(signal, []) for signal in signals])
        self.type_matches = dict.fromkeys(signals, 0.)#dict([(signal, 0.) for signal in signals])
        self.response_signal_matches = self.response_signal_dict(signals, responses)
        #self.risk_log = dict([(signal, []) for signal in signals])
        #self.risk_log_general = dict([(signal, []) for signal in signals])
        super(Signaller, self).__init__(player_type, signals, responses, seed)

    def response_signal_dict(self, signals, responses):
        return {s:dict.fromkeys(responses, 0.) for s in signals}

    def response_belief_dict(self, signals, responses):
        return {s:{k:[] for k in responses} for s in signals}#dict([(signal, dict([(response, []) for response in responses])) for signal in signals])

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

        # Front load alpha_dot values
        for signal, responses in self.response_signal_matches.iteritems():
            for response, count in responses.iteritems():
                self.response_signal_matches[signal][response] = response_weights[signal][response]
        #Response per signal per type
        self.update_counts(None, None, None)
        self.update_beliefs()

    def init_payoffs_(self, baby_payoffs, social_payoffs, type_weights=[1., 1., 1.], 
                     response_weights=[[1., 1.], [1., 1.], [1., 2.]], num=10):
        """
        An alternative way of generating priors by using the provided weights
        as weightings for random encounters.
        """
        # Don't set up twice.
        if self.baby_payoffs is not None:
            return
        #Only interested in payoffs for own type
        self.baby_payoffs = baby_payoffs[self.player_type]
        self.social_payoffs = social_payoffs
        self.type_weights = [0., 0., 0.]
        self.response_weights = response_weights

        for i in xrange(num):
            # Choose a random signal
            signal = self.random.choice(self.signals)
            # A weighted response
            response = weighted_random_choice(self.responses, response_weights[signal], self.random)
            # A weighted choice of type
            player_type = weighted_random_choice(self.signals, type_weights, self.random)
            # Payoffs
            payoff = baby_payoffs[self.player_type][response] + social_payoffs[signal][player_type]
            self.response_signal_matches[signal][response] += 1
            self.type_weights[player_type] += 1
        
        self.update_counts(None, None, None)
        self.update_beliefs()

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

    def round_response_belief(self, rounds):
        result = {}
        try:
            for signal, responses in self.response_belief.items():
                #signal_matches = [x == signal for x in self.signal_log]
                result[signal] = {}
                for response, belief in responses.items():
                    result[signal][response] = belief[rounds]
            return result
        except IndexError:
            return self.current_response_belief()

    def current_signal_risk(self):
        result = {}
        for signal, risk in self.risk_log.items():
            result[signal] = risk[len(risk) - 1]
        return result

    def round_signal_risk(self, rounds):
        try:
            result = {}
            for signal, risk in self.risk_log.items():
                result[signal] = risk[rounds]
            return result
        except IndexError:
            return self.current_signal_risk()

    def round_signal(self, rounds):
        try:
            sig = self.signal_log[rounds]
        except IndexError:
            sig = self.do_signal()
            self.signal_log.pop()
        return sig


    def current_type_distribution(self):
        """
        Return the most current believed type distribution.
        """
        result = {}
        for signal, record in self.type_distribution.items():
            result[signal] = record[len(record) - 1]
        return result

    def round_type_distribution(self, rounds):
        try:
            result = {}
            for signal, record in self.type_distribution.items():
                result[signal] = record[rounds]
            return result
        except IndexError:
            return self.current_type_distribution()

    def update_counts(self, response, midwife, payoff, midwife_type=None, weight=1.):
        """
        Update the counts of midwife types observed, payoffs received, and responses
        to signals. Counts are incremented by weight, which defaults to 1.
        """
        if payoff is not None:
            self.payoff_log.append(payoff)
        #rounds = self.rounds

        # Update type beliefs
        if midwife is not None:
            # Log true type for bookkeeping
            self.type_log.append(midwife.player_type)
            if midwife_type is None:
                midwife_type = midwife.player_type
            self.type_matches[midwife_type] += weight

        if response is not None:
            self.response_log.append(response)
            #self.response_matches[response] += 1.
            signal = self.signal_log[len(self.signal_log) - 1]
            self.response_signal_matches[signal][response] += weight

   #@profile
    def update_beliefs(self):
        """
        Update the agent's beliefs about the distribution of midwife types, and
        responses to signals.
        """

        #alpha_dot = sum(self.type_weights)
        n = float(sum(self.type_matches.values()) + sum(self.type_weights))
        for player_type, estimate in self.type_distribution.iteritems():
            alpha_k = self.type_weights[player_type]
            n_k = self.type_matches[player_type]
            
            #del estimate [:]
            #estimate.append((alpha_k + n_k) / float(alpha_dot + n))
            self.type_distribution[player_type] = 0.
            if n > 0:
                self.type_distribution[player_type] = (alpha_k + n_k) / n

        # Update signal-response beliefs
        
        for signal, responses in self.response_signal_matches.iteritems():
            # alpha_dot + n
            n = float(sum(responses.values()))
            # Count is alpha_k + n_k
            for response, count in responses.iteritems():
                self.response_belief[signal][response] = 0.
                if n > 0:
                    self.response_belief[signal][response] = count / n#prob


    def log_signal(self, signal, opponent=None, weight=1.):
        """
        Record a signal.
        """
        self.signal_matches[signal] += weight
        self.signal_log.append(signal)


class BayesianSignaller(Signaller):

    def __str__(self):
        return "bayes"

    def loss(self, payoff):
        """ Make a loss out of a payoff.
        """
        return -payoff

    def risk(self, signal, opponent):
        """
        Compute the bayes risk of sending this signal.
        """
        signal_risk = 0.
        for player_type, type_belief in self.type_distribution.items():
            for response, response_belief in self.response_belief[signal].items():
                payoff = self.baby_payoffs[response] + self.social_payoffs[player_type][signal]
                #payoff = self.loss(payoff)
                #print "Believe payoff will be",payoff,"with confidence",payoff_belief
                #print "Risk is",payoff,"*",payoff_belief
                signal_risk += -payoff * response_belief * type_belief
       #print "R(%d|x)=%f" % (signal, signal_risk)
        return signal_risk

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


class Responder(Agent):

    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1], seed=None):
        # Belief that a particular signal means a state
        self.signal_belief = {s:dict.fromkeys(signals, 0.) for s in signals} #dict([(y, dict([(x, []) for x in signals])) for y in signals])
        self.signal_type_matches = {s:dict.fromkeys(signals, 0.) for s in signals} #dict([(y, dict([(x, 0.) for x in signals])) for y in signals])

        super(Responder, self).__init__(player_type, signals, responses, seed)

    def init_payoffs(self, payoffs, type_weights=[[10., 2., 1.], [1., 10., 1.], [1., 1., 10.]]):
        self.type_weights = type_weights
        #Only interested in payoffs for own type
        self.payoffs = payoffs
        self.update_beliefs(None, None, None)

    def init_payoffs_(self, payoffs, type_weights=[[10., 2., 1.], [1., 10., 1.], [1., 1., 10.]], num=25):
        self.type_weights = [[0.]*3]*3
        for i in xrange(num):
            signal = self.random.choice(self.signals)
            self.type_weights[signal][weighted_random_choice(self.signals, type_weights[signal])] += 1
        #Only interested in payoffs for own type
        self.payoffs = payoffs
        self.update_beliefs(None, None, None)

    ##@profile
    def update_beliefs(self, payoff, signaller, signal, signaller_type=None, weight=1.):
        rounds = self.rounds
        if signaller is not None:
            signaller_type = signaller.player_type
            #self.type_matches[signaller_type] += 1
            self.signal_type_matches[signal][signaller_type] += weight
        if payoff is not None:
            self.payoff_log.append(payoff)

        #type_matches = {}
        #for player_type in self.signals:
        #    type_matches[player_type] = [x == player_type for x in self.type_log]

        for signal_i, types in self.signal_belief.iteritems():
            alpha_dot = sum(self.type_weights[signal_i])
            n = sum(self.signal_type_matches[signal_i].values())
            for player_type, belief in types.iteritems():
                #signal_matches = [x == signal_i for x in self.signal_log]
               #print "Updating P(%d|%d).." % (player_type, signal_i)
                alpha_k = self.type_weights[signal_i][player_type]
               #print "alpha_k = %f" % alpha_k
                #alpha_dot = sum(self.type_weights[signal_i])
               #print "Num alternatives = %d" % alpha_dot
                #n = sum(self.signal_type_matches[signal_i].values())
               #print "n = %d" % n

                #matched_pairs = zip(type_matches[player_type], signal_matches)
                #signal_type_matches = [a and b for a, b in matched_pairs]
                n_k = self.signal_type_matches[signal_i][player_type]
               #print "n_k = %d" % n_k
                prob = 0.
                if (alpha_dot + n) > 0:
                    prob = (alpha_k + n_k) / (alpha_dot + n)
               #print "Probability = (%f + %d) / (%d + (%d - 1)) = %f" % (alpha_k, n_k, alpha_dot, n, prob)
                #del self.signal_belief[signal_i][player_type][:]
                self.signal_belief[signal_i][player_type] = prob

    def current_beliefs(self):
        """ Return the current beliefs about signals.
        """
        current = {}
        for signal, types in self.signal_belief.items():
            current[signal] = {}
            for player_type, log in types.items():
                current[signal][player_type] = log[len(log) - 1]
        return current


class BayesianResponder(Responder):
    """ Responds based on belief, and the bayes action rule.
    i.e. minimise the expected risk.
    """

    def __str__(self):
        return "bayes"

    def loss(self, payoff):
        """ Transmute a payoff into a loss value.
        """
        return -payoff

    def risk(self, act, signal, opponent):
        """
        Return the expected risk of this action given this signal
        was received.
        """
        act_risk = 0.

       #print "Assessing risk for action",act,"given signal",signal
        for player_type, type_belief in self.signal_belief[signal].items():
            payoff = self.loss(self.payoffs[player_type][act])
           #print "Believe true type is",player_type,"with confidence",type_belief
           #print "Risk is",payoff,"*",type_belief
            act_risk += payoff * type_belief
       #print "R(%d|%d)=%f" % (act, signal, act_risk)
        return act_risk

    def respond(self, signal, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent by minimising bayesian risk.
        """
        if opponent is not None:
            self.type_log.append(opponent.player_type)
        self.signal_log.append(signal)
        self.signal_matches[signal] += 1.
        best = (self.random.randint(0, 1), 9999999)
        for response in shuffled(self.responses, self.random):
            act_risk = self.risk(response, signal, opponent)
            if act_risk < best[1]:
                best = (response, act_risk)
        self.response_log.append(best[0])
        self.rounds += 1
        #print "Player type is %d, decision is %d" % (opponent.player_type, best[0])
        return best[0]


class Game(object):
    # b > m > n
    def __init__(self, baby_payoff=2, no_baby_payoff=2, mid_baby_payoff=1,referral_cost=1, harsh_high=2,
     harsh_mid=1, harsh_low=0, mid_high=1, mid_mid=0, mid_low=0, low_high=0,low_mid=0,low_low=0, randomise_payoffs=False,
     type_weights=[[10., 1., 1.], [1., 10., 1.], [1., 1., 10.]], rounds=100, measures_women=measures_women(),
     measures_midwives=measures_midwives(), params=None, num_appointments=12, seed=None):
        """ A multistage game played by two agents.
        """
        self.random = Random(seed)
        self.signal_log = []
        self.act_log = []
        self.disclosure_log = []
        self.woman_baby_payoff = [[0, 0] for x in range(3)]
        self.woman_social_payoff = [[0, 0, 0] for x in range(3)]
        self.midwife_payoff = [[0, 0] for x in range(3)]
        self.payoffs = {}
        self.type_weights = type_weights
        self.rounds = rounds
        self.measures_women = measures_women
        self.measures_midwives = measures_midwives
        self.num_appointments = num_appointments
        if params is None:
            self.parameters = OrderedDict()
        else:
            self.parameters = params
        self.parameters['baby_payoff'] = baby_payoff
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
        self.init_payoffs()

    def random_payoffs(self):

        self.payoffs["baby_payoff"] = self.self.random.randint(0, 100)
        self.payoffs["no_baby_payoff"] = self.random.randint(-100, 0)
        self.payoffs["mid_baby_payoff"] = self.random.randint(self.payoffs["no_baby_payoff"], 0)
        self.payoffs["referral_cost"] = self.random.randint(self.payoffs["no_baby_payoff"], 0)

        self.payoffs["harsh_high"] = self.random.randint(self.payoffs["mid_baby_payoff"], 0)
        self.payoffs["harsh_mid"] = self.random.randint(self.payoffs["harsh_high"], 0)
        self.payoffs["harsh_low"] = self.random.randint(self.payoffs["harsh_mid"], 0)
        self.payoffs["mid_high"] = self.random.randint(self.payoffs["harsh_low"], 0)
        self.payoffs["mid_mid"] = self.random.randint(self.payoffs["mid_high"], 0)
        self.payoffs["mid_low"] = self.random.randint(self.payoffs["mid_mid"], 0)
        self.payoffs["low_high"] = self.random.randint(self.payoffs["mid_low"], 0)
        self.payoffs["low_mid"] = self.random.randint(self.payoffs["low_high"], 0)
        self.payoffs["low_low"] = self.random.randint(self.payoffs["low_mid"], 0)

    def init_payoffs(self):
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

    def all_played(self, women, rounds=12):
        for woman in women:
            if(woman.rounds < rounds) and not woman.is_finished:
                return False
            LOG.debug("Player %d finished after %d rounds." % (hash(woman), woman.rounds))
        return True

    def play_round(self, signaller, receiver):
        """ Play a round of this game between the
        two players.
        """
        #print "Playing between", signaller, "and", receiver
        signal = signaller.do_signal(receiver)
        #print "Signal is %d" % signal
        #print "Signaller played %d rounds" % signaller.rounds
        act = receiver.respond(signal, opponent=signaller)
        #print "Response was %d" % act
        signal_payoff = self.woman_baby_payoff[signaller.player_type][act] + self.woman_social_payoff[signal][receiver.player_type]
        receive_payoff = self.midwife_payoff[signaller.player_type][act]
        #self.signal_log.append(signal)
        #self.act_log.append(act)
        signaller.accrued_payoffs += signal_payoff
        receiver.accrued_payoffs += receive_payoff
        signaller.update_counts(act, receiver, signal_payoff)
        signaller.update_beliefs()
        receiver.update_beliefs(receive_payoff, signaller, signal)
        # Log honesty of signal
        #self.disclosure_log.append(signal == signaller.player_type)

    def play_game(self, players):
        women, midwives = players

        rounds = self.num_appointments
        birthed = []
        self.random.shuffle(women)
        while not self.all_played(women, rounds):
            woman = women.pop()
            self.play_round(woman, self.random.choice(midwives))
            if self.all_played([woman], rounds):
                birthed.append(woman)
                woman.is_finished = True
            else:
                women.insert(0, woman)
                woman.finished += 1
        return self.measure(birthed, midwives)

    def is_caseloaded(self):
        return False

    def name(self):
        return "standard"

    def measure(self, women, midwives):
        res_women = self.measures_women.dump(women, self.rounds, self)
        res_mw  = self.measures_midwives.dump(midwives, self.rounds, self)
        return res_women, res_mw, (women, midwives, self)


    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        rep = "%s" % self.name()
        rep = "%s_caseload" % rep if self.is_caseloaded() else rep
        return rep


class CaseloadGame(Game):
    """
    Just like the standard game, but operates a caseloading system. Women
    are assigned a midwife who they then have all appointments with.
    """

    def all_played_caseload(self, caseload, rounds=12):
        for midwife, cases in caseload.items():
            if not self.all_played(cases, rounds):
                return False
        return True

    def play_game(self, players):
        women, midwives = players
        rounds = self.num_appointments
        birthed = []
        #Assign women to midwives
        caseloads = {}
        num_women = len(women)
        num_midwives = len(midwives)
        load = num_women / num_midwives
        self.random.shuffle(women)
        for midwife in midwives:
            caseloads[midwife] = []
            for i in range(load):
                caseloads[midwife].append(women.pop())

        # Assign leftovers at random
        while len(women) > 0:
            caseloads[self.random.choice(midwives)].append(women.pop())

        while not self.all_played_caseload(caseloads, rounds):
            for midwife, cases in caseloads.items():
                if not self.all_played(cases, rounds):
                    woman = cases.pop()
                    self.play_round(woman, midwife)
                if self.all_played([woman], rounds):
                    birthed.append(woman)
                    woman.is_finished = True
                else:
                    cases.insert(0, woman)
                    woman.finished += 1
        return self.measure(birthed, midwives)

    def is_caseloaded(self):
        return True
