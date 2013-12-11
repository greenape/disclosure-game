from collections import OrderedDict
import collections
from Results import *
import itertools

class Measures(object):
    take_at_end = True
    def __init__(self, measures):
        self.measures = measures

    def keys(self):
        return self.measures.keys()

    def values(self):
        return self.measures.values()

    def dump(self, women, rounds, game):
        """
        A results dumper. Takes a tuple of a game and players, and two dictionaries.
        Measures should contain a mapping from a field name to method for getting a result
        given an appointment, set of players, and a game. Params should contain mappings
        from parameter names to values.
        Optionally takes an exist results object to add records to. This should have the same
        measures and params.
        Returns a results object for writing to csv.
        """
        results = []
        if women is None:
            return Result(self.measures.keys(), game.parameters, results)
        for i in range(rounds):
            line = map(lambda x: x.measure(i, women, game), self.measures.values())
            results.append(line)
        results = Result(self.measures.keys(), game.parameters, results)
        return results

class IndividualMeasures(Measures):
    take_at_end = False
    def dump(self, women, rounds, game):
        """
        A results dumper. Takes a tuple of a game and players, and two dictionaries.
        Measures should contain a mapping from a field name to method for getting a result
        given an appointment, set of players, and a game. Params should contain mappings
        from parameter names to values.
        Writes rows as individuals, and takes the measure of the last round.
        Returns a results object for writing to csv.
        """
        results = []
        if women is None:
            return Result(self.measures.keys(), game.parameters, results)
        for woman in women:
            line = map(lambda x: x.measure(rounds, [woman], game), self.measures.values())
            results.append(line)
        results = Result(self.measures.keys(), game.parameters, results)
        return results

# Measures

class Measure(object):
    def __init__(self, player_type=None, midwife_type=None, signal=None, present=True):
        self.player_type = player_type
        self.midwife_type = midwife_type
        self.signal = signal
        self.present = present

    def filter_present(self, women, roundnum):
        """
        Filter out any women not present on this round.
        """
        women = filter(lambda x: x.started < roundnum, women)
        women = filter(lambda x: x.finished > roundnum, women)
        return women

class PlayerHash(Measure):
    """
    Return a unique ident for a player.
    """
    def measure(self, roundnum, woman, game):
        return hash(woman[0])

class TypeWeight(Measure):
    """
    Return the starting weight for midwife type.
    """
    def measure(self, roundnum, woman, game):
        return woman[0].type_weights[self.midwife_type]

class PlayerType(Measure):
    """
    Return a player type.
    """
    def measure(self, roundnum, woman, game):
        woman = woman[0]
        return woman.player_type

class NumRounds(Measure):
    """
    Return the number of rounds a player played.
    """
    def measure(self, roundnum, woman, game):
        woman = woman[0]
        return woman.finished - woman.started

class Referred(Measure):

    def measure(self, roundnum, women, game):
        return map(lambda x: 1 in x.response_log, women)[0]

class Started(Measure):
    def measure(self, roundnum, women, game):
        return women[0].started

class Appointment(Measure):
    def measure(self, roundnum, women, game):
        """
        Return the value passed as roundnum.
        """
        return roundnum

class Finished(Measure):
    def measure(self, roundnum, women, game):
        """
        Return the fraction of the women finished by this round
        """
        women = filter(lambda x: x.started < roundnum, women)
        num_women = float(len(women))
        num_finished = sum(map(lambda x: 1 if x.finished < roundnum else 0, women))
        if num_women == 0:
            return 0
        return num_finished / num_women

class TypeFinished(Measure):
    """
    Return the fraction of women of a particular type who finished this round.
    """
    def measure(self, roundnum, women, game):
        women = filter(lambda x: x.player_type == self.player_type, women)
        women = filter(lambda x: x.started < roundnum, women)
        num_women = float(len(women))
        num_finished = sum(map(lambda x: 1 if x.finished < roundnum else 0, women))
        if num_women == 0:
            return 0
        return num_finished / num_women

class LastSignal(Measure):
    def measure(self, roundnum, women, game):
        signal = 0
        try:
            signal = women[0].signal_log.pop()
            women[0].signal_log.append(signal)
        except IndexError:
            pass
        return signal


class TypeSignal(Measure):
    """
    Return a function that yields the fraction of that type
    who signalled so in that round.
    """
    def measure(self, roundnum, women, game):
        women = filter(lambda x: x.player_type == self.player_type, women)
        #women = filter(lambda x: len(x.signal_log) > roundnum, women)
        women = self.filter_present(women, roundnum)
        num_women = len(women)
        women = filter(lambda x: x.signal_log[roundnum - x.started] == self.signal, women)
        signalled = len(women)
        if num_women == 0:
            return 0
        return signalled / float(num_women)
    


class TypeSignalBreakdown(Measure):
    """
    Return a function that yields the fraction of women of some type signalling
    a particular way who had a midwife of a particular type.
    """
    def measure(self, roundnum, women, game):
        women = filter(lambda x: x.player_type == self.player_type, women)
        women = self.filter_present(women, roundnum)
        women = filter(lambda x: x.type_log[roundnum] == self.midwife_type, women)
        num_women = len(women)
        women = filter(lambda x: x.signal_log[roundnum - x.started] == self.signal, women)
        signalled = len(women)
        if num_women == 0:
            return 0
        return signalled / float(num_women)
    

class TypeReferralBreakdown(Measure):
    """
    Return a function that yields the fraction of women of some type signalling
    a particular way who had a midwife of a particular type and got referred.
    If signal is None, then this is for all signals.
    If midwife_type is None, then this is for all midwife types.
    """
    def measure(self, roundnum, women, game):
        women = filter(lambda x: x.player_type == self.player_type, women)
        women = self.filter_present(women, roundnum)
        if self.midwife_type is not None:
            women = filter(lambda x: x.type_log[roundnum - x.started] == self.midwife_type, women)
        num_women = len(women)
        if self.signal is not None:
            women = filter(lambda x: x.signal_log[roundnum - x.started] == self.signal, women)
        women = filter(lambda x: x.response_log[roundnum - x.started] == 1, women)
        signalled = len(women)
        if num_women == 0:
            return 0
        return signalled / float(num_women)
    


class PayoffType(Measure):
    """
    Return a function that gives the average payoff in that
    round for a given type. If type is None, then the average
    for all types is returned.
    """
    def measure(self, roundnum, women, game):
        if self.player_type is not None:
            women = filter(lambda x: x.player_type == self.player_type, women)
        women = self.filter_present(women, roundnum)
        if len(women) == 0:
            return 0
        return sum(map(lambda x: x.payoff_log[roundnum - x.started], women)) / float(len(women))
    

class SignalChange(Measure):
    """
    Return a function that yields average change in signal
    by women this round from last round.
    """
    def measure(self, roundnum, women, game):
        if roundnum == 0:
            return 0
        women = filter(lambda x: x.player_type == self.player_type, women)
        women = self.filter_present(women, roundnum)
        num_women = len(women)
        if num_women == 0:
            return 0
        change = map(lambda x: x.signal_log[roundnum - x.started] - x.signal_log[roundnum - 1 - x.started], women)
        return sum(change) / float(num_women)
    

class Signals(Measure):
    def measure(self, roundnum, women, game):
        """
        Return a colon separated list of the signals of all women this round.
        Women who have finished are denoted by a -1.
        """
        sigs = map(lambda x: -1 if x.finished < roundnum else x.signal_log[roundnum], women)
        return ":".join(str(x) for x in sigs)

class SignalImpliesReferral(Measure):

    """
    Return a function that gives the average belief of players of this
    type that that signal will lead to referral, who had this type of midwife
    on a round. If player_type or midwife_type are None, this returns for all of that type.
    """
    def measure(self, roundnum, women, game):
        if self.player_type is not None:
            women = filter(lambda x: x.player_type == self.player_type, women)
        if self.midwife_type is not None:
            women = filter(lambda x: len(x.type_log) > roundnum, women)
            women = filter(lambda x: x.type_log[roundnum] == self.midwife_type, women)
        women = self.filter_present(women, roundnum)
        #women = filter(lambda x: len(x.response_belief[self.signal][1]) > roundnum, women)
        belief = sum(map(lambda x: x.round_response_belief(roundnum)[self.signal][1], women))
        if len(women) == 0:
            return 0
        return belief / len(women)
    

class SignalRisk(Measure):
    """
    Return a function that gives the average risk associated
    with sending signal by players of this type who had that
    midwife type on a round.
    """
    def measure(self, roundnum, women, game):
        #women = filter(lambda x: len(x.type_log) > roundnum, women)
        if self.player_type is not None:
            women = filter(lambda x: x.player_type == self.player_type, women)
        if self.midwife_type is not None:
            women = filter(lambda x: len(x.type_log) > roundnum, women)
            women = filter(lambda x: x.type_log[roundnum] == self.midwife_type, women)
        women = self.filter_present(women, roundnum)
        total = sum(map(lambda x: x.round_signal_risk(roundnum)[self.signal], women))
        if len(women) == 0:
            return 0.
        return total / float(len(women))
    

class DistributionBelief(Measure):
    """
    Return a function that gives the average believed prevalence
    of this midwife type by this type of player. Or for all players
    where player_type is None.
    """
    
    def measure(self, roundnum, women, game):
        if self.player_type is not None:
            women = filter(lambda x: x.player_type == self.player_type, women)
        #women = filter(lambda x: len(x.type_distribution[midwife_type]) > roundnum, women)
        women = self.filter_present(women, roundnum)
        num_women = len(women)
        belief = sum(map(lambda x: x.round_type_distribution(roundnum)[self.midwife_type], women))
        if num_women == 0:
            return 0.
        return belief / num_women

class TypeFrequency(Measure):
    """
    Return the frequency of this type in the population at this round.
    """
    def measure(self, roundnum, women, game):
        women = self.filter_present(women, roundnum)
        types = map(lambda x: x.player_type, women)
        frequencies = collections.Counter(types)
        total = sum(frequencies.values())
        if total == 0:
            return 0
        return frequencies[self.player_type] / float(total)

class SignalMeaning(Measure):
    """
    Return a function that yields the average belief
    that this signal means that type.
    """
    
    def measure(self, roundnum, women, game):
        women = self.filter_present(women, roundnum)
        total = sum(map(lambda x: x.signal_belief[self.signal][self.player_type][roundnum], women))
        if len(women) == 0:
            return 0.
        return total / float(len(women))

class SignalExperience(Measure):
    """
    A measure that gives the frequency of a signal experienced up
    to that round by some (or all) types of midwife.
    """
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        if self.present:
            women = filter(lambda x: len(x.signal_log) > roundnum, women)
            group_log = itertools.chain(*map(lambda x: x.signal_log[:roundnum], women))
        else:
            group_log = itertools.chain(*map(lambda x: x.signal_log, women))
        frequencies = collections.Counter(group_log)
        total_signals = sum(frequencies.values())
        if total_signals == 0:
            return 0
        return frequencies[self.signal] / float(total_signals)

class TypeExperience(Measure):
    """
    A measure that gives the frequency of a type experienced up
    to that round by some (or all) types of midwife.
    """
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        if self.present:
            women = filter(lambda x: len(x.type_log) > roundnum, women)
            group_log = itertools.chain(*map(lambda x: x.type_log[:roundnum], women))
        else:
            group_log = itertools.chain(*map(lambda x: x.type_log, women))
        frequencies = collections.Counter(group_log)
        total_signals = sum(frequencies.values())
        if total_signals == 0:
            return 0
        return frequencies[self.player_type] / float(total_signals)


class RightCallUpto(Measure):
    """
    Gives the frequency of right calls given by midwives of
    some (or any) type, up to a round.
    """
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        total_calls = 0.
        total_right = 0.
        for midwife in women:
            r_log = midwife.response_log[:roundnum]
            t_log = midwife.type_log[:roundnum]
            total_calls += len(r_log)
            for i in range(len(r_log)):
                response = r_log[i]
                player = t_log[i]
                if response == 0:
                    if player == 0:
                        total_right += 1
                else:
                    if player != 0:
                        total_right += 1
        if total_calls == 0:
            return 0
        return total_right / total_calls

class RightCall(Measure):
    """
    Gives the frequency of right calls given by midwives of
    some (or any) type, in a round.
    """
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        total_calls = 0.
        total_right = 0.
        for midwife in women:
            try:
                response = midwife.response_log[roundnum]
                player = midwife.type_log[roundnum]
                total_calls += 1
                if response == 0:
                    if player == 0:
                        total_right += 1
                else:
                    if player != 0:
                        total_right += 1
            except IndexError:
                pass
        if total_calls == 0:
            return 0
        return total_right / total_calls

class FalsePositive(Measure):
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        total_calls = 0.
        total_right = 0.
        for midwife in women:
            try:
                response = midwife.response_log[roundnum]
                player = midwife.type_log[roundnum]
                if response == 1:
                    if player == 0:
                        total_right += 1
                    total_calls += 1
            except IndexError:
                pass
        if total_calls == 0:
            return 0
        return total_right / total_calls

class FalseNegative(Measure):
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        total_calls = 0.
        total_right = 0.
        for midwife in women:
            try:
                response = midwife.response_log[roundnum]
                player = midwife.type_log[roundnum]
                if response == 0:
                    if player != 0:
                        total_right += 1
                    total_calls += 1
            except IndexError:
                pass
        if total_calls == 0:
            return 0
        return total_right / total_calls

class TypedFalseNegativeUpto(Measure):
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        total_calls = 0.
        total_right = 0.
        for midwife in women:
            r_log = midwife.response_log[:roundnum]
            t_log = midwife.type_log[:roundnum]
            for i in range(len(r_log)):
                response = r_log[i]
                player = t_log[i]
                if player == self.player_type:
                    total_calls += 1
                    if response == 0:
                        total_right += 1
        if total_calls == 0:
            return 0
        return total_right / total_calls


class FalsePositiveUpto(Measure):
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        total_calls = 0.
        total_right = 0.
        for midwife in women:
            r_log = midwife.response_log[:roundnum]
            t_log = midwife.type_log[:roundnum]
            for i in range(len(r_log)):
                response = r_log[i]
                player = t_log[i]
                if response == 1:
                    if player == 0:
                        total_right += 1
                    total_calls += 1
        if total_calls == 0:
            return 0
        return total_right / total_calls

class FalseNegativeUpto(Measure):
    def measure(self, roundnum, women, game):
        if self.midwife_type is not None:
            women = filter(lambda x: x.player_type == self.midwife_type, women)
        total_calls = 0.
        total_right = 0.
        for midwife in women:
            r_log = midwife.response_log[:roundnum]
            t_log = midwife.type_log[:roundnum]
            for i in range(len(r_log)):
                response = r_log[i]
                player = t_log[i]
                if response == 0:
                    if player != 0:
                        total_right += 1
                    total_calls += 1
        if total_calls == 0:
            return 0
        return total_right / total_calls

class Response(Measure):
    def measure(self, roundnum, women, game):
        woman = women[0]
        signaller = type(woman)()
        #print "Hashing by", hash(woman), "hashing", hash(signaller)
        r = woman.respond(self.signal, signaller)
        woman.signal_log.pop()
        woman.response_log.pop()
        woman.rounds -= 1
        woman.signal_matches[self.signal] -= 1
        try:
            woman.signal_memory.pop(hash(signaller), None)
            woman.shareable = None
        except:
            raise
        return r

class AccruedPayoffs(Measure):
    def measure(self, roundnum, women, game):
        total = sum(map(lambda x: x.accrued_payoffs, women))
        return total / float(len(women))
               
def indiv_measures_women():
    measures = OrderedDict()
    measures['player_id'] = PlayerHash()
    measures['player_type'] = PlayerType()
    measures['num_rounds'] = NumRounds()
    measures['referred'] = Referred()
    measures['started'] = Started()
    measures['signalled'] = LastSignal()
    measures['accrued_payoffs'] = AccruedPayoffs()
    for i in range(3):
        # Midwife types seen, signals sent
        measures['type_%d_frequency' % i] = TypeExperience(player_type=i, present=False)
        measures['signal_%d_frequency' % i] = SignalExperience(signal=i, present=False)
    return IndividualMeasures(measures)

def indiv_measures_mw():
    measures = OrderedDict()
    measures['player_id'] = PlayerHash()
    measures['player_type'] = PlayerType()
    measures['num_rounds'] = NumRounds()
    measures['all_right_calls_upto'] = RightCallUpto()
    measures['false_positives'] = FalsePositiveUpto()
    measures['false_negatives_upto'] = FalseNegativeUpto()
    measures['accrued_payoffs'] = AccruedPayoffs()
    for i in range(3):
        # Women types seen, signals sent
        measures['type_%d_frequency' % i] = TypeExperience(player_type=i, present=False)
        measures['signal_%d_frequency' % i] = SignalExperience(signal=i, present=False)
        measures['response_to_signal_%d' % i] = Response(signal=i)
        measures['type_%d_misses' % i] = TypedFalseNegativeUpto(player_type=i)
    return IndividualMeasures(measures)


def measures_women():
    measures = OrderedDict()
    measures['appointment'] = Appointment()
    measures['finished'] = Finished()
    for i in range(3):
        measures["type_%d_ref" % i] = TypeReferralBreakdown(player_type=i)
        measures["type_%d_finished" % i] = TypeFinished(player_type=i)
        measures["global_type_frequency_%d" % i] = DistributionBelief(midwife_type=i)
        for j in range(3):
            measures["type_%d_signal_%d" % (i, j)] = TypeSignal(player_type=i, signal=j)
            measures["type_%d_mw_%d_ref" % (i, j)] = TypeReferralBreakdown(player_type=i, midwife_type=j)
            measures["type_%d_sig_%d_ref" % (i, j)] = TypeReferralBreakdown(player_type=i, signal=j)
            for k in range(3):
                measures["type_%d_mw_%d_sig_%d" % (i, j, k)] = TypeReferralBreakdown(player_type=i, midwife_type=j, signal=k)
    return Measures(measures)

def measures_midwives():
    measures = OrderedDict()
    measures['appointment'] = Appointment()
    measures['all_right_calls_upto'] = RightCallUpto()
    measures['all_right_calls'] = RightCall()
    measures['false_positives_upto'] = FalsePositiveUpto()
    measures['false_positives'] = FalsePositive()
    measures['false_negatives_upto'] = FalseNegativeUpto()
    measures['false_negatives'] = FalseNegative()
    for i in range(3):
        measures['signal_%d_frequency' % i] = SignalExperience(signal=i)
        measures['type_%d_frequency' % i] = TypeExperience(player_type=i)
        measures['type_%d_right_calls_upto' % i] = RightCallUpto(midwife_type=i)
        measures['type_%d_right_calls' % i] = RightCall(midwife_type=i)
        measures['type_%d_false_positives_upto' % i] = FalsePositiveUpto(midwife_type=i)
        measures['type_%d_false_positives' % i] = FalsePositive(midwife_type=i)
        measures['type_%d_false_negatives_upto' % i] = FalseNegativeUpto(midwife_type=i)
        measures['type_%d_false_negatives' % i] = FalseNegative(midwife_type=i)
        for j in range(3):
            measures["signal_%d_means_%d" % (i, j)] = SignalMeaning(signal=i, player_type=j)
    return Measures(measures)