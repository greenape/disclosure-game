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
import multiprocessing
from Measures import *
import itertools
from collections import OrderedDict
import argparse
from os.path import expanduser
import cPickle
import pickle
import gzip
from Experiments import *
from copy import deepcopy
import sqlite3
import sys
import logging

logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

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
        help="Proportions of type 0, 1, 2 women as decimals.")
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
            logger.info("Couldn't open %s." % args.kwargs)
            raise
        except cPickle.UnpicklingError:
            logger.info("Not a valid pickle file.")
            raise
    return games, players, kwargs, args.runs, args.test_only, file_name


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
    nested=False, mw_priors=None, file_name=""):

    if game is None:
        game = Game()
    if mw_priors is not None:
        game.type_weights = mw_priors

    game.measures_midwives = measures_midwives
    game.measures_women = measures_women
    params = params_dict(str(signaller_fn()), str(responder_fn()), mw_weights, women_weights, game, rounds)
    for key, value in params.items():
        game.parameters[key] = value
    game.rounds = rounds

    if seeds is None:
        seeds = [random.random() for x in range(runs)]
    player_pairs = []
    #for i in range(runs):
    i =  0
    while i < runs:
        # Parity across different conditions but random between runs.
        random.seed(seeds[i])
        #logger.info "Making run %d/%d on %s" % (i + 1, runs, file_name)

        #Make players and initialise beliefs
        women = make_players(signaller_fn, num=num_women, weights=women_weights, nested=nested)
        #logger.info "made %d women." % len(women)
        for j in range(len(women)):
            woman = women[j]
            if women_priors is not None:
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff, women_priors[j][0], women_priors[j][1])
            else:
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff, random_expectations(), [random_expectations(breadth=2) for x in range(3)])
        if women_modifier is not None:
            women_modifier(women)
        #logger.info("Set priors.")
        mw = make_players(responder_fn, num_midwives, weights=mw_weights, nested=nested, signaller=False)
        #logger.info("Made agents.")
        for midwife in mw:
            midwife.init_payoffs(game.midwife_payoff, game.type_weights)
        #logger.info("Set priors.")
        #player_pairs.append((deepcopy(game), women, mw))
        yield (deepcopy(game), women, mw)
        i += 1

        #pair = game.play_game(women, mw, rounds=rounds)
    #played = map(lambda x: game.play_game(x, "%s_%s" % (file_name, str(game))), player_pairs)
    #logger.info("Ran a set of parameters.")
    #return player_pairs

def play_game(config):
    """
    Play a game.
    """
    game, women, midwives = config
    return game.play_game((women, midwives))


def make_work(queue, kwargs, num_consumers):
    i = 1
    while len(kwargs) > 0:
        exps = decision_fn_compare(**kwargs.pop())
        for exp in exps:
            logger.info("Enqueing experiment %d" %  i)
            queue.put((i, exp))
            i += 1
    for i in range(num_consumers):
        queue.put(None)


def do_work(queueIn, queueOut):
    """
    Consume games, play them, then put their results in the output queue.
    """
    while True:
        try:
            number, config = queueIn.get()
            logger.info("Running game %d." % number)
            res = (number, play_game(config))
            queueOut.put(res)
            del config
        except:
            logger.info("Done.")
            break

def write(queue, db_name):
    while True:
        try:
            number, res = queue.get()
            women_res, mw_res = res
            logger.info("Writing game %d." % number)
            women_res.write_db("%s_women" % db_name)
            mw_res.write_db("%s_mw" % db_name)
            del women_res
            del mw_res
        except sqlite3.OperationalError:
            raise
        except:
            break


def experiment(file_name, game_fns=[Game, CaseloadGame], 
    agents=[(ProspectTheorySignaller, ProspectTheoryResponder), (BayesianSignaller, BayesianResponder)],
    kwargs=[{}]):
    run_params = []
    for pair in agents:
        for game_fn in game_fns:
            for kwarg in kwargs:
                arg = kwarg.copy()
                game = game_fn(**arg.pop('game_args', {}))
                #kwarg.update({'measures_midwives': measures_midwives, 'measures_women': measures_women})
                arg['game'] = game
                arg['signaller_fn'] = pair[0]
                arg['responder_fn'] = pair[1]
                run_params.append(arg)
    kw_experiment(run_params, file_name)

def kw_experiment(kwargs, file_name):
    """
    Run a bunch of experiments in parallel. Experiments are
    defined by a list of keyword argument dictionaries.
    """
    num_consumers = multiprocessing.cpu_count()
    #Make tasks
    jobs = multiprocessing.Queue(num_consumers)
    results = multiprocessing.Queue()
    producer = multiprocessing.Process(target = make_work, args = (jobs, kwargs, num_consumers))
    producer.start()
    calcProc = [multiprocessing.Process(target = do_work , args = (jobs, results)) for i in range(num_consumers)]
    writProc = multiprocessing.Process(target = write, args = (results, file_name))
    writProc.start()

    for p in calcProc:
        p.start()
    for p in calcProc:
        try:
            p.join()
        except KeyboardInterrupt:
            break
    results.put(None)
    writProc.join()
    producer.join()


def main():
    games, players, kwargs, runs, test, file_name = arguments()
    logger.info("Running %d game type%s, with %d player pair%s, and %d run%s of each." % (
        len(games), "s"[len(games)==1:], len(players), "s"[len(players)==1:], runs, "s"[runs==1:]))
    logger.info("Total simulations runs is %d" % (len(games) * len(players) * runs * len(kwargs)))
    logger.info("File is %s" % file_name)
    if test:
        logger.info("This is a test of the emergency broadcast system. This is only a test.")
    else:
        experiment(file_name, games, players, kwargs=kwargs)

if __name__ == "__main__":
    main()