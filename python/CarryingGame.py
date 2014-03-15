import Model
from Model import random_expectations
from ReferralGame import *
import collections
from random import Random
try:
    import scoop
    scoop.worker
    scoop_on = True
except:
    scoop_on = False
    pass

class CarryingGame(Model.Game):
    def __unicode__(self):
        return "carrying_%s" % super(CarryingGame, self).__unicode__()

    def __init__(self, baby_payoff=2, no_baby_payoff=2, mid_baby_payoff=1,referral_cost=1, harsh_high=2,
     harsh_mid=1, harsh_low=0, mid_high=1, mid_mid=0, mid_low=0, low_high=0,low_mid=0,low_low=0, randomise_payoffs=False,
     type_weights=[[10., 1., 1.], [1., 10., 1.], [1., 1., 10.]], rounds=100, measures_women=measures_women(),
     measures_midwives=measures_midwives(), params=None, mw_share_prob=0, mw_share_bias=-.99, women_share_prob=0, women_share_bias=0.99,
     num_appointments=12, seed=None):
        super(CarryingGame, self).__init__(baby_payoff, no_baby_payoff, mid_baby_payoff, referral_cost, harsh_high,
            harsh_mid, harsh_low, mid_high, mid_mid, mid_low, low_high, low_mid, low_low, randomise_payoffs, type_weights,
            rounds, measures_women, measures_midwives, params, seed)
        self.player_random = Random(self.random.random())

    def random_player(self, probabilities, player, args={}):
        """
        Generate a random player, based on the probabilities
        provided by roulette.
        """
        draw = self.player_random.random()
        bracket = 0.
        for i in range(len(probabilities)):
            bracket += probabilities[i]
            if draw < bracket:
                try:
                    new_player = type(player)(player_type=i, child_fn=player.child_fn, **args)
                    player = new_player
                except AttributeError:
                    player = type(player)(player_type=i, seed=self.player_random.random(), **args)
                return player
        print "Whoops!",bracket,draw


    def get_distribution(self, players):
        """
        Return a list giving the distribution of player types.
        """
        player_types = map(lambda x: x.player_type, players)
        counts = collections.Counter(player_types)
        return map(lambda x: float(x) / sum(counts.values()), counts.values())



    """
    A game type that maintains the size of the population of
    women, by adding in a new one of the same type as any that finish.
    """
    def play_game(self, players, file_name=""):
        women, midwives = players
        player_dist = self.get_distribution(women)

        rounds = self.rounds
        birthed = []
        self.random.shuffle(women)
        num_midwives = len(midwives)
        women_res = self.measures_women.dump(None, self.rounds, self, None)
        mw_res = self.measures_midwives.dump(None, self.rounds, self, None)
        for i in range(rounds):
            players = [women.pop() for j in range(num_midwives)]
            self.random.shuffle(midwives)
            map(self.play_round, players, midwives)
            for x in midwives:
                x.finished += 1
            women_res = self.measures_women.dump(players, i, self, women_res)
            mw_res = self.measures_midwives.dump(midwives, i, self, mw_res)
            for woman in players:
                if self.all_played([woman], 12):
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = self.random_player(player_dist, woman)#type(woman)(player_type=woman.player_type)
                    new_woman.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff,
                        random_expectations(random=self.player_random), [random_expectations(breadth=2, random=self.player_random) for x in range(3)])
                    new_woman.started = i
                    new_woman.finished = i
                    women.insert(0, new_woman)
                    women_res.add_results(self.measures_women.dump([woman, new_woman], self.rounds, self))
                    del woman
                else:
                    women.insert(0, woman)
                    woman.finished += 1
            #if scoop_on:
            #    scoop.logger.info("Worker %s played %d rounds." % (scoop.worker[0], i))

        del women
        del midwives

        if scoop_on:
            scoop.logger.info("Worker %s completed a game." % (scoop.worker[0]))
        return women_res, mw_res

class CaseloadCarryingGame(CarryingGame, Model.CaseloadGame):
    def __unicode__(self):
        return "caseload_carrying_%s" % super(CarryingGame, self).__unicode__()

    def play_game(self, players, file_name=""):
        women, midwives = players
        player_dist = self.get_distribution(women)

        rounds = self.rounds
        birthed = []
        self.random.shuffle(women)
        num_midwives = len(midwives)
        women_res = self.measures_women.dump(None, self.rounds, self, None)
        mw_res = self.measures_midwives.dump(None, self.rounds, self, None)

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

        for i in range(rounds):
            players = [caseloads[midwife].pop() for midwife in midwives]
            map(self.play_round, players, midwives)
            for x in midwives:
                x.finished += 1
            women_res = self.measures_women.dump(players, i, self, women_res)
            mw_res = self.measures_midwives.dump(midwives, i, self, mw_res)
            for j in range(len(players)):
                woman = players[j]
                women = caseloads[midwives[j]]
                if self.all_played([woman], 12):
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = self.random_player(player_dist, woman)#type(woman)(player_type=woman.player_type)
                    new_woman.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff,
                        random_expectations(random=self.player_random), [random_expectations(breadth=2, random=self.player_random) for x in range(3)])
                    new_woman.started = i
                    new_woman.finished = i
                    women.insert(0, new_woman)
                    women_res.add_results(self.measures_women.dump([woman, new_woman], self.rounds, self))
                    del woman
                else:
                    women.insert(0, woman)
                    woman.finished += 1
            if scoop_on:
                scoop.logger.info("Worker %s played %d rounds." % (scoop.worker[0], i))
        del women
        del midwives
        
        if scoop_on:
            scoop.logger.info("Worker %s completed a game." % (scoop.worker[0]))
        return women_res, mw_res


class CarryingReferralGame(CarryingGame, ReferralGame):
        """
        Just like the referral game, but maintains a carrying capacity.
        """

class CarryingCaseloadReferralGame(CaseloadCarryingGame, ReferralGame):
    """
    Ditto, but caseloaded.
    """