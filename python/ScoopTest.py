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
from Experiments import *
from scoop import futures
import scoop
from Run import play_game, decision_fn_compare, arguments, write, make_work, logger

def do_work(queueIn, queueOut):
    """
    Consume games, play them, then put their results in the output queue.
    """
    while True:
        try:
            number, config = queueIn.get()
            logger.info("Running game %d." % number)
            res = futures.submit(play_game, config)
            del config
            queueOut.put((number, res.result()))
        except:
            logger.info("Done.")
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
    num_consumers = scoop.SIZE
    #Make tasks
    jobs = multiprocessing.Queue(num_consumers)
    results = multiprocessing.Queue()
    producer = multiprocessing.Process(target = make_work, args = (jobs, kwargs, num_consumers))
    producer.start()
    calcProc = [multiprocessing.Process(target = do_work , args = (jobs, results)) for i in range(num_consumers - 1)]
    writProc = multiprocessing.Process(target = write, args = (results, file_name))
    writProc.start()

    for p in calcProc:
        p.start()
    for p in calcProc:
        try:
            p.join()
        except KeyboardInterrupt:
            for p in calcProc:
                jobs.put(None)
            jobs.close()
    results.put(None)
    writProc.join()
    while True:
        if jobs.get() is None:
            break
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