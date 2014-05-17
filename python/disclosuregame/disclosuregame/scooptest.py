from disclosuregame.Games.game import *
from disclosuregame.Games.referral import *
from disclosuregame.Games.recognition import *
from disclosuregame.Games.carrying import *
from disclosuregame.Games.sharing import *

from disclosuregame.Agents.cpt import *
from disclosuregame.Agents.recognition import *
from disclosuregame.Agents.heuristic import *
from disclosuregame.Agents.payoff import *
from disclosuregame.Agents.rl import *

from disclosuregame.Measures import *
from disclosuregame.Measures.abstract import *

from disclosuregame.experiments import *

import multiprocessing
import itertools
from scoop import futures
import scoop
from run import play_game, decision_fn_compare, arguments, main, version
import time
logger = scoop.logger


def imap(function, iterable, chunksize):
    results_generator = (scoop.futures.submit(function, i) for i in iterable)

    results = []
    for res in results_generator:  # active evaluation of item
        results.append(res)

        while len(results) >= chunksize:
            r = scoop.futures.wait(results, return_when=scoop.futures.FIRST_COMPLETED)
            results = list(r.not_done)
            for d in r.done:
                d._delete() #This is bad, but seems to be the only way to not boondoggle memory
                try:
                    res = results_generator.next()
                    results.append(res)
                except StopIteration:
                    pass
                yield d.result()

            if len(results) >= chunksize:
                logger.debug("Did not remove any element?")

    # empty remaining
    r = scoop.futures.wait(results, return_when=scoop.futures.ALL_COMPLETED)
    for d in r.done:
        yield d.result()

    if len(r.not_done) > 0:
        print (str(len(r.not_done)))
        raise Exception("Not all done? Remaining:" + str(len(r.not_done)))

def make_work(kwargs):
    i = 1
    while len(kwargs) > 0:
        exps = decision_fn_compare(**kwargs.pop())
        for exp in exps:
            logger.info("Enqueing experiment %d for scoop." %  i)
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
    results = imap(play_game, make_work(kwargs), num_consumers - 1)
    
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