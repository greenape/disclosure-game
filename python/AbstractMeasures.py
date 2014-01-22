from Measures import *

class PopCount(Measure):
    def __init__(self, player_type=None, midwife_type=None, signal=None):
        super(PopCount, self).__init__(player_type, midwife_type, signal)
        self.hash_bucket = set()

    """
    Return the count of this type up to roundnum.
    """
    def measure(self, roundnum, women, game):
        if self.player_type is not None:
            women = filter(lambda x: x.player_type == self.player_type, women)
        women = map(lambda x: hash(x), women)
         
        self.hash_bucket.update(women)
        return len(self.hash_bucket)


class HonestyMeasure(Measure):
    def __init__(self, player_type=None, midwife_type=None, signal=None, counted=set()):
        super(HonestyMeasure, self).__init__(player_type, midwife_type, signal)
        self.count = 0
        self.counted = counted

    """
    Return the number of honest signals sent on an appointment.
    """
    def measure(self, roundnum, women, game):
        if self.player_type is not None:
            women = filter(lambda x: x.player_type == self.player_type, women)
        women = filter(lambda x: x.rounds == self.signal, women)
        women = filter(lambda x: x.player_type in x.signal_log, women)
        women = filter(lambda x: hash(x) not in self.counted, women)
        self.counted.update(map(hash, women))
        self.count += len(women)
        return self.count


class RefCount(Measure):
    def __init__(self, player_type=None, midwife_type=None, signal=None, counted=set()):
        super(RefCount, self).__init__(player_type, midwife_type, signal)
        self.count = 0
        self.counted = counted

    """
    Return the number of women referred on an appointment.
    """
    def measure(self, roundnum, women, game):
        if self.player_type is not None:
            women = filter(lambda x: x.player_type == self.player_type, women)
        women = filter(lambda x: x.rounds == self.signal, women)
        women = filter(lambda x: 1 in x.response_log, women)
        women = filter(lambda x: hash(x) not in self.counted, women)
        self.counted.update(map(hash, women))
        self.count += len(women)
        return self.count
        
class CumulativeRefCount(Measure):
    def __init__(self, player_type=None, midwife_type=None, signal=None):
        super(CumulativeRefCount, self).__init__(player_type, midwife_type, signal)
        counted = set()
        self.counters = [RefCount(player_type, midwife_type, x, counted) for x in range(signal)]

    """
    Return the number of women referred upto an appointment.
    """
    def measure(self, roundnum, women, game):
        return sum(map(lambda x: x.measure(roundnum, women, game), self.counters))
        
class CumulativeHonestyCount(Measure):
    def __init__(self, player_type=None, midwife_type=None, signal=None):
        super(CumulativeHonestyCount, self).__init__(player_type, midwife_type, signal)
        counted = set()
        self.counters = [HonestyMeasure(player_type, midwife_type, x, counted) for x in range(signal)]

    """
    Return the number of women referred upto an appointment.
    """
    def measure(self, roundnum, women, game):
        return sum(map(lambda x: x.measure(roundnum, women, game), self.counters))


def abstract_measures_women():
    measures = OrderedDict()
    measures['round'] = Appointment()
    for i in range(3):
        measures["type_%d_pop" % i] = PopCount(player_type = i)
        for j in range(11):
            measures["type_%d_round_%d_ref" % (i, j)] = CumulativeRefCount(player_type=i, signal=j+1)
            measures["type_%d_round_%d_honesty" % (i, j)] = CumulativeHonestyCount(player_type=i, signal=j+1)
    return Measures(measures)

def abstract_measures_mw():
    measures = OrderedDict()
    measures['appointment'] = Appointment()
    return Measures(measures)