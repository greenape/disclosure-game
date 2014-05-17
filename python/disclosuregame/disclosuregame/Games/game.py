from random import Random
from disclosuregame.Measures import measures_midwives, measures_women
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



class Game(object):
    # b > m > n
    def __init__(self, baby_payoff=2, no_baby_payoff=2, mid_baby_payoff=1,referral_cost=1, harsh_high=2,
     harsh_mid=1, harsh_low=0, mid_high=1, mid_mid=0, mid_low=0, low_high=0,low_mid=0,low_low=0, randomise_payoffs=False,
     type_weights=[[10., 1., 1.], [1., 10., 1.], [1., 1., 10.]], rounds=100, measures_women=measures_women(),
     measures_midwives=measures_midwives(), params=None, num_appointments=12, seed=None):
        """ A multistage game played by two agents.
        """
        self.seed = seed
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
