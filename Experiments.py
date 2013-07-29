from Model import *
from ProspectTheoryModel import *

line_type = {}
line_type[0] = '+-'
line_type[1] = 'o-'
line_type[2] = '1-'
line_colour = {}
line_colour[0] = 'r'
line_colour[1] = 'b'
line_colour[2] = 'g'

def generate_players():
    """ Generate players for a game.
    """
    return (Agent(None), Agent(None))

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
    


def make_random_patients(signaller, num=1000, weights=[1/3., 1/3., 1/3.]):
    women = []
    for i in range(num):
        women.append(signaller(player_type=weighted_choice(zip([0, 1, 2], weights))))
    return women

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
        for signal in signals:
            for i in range(women[0].rounds):
                choices[player_type][signal][i] /= float(counts[player_type])
    return choices

def dump_game_women_pair(pair, params, file_name, mode):
    file_name = "results/" + file_name
    game, women = pair
    sigs = signal_choice(women)
    dist = distribution_belief(women)
    ref = signal_ref_belief(women)
    header = "\n"
    try:
        with open(file_name): pass
    except IOError:
        mode = 'w'
    if mode == 'a':
        target = open(file_name, 'a')
        target.write(header)
        target.close()

    elif mode == 'w':
        target = open(file_name, 'w')
        header = "appointment"
        for i in range(3):
            for j in range(3):
                header += ",type_%d_signal_%d" % (i, j)
        for name, value in dist.items():
            header += ", %s" % name
        for name, value in ref.items():
            header += ", %s" % name
        for name, value in params.items():
            header += ",%s" % name
        for name, value in game.payoffs.items():
            header += ",%s" % name
        header += "\n"
        target.write(header)
        target.close()
    param_vals = ""
    for name, value in params.items():
        param_vals += ",%s" % value
    lines = []
    for x in range(women[0].rounds - 1):
            line = "%d" % x
            for i in range(3):
                for j in range(3):
                    line += ",%f" % sigs[i][j][x]
            for name, value in dist.items():
                line += ", %f" % value[x]
            for name, value in ref.items():
                line += ", %f" % value[x]
            line += param_vals
            for name, value in game.payoffs.items():
                line += ",%d" % value
            lines.append(line)
    target = open(file_name, 'a')
    target.write("\n".join(lines))
    target.close()

def dump_game_women_pair_change(pair, params, file_name, mode):
    file_name = "results/" + file_name
    game, women = pair
    sigs = signal_choice(women)
    dist = distribution_belief(women)
    ref = signal_ref_belief(women)
    header = "\n"
    try:
        with open(file_name): pass
    except IOError:
        mode = 'w'
    if mode == 'a':
        target = open(file_name, 'a')
        target.write(header)
        target.close()

    elif mode == 'w':
        target = open(file_name, 'w')
        headers = []
        for i in range(3):
            for j in range(3):
                headers.append("type_%d_signal_%d" % (i, j))
        for name, value in dist.items():
            headers.append("%s" % name)
        for name, value in ref.items():
            headers.append("%s" % name)
        for name, value in params.items():
            headers.append("%s" % name)
        for name, value in game.payoffs.items():
            headers.append("%s" % name)
        target.write(", ".join(headers) + "\n")
        target.close()
    param_vals = []
    for name, value in params.items():
        param_vals.append("%s" % value)
    param_vals = ", ".join(param_vals)
    vals = []
    line = ""
    for i in range(3):
        for j in range(3):
            vals.append("%f" % (sigs[i][j][0] - sigs[i][j][len(sigs[i][j]) - 1]))
    for name, value in dist.items():
        vals.append("%f" % (value[0] - value[len(value) - 1]))
    for name, value in ref.items():
        vals.append("%f" % (value[0] - value[len(value) - 1]))
    vals.append(param_vals)
    for name, value in game.payoffs.items():
        vals.append("%d" % value)
    line = ", ".join(vals) + "\n"
    target = open(file_name, 'a')
    target.write(line)
    target.close()

def dump_game_mw_pair(pair, params, file_name, mode):
    file_name = "results/" + file_name
    game, women = pair
    sigs = type_belief(women)
    header = "\n"
    try:
        with open(file_name): pass
    except IOError:
        mode = 'w'
    if mode == 'a':
        target = open(file_name, 'a')
        target.write(header)
        target.close()

    elif mode == 'w':
        target = open(file_name, 'w')
        header = "appointment, signal -> type, belief, %s, %s" % (",".join(params.keys()), ",".join(game.payoffs.keys()))
        header += "\n"
        target.write(header)
        target.close()
    param_vals = ""
    game_string = ""
    for name, value in params.items():
        param_vals += ",%s" % value
    for name, value in game.payoffs.items():
        game_string += ",%d" % value
    lines = []
    for x in range(len(sigs["0"]["0"])):
            for i in range(3):
                for j in range(3):
                    line = "%d, %d -> %d, %f %s %s" % (x, i, j, sigs["%d" % i]["%d" % j][x], param_vals, game_string)
                    lines.append(line)
    target = open(file_name, 'a')
    target.write("\n".join(lines))
    target.close()



def dump_women(pair, params,file_name, mode):
    file_name = "results/" + file_name
    game, women = pair
    header = "\n"
    try:
        with open(file_name): pass
    except IOError:
        mode = 'w'
    if mode == 'a':
        target = open(file_name, 'a')
        target.write(header)
        target.close()

    elif mode == 'w':
        target = open(file_name, 'w')
        header = "id, appointment, type, signal, payoff, referred, mw_0, mw_1, mw_2, ref_0, ref_1, ref_2"
        for name, value in params.items():
            header += ",%s" % name
        for name, value in game.payoffs.items():
            header += ",%s" % name
        header += "\n"
        target.write(header)
        target.close()
    param_vals = ""
    for name, value in params.items():
        param_vals += ",%s" % value
    lines = []
    j = 0
    for woman in women:
        for i in range(woman.rounds):
            line = "%d, %d,%d,%d, %f, %s, %f, %f, %f, %f, %f, %f %s" % (j, i, woman.player_type, woman.signal_log[i], woman.payoff_log[i],
             woman.response_log[i] == 1, woman.type_distribution[0][i], woman.type_distribution[1][i], woman.type_distribution[2][i],
             woman.response_belief[0][1][i], woman.response_belief[1][1][i], woman.response_belief[2][1][i],param_vals)
            for name, value in game.payoffs.items():
                line += ",%d" % value
            lines.append(line)
        j += 1
    target = open(file_name, 'a')
    target.write("\n".join(lines))
    target.close()

def dump_midwives(pair, params,file_name, mode):
    file_name = "results/" + file_name
    game, midwives = pair
    header = "\n"
    try:
        with open(file_name): pass
    except IOError:
        mode = 'w'
    if mode == 'a':
        target = open(file_name, 'a')
        target.write(header)
        target.close()
        target = open("signals_"+file_name, 'a')
        target.write(header)
        target.close()

    elif mode == 'w':
        target = open(file_name, 'w')
        header = "id, appointment, type, signal, payoff, referred"
        for name, value in params.items():
            header += ",%s" % name
        for name, value in game.payoffs.items():
            header += ",%s" % name
        header += "\n"
        target.write(header)
        target.close()

        target = open("signals_"+file_name, 'w')
        header = "id, appointment, type, belief, b_type, belief_level"
        for name, value in params.items():
            header += ",%s" % name
        for name, value in game.payoffs.items():
            header += ",%s" % name
        header += "\n"
        target.write(header)
        target.close()
    param_vals = ""
    for name, value in params.items():
        param_vals += ",%s" % value
    lines = []
    sig_lines = []
    j = 0
    for woman in midwives:
        for i in range(woman.rounds):
            line = "%d, %d,%d,%d, %f, %s %s" % (j, i, woman.player_type, woman.signal_log[i], woman.payoff_log[i], woman.response_log[i] == 1, param_vals)
            for name, value in game.payoffs.items():
                line += ",%d" % value
            lines.append(line)

            for signal, types in woman.signal_belief.items():
                for player_type, log in types.items():
                    line = "%d, %d,%d,%d, %d, %f %s" % (j, i, woman.player_type, signal, player_type, woman.signal_belief[signal][player_type][i], param_vals)
                    for name, value in game.payoffs.items():
                        line += ",%d" % value
                    sig_lines.append(line)
        j += 1
    target = open(file_name, 'a')
    target.write("\n".join(lines))
    target.close()
    target = open("signals_"+file_name, 'a')
    target.write("\n".join(sig_lines))
    target.close()

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
    Return the probability of referring over time.
    """
    counts = rounds_count(midwives)
    max_rounds = max(counts.keys())
    referral = {'all':[0 for x in range(max_rounds)]}
    for signal in range(3):
        referral[signal] = [[0, 0] for x in range(max_rounds)]

    for midwife in midwives:
        for i in range(midwife.rounds):
            if midwife.response_log[i] == 1:
                referral['all'][i] += 1.
                referral[midwife.signal_log[i]][i][1] += 1.
            referral[midwife.signal_log[i]][i][0] += 1.
    for i in range(max_rounds):
        referral['all'][i] /= float(counts[i])
        for signal in range(3):
            if referral[signal][i][0] > 0:
                referral[signal][i] = referral[signal][i][1] / referral[signal][i][0]
            else:
                referral[signal][i] = 0.
    return referral

def plot_referral_choice(midwives):
    choices = referral_choice(midwives)
    for signal, log in choices.items():
        label = "Signal:", signal
        pylab.plot(range(len(log)), log, label=label)
    pylab.legend(loc='upper right')
    pylab.show()



def plot_signal_beliefs(midwives):
    beliefs = type_belief(midwives)
    for signal, types in beliefs.items():
        for player_type, log in types.items():
            label = "Signal: %d, type: %d" % (signal, player_type)
            line = "%s%s" % (line_colour[player_type], line_type[signal])
            pylab.plot(range(len(log)), log, line, label=label)
    pylab.legend(loc='upper right')
    pylab.show()




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


def plot_average_signal_choice(women):
    choices = signal_choice(women)

    for player_type, signals in choices.items():
        for signal, log in signals.items():
            label = "Type: %d, signal: %d" % (player_type, signal)
            line = "%s%s" % (line_colour[signal], line_type[player_type])
            pylab.plot(range(women[0].rounds), log, line, label=label)
    pylab.legend(loc='upper right')
    pylab.show()

def plot_signal_choice(women):
    for player_type, signals in choices.items():
        for signal, log in signals.items():
            label = "Type: %d, signal: %d" % (player_type, signal)
            line = "%s%s" % (line_colour[signal], line_type[player_type])
            pylab.scatter(range(12), log, line, label=label)
    pylab.legend(loc='upper right')
    pylab.show()


def count(players):
    """
    Return the number of each player type.
    """
    types = {}
    types[0] = 0
    types[1] = 0
    types[2] = 0
    for player in players:
        types[player.player_type] += 1
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
    while not all_played(women, rounds):
        woman = women.pop()
        game.play_game(woman, random.choice(midwives))
        if woman.rounds == rounds:
            birthed.append(woman)
        else:
            women.append(woman)
        random.shuffle(women)
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
            results.append(random_expectations(depth - 1, breadth))
    return results


def decision_fn_compare(signaller_fn=BayesianSignaller, responder_fn=BayesianResponder, signaller_rule="bayes", 
    responder_rule="bayes", file_name="compare.csv",test_fn=test, num_midwives=100, num_women=1000, runs=100, caseload="FALSE", game=None, rounds=100,
    mw_weights=[80/100., 15/100., 5/100.]):
    prospect_women = []
    prospect_midwives = []
    bayes_women = []
    bayes_midwives = []
    if game is None:
        game = Game()
    for i in range(runs):
        type_weights = random_expectations()
        response_weights = [random_expectations(breadth=2) for x in range(3)]
        #type_weights = map(lambda x: x / 100., type_weights)
        game.init_payoffs(type_weights, response_weights)
        #{'mw_1':type_weights[0], 'mw_2':type_weights[1], 'mw_3':type_weights[2],'sig_0_ref':response_weights[0][1], 'sig_1_ref':response_weights[1][1], 'sig_2_ref':response_weights[2][1]
        params = {'decision_rule':responder_rule, 'caseload':caseload,'run':i}
        print "Starting run %d/%d on %s" % (i + 1, runs, file_name)

        women = make_random_patients(signaller_fn, num=num_women,weights=[1/3.]*3)
        mw = make_random_midwives(responder_fn, num_midwives, weights=mw_weights)
        print "Made agents."

        pair = test_fn(game, women, mw, rounds=rounds)
        print "Ran trial."
        #dump_women(pair, params, file_name, 'a')
        #dump_midwives((game, mw), params, "mw_"+file_name, 'a')
        dump_game_women_pair(pair, params, "summary_"+file_name, 'a')
        dump_game_women_pair_change(pair, params, "change_summary_"+file_name, 'a')
        dump_game_mw_pair((game, mw), params, "mw_summary_"+file_name, 'a')
        print "Dumped results."

def compare():
    game = Game()
    decision_fn_compare(ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", "monte_carlo_mw.csv", caseload="FALSE", game=game)
    decision_fn_compare(ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", "monte_carlo_mw.csv", test_fn=caseload_test, caseload="TRUE", game=game)
    decision_fn_compare(file_name="monte_carlo_mw.csv", test_fn=caseload_test, caseload="TRUE", game=game)
    decision_fn_compare(file_name="monte_carlo_mw.csv", caseload="FALSE", game=game)

def no_harsh_compare():
    game = Game()
    mw_weights=[80/100., 20/100., 0]
    decision_fn_compare(ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", "no_harsh_mw.csv", caseload="FALSE", game=game, mw_weights=mw_weights)
    decision_fn_compare(ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", "no_harsh_mw.csv", test_fn=caseload_test, caseload="TRUE", game=game, mw_weights=mw_weights)
    decision_fn_compare(file_name="no_harsh_mw.csv", test_fn=caseload_test, caseload="TRUE", game=game, mw_weights=mw_weights)
    decision_fn_compare(file_name="no_harsh_mw.csv", caseload="FALSE", game=game, mw_weights=mw_weights)

def high_stakes_compare():
    game = Game(num_rounds=1, baby_payoff=200, no_baby_payoff=200, mid_baby_payoff=100,referral_cost=100, harsh_high=200,
     harsh_mid=100, harsh_low=0, mid_high=100, mid_mid=0, mid_low=0, low_high=0,low_mid=0,low_low=0, randomise_payoffs=False)
    decision_fn_compare(ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", "high_stakes_compare.csv", caseload="FALSE", game=game)
    decision_fn_compare(ProspectTheorySignaller, ProspectTheoryResponder, "prospect", "prospect", "high_stakes_compare.csv", test_fn=caseload_test, caseload="TRUE", game=game)
    decision_fn_compare(file_name="high_stakes_compare.csv", test_fn=caseload_test, caseload="TRUE", game=game)
    decision_fn_compare(file_name="high_stakes_compare.csv", caseload="FALSE", game=game)

if __name__ == "__main__":
    compare()
    no_harsh_compare()
