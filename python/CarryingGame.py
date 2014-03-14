import Model
from Model import random_expectations
from ReferralGame import *
import collections
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

    def random_player(self, probabilities, player):
        """
        Generate a random player, based on the probabilities
        provided by roulette.
        """
        draw = self.random.random()
        bracket = 0.
        for i in range(len(probabilities)):
            bracket += probabilities[i]
            if draw < bracket:
                try:
                    new_player = type(player)(player_type=i, child_fn=player.child_fn)
                    player = new_player
                except AttributeError:
                    player = type(player)(player_type=i)
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
                        random_expectations(random=self.random), [random_expectations(breadth=2, random=self.random) for x in range(3)])
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
                        random_expectations(random=self.random), [random_expectations(breadth=2, random=self.random) for x in range(3)])
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