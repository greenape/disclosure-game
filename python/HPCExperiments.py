from scoop import futures
from Model import *
from ReferralGame import *
from RecognitionGame import *
from RecognitionAgents import *
from AmbiguityAgents import *
from Experiments import *
import random

def run(args):
    args, kwargs = args
    return decision_fn_compare(*args, **kwargs)

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
                kwarg['game'] = game
                args = (pair[0], pair[1],)
                run_params.append((args, kwarg.copy()))
    #pool = Pool()
    #print run_params
    return list(futures.map(run, run_params))
    #pool.map(run, run_params)


def decision_fn_compare(signaller_fn=BayesianSignaller, responder_fn=BayesianResponder,
                        file_name="compare.csv", num_midwives=100, num_women=1000,
                        runs=1, game=None, rounds=100,
                        mw_weights=[80/100., 15/100., 5/100.],
                        women_weights=[1/3., 1/3., 1/3.], women_priors=None, seeds=None,
                        women_modifier=None, measures_women=measures_women(),
                        measures_midwives=measures_midwives()):

    output_w = {'fields': [], 'results': []}
    output_mw = {'fields': [], 'results': []}
    
    if game is None:
        game = Game()
    game.rounds = rounds

    params = params_dict(str(responder_fn), str(signaller_fn),
                         mw_weights, women_weights, game, rounds)

    #Unique filename by gametype
    if file_name is not None:
        file_name = "%s_%s" % (game, file_name)

    if seeds is None:
        seeds = [random.random() for x in range(runs)]
    player_pairs = []
    for i in range(runs):
        # Parity across different conditions but random between runs.
        random.seed(seeds[i])
        params['run'] = i
        #print "Making run %d/%d on %s" % (i + 1, runs, file_name)

        #Make players and initialise beliefs
        women = make_players(signaller_fn, num=num_women, weights=women_weights)
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
        mw = make_players(responder_fn, num_midwives, weights=mw_weights)
        #print "Made agents."
        for midwife in mw:
            midwife.init_payoffs(game.midwife_payoff, game.type_weights)
        #print "Set priors."
        player_pairs.append((game, women, mw))

    played = list(futures.map(play_game, player_pairs))
    #print "Played!"
    #played = [(game, women, mw)]
    if measures_women is not None:
        output_w = reduce(lambda x, y: dump((y[0], y[1]), measures_women, params, x),
                          played, dump(None, measures_women, params))
    if measures_midwives is not None:
        output_mw = reduce(lambda x, y: dump((y[0], y[2]), measures_midwives, params, x),
                           played, dump(None, measures_midwives, params))

    return (output_w, output_mw)


if __name__ == "__main__":
    games = [RecognitionGame, CaseloadRecognitionGame, ReferralGame, CaseloadReferralGame]
    players = [(AmbiguitySignaller, RecognitionResponder)]
    #kwargs = [{'measures_midwives': measures_midwives(), 'measures_women': measures_women()}]
    women, mw = zip(*experiment(games, players))
    write_results_set("mw.csv", mw)
    write_results_set("women.csv", women)

