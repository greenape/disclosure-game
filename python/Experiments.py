from Model import *
from ProspectTheoryModel import *
from ReferralGame import *
from RecognitionAgents import *
from multiprocessing import Pool
import multiprocessing
import itertools
from collections import OrderedDict


def write_results_set(file_name, results, sep=","):
    write_results(file_name, results.pop(), 'w')
    for result in results:
        write_result(file_name, 'a', sep)


def write_results(file_name, results, mode, sep=","):
    """
    Write a results dictionary to a (csv) file.
    """
    if mode == 'w':
        result = [sep.join(results['fields'])]
    else:
        result = []
    result += map(lambda l: sep.join(map(str, l)), results['results'])
    file = open(file_name, mode)
    file.write("\n".join(result))
    file.close()


def all_played(women, rounds=12):
    for woman in women:
        if(woman.rounds < rounds):
            return False
    return True


def weighted_choice(choices):
    """
    Return a weighted random choice amongst player types,
    given a list of tuples of form (type, weight)
    """
    total = sum(weight for player_type, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for player_type, weight in choices:
        if upto + weight > r:
            return player_type
        upto += weight


def scale_weights(weights, top):
    scaling = top / float(sum(weights))
    for i in range(len(weights)):
        weights[i] *= scaling
    return weights


def make_players(constructor, num=100, weights=[1/3., 1/3., 1/3.]):
    women = []
    player_type = 0
    for weight in weights:
        for i in range(int(round(weight*num))):
            if len(women) == num: break
            women.append(constructor(player_type=player_type))
        player_type += 1
    while len(women) < num:
        women.append(constructor(player_type=0))
    return women


def make_random_patients(signaller, num=1000, weights=[1/3., 1/3., 1/3.]):
    women = []
    player_type = 0
    for weight in weights:
        for i in range(weight*100):
            women.append(signaller(player_type=player_type))
        player_type += 1
    return women


def make_random_weights(num=1000):
    weights = []
    for i in range(num):
        weights.append((Model.random_expectations(), [Model.random_expectations(breadth=2) for x in range(3)]))
    return weights


def inject_type_belief(weights, num):
    """
    Return a function that will modify the type distribution priors of num 
    random women to be those in weights and restarts faith.
    """
    def f(women):
        target = random.sample(women, num)
        signals = [0, 1, 2]
        for agent in target:
            agent.response_belief = dict([(signal, dict([(response, []) for response in [0, 1]])) for signal in signals])
            agent.type_distribution = dict([(signal, []) for signal in signals])
            agent.type_weights = weights
            agent.update_beliefs(None, None, None)
    return f


def make_random_midwives(responder, num=100, weights=[80/100., 15/100., 5/100.]):
    midwives = []
    for i in range(num):
        midwives.append(responder(player_type=weighted_choice(zip([0, 1, 2], weights))))
    return midwives


def signal_choice(women):
    """
    Return a dictionary of women type vs. average signal choice per
    round.
    """
    choices = {}
    for player_type in range(3):
        choices[player_type] = {}
        for signal in range(3):
            choices[player_type][signal] = [0 for x in range(women[0].rounds)]
    for player_type, players in by_type(women).items():
        for i in range(women[0].rounds):
            for player in players:
                choices[player_type][player.signal_log[i]][i] += 1
    counts = count(women)
    for player_type, signals in choices.items():
        if counts[player_type] > 0:
            for signal in signals:
                for i in range(women[0].rounds):
                    choices[player_type][signal][i] /= float(counts[player_type])
    return choices


def honesty_by_midwife_type(women):
    """
    Return a dictionary of women type vs. average signal choice per
    round, broken down by the type of midwife they caseloaded with.
    """
    choices = {}
    #counts = [[[[0 for x in range(women[0].rounds)] * 3] * 3] * 3]
    for player_type in range(3):
        choices[player_type] = {}
        for mw_type in range(3):
                choices[player_type][mw_type] = {}
                for signal in range(3):
                    choices[player_type][mw_type][signal] = [0 for x in range(women[0].rounds)]
    for player_type, players in by_type(women).items():
        for i in range(women[0].rounds):
            for player in players:
                midwife_type = player.type_log[0]
                choices[player_type][midwife_type][player.signal_log[i]][i] += 1
    counts = count_by_mw_type(women)
    for player_type, signals in choices.items():
        if counts[player_type][mw_type] > 0:
            for signal in signals:
                for mw_type in signals:
                    for i in range(women[0].rounds):
                        choices[player_type][mw_type][signal][i] /= float(counts[player_type][mw_type])
    return choices


def referral_by_midwife_type_woman_type(women):
    """
    Return a dictionary of women type vs. frequency of referral per
    round, broken down by the type of midwife they caseloaded with.
    """
    choices = {}
    #counts = [[[[0 for x in range(women[0].rounds)] * 3] * 3] * 3]
    for player_type in range(3):
        choices[player_type] = {}
        for mw_type in range(3):
                choices[player_type][mw_type] = {}
                for signal in range(2):
                    choices[player_type][mw_type][signal] = [0 for x in range(women[0].rounds)]
    for player_type, players in by_type(women).items():
        for i in range(women[0].rounds):
            for player in players:
                midwife_type = player.type_log[0]
                choices[player_type][midwife_type][player.response_log[i]][i] += 1
    counts = count_by_mw_type(women)
    for player_type, signals in choices.items():
        if counts[player_type][mw_type] > 0:
            for mw_type in signals:
                for i in range(women[0].rounds):
                    choices[player_type][mw_type][1][i] /= float(counts[player_type][mw_type])
    return choices


def referral_by_midwife_type(midwives):
    """
    Return a dictionary of frequency of referral per
    round, broken down by the type of midwife.
    """
    choices = {}
    #counts = [[[[0 for x in range(women[0].rounds)] * 3] * 3] * 3]
    rounds_counts = rounds_count(midwives)
    max_rounds = max(rounds_counts.keys())
    for mw_type in range(3):
            choices[mw_type] = {}
            for signal in range(2):
                choices[mw_type][signal] = [0 for x in range(max_rounds)]
    counts = [[0, 0, 0] for x in range(max_rounds)]
    for midwife in midwives:
        for i in range(midwife.rounds - 1):
            choices[midwife.player_type][midwife.response_log[i]][i] += 1.
            counts[i][midwife.player_type] += 1.

    for i in range(max_rounds):
        for j in range(3):
            if counts[i][j] > 0:
                choices[j][0][i] /= counts[i][j]
                choices[j][1][i] /= counts[i][j]
    return choices


def payoff(women):
    """
    Return a dictionary of women type vs. average payoff per
    round.
    """
    choices = {}
    rounds_counts = rounds_count(women)
    max_rounds = max(rounds_counts.keys())
    result = {}
    for player_type in range(3):
        choices[player_type] = {}
        for signal in range(3):
            choices[player_type] = [0. for x in range(max_rounds)]
            result["payoff_%d" % player_type] = [0. for x in range(max_rounds)]
    choices['all'] = [0. for x in range(max_rounds)]
    result['payoff_all'] = [0. for x in range(max_rounds)]
    for player_type, players in by_type(women).items():
        for i in range(max_rounds):
            for player in players:
                if len(player.payoff_log) > i:
                    choices[player_type][i] += player.payoff_log[i]
                    choices['all'][i] += player.payoff_log[i]
    for i in range(max_rounds):
        counts = count(women, i)
        for player_type, signals in choices.items():
            if counts[player_type] > 0:
                result["payoff_" + str(player_type)][i] = choices[player_type][i] / float(counts[player_type])

    return result


def dump_game_women_pair(pair, params):
    """
    Return a results dictionary.
    """
    header = "appointment,type_0_signal_0,type_0_signal_0_change,type_0_signal_1,type_0_signal_1_change,type_0_signal_2,type_0_signal_2_change,type_1_signal_0,type_1_signal_0_change,type_1_signal_1,type_1_signal_1_change,type_1_signal_2,type_1_signal_2_change,type_2_signal_0,type_2_signal_0_change,type_2_signal_1,type_2_signal_1_change,type_2_signal_2,type_2_signal_2_change,type_2,type_2_change,type_1,type_1_change,type_0,type_0_change,signal_1,signal_1_change,signal_0,signal_0_change,signal_2,signal_2_change,decision_rule,caseload,mw_0,mw_1,mw_2,women_0,women_1,women_2,weight_0_0,weight_0_1,weight_0_2,weight_1_0,weight_1_1,weight_1_2,weight_2_0,weight_2_1,weight_2_2,run,harsh_mid,mid_high,mid_baby_payoff,referral_cost,baby_payoff,harsh_high,low_high,mid_low,low_low,low_mid,no_baby_payoff,harsh_low,mid_mid,payoff_0,payoff_1,payoff_2,payoff_all"
    results = {'fields': header.split(","), 'results': []}
    game, women = pair
    sigs = signal_choice(women)
    #sigs_by_mw = honesty_by_midwife_type(women)
    dist = distribution_belief(women)
    ref = signal_ref_belief(women)
    payoffs = payoff(women)

    for x in range(women[0].rounds - 1):
            line = [x]
            for i in range(3):
                for j in range(3):
                    line += [sigs[i][j][x], sigs[i][j][x] - sigs[i][j][0]]
            for name, value in dist.items():
                line += [value[x], value[x] - value[0]]
            for name, value in ref.items():
                line += [value[x], value[x] - value[0]]
            line += params.values()
            line += game.payoffs.values()
            for name, value in payoffs.items():
                line += [value[x]]
            print line
            results['results'].append(line)
    return results


def dump_game_women_pair_breakdown(pair, params):
    game, women = pair
    sigs = signal_choice(women)
    sigs_by_mw = honesty_by_midwife_type(women)
    refs_by_mw = referral_by_midwife_type_woman_type(women)
    dist = distribution_belief(women)
    ref = signal_ref_belief(women)
    payoffs = payoff(women)

    header = "appointment,type_0_signal_0,type_0_signal_0_change,type_0_signal_1,type_0_signal_1_change,type_0_signal_2,type_0_signal_2_change,type_1_signal_0,type_1_signal_0_change,type_1_signal_1,type_1_signal_1_change,type_1_signal_2,type_1_signal_2_change,type_2_signal_0,type_2_signal_0_change,type_2_signal_1,type_2_signal_1_change,type_2_signal_2,type_2_signal_2_change, type_2, type_2_change, type_1, type_1_change, type_0, type_0_change, signal_1, signal_1_change, signal_0, signal_0_change, signal_2, signal_2_change,decision_rule_responder,decision_rule_signaller,caseload,mw_0,mw_1,mw_2,women_0,women_1,women_2,weight_0_0,weight_0_1,weight_0_2,weight_1_0,weight_1_1,weight_1_2,weight_2_0,weight_2_1,weight_2_2,run,harsh_mid,mid_high,mid_baby_payoff,referral_cost,baby_payoff,harsh_high,low_high,mid_low,low_low,low_mid,no_baby_payoff,harsh_low,mid_mid,payoff_0,payoff_1,payoff_2,payoff_all"
    header = header.split(",")
    for i in range(3):
        for j in range(3):
            header += ["type_%d_mw_%d_ref" % (i, j)]
            for k in range(3):
                header += ["type_%d_mw_%d_sig_%d" % (i, j, k)]
    results = {'fields':header, 'results':[]}

    for x in range(women[0].rounds - 1):
            line = [x]
            for i in range(3):
                for j in range(3):
                    line += [sigs[i][j][x], sigs[i][j][x] - sigs[i][j][0]]
            for name, value in dist.items():
                line += [value[x], value[x] - value[0]]
            for name, value in ref.items():
                line += [value[x], value[x] - value[0]]
            line += params.values()
            line += game.payoffs.values()
            for name, value in payoffs.items():
                line += [value[x]]
            for i in range(3):
                for j in range(3):
                    line += [refs_by_mw[i][j][1][x]]
                    for k in range(3):
                        line += [sigs_by_mw[i][j][k][x]]
            print line
            results['results'].append(line)
    return results


def outcome(pair, params):
    header = "type_2_sig_2,type_1_sig_1,type_2_sig_0,type_1_sig_0,type_2_sig_2_change,type_1_sig_1_change,type_2_sig_0_change,type_1_sig_0_change"
    header = header.split(",")
    header += params.keys()

    results = {'fields':header,'results':[]}
    game, women = pair
    sigs = signal_choice(women)

    line = [sigs[2][2][0], sigs[1][1][0], sigs[2][0][0], sigs[1][0][0], sigs[2][2][women[0].rounds - 1] - sigs[2][2][0], 
    sigs[1][1][women[0].rounds - 1] - sigs[1][1][0], sigs[2][0][women[0].rounds - 1] - sigs[2][0][0], 
    sigs[1][0][women[0].rounds - 1] - sigs[1][0][0]]
    line += params.values()
    results['results'].append(line)

    return results


def dump_game_mw_pair(pair, params):
    game, women = pair
    sigs = type_belief(women)
    choices = referral_choice(women)
    refs = referral_by_midwife_type(women)
    payoffs = payoff(women)

    header = ["appointment","payoff"]
    header += params.keys()
    header += game.payoffs.keys()
    for i in range(3):
        for j in range(3):
            header += ["type_%d_signal_%d" % (i, j)]
            header += ["type_%d_signal_%d_change" % (i, j)]
        header += ["signal_%d_ref" % (i)]
        header += ["signal_%d_ref_change" % (i)]
        header += ["type_%d_ref" % i]
    results = {'fields':header, 'results':[]}
    param_vals = params.values()
    game_string = game.payoffs.values()
    for x in range(len(sigs["0"]["0"])):
        line = [x, payoffs['payoff_all'][x]]
        line += param_vals
        line += game_string
        for i in range(3):
            for j in range(3):
                line += [sigs["%d" % i]["%d" % j][x], sigs["%d" % i]["%d" % j][x] - sigs["%d" % i]["%d" % j][0]]
            line += [choices["signal_%d_ref" % i][x], choices["signal_%d_ref" % i][x] - choices["signal_%d_ref" % i][0]]
            line += [refs[i][1][x]]
        results['results'].append(line)
    return results


def type_belief(midwives):
    """
    Return a dictionary of signals vs. average belief about what they mean
    per round.
    """
    beliefs = {}
    counts = rounds_count(midwives)
    max_rounds = max(counts.keys())
    for i in range(3):
        beliefs["%d" % i] = {}
        for j in range(3):
            beliefs["%d" % i]["%d" % j] = [0 for x in range(max_rounds)]
    for midwife in midwives:
        for i in range(3):
            for j in range(3):
                for k in range(midwife.rounds - 1):
                    beliefs["%d" % i]["%d" % j][k] += midwife.signal_belief[i][j][k]
    for i in range(3):
        for j in range(3):
            for k in range(max_rounds - 1):
                beliefs["%d" % i]["%d" % j][k] /= float(counts[k])
    return beliefs


def distribution_belief(women):
    beliefs = {"type_0": [0.]*(women[0].rounds - 1), "type_1": [0.]*(women[0].rounds - 1), "type_2": [0.]*(women[0].rounds - 1)}
    for i in range(women[0].rounds - 1):
        for woman in women:
            for player_type, belief in woman.type_distribution.items():
                beliefs["type_%d" % player_type][i] += belief[i] / len(women)
    return beliefs


def signal_ref_belief(women):
    beliefs = {"signal_0": [0.]*(women[0].rounds - 1), "signal_1": [0.]*(women[0].rounds - 1), "signal_2": [0.]*(women[0].rounds - 1)}
    for i in range(women[0].rounds - 1):
        for woman in women:
            for signal, responses in woman.response_belief.items():
                belief = responses[1][i]
                beliefs["signal_%d" % signal][i] += belief / len(women)
    return beliefs


def referral_choice(midwives):
    """
    Return the probability of referring over time broken down by signal.
    """
    counts = rounds_count(midwives)
    max_rounds = max(counts.keys())
    referral = {'all':[0 for x in range(max_rounds)]}
    for signal in range(3):
        referral["signal_%d_ref" % signal] = [[0, 0] for x in range(max_rounds)]

    for midwife in midwives:
        for i in range(midwife.rounds - 1):
            if midwife.response_log[i] == 1:
                referral['all'][i] += 1.
                referral["signal_%d_ref" % midwife.signal_log[i]][i][1] += 1.
            referral["signal_%d_ref" % midwife.signal_log[i]][i][0] += 1.
    for i in range(max_rounds):
        referral['all'][i] /= float(counts[i])
        for signal in range(3):
            if referral["signal_%d_ref" % signal][i][0] > 0:
                referral["signal_%d_ref" % signal][i] = referral["signal_%d_ref" % signal][i][1] / referral["signal_%d_ref" % signal][i][0]
            else:
                referral["signal_%d_ref" % signal][i] = 0.
    return referral


def rounds_count(players):
    """
    Return a dictionary mapping number of rounds played
    to the number of players who played at least that many.
    """
    counts = {}
    for player in players:
        for i in range(player.rounds):
            if i in counts:
                counts[i] += 1
            else:
                counts[i] = 1
    return counts


def count(players, rounds=None):
    """
    Return the number of each player type.
    """
    types = {}
    types[0] = 0
    types[1] = 0
    types[2] = 0
    types['all'] = 0
    for player in players:
        if rounds is None or player.rounds > rounds:
            types[player.player_type] += 1.
            types['all'] += 1.
    return types


def count_by_mw_type(players, rounds=None):
    """
    Return the number of each player type, broken down by their midwife type.
    """
    types = {}
    types[0] = [0, 0, 0]
    types[1] = [0, 0, 0]
    types[2] = [0, 0, 0]
    types['all'] = [0, 0, 0]
    for player in players:
        if rounds is None or player.rounds > rounds:
            types[player.player_type][player.type_log[0]] += 1.
            types['all'][player.type_log[0]] += 1.
    return types


def by_type(players):
    """ Return a dictionary mapping player type
    to a list of players with it.
    """
    types = {}
    for player_type in range(3):
        types[player_type] = []
    for player in players:
        types[player.player_type].append(player)
    return types


def test(game, women, midwives, rounds=12):
    birthed = []
    random.shuffle(women)
    while not all_played(women, rounds):
        woman = women.pop()
        game.play_game(woman, random.choice(midwives))
        if woman.rounds == rounds:
            birthed.append(woman)
        else:
            women.append(woman)
    return (game, birthed)


def all_played_caseload(caseload, rounds=12):
    for midwife, cases in caseload.items():
        if not all_played(cases, rounds):
            return False
    return True


def caseload_test(game, women, midwives, rounds=12):
    birthed = []
    #Assign women to midwives
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

    while not all_played_caseload(caseloads, rounds):
        for midwife, cases in caseloads.items():
            if not all_played(cases, rounds):
                woman = cases.pop()
                game.play_game(woman, midwife)
                if woman.rounds == rounds:
                    birthed.append(woman)
                else:
                    cases.append(woman)
    return (game, birthed)


def equal_rounds(game, women, midwives, rounds=100):
    game.init_payoffs()

    for i in range(rounds):
        random.shuffle(women)
        random.shuffle(midwives)

        for j in range(len(women)):
            game.play_game(women[j], midwives[j])
    return (game, women)


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


def decision_fn_compare(signaller_fn=BayesianSignaller, responder_fn=BayesianResponder, signaller_rule="bayes", 
    responder_rule="bayes", file_name="compare.csv",test_fn=test, num_midwives=100, num_women=1000, runs=10, caseload="FALSE", game=None, rounds=100,
    mw_weights=[80/100., 15/100., 5/100.], women_weights=[1/3., 1/3., 1/3.], dumper_w=dump_game_women_pair_breakdown, dumper_mw=dump_game_mw_pair, women_priors=None, seeds=None,
    women_modifier=None):

    output_w = {'fields': [], 'results': []}
    output_mw = {'fields': [], 'results': []}
    if game is None:
        game = Game()

    params = OrderedDict()
    params['decision_rule_responder'] = responder_rule
    params['decision_rule_signaller'] = signaller_rule
    params['caseload'] = caseload
    params['mw_0'] = mw_weights[0]
    params['mw_1'] = mw_weights[1]
    params['mw_2'] = mw_weights[2]
    params['women_0'] = women_weights[0]
    params['women_1'] = women_weights[1]
    params['women_2'] = women_weights[2]

    for i in range(3):
        for j in range(3):
            params['weight_%d_%d' % (i, j)] = game.type_weights[i][j]

    if seeds is None:
        seeds = [random.random() for x in range(runs)]

    for i in range(runs):
        # Parity across different conditions but random between runs.
        random.seed(seeds[i])
        params['run'] = i
        print "Starting run %d/%d on %s" % (i + 1, runs, file_name)

        #Make players and initialise beliefs
        women = make_players(signaller_fn, num=num_women,weights=women_weights)
        print "made %d women." % len(women)
        for j in range(len(women)):
            woman = women[j]
            if women_priors is not None:
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff, women_priors[j][0], women_priors[j][1])
            else:
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff, random_expectations(), [random_expectations(breadth=2) for x in range(3)])
        if women_modifier is not None:
            women_modifier(women)
        print "Set priors."
        mw = make_players(responder_fn, num_midwives, weights=mw_weights)
        print "Made agents."
        for midwife in mw:
            midwife.init_payoffs(game.midwife_payoff, game.type_weights)
        print "Set priors."

        pair = test_fn(game, women, mw, rounds=rounds)
        #print "Ran trial."
        #dump_women(pair, params, file_name, 'a')
        #dump_midwives((game, mw), params, "mw_"+file_name, 'a')
        if dumper_w is not None:
            results = dumper_w(pair, params)
            output_w['fields'] = results['fields']
            output_w['results'] += results['results']
            print output_w['results']
        #dump_game_women_pair_change(pair, params, "change_summary_"+file_name, 'a')
        if dumper_mw is not None:
            results = dumper_mw((game, mw), params)
            output_mw['fields'] = results['fields']
            output_mw['results'] += results['results']
        #print "Dumped results."
    if file_name is not None:
        write_results("women_"+file_name, output_w, 'w')
        write_results("mw_"+file_name, output_mw, 'w')
    return (output_w, output_mw)


def caseload_experiment(file_name="caseload.csv", game_fn=Game, 
    agents=[(ProspectTheorySignaller, ProspectTheoryResponder), (BayesianSignaller, BayesianResponder)]):
    game = game_fn()
    game.init_payoffs()
    for pair in agents:
        p = multiprocessing.Process(target=decision_fn_compare, args=(pair[0], pair[1], str(pair[0]), str(pair[1]), file_name,), kwargs={'caseload':"FALSE", 'game':game, 'dumper_w':dump_game_women_pair, 'dumper_mw':None})
        p.start()
        p = multiprocessing.Process(target=decision_fn_compare, args=(pair[0], pair[1], str(pair[0]), str(pair[1]), "caseload_%s" % file_name,), kwargs={'test_fn':caseload_test, 'caseload':"TRUE", 'game':game, 'dumper_mw':None})
        p.start()


def priors_experiment(file_name):
    proportions = []#list(itertools.permutations([80/100., 15/100., 5/100.]))
    proportions.append([1/3.]*3)
    prop_women = proportions
    #prop_women = [(0.05, 0.15, 0.8), (0.15, 0.05, 0.8)]
    #prop_women.remove((0.8, 0.15, 0.05))
    #prop_women.remove((0.8, 0.05, 0.15))
    priors =  [[[x, 1., 1.], [1., x, 1.], [1., 1., x]] for x in xrange(5, 51, 5)]
    variations = []
    for prior in priors:
        for variation in itertools.permutations(prior, 3):
            variations.append(variation)
    priors = variations
    priors.append([[1., 1., 1.], [1., 1., 1.], [1., 1., 1.]])
    for i in range(5):
        priors.append([[i + 1., 1., 1.], [1., i + 1., 1.], [1., 1., i + 1.]])
    #women_priors = make_random_weights(1000)
    run_params = []
    header = "type_2_sig_2,type_1_sig_1,type_2_sig_0,type_1_sig_0,type_2_sig_2_change,type_1_sig_1_change,type_2_sig_0_change,type_1_sig_0_change,decision_rule,caseload,mw_0,mw_1,mw_2,women_0,women_1,women_2"
    header = header.split(",")
    for i in range(3):
        for j in range(3):
            header += ['weight_%d_%d'] % (i, j)
    header += ["run"]
    total = len(prop_women)*len(proportions)*len(priors)*100
    pool = Pool(processes=2)
    for woman_prop in prop_women:
        for mw_prop in proportions:
            for prior in priors:
                #game = Game()
                #game.init_payoffs(type_weights=prior)
                #run_params.append([ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", file_name, False, game, mw_prop, woman_prop, outcome, None, None, None, 100])
                #game = Game()
                #game.init_payoffs(type_weights=prior)
                #run_params.append([ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", file_name, True, game, mw_prop, woman_prop, outcome, None, None])
                game = Game()
                game.init_payoffs(type_weights=prior)
                run_params.append([BayesianSignaller, BayesianResponder, "Bayesian", "Bayesian", None, False, game, mw_prop, woman_prop, outcome, None, None, range(100), 100])
                #game = Game()
                #game.init_payoffs(type_weights=prior)
                #run_params.append([BayesianSignaller, BayesianResponder, "Bayesian", "Bayesian", file_name, True, game, mw_prop, woman_prop, outcome, None, None])
    results = zip(*pool.map(run_game, run_params))
    write_results_set("mw_"+file_name, results[1])
    write_results_set("women_"+file_name, results[0])


def lhs_sampling(file_name, samples):
    i = 0
    run_params = []
    seeds = []
    priors = []
    mw_types = []
    types = []

    with open(samples) as f:
        content = f.readlines()
    f.close()
    for line in content:
        vals = line.split(" ")
        vals = vals[1:]
        print vals
        priors.append(vals[0:9])
        mw_types.append(vals[9:12])
        types.append(vals[12:15])
        seeds.append(5)
    total = len(content)
    pool = Pool(processes=2)
    for i in range(total):
        mw_priors = [float(priors[i][x]) for x in range(9)]
        mw_priors = [mw_priors[x:x+3] for x in xrange(0, len(mw_priors), 3)]
        mw_numbers = scale_weights([float(mw_types[i][x]) for x in range(3)], 1.)
        women_numbers = scale_weights([float(types[i][x]) for x in range(3)], 1.)
        seed = [5]

        game = Game()
        game.init_payoffs(type_weights=mw_priors)
        run_params.append([BayesianSignaller, BayesianResponder, "bayes", "bayes", file_name, False, game, mw_numbers, women_numbers, outcome, None, None, None, 1])
        #random.setstate(random_state)
    results = zip(*pool.map(run_game, run_params))
    write_results_set("mw_"+file_name, results[1])
    write_results_set("women_"+file_name, results[0])


def run_game(args):
    signaller, responder, junk, junk2, file_name, caseload, game, mw_weights, women_weights, dumper_w, dumper_mw, women_priors, seeds, runs = args
    test_fn = test
    if caseload:
        test_fn = caseload_test
    return decision_fn_compare(signaller, responder, junk, junk2, file_name, test_fn=test_fn, caseload=caseload, game=game, 
        mw_weights=mw_weights, women_weights=women_weights, dumper_w=dumper_w, dumper_mw=dumper_mw, women_priors=women_priors, seeds=seeds, runs=runs)

if __name__ == "__main__":
    #lhs_sampling("lhs_final.csv", "sa_final.txt")
    caseload_experiment("referral_test.csv", ReferralGame, [(RecognitionSignaller, BayesianResponder)])
    #priors_experiment("priors_final.csv")
    #alspac_caseload_experiment("alspac_caseloading_compare.csv")
    #muddy_caseload_experiment("caseloading_compare_breakdown_ref_muddy.csv")
