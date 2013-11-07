from Model import *
from ProspectTheoryModel import *
from ReferralGame import *
from RecognitionGame import *
from RecognitionAgents import *
from AmbiguityAgents import *
from multiprocessing import Pool
import multiprocessing
import itertools
from collections import OrderedDict
import argparse


def arguments():
    parser = argparse.ArgumentParser(description='Run some variations of the disclosure game.')
    parser.add_argument('-g', '--games', type=str, nargs='*',
                   help='A game type to play.', default=['Game', 'CaseloadGame'],
                   choices=['Game', 'CaseloadGame', 'RecognitionGame', 'ReferralGame',
                   'CaseloadRecognitionGame', 'CaseloadReferralGame'],
                   dest="games")
    parser.add_argument('-s','--signallers', type=str, nargs='*',
        help='A signaller type.', default=["BayesianSignaller"],
        choices=['BayesianSignaller', 'RecognitionSignaller', 'AmbiguitySignaller'],
        dest="signallers")
    parser.add_argument('-r','--responders', type=str, nargs='*',
        help='A responder type.', default=["BayesianResponder"],
        choices=['BayesianResponder', 'RecognitionResponder'], dest="responders")
    parser.add_argument('-R','--runs', dest='runs', type=int,
        help="Number of runs for each combination of players and games.",
        default=100)
    parser.add_argument('-f','--file', dest='file_name', default="", type=str,
        help="File name prefix for csv output.")
    return parser


def write_results_set(file_name, results, sep=","):
    results = list(results)
    write_results(file_name, results.pop(), 'w')
    for result in results:
        write_results(file_name, result, 'a', sep)


def write_results(file_name, results, mode, sep=","):
    """
    Write a results dictionary to a (csv) file.
    """
    if mode == 'w':
        result = [sep.join(results['fields'])]
    else:
        result = ["\n"]
    result += map(lambda l: sep.join(map(str, l)), results['results'])
    file = open(file_name, mode)
    file.write("\n".join(result))
    file.close()


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


def params_dict(responder_rule, signaller_rule, mw_weights, women_weights, game, rounds):
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


def decision_fn_compare(signaller_fn=BayesianSignaller, responder_fn=BayesianResponder,
    num_midwives=100, num_women=1000, 
    runs=1, game=None, rounds=100,
    mw_weights=[80/100., 15/100., 5/100.], women_weights=[1/3., 1/3., 1/3.], women_priors=None, seeds=None,
    women_modifier=None, measures_women=measures_women(), measures_midwives=measures_midwives()):

    output_w = {'fields': [], 'results': []}
    output_mw = {'fields': [], 'results': []}
    if game is None:
        game = Game()

    params = params_dict(str(responder_fn), str(signaller_fn), mw_weights, women_weights, game, rounds)

    if seeds is None:
        seeds = [random.random() for x in range(runs)]
    player_pairs = []
    for i in range(runs):
        # Parity across different conditions but random between runs.
        random.seed(seeds[i])
        params['run'] = i
        #print "Making run %d/%d on %s" % (i + 1, runs, file_name)

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
        player_pairs.append((women, mw))

        #pair = game.play_game(women, mw, rounds=rounds)
    played = map(lambda x: game.play_game(x), player_pairs)
    if measures_women is not None:
        output_w = reduce(lambda x, y: dump((y[0], y[1]), measures_women, params, x), played, dump(None, measures_women, params))
    if measures_midwives is not None:
        output_mw = reduce(lambda x, y: dump((y[0], y[2]), measures_midwives, params, x), played, dump(None, measures_midwives, params))
    return (output_w, output_mw)


def experiment(game_fns=[Game, CaseloadGame], 
    agents=[(ProspectTheorySignaller, ProspectTheoryResponder), (BayesianSignaller, BayesianResponder)],
    kwargs=[{}]):
    run_params = []
    for pair in agents:
        for game_fn in game_fns:
            for kwarg in kwargs:
                game = game_fn()
                #kwarg.update({'measures_midwives': measures_midwives, 'measures_women': measures_women})
                kwarg['game'] = game
                args = (pair[0], pair[1],)
                run_params.append((args, kwarg.copy()))
    pool = Pool()
    return pool.map(run, run_params)


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
                game = Game(type_weights=prior)
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

        game = Game(type_weights=mw_priors)
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
        mw_weights=mw_weights, women_weights=women_weights, measures_women=dumper_w, measures_midwives=dumper_mw, women_priors=women_priors, seeds=seeds, runs=runs)

def run(args):
    args, kwargs = args
    return decision_fn_compare(*args, **kwargs)

if __name__ == "__main__":
    parser = arguments()
    args = parser.parse_args()
    games = map(eval, args.games)
    players = zip(map(eval, args.signallers), map(eval, args.responders))
    kwargs = [{'runs':args.runs}]
    print "Running %d game type%s, with %d player pair%s, and %d run%s of each." % (
        len(games), "s"[len(games)==1:], len(players), "s"[len(players)==1:], args.runs, "s"[args.runs==1:])
    print "Total simulations runs is %d" % (len(games) * len(players) * args.runs)
    women, mw = zip(*experiment(games, players, kwargs=kwargs))
    write_results_set("%smw.csv" % args.file_name, mw)
    write_results_set("%swomen.csv" % args.file_name, women)
