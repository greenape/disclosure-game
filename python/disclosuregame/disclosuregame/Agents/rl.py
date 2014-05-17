from bayes import *
from disclosuregame.Util import weighted_random_choice
from random import Random

def delta_v(alpha, beta, us, v):
    return alpha*beta*(us - v)

def weighted_choice(choices, weights, random=Random()):
    low = abs(min(weights))
    weights = map(lambda x: x + low, weights)
    #print "rescaled to", weights
    #for weight in weights:
    #    assert weight > -0.0000001
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for c, w in zip(choices, weights):
        if upto + w > r:
            return c
        upto += w
    assert False, "Shouldn't get here"

class RWSignaller(BayesianSignaller):
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1], 
        signal_alpha=.25, mw_alpha=.3, type_alpha=.3, configural_alpha=.03, beta=.75, seed=None):
        self.signal_alpha = signal_alpha
        self.mw_alpha = mw_alpha
        self.type_alpha = type_alpha
        self.configural_alpha = configural_alpha
        self.beta = beta
        self.v_sig = [0.]*3
        self.v_type = [0.]*3
        self.v_mw = {}
        self.v_configural = {}
        self.observed_type = False
        self.low = 0.
        self.diff = 0.
        super(RWSignaller, self).__init__(player_type, signals, responses, seed=seed)

    def init_payoffs(self, baby_payoffs, social_payoffs, type_weights=[1., 1., 1.],
                     response_weights=[[1., 1.], [1., 1.], [1., 1.]], num=10):
        """
        An alternative way of generating priors by using the provided weights
        as weightings for random encounters.
        """
        self.low = min(min(l) for l in baby_payoffs) + min(min(l) for l in social_payoffs)
        self.diff = float(max(max(l) for l in baby_payoffs) + max(max(l) for l in social_payoffs) - self.low)
        tmp = type(self)()
        for i in xrange(num):
            # Choose a random signal
            signal = self.random.choice(self.signals)
            # A weighted response
            response = weighted_random_choice(self.responses, response_weights[signal], self.random)
            # A weighted choice of type
            player_type = weighted_random_choice(self.signals, type_weights, self.random)
            # Payoffs
            tmp.player_type = player_type
            payoff = baby_payoffs[self.player_type][response] + social_payoffs[signal][player_type]
            self.signal_log.append(signal)
            self.last_v = self.risk(signal, tmp)
            self.update_counts(response, tmp, payoff, player_type)
            self.update_beliefs()
            self.signal_log.pop()
            self.response_log.pop()
            #self.type_log.pop()

    def update_counts(self, response, midwife, payoff, midwife_type=None, weight=1.):
        if response is not None:
            self.response_log.append(response)
        if midwife is not None:
            # Log true type for bookkeeping
            self.type_log.append(midwife.player_type)
            midwife_type = midwife.player_type
        self.last_sig = self.signal_log[len(self.signal_log) - 1]
        self.last_mw = hash(midwife)
        self.last_payoff = (payoff - self.low) / self.diff
        #print "Payoff was %d, rescaled it to %f" % (payoff, self.last_payoff)
        self.last_type = midwife_type
        self.update_weight = weight

    #@profile
    def update_beliefs(self):
        #Cues
        # Signal
        self.v_sig[self.last_sig] += delta_v(self.signal_alpha*self.update_weight, self.beta, self.last_payoff, self.last_v)
        # Midwife 
        try:
            self.v_mw[self.last_mw] += delta_v(self.mw_alpha*self.update_weight, self.beta, self.last_payoff, self.last_v)
            self.v_type[self.last_type] += delta_v(self.type_alpha*self.update_weight, self.beta, self.last_payoff, self.last_v)
        except KeyError:
            self.v_mw[self.last_mw] = delta_v(self.type_alpha*self.update_weight, self.beta, self.last_payoff, self.last_v)
        # Midwife type 
        #Configurals
        try:
            self.v_configural[(self.last_sig, self.last_type)] += delta_v(self.configural_alpha*self.update_weight, self.beta, self.last_payoff, self.last_v)
        except:
            self.v_configural[(self.last_sig, self.last_type)] = delta_v(self.configural_alpha*self.update_weight, self.beta, self.last_payoff, self.last_v)

    def risk(self, signal, opponent):
        risk = 0.
        risk += self.v_sig[signal]
        self.observed_type = False
        try:
            self.v_mw[hash(opponent)]
            risk += self.v_type[opponent.player_type]
            self.observed_type = True
            risk += self.v_configural[(signal, opponent.player_type)]
        except:
            pass
        return risk

    def do_signal(self, opponent=None):
        best = (self.random.randint(0, 2), -9999999)
       #print "Type %d woman evaluating signals." % self.player_type
        weights = map(lambda signal: self.risk(signal, opponent), self.signals)
        best = weighted_choice(self.signals, weights, self.random)
        #best = (best, weights[best])
        self.rounds += 1
        self.log_signal(best, opponent)
        self.last_v = weights[best]
        return best


class RWResponder(BayesianResponder):
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1], 
        signal_alpha=.3, w_alpha=.3, response_alpha=.3, configural_alpha=.03, beta=.75, seed=None):
        self.signal_alpha = signal_alpha
        self.w_alpha = w_alpha
        self.response_alpha = response_alpha
        self.configural_alpha = configural_alpha
        self.beta = beta
        self.v_sig = [0.]*3
        self.v_response = [0.]*2
        self.v_mw = {}
        self.v_configural = {}
        self.observed_type = False
        self.low = 0.
        self.diff = 0.
        super(RWResponder, self).__init__(player_type, signals, responses, seed=seed)

    def init_payoffs(self, payoffs, type_weights=[[10., 2., 1.], [1., 10., 1.], [1., 1., 10.]], num=1000):
        self.type_weights = [[0.]*3]*3
        self.low = min(min(l) for l in payoffs)
        self.diff = float(max(max(l) for l in payoffs) - self.low)
        #[map(lambda x: (x - low) / diff, l) for l in payoffs]
        for i in xrange(num):
            signal = self.random.choice(self.signals)
            player_type = weighted_random_choice(self.signals, type_weights[signal])
            #print "Signal is %d, type is %d" % (signal, player_type)
            response = self.random.choice(self.responses)
            self.response_log.append(response)
            payoff = payoffs[player_type][response]
            self.last_v = self.risk(response, signal, None)
            self.update_beliefs(payoff, None, signal, player_type)
            self.response_log.pop()

        #Only interested in payoffs for own type
        self.payoffs = payoffs
        #self.update_beliefs(None, None, None)


    def update_counts(self, response, midwife, payoff, midwife_type=None, weight=1.):
        payoff = (payoff - self.low) / self.diff
        if response is not None:
            self.response_log.append(response)
        if midwife is not None:
            # Log true type for bookkeeping
            self.type_log.append(midwife.player_type)
            midwife_type = midwife.player_type
        self.last_sig = self.signal_log[len(self.signal_log) - 1]
        self.last_mw = hash(midwife)
        self.last_payoff = payoff
        self.last_type = midwife_type

    def update_beliefs(self, payoff, signaller, signal, signaller_type=None, weight=1.):
        payoff = (payoff - self.low) / self.diff
        response = self.response_log[len(self.response_log) - 1]
        self.v_sig[signal] += delta_v(self.signal_alpha*weight, self.beta, payoff, self.last_v)
        self.v_response[response] += delta_v(self.response_alpha*weight, self.beta, payoff, self.last_v)
        try:
            self.v_configural[(signal, response)] += delta_v(self.configural_alpha*weight, self.beta, payoff, self.last_v)
        except:
            self.v_configural[(signal, response)] = delta_v(self.configural_alpha*weight, self.beta, payoff, self.last_v)

    def risk(self, act, signal, opponent):
        risk = 0.
        risk += self.v_sig[signal]
        risk += self.v_response[act]
        #self.observed_type = False
        try:
            #risk += self.v_mw[hash(opponent)]
            #risk += self.v_type[opponent.player_type]
            #.observed_type = True
            risk += self.v_configural[(signal, act)]
        except:
            pass
        return risk

    def respond(self, signal, opponent=None):
        """
        Make a judgement about somebody based on
        the signal they sent based on expe
        """
        best = (self.random.randint(0, 2), -9999999)
       #print "Type %d woman evaluating signals." % self.player_type
        weights = map(lambda response: self.risk(response, signal, opponent), self.responses)
        best = weighted_choice(self.responses, weights, self.random)
        #best = (best, weights[best])
        self.last_v = weights[best]
        self.response_log.append(best)
        return best