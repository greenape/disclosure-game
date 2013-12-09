from Model import *
from ProspectTheoryModel import *
from ReferralGame import *
from RecognitionGame import *
from CarryingGame import *
from RecognitionAgents import *
from AmbiguityAgents import *
from HeuristicAgents import *
from PayoffAgents import *
from SharingGames import *
from Dolls import *
from multiprocessing import Pool
from Measures import *
import multiprocessing
import itertools
from collections import OrderedDict
import argparse
from os.path import expanduser
import cPickle
import gzip

def load_kwargs(file_name):
    
    f = open(file_name, "r")
    kwargs = cPickle.load(f)
    f.close()
    assert type(kwargs) is list, "%s does not contain a pickled list." % file_name
    #Check this is a valid list of dicts
    valid_args = decision_fn_compare.func_code.co_varnames[:decision_fn_compare.func_code.co_argcount]
    line = 0
    for kwarg in kwargs:
        assert type(kwarg) is dict, "Kwargs %d is not a valid dictionary." % line
        for arg, value in kwarg.items():
            if arg != "game_args":
                assert arg in valid_args, "Kwargs %d, argument: %s is not valid." % (line, arg)

        line +=1

    return kwargs

def arguments():
    parser = argparse.ArgumentParser(
        description='Run some variations of the disclosure game with all combinations of games, signallers and responders provided.')
    parser.add_argument('-g', '--games', type=str, nargs='*',
                   help='A game type to play.', default=['Game', 'CaseloadGame'],
                   choices=['Game', 'CaseloadGame', 'RecognitionGame', 'ReferralGame',
                   'CaseloadRecognitionGame', 'CaseloadReferralGame', 'CarryingGame',
                   'CarryingReferralGame', 'CarryingCaseloadReferralGame', 'CaseloadSharingGame',
                   'CarryingInformationGame'],
                   dest="games")
    parser.add_argument('-s','--signallers', type=str, nargs='*',
        help='A signaller type.', default=["BayesianSignaller"],
        choices=['BayesianSignaller', 'RecognitionSignaller', 'AmbiguitySignaller',
        'ProspectTheorySignaller', 'LexicographicSignaller', 'BayesianPayoffSignaller',
        'PayoffProspectSignaller', 'SharingBayesianPayoffSignaller', 'SharingLexicographicSignaller',
        'SharingPayoffProspectSignaller'],
        dest="signallers")
    parser.add_argument('-r','--responders', type=str, nargs='*',
        help='A responder type.', default=["BayesianResponder"],
        choices=['BayesianResponder', 'RecognitionResponder', 'ProspectTheoryResponder',
        'AmbiguityResponder', 'LexicographicResponder', 'BayesianPayoffResponder',
        'SharingBayesianPayoffResponder', 'SharingLexicographicResponder',
        'PayoffProspectResponder', 'SharingPayoffProspectResponder',
        'RecognitionResponder', 'RecognitionBayesianPayoffResponder', 'RecognitionLexicographicResponder',
        'PayoffProspectResponder', 'RecognitionPayoffProspectResponder'], dest="responders")
    parser.add_argument('-R','--runs', dest='runs', type=int,
        help="Number of runs for each combination of players and games.",
        default=100)
    parser.add_argument('-i','--rounds', dest='rounds', type=int,
        help="Number of rounds each woman plays for.",
        default=100)
    parser.add_argument('-f','--file', dest='file_name', default="", type=str,
        help="File name prefix for csv output.")
    parser.add_argument('-t', '--test', dest='test_only', action="store_true", 
        help="Sets test mode on, and doesn't actually run the simulations.")
    parser.add_argument('-n', '--nested_agents', dest="nested", action="store_true",
        help="Use nested agents to recognise opponents.")
    parser.add_argument('-p', '--prop_women', dest='women', nargs=3, type=float,
        help="Proportion sof type 0, 1, 2 women as decimals.")
    parser.add_argument('-c', '--combinations', dest='combinations', action="store_true",
        help="Run all possible combinations of signallers & responders.")
    parser.add_argument('-d', '--directory', dest='dir', type=str,
        help="Optional directory to store results in. Defaults to user home.",
        default=expanduser("~"), nargs="?")
    parser.add_argument('--pickled-arguments', dest='kwargs', type=str, nargs='?',
        default=None, help="A file containing a pickled list of kwarg dictionaries to be run.")
    parser.add_argument('--individual-measures', dest='indiv', action="store_true",
        help="Take individual outcome measures instead of group level.", default=False)

    args = parser.parse_args()
    file_name = "%s/%s" % (args.dir, args.file_name)
    games = map(eval, args.games)
    if args.combinations:
        players = list(itertools.product(map(eval, set(args.signallers)), map(eval, set(args.responders))))
    else:
        players = zip(map(eval, args.signallers), map(eval, args.responders))
    kwargs = {'runs':args.runs, 'rounds':args.rounds, 'nested':args.nested, 'file_name':file_name}
    if args.women is not None:
        kwargs['women_weights'] = args.women
    if args.indiv:
        kwargs['measures_midwives'] = indiv_measures_mw()
        kwargs['measures_women'] = indiv_measures_women()
    kwargs = [kwargs]
    if args.kwargs is not None:
        try:
            new_args = load_kwargs(args.kwargs)
            old = kwargs[0]
            kwargs = []
            for arg in new_args:
                tmp = old.copy()
                tmp.update(arg)
                kwargs.append(tmp)
        except IOError:
            print("Couldn't open %s." % args.kwargs)
            raise
        except cPickle.UnpicklingError:
            print("Not a valid pickle file.")
            raise
    return games, players, kwargs, args.runs, args.test_only, file_name


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


def make_players(constructor, num=100, weights=[1/3., 1/3., 1/3.], nested=False,
    signaller=True):
    women = []
    player_type = 0
    for weight in weights:
        for i in range(int(round(weight*num))):
            if len(women) == num: break
            if nested:
                if signaller:
                    women.append(DollSignaller(player_type=player_type, child_fn=constructor))
                else:
                    women.append(constructor(player_type=player_type))    
            else:
                women.append(constructor(player_type=player_type))
        player_type += 1
    while len(women) < num:
        player_type = 0
        if nested:
            if signaller:
                women.append(DollSignaller(player_type=player_type, child_fn=constructor))
            else:
                women.append(constructor(player_type=player_type))    
        else:
            women.append(constructor(player_type=player_type))
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

def decision_fn_compare(signaller_fn=BayesianSignaller, responder_fn=BayesianResponder,
    num_midwives=100, num_women=1000, 
    runs=1, game=None, rounds=100,
    mw_weights=[80/100., 15/100., 5/100.], women_weights=[1/3., 1/3., 1/3.], women_priors=None, seeds=None,
    women_modifier=None, measures_women=measures_women(), measures_midwives=measures_midwives(),
    nested=False, mw_priors=None):

    if game is None:
        game = Game()
    if mw_priors is not None:
        game.type_weights = mw_priors

    game.measures_midwives = measures_midwives
    game.measures_women = measures_women

    if seeds is None:
        seeds = [random.random() for x in range(runs)]
    player_pairs = []
    for i in range(runs):
        # Parity across different conditions but random between runs.
        random.seed(seeds[i])
        #print "Making run %d/%d on %s" % (i + 1, runs, file_name)

        #Make players and initialise beliefs
        women = make_players(signaller_fn, num=num_women, weights=women_weights, nested=nested)
        #print "made %d women." % len(women)
        for j in range(len(women)):
            woman = women[j]
            if women_priors is not None:
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff, women_priors[j][0], women_priors[j][1])
            else:
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff, random_expectations(), [random_expectations(breadth=2) for x in range(3)])
        if women_modifier is not None:
            women_modifier(women)
        #print("Set priors.")
        mw = make_players(responder_fn, num_midwives, weights=mw_weights, nested=nested, signaller=False)
        #print("Made agents.")
        for midwife in mw:
            midwife.init_payoffs(game.midwife_payoff, game.type_weights)
        #print("Set priors.")
        player_pairs.append((women, mw))

        #pair = game.play_game(women, mw, rounds=rounds)
    params = params_dict(str(player_pairs[0][0][0]), str(player_pairs[0][1][0]), mw_weights, women_weights, game, rounds)
    game.parameters = params
    game.rounds = rounds
    played = map(lambda x: game.play_game(x), player_pairs)
    print("Ran a set of parameters.")
    women_res, midwives_res, pile = zip(*played)
    women_res = reduce(lambda x, y: x.add_results(y), women_res)
    midwives_res = reduce(lambda x, y: x.add_results(y), midwives_res)
    return women_res, midwives_res, pile


def experiment(game_fns=[Game, CaseloadGame], 
    agents=[(ProspectTheorySignaller, ProspectTheoryResponder), (BayesianSignaller, BayesianResponder)],
    kwargs=[{}]):
    run_params = []
    for pair in agents:
        for game_fn in game_fns:
            for kwarg in kwargs:
                game = game_fn(**kwarg.pop('game_args', {}))
                #kwarg.update({'measures_midwives': measures_midwives, 'measures_women': measures_women})
                kwarg['game'] = game
                kwarg['signaller_fn'] = pair[0]
                kwarg['responder_fn'] = pair[1]
                run_params.append(kwarg.copy())
    return kw_experiment(run_params)

def kw_experiment(kwargs):
    """
    Run a bunch of experiments in parallel. Experiments are
    defined by a list of keyword argument dictionaries.
    """
    pool = Pool()
    return pool.map(run, kwargs)


def proportions(num):
    """
    Generate some number of combinations of 3
    random numbers that sum to 1.
    """
    proportions = []
    for i in range(num):
        initial = 100
        result = []
        for i in range(2):
            n = random.randint(0, initial)
            initial -= n
            result.append(n)
        result.append(initial)

        proportions.append([x/100. for x in result])
    return proportions

def proportions_experiment():
    """
    Sample space for type proportions.
    """
    mw = proportions(10000)
    w = proportions(10000)
    kwargs = []
    for i in range(10000):
        kwarg = {'women_weights':w[i], 'mw_weights':mw[i]}
        kwargs.append(kwarg)
    return kwargs

def naive_partition():
    parts = []
    for x in itertools.product(xrange(0, 101, 5), repeat=3):
        if sum(x) == 100:
            parts.append(map(lambda y: y / 100., x))
    return parts

def naive_women_proportions():
    """
    Sample space for type proportions.
    """
    w = naive_partition()
    kwargs = []
    for x in w:
        kwarg = {'women_weights':x}
        kwargs.append(kwarg)
    return kwargs

def priors_experiment():
    """
    Sample space for midwives' priors.
    """
    mw = [random_expectations(1, 3, 1, 50) for x in range(10000)]
    kwargs = []
    for i in range(10000):
        kwarg = {'mw_priors':mw[i]}
        kwargs.append(kwarg)
    return kwargs

def synthetic_caseload():
    """
    Synthetic caseload with a harsh midwife.
    """
    kwargs = []
    for i in range(3):
        mw_weights = [0]*3
        mw_weights[i] = 1

        kwargs.append({'num_midwives':1, 'num_women':10, 'mw_weights':mw_weights})
    return kwargs

def mw_sharing_experiment():
    kwargs = []
    for x in itertools.product((y/10. for y in range(0, 11)), repeat=2):
        kwarg = {'game_args': {'mw_share_width':x[0], 'mw_share_bias':-x[1]}}
        kwargs.append(kwarg)
    return kwargs

def w_sharing_experiment():
    kwargs = []
    for x in itertools.product((y/10. for y in range(0, 11)), repeat=2):
        kwarg = {'game_args': {'mw_share_width':0, 'mw_share_bias':1,
            'women_share_width':x[0], 'women_share_bias':-x[1]}}
        kwargs.append(kwarg)
    return kwargs



def midwife_priors():
    priors =  [[[x, 1., 1.], [1., x, 1.], [1., 1., x]] for x in xrange(5, 51, 5)]
    for i in range(4):
        priors.append([[i + 1., 1., 1.], [1., i + 1., 1.], [1., 1., i + 1.]])
    run_params = []
    for prior in priors:
        args = {'mw_priors':prior}
        run_params.append(args)
    return run_params


def lhs_sampling(samples):
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
        priors.append(vals[0:9])
        mw_types.append(vals[9:12])
        types.append(vals[12:15])
        seeds.append(5)
    total = len(content)
    for i in range(total):
        mw_priors = [float(priors[i][x]) for x in range(9)]
        mw_priors = [mw_priors[x:x+3] for x in xrange(0, len(mw_priors), 3)]
        mw_numbers = scale_weights([float(mw_types[i][x]) for x in range(3)], 1.)
        women_numbers = scale_weights([float(types[i][x]) for x in range(3)], 1.)
        seed = [5]

        game = Game(type_weights=mw_priors)
        args = {'game':game, 'seeds':seed, 'signaller_fn':BayesianSignaller, 'responder_fn':BayesianResponder,
                'runs':100, 'mw_weights':mw_numbers, 'women_weights':women_numbers}
        run_params.append(args)
        #random.setstate(random_state)
    return kw_experiment(run_params)

def run(kwargs):
    return decision_fn_compare(**kwargs)


def main():
    games, players, kwargs, runs, test, file_name = arguments()
    print("Running %d game type%s, with %d player pair%s, and %d run%s of each." % (
        len(games), "s"[len(games)==1:], len(players), "s"[len(players)==1:], runs, "s"[runs==1:]))
    print("Total simulations runs is %d" % (len(games) * len(players) * runs * len(kwargs)))
    print "File is %s" % file_name
    if test:
        print("This is a test of the emergency broadcast system. This is only a test.")
    else:
        women, midwives, pile = zip(*experiment(games, players, kwargs=kwargs))
        women = reduce(lambda x, y: x.add_results(y), women)
        midwives = reduce(lambda x, y: x.add_results(y), midwives)
        women.write("%swomen.csv.gz" % file_name)
        midwives.write("%smw.csv.gz" % file_name)
        women.write_params("%sparams.csv.gz" % file_name)
        fp = gzip.open("%s.pickle.gz" % file_name, "wb")
        cPickle.dump(pile, fp, cPickle.HIGHEST_PROTOCOL)
        fp.close()

if __name__ == "__main__":
    main()
