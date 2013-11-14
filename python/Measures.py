from collections import OrderedDict
# Measures

def appointment(roundnum, women, game):
    """
    Return the value passed as roundnum.
    """
    return roundnum


def finished(roundnum, women, game):
    """
    Return the fraction of the women finished by this round
    """
    num_women = float(len(women))
    num_finished = sum(map(lambda x: 1 if x.finished < roundnum else 0, women))
    if num_women == 0:
            return 0
    return num_finished / num_women

def type_finished(player_type):
    """
    Return the fraction of women of a particular type who finished this round.
    """
    def f(roundnum, women, game):
        women = filter(lambda x: x.player_type == player_type, women)
        num_women = float(len(women))
        num_finished = sum(map(lambda x: 1 if x.finished < roundnum else 0, women))
        if num_women == 0:
            return 0
        return num_finished / num_women
    return f



def type_signal(player_type, signal):
    """
    Return a function that yields the fraction of that type
    who signalled so in that round.
    """
    def f(roundnum, women, game):
        women = filter(lambda x: x.player_type == player_type, women)
        #women = filter(lambda x: len(x.signal_log) > roundnum, women)
        num_women = len(women)
        women = filter(lambda x: x.round_signal(roundnum) == signal, women)
        signalled = len(women)
        if num_women == 0:
            return 0
        return signalled / float(num_women)
    return f


def type_signal_breakdown(player_type, signal, midwife_type):
    """
    Return a function that yields the fraction of women of some type signalling
    a particular way who had a midwife of a particular type.
    """
    def f(roundnum, women, game):
        women = filter(lambda x: x.player_type == player_type, women)
        women = filter(lambda x: len(x.signal_log) > roundnum, women)
        women = filter(lambda x: x.type_log[roundnum] == midwife_type, women)
        num_women = len(women)
        women = filter(lambda x: x.signal_log[roundnum] == signal, women)
        signalled = len(women)
        if num_women == 0:
            return 0
        return signalled / float(num_women)
    return f


def type_referral_breakdown(player_type, signal, midwife_type):
    """
    Return a function that yields the fraction of women of some type signalling
    a particular way who had a midwife of a particular type and got referred.
    If signal is None, then this is for all signals.
    If midwife_type is None, then this is for all midwife types.
    """
    def f(roundnum, women, game):
        women = filter(lambda x: x.player_type == player_type, women)
        women = filter(lambda x: len(x.signal_log) > roundnum, women)
        if midwife_type is not None:
            women = filter(lambda x: x.type_log[roundnum] == midwife_type, women)
        num_women = len(women)
        if signal is not None:
            women = filter(lambda x: x.signal_log[roundnum] == signal, women)
        women = filter(lambda x: x.response_log[roundnum] == 1, women)
        signalled = len(women)
        if num_women == 0:
            return 0
        return signalled / float(num_women)
    return f


def payoff_type(player_type=None):
    """
    Return a function that gives the average payoff in that
    round for a given type. If type is None, then the average
    for all types is returned.
    """
    def f(roundnum, women, game):
        if player_type is not None:
            women = filter(lambda x: x.player_type == player_type, women)
        women = filter(lambda x: len(x.payoff_log) > roundnum, women)
        if len(women) == 0:
            return 0
        return sum(map(lambda x: x.payoff_log[roundnum], women)) / float(len(women))
    return f

def signal_change(player_type):
    """
    Return a function that yields average change in signal
    by women this round from last round.
    """
    def f(roundnum, women, game):
        if roundnum == 0:
            return 0
        women = filter(lambda x: x.player_type == player_type, women)
        women = filter(lambda x: len(x.signal_log) > roundnum, women)
        num_women = len(women)
        if num_women == 0:
            return 0
        change = map(lambda x: x.signal_log[roundnum] - x.signal_log[roundnum - 1], women)
        return sum(change) / float(num_women)
    return f

def signals(roundnum, women, game):
    """
    Return a colon separated list of the signals of all women this round.
    Women who have finished are denoted by a -1.
    """
    sigs = map(lambda x: -1 if x.finished < roundnum else x.signal_log[roundnum], women)
    return ":".join(str(x) for x in sigs)

def signal_implies_referral(player_type, signal, midwife_type):
    """
    Return a function that gives the average belief of players of this
    type that that signal will lead to referral, who had this type of midwife
    on a round. If player_type or midwife_type are None, this returns for all of that type.
    """
    def f(roundnum, women, game):
        if player_type is not None:
            women = filter(lambda x: x.player_type == player_type, women)
        if midwife_type is not None:
            women = filter(lambda x: len(x.type_log) > roundnum, women)
            women = filter(lambda x: x.type_log[roundnum] == midwife_type, women)
        #women = filter(lambda x: len(x.response_belief[signal][1]) > roundnum, women)
        belief = sum(map(lambda x: x.round_response_belief(roundnum)[signal][1], women))
        if len(women) == 0:
            return 0
        return belief / len(women)
    return f

def signal_risk(player_type, signal, midwife_type):
    """
    Return a function that gives the average risk associated
    with sending signal by players of this type who had that
    midwife type on a round.
    """
    def f(roundnum, women, game):
        #women = filter(lambda x: len(x.type_log) > roundnum, women)
        if player_type is not None:
            women = filter(lambda x: x.player_type == player_type, women)
        if midwife_type is not None:
            women = filter(lambda x: len(x.type_log) > roundnum, women)
            women = filter(lambda x: x.type_log[roundnum] == midwife_type, women)
        total = sum(map(lambda x: x.round_signal_risk(roundnum)[signal], women))
        if len(women) == 0:
            return 0.
        return total / float(len(women))
    return f

def distribution_belief(player_type, midwife_type):
    """
    Return a function that gives the average believed prevalence
    of this midwife type by this type of player. Or for all players
    where player_type is None.
    """
    def f(roundnum, women, game):
        if player_type is not None:
            women = filter(lambda x: x.player_type == player_type, women)
        #women = filter(lambda x: len(x.type_distribution[midwife_type]) > roundnum, women)
        num_women = len(women)
        belief = sum(map(lambda x: x.round_type_distribution(roundnum)[midwife_type], women))
        if num_women == 0:
            return 0.
        return belief / num_women
    return f

def signal_meaning(player_type, signal):
    """
    Return a function that yields the average belief
    that this signal means that type.
    """
    def f(roundnum, women, game):
        women = filter(lambda x: len(x.signal_belief[signal][player_type]) > roundnum, women)
        total = sum(map(lambda x: x.signal_belief[signal][player_type][roundnum], women))
        if len(women) == 0:
            return 0.
        return total / float(len(women))
    return f

def params_dict(signaller_rule, responder_rule, mw_weights, women_weights, game, rounds):
    params = OrderedDict()
    params['game'] = str(game)
    params['decision_rule_responder'] = responder_rule
    params['decision_rule_signaller'] = signaller_rule
    params['caseload'] = game.is_caseloaded()
    params['mw_0'] = mw_weights[0]
    params['mw_1'] = mw_weights[1]
    params['mw_2'] = mw_weights[2]
    params['women_0'] = women_weights[0]
    params['women_1'] = women_weights[1]
    params['women_2'] = women_weights[2]
    params['max_rounds'] = rounds

    for i in range(3):
        for j in range(3):
            params['weight_%d_%d' % (i, j)] = game.type_weights[i][j]
    return params


def measures_women():
    measures = OrderedDict()
    measures['appointment'] = appointment
    measures['finished'] = finished
    for i in range(3):
        measures["type_%d_ref" % i] = type_referral_breakdown(i, None, None)
        measures["type_%d_finished" % i] = type_finished(i)
        measures["type_%d_signal_change" % i] = signal_change(i)
        measures["global_type_frequency_%d" % i] = distribution_belief(None, i)
        for j in range(3):
            measures["type_%d_signal_%d" % (i, j)] = type_signal(i, j)
            measures["type_%d_mw_%d_ref" % (i, j)] = type_referral_breakdown(i, None, j)
            measures["type_%d_sig_%d_ref" % (i, j)] = type_referral_breakdown(i, j, None)
            measures["type_%d_signal_%d_means_referral" % (i, j)] = signal_implies_referral(i, j, None)
            measures["type_%d_sig_%d_risk" % (i, j)] = signal_risk(i, j, None)
            measures["player_type_%d_frequency_%d" % (i, j)] = distribution_belief(i, j)
            for k in range(3):
                measures["type_%d_sig_%d_mw_%d_risk" % (i, j, k)] = signal_risk(i, j, k)
                measures["type_%d_mw_%d_sig_%d" % (i, j, k)] = type_signal_breakdown(i, k, j)
                measures["type_%d_signal_%d_with_mw_type_%d_means_referral" % (i, j, k)] = signal_implies_referral(i, j, k)
    return measures

def measures_midwives():
    measures_mw = OrderedDict()
    measures_mw['appointment'] = appointment
    for i in range(3):
        for j in range(3):
            measures_mw["signal_%d_means_%d" % (i, j)] = signal_meaning(j, i)
    return measures_mw