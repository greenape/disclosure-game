import Model
from Model import random_expectations
import random
from ReferralGame import *
import collections

class CarryingGame(Model.Game):
    def __unicode__(self):
        return "carrying_%s" % super(CarryingGame, self).__unicode__()

    def random_player(self, probabilities, player_fn):
        """
        Generate a random player, based on the probabilities
        provided by roulette.
        """
        draw = random.random()
        bracket = 0.
        for i in range(len(probabilities)):
            bracket += probabilities[i]
            if draw < bracket:
                player = player_fn(player_type=i)
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
        random.shuffle(women)
        num_midwives = len(midwives)
        if not self.measures_women.take_at_end:
            women_res = self.measures_women.dump(women, self.rounds, self)
        if not self.measures_midwives.take_at_end:
            mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        for i in range(rounds):
            players = [women.pop() for i in range(num_midwives)]
            random.shuffle(midwives)
            map(self.play_round, players, midwives)
            for x in midwives:
                x.finished += 1
            for woman in players:
                if self.all_played([woman], 12):
                    if self.measures_women.take_at_end:
                        birthed.append(woman)
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = self.random_player(player_dist, type(woman))#type(woman)(player_type=woman.player_type)
                    new_woman.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff,
                        random_expectations(), [random_expectations(breadth=2) for x in range(3)])
                    new_woman.started = i
                    new_woman.finished = i
                    women.insert(0, new_woman)
                else:
                    women.insert(0, woman)
                    woman.finished += 1
            if not self.measures_women.take_at_end:
                women_res.add_results(self.measures_women.dump(players, self.rounds, self))
            if not self.measures_midwives.take_at_end:
                mw_res.add_results(self.measures_midwives.dump(midwives, self.rounds, self))
        birthed += women
        if self.measures_women.take_at_end:
            women_res = self.measures_women.dump(birthed, self.rounds, self)
        if self.measures_midwives.take_at_end:
            mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        women_res.write_db("%s_women" % file_name)
        mw_res.write_db("%s_mw" % file_name)
        return None

class CaseloadCarryingGame(CarryingGame, Model.CaseloadGame):
    def __unicode__(self):
        return "caseload_carrying_%s" % super(CarryingGame, self).__unicode__()

    def play_game(self, players, file_name=""):
        women, midwives = players
        player_dist = self.get_distribution(women)

        rounds = self.rounds
        birthed = []
        random.shuffle(women)
        num_midwives = len(midwives)
        if not self.measures_women.take_at_end:
            women_res = self.measures_women.dump(women, self.rounds, self)
        if not self.measures_midwives.take_at_end:
            mw_res = self.measures_midwives.dump(midwives, self.rounds, self)

        caseloads = {}
        num_women = len(women)
        num_midwives = len(midwives)
        load = num_women / num_midwives
        random.shuffle(women)
        for midwife in midwives:
            caseloads[midwife] = []
            for i in range(load):
                caseloads[midwife].append(women.pop())

        # Assign leftovers at random
        while len(women) > 0:
            caseloads[random.choice(midwives)].append(women.pop())

        for i in range(rounds):
            players = [caseloads[midwife].pop() for midwife in midwives]
            map(self.play_round, players, midwives)
            for x in midwives:
                x.finished += 1
            for i in range(len(players)):
                woman = players[i]
                women = caseloads[midwives[i]]
                if self.all_played([woman], 12):
                    if self.measures_women.take_at_end:
                        birthed.append(woman)
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = self.random_player(player_dist, type(woman))#type(woman)(player_type=woman.player_type)
                    new_woman.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff,
                        random_expectations(), [random_expectations(breadth=2) for x in range(3)])
                    new_woman.started = i
                    new_woman.finished = i
                    women.insert(0, new_woman)
                else:
                    women.insert(0, woman)
                    woman.finished += 1
            if not self.measures_women.take_at_end:
                women_res.add_results(self.measures_women.dump(players, self.rounds, self))
            if not self.measures_midwives.take_at_end:
                mw_res.add_results(self.measures_midwives.dump(midwives, self.rounds, self))
        birthed += women
        if self.measures_women.take_at_end:
            women_res = self.measures_women.dump(birthed, self.rounds, self)
        if self.measures_midwives.take_at_end:
            mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        women_res.write_db("%s_women" % file_name)
        mw_res.write_db("%s_mw" % file_name)
        return None


class CarryingReferralGame(CarryingGame, ReferralGame):
        """
        Just like the referral game, but maintains a carrying capacity.
        """

class CarryingCaseloadReferralGame(CaseloadCarryingGame, ReferralGame):
    """
    Ditto, but caseloaded.
    """