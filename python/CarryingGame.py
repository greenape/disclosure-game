import Model
from Model import random_expectations
import random
from ReferralGame import *

class CarryingGame(Model.Game):
    def __unicode__(self):
        return "carrying_%s" % super(CarryingGame, self).__unicode__()

    """
    A game type that maintains the size of the population of
    women, by adding in a new one of the same type as any that finish.
    """
    def play_game(self, players):
        women, midwives = players

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
                if self.all_played([woman], rounds / 10):
                    birthed.append(woman)
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = type(woman)(player_type=woman.player_type)
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
        return women_res, mw_res, (birthed, midwives, self)

class CarryingReferralGame(CarryingGame, ReferralGame):
        """
        Just like the referral game, but maintains a carrying capacity.
        """