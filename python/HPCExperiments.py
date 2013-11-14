from scoop import futures
from Model import *
from ReferralGame import *
from RecognitionGame import *
from RecognitionAgents import *
from AmbiguityAgents import *
from Experiments import *
from Measures import *
import random
import sys

def run(kwargs):
    return decision_fn_compare(**kwargs)

def play_game(config):
    game, women, midwives = config
    return game.play_game((women, midwives))

def experiment(game_fns=[Game, CaseloadGame], 
    agents=[(BayesianSignaller, BayesianResponder)],
    kwargs=[{}]):
    run_params = []
    for pair in agents:
        for game_fn in game_fns:
            for kwarg in kwargs:
                game = game_fn()
                #kwarg.update({'measures_midwives': measures_midwives, 'measures_women': measures_women})
                kwarg['game'] = game
                kwarg['signaller_fn'] = pair[0]
                kwarg['responder_fn'] = pair[1]
                run_params.append(kwarg.copy())
    scoop.logger.info("Made %d parameter sets" % len(run_params))
    return kw_experiment(run_params)

def kw_experiment(kwargs):
    """
    Run a bunch of experiments in parallel. Experiments are
    defined by a list of keyword argument dictionaries.
    """
    return list(futures.map(run, kwargs))
    

def decision_fn_compare(signaller_fn=BayesianSignaller, responder_fn=BayesianResponder,
                        num_midwives=100, num_women=1000,
                        runs=1000, game=None, rounds=100,
                        mw_weights=[80/100., 15/100., 5/100.],
                        women_weights=[1/3., 1/3., 1/3.], women_priors=None, seeds=None,
                        women_modifier=None, measures_women=measures_women(),
                        measures_midwives=measures_midwives(), nested=False):

    sys.setrecursionlimit(1000)

    output_w = {'fields': [], 'results': []}
    output_mw = {'fields': [], 'results': []}
    
    if game is None:
        game = Game()
    game.rounds = rounds

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
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff,
                                   women_priors[j][0], women_priors[j][1])
            else:
                woman.init_payoffs(game.woman_baby_payoff, game.woman_social_payoff,
                                   random_expectations(),
                                   [random_expectations(breadth=2) for x in range(3)])
        if women_modifier is not None:
            women_modifier(women)
        #print "Set priors."
        mw = make_players(responder_fn, num_midwives, weights=mw_weights, nested=nested, signaller=False)
        #print "Made agents."
        for midwife in mw:
            midwife.init_payoffs(game.midwife_payoff, game.type_weights)
        #print "Set priors."
        player_pairs.append((game, women, mw))
    params = params_dict(str(player_pairs[0][1][0]), str(player_pairs[0][2][0]), mw_weights, women_weights, game, rounds)
    game.parameters = params
    played = list(futures.map(play_game, player_pairs))
    scoop.logger.info("Completed a parameter set.")
    
    women, midwives = zip(*played)
    women = reduce(lambda x, y: x.add_results(y), women)
    midwives = reduce(lambda x, y: x.add_results(y), midwives)
    return women, midwives

if __name__ == "__main__":
    games, players, kwargs, runs, test, file_name = arguments()
    scoop.logger.info("Running %d game type%s, with %d player pair%s, and %d run%s of each." % (
        len(games), "s"[len(games)==1:], len(players), "s"[len(players)==1:], runs, "s"[runs==1:]))
    scoop.logger.info("Total simulations runs is %d" % (len(games) * len(players) * runs))
    if test:
        scoop.logger.info("This is a test of the emergency broadcast system. This is only a test.")
    else:
        women, midwives = zip(*experiment(games, players, kwargs=kwargs))
        women = reduce(lambda x, y: x.add_results(y), women)
        midwives = reduce(lambda x, y: x.add_results(y), midwives)
        women.write("%swomen.csv" % file_name)
        midwives.write("%smw.csv" % file_name)

