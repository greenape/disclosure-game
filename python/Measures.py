from collections import OrderedDict

def measures_women():
    measures = OrderedDict()
    measures['appointment'] = Appointment()
    measures['finished'] = Finished()
    for i in range(3):
        measures["type_%d_ref" % i] = TypeReferralBreakdown(player_type=i)
        measures["type_%d_finished" % i] = TypeFinished(player_type=i)
        measures["type_%d_signal_change" % i] = SignalChange(player_type=i)
        measures["global_type_frequency_%d" % i] = DistributionBelief(midwife_type=i)
        for j in range(3):
            measures["type_%d_signal_%d" % (i, j)] = TypeSignal(player_type=i, signal=j)
            measures["type_%d_mw_%d_ref" % (i, j)] = TypeReferralBreakdown(player_type=i, midwife_type=j)
            measures["type_%d_sig_%d_ref" % (i, j)] = TypeReferralBreakdown(player_type=i, signal=j)
            measures["type_%d_signal_%d_means_referral" % (i, j)] = SignalImpliesReferral(player_type=i, signal=j)
            measures["type_%d_sig_%d_risk" % (i, j)] = SignalRisk(player_type=i, signal=j)
            measures["player_type_%d_frequency_%d" % (i, j)] = DistributionBelief(player_type=i, midwife_type=j)
            for k in range(3):
                measures["type_%d_sig_%d_mw_%d_risk" % (i, j, k)] = SignalRisk(player_type=i, signal=j, midwife_type=k)
                measures["type_%d_mw_%d_sig_%d" % (i, j, k)] = TypeReferralBreakdown(player_type=i, midwife_type=j, signal=k)
                measures["type_%d_signal_%d_with_mw_type_%d_means_referral" % (i, j, k)] = SignalImpliesReferral(player_type=i, signal=j, midwife_type=k)
    return measures

def measures_midwives():
    measures_mw = OrderedDict()
    measures_mw['appointment'] = Appointment()
    for i in range(3):
        for j in range(3):
            measures_mw["signal_%d_means_%d" % (i, j)] = SignalMeaning(signal=i, player_type=j)
    return measures_mw

# Measures

class Measure(object):
    def __init__(self, player_type=None, midwife_type=None, signal=None):
        self.player_type = player_type
        self.midwife_type = midwife_type
        self.signal = signal


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
        num_women = float(len(women))
        num_finished = sum(map(lambda x: 1 if x.finished < roundnum else 0, women))
        if num_women == 0:
            return 0
        return num_finished / num_women



class TypeSignal(Measure):
    """
    Return a function that yields the fraction of that type
    who signalled so in that round.
    """
    def measure(self, roundnum, women, game):
        women = filter(lambda x: x.player_type == self.player_type, women)
        #women = filter(lambda x: len(x.signal_log) > roundnum, women)
        num_women = len(women)
        women = filter(lambda x: x.round_signal(roundnum) == self.signal, women)
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
        women = filter(lambda x: len(x.signal_log) > roundnum, women)
        women = filter(lambda x: x.type_log[roundnum] == self.midwife_type, women)
        num_women = len(women)
        women = filter(lambda x: x.signal_log[roundnum] == self.signal, women)
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
        women = filter(lambda x: len(x.signal_log) > roundnum, women)
        if self.midwife_type is not None:
            women = filter(lambda x: x.type_log[roundnum] == self.midwife_type, women)
        num_women = len(women)
        if self.signal is not None:
            women = filter(lambda x: x.signal_log[roundnum] == self.signal, women)
        women = filter(lambda x: x.response_log[roundnum] == 1, women)
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
        women = filter(lambda x: len(x.payoff_log) > roundnum, women)
        if len(women) == 0:
            return 0
        return sum(map(lambda x: x.payoff_log[roundnum], women)) / float(len(women))
    

class SignalChange(Measure):
    """
    Return a function that yields average change in signal
    by women this round from last round.
    """
    def measure(self, roundnum, women, game):
        if roundnum == 0:
            return 0
        women = filter(lambda x: x.player_type == self.player_type, women)
        women = filter(lambda x: len(x.signal_log) > roundnum, women)
        num_women = len(women)
        if num_women == 0:
            return 0
        change = map(lambda x: x.signal_log[roundnum] - x.signal_log[roundnum - 1], women)
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
        num_women = len(women)
        belief = sum(map(lambda x: x.round_type_distribution(roundnum)[self.midwife_type], women))
        if num_women == 0:
            return 0.
        return belief / num_women

class SignalMeaning(Measure):
    """
    Return a function that yields the average belief
    that this signal means that type.
    """
    
    def measure(self, roundnum, women, game):
        women = filter(lambda x: len(x.signal_belief[self.signal][self.player_type]) > roundnum, women)
        total = sum(map(lambda x: x.signal_belief[self.signal][self.player_type][roundnum], women))
        if len(women) == 0:
            return 0.
        return total / float(len(women))
    