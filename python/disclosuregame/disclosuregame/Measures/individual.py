from measures import *

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

class Started(Measure):
    """
    Return the
    """
    def measure(self, roundnum, women, game):
        return women[0].started

class LastSignal(Measure):
    def measure(self, roundnum, women, game):
        signal = 0
        try:
            signal = women[0].signal_log.pop()
            women[0].signal_log.append(signal)
        except IndexError:
            pass
        return signal

class RoundSignal(Measure):
    def measure(self, roundnum, women, game):
        try:
            signal = woman[0].signal_log[self.player_type]
        except:
            signal = "NA"
        return signal

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
    for i in range(12):
        measures['round_%d_signal' % i] = RoundSignal(player_type = i)
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