from Model import *
from ProspectTheoryModel import *
from ReferralGame import *
from RecognitionGame import *
from CarryingGame import *
from RecognitionAgents import *
from HeuristicAgents import *
from PayoffAgents import *
from SharingGames import *
from SharingAgents import *
import multiprocessing
from Measures import *
import itertools
from Experiments import *
from scoop import futures
import scoop
from Run import play_game, decision_fn_compare, arguments, main, version
import time
logger = scoop.logger

def make_work(kwargs):
    i = 1
    while len(kwargs) > 0:
        exps = decision_fn_compare(**kwargs.pop())
        for exp in exps:
            logger.info("Enqueing experiment for scoop %d" %  i)
            i += 1
            yield exp

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
    num_consumers = scoop.SIZE
    #Make tasks
    results = futures.map_as_completed(play_game, make_work(kwargs))
    
    for result in results:
        write(result, file_name)

def write(result, db_name):
    try:
        women_res, mw_res = result
        logger.info("Writing game.")
        women_res.write_db("%s_women" % db_name)
        mw_res.write_db("%s_mw" % db_name)
        del women_res
        del mw_res
    except sqlite3.OperationalError, e:
        print e
        raise
    except:
        raise

def main():
    games, players, kwargs, runs, test, file_name = arguments()
    logger.info("Version %f" % version)
    logger.info("Running %d game type%s, with %d player pair%s, and %d run%s of each." % (
        len(games), "s"[len(games)==1:], len(players), "s"[len(players)==1:], runs, "s"[runs==1:]))
    logger.info("Total simulations runs is %d" % (len(games) * len(players) * runs * len(kwargs)))
    logger.info("File is %s" % file_name)
    if test:
        logger.info("This is a test of the emergency broadcast system. This is only a test.")
    else:
        start = time.clock()
        experiment(file_name, games, players, kwargs=kwargs)
        print "Ran in %f" % (time.clock() - start)

if __name__ == "__main__":
    main()