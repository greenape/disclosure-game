from collections import OrderedDict

def dump(pair, measures, params, results=None):
    """
    A results dumper. Takes a tuple of a game and players, and two dictionaries.
    Measures should contain a mapping from a field name to method for getting a result
    given an appointment, set of players, and a game. Params should contain mappings
    from parameter names to values.
    Optionally takes an exist results object to add records to. This should have the same
    measures and params.
    Returns a results object for writing to csv.
    """
    if results is None:
        results = {'fields':measures.keys() + params.keys(), 'results':[]}
    if pair is None:
        return results
    game, women = pair
    for i in range(params['max_rounds']):
        line = map(lambda x: x(i, women, game), measures.values())
        line += params.values()
        results['results'].append(line)
    return results


def random_expectations(depth=0, breadth=3, low=0, high=10):
    initial = [low, high]
    for i in range(breadth - 1):
        initial.append(random.random()*high)
    initial.sort()
    results = []
    for i in range(breadth):
        if depth == 0:
            results.append(float(initial[i + 1] - initial[i]))
        else:
            results.append(random_expectations(depth - 1, breadth, low, high))
    return results


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