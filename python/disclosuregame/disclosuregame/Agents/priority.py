from heuristic import *
from bayes import *
import operator
from itertools import count

def nearest_power_of_ten(x):
    if x == 0:
        return 0.
    return 10**(floor(log(2*x, 10)))

def nearest_prominent(num):
    """
    Round to the nearest power of ten, half of a power of ten, or
    double of a power of ten.
    """
    nearest = nearest_power_of_ten(num)
    next_nearest = 10**(log(nearest, 10) + 1)
    possibles = map(lambda x: x/2, [nearest, next_nearest]) + map(lambda x: x*2, [nearest, next_nearest])
    possibles += [nearest, next_nearest]
    dists = sorted(map(lambda x: (x, abs(x-num)), possibles), key=operator.itemgetter(1))
    return dists[0][0]

class PrioritySignaller(LexicographicSignaller):
    def min_outcome(self, signal):
        """
        Return the smallest gain associated with this signal.
        """
        payoffs = sorted(self.payoff_count[signal].keys())
        return payoffs[0]

    def max_outcome(self, signal):
        payoffs = sorted(self.payoff_count[signal].keys())
        payoffs.reverse()
        return payoffs[0]

    def outcome_probability(self, signal, outcome):
        return float(self.payoff_count[signal][outcome]) / sum(self.payoff_count[signal].values())

    def do_signal(self, opponent=None):
        super(PrioritySignaller, self).do_signal(opponent)
        signals = shuffled(self.signals)
        n = 0
        # Reduce to possible
        max_outcomes = {}
        min_outcomes = {}
        max_probabilities = {}
        min_probabilities = {}
        for signal in signals:
            payoff = self.max_outcome(signal)
            max_probabilities[signal] = self.outcome_probability(signal, payoff)
            max_outcomes[signal] = payoff
            payoff = self.min_outcome(signal)
            min_outcomes[signal] = payoff
            min_probabilities[signal] = self.outcome_probability(signal, payoff)

        max_outcomes = sorted(max_outcomes.items(), key=operator.itemgetter(1), reverse=True)
        min_outcomes = sorted(min_outcomes.items(), key=operator.itemgetter(1), reverse=True)
        min_probabilities = sorted(min_probabilities.items(), key=operator.itemgetter(1), reverse=True)
        max_probabilities = sorted(max_probabilities.items(), key=operator.itemgetter(1), reverse=True)

        # Highest absolute gain or loss
        highest = nearest_prominent(max(abs(max_outcomes[0][0]), abs(min_outcomes[0][0])) / 10.)

        #Rule 1: do worst outcomes differ by highest or more?
        if abs(min_outcomes[0][1] - min_outcomes[1][1]) >= highest:
            best = min_outcomes[0][0]

        #Rule 2: do the probabilities differ by 10% or more
        elif abs(self.outcome_probability)
        #Rule 3: do the best outcomes differ by highest or more?

        #Rule 4: do the probabilities of the best outcomes differ by 10% or more?

        self.signal_log.pop()
        self.log_signal(best, opponent)
        return best

class PriorityResponder(LexicographicResponder):