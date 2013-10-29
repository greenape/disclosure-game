from Model import *
from ProspectTheoryModel import *
from ReferralGame import *
from RecognitionGame import *
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


def type_signal(player_type, signal):
    """
    Return a function that yields the fraction of that type
    who signalled so in that round.
    """
    def f(roundnum, women, game):
        women = filter(lambda x: x.player_type == player_type, women)
        women = filter(lambda x: len(x.signal_log) > roundnum, women)
        num_women = len(women)
        women = filter(lambda x: x.signal_log[roundnum] == signal, women)
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
        return sum(map(lambda x: x.payoff_log[roundnum], women)) / float(len(women))
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
    game, women = pair
    if results is None:
        results = {'fields':measures.keys() + params.keys(), 'results':[]}
    for i in range(params['max_rounds']):
        line = map(lambda x: x(i, women, game), measures.values())
        line.append(params.values())
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

measures = OrderedDict()
measures['appointment'] = appointment
measures['finished'] = finished
for i in range(3):
    for j in range(3):
        measures["type_%d_signal_%d" % (i, j)] = type_signal(i, j)
        measures["type_%d_mw_%d_ref" % (i, j)] = type_referral_breakdown(i, None, j)
        measures["type_%d_sig_%d_ref" % (i, j)] = type_referral_breakdown(i, j, None)
        for k in range(3):
            measures["type_%d_mw_%d_sig_%d" % (i, j, k)] = type_signal_breakdown(i, k, j)


def decision_fn_compare(signaller_fn=BayesianSignaller, responder_fn=BayesianResponder,
    file_name="compare.csv", num_midwives=100, num_women=1000, 
    runs=10, game=None, rounds=100,
    mw_weights=[80/100., 15/100., 5/100.], women_weights=[1/3., 1/3., 1/3.], women_priors=None, seeds=None,
    women_modifier=None, measures_women=measures, measures_midwives=measures):

    output_w = {'fields': [], 'results': []}
    output_mw = {'fields': [], 'results': []}
    if game is None:
        game = Game()

    params = params_dict(str(responder_fn), str(signaller_fn), mw_weights, women_weights, game, rounds)

    #Unique filename by gametype
    if file_name is not None:
        file_name = "%s_%s" % (game, file_name)

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

        pair = game.play_game(women, mw, rounds=rounds)
        #print "Ran trial."
        #dump_women(pair, params, file_name, 'a')
        #dump_midwives((game, mw), params, "mw_"+file_name, 'a')
        if measures_women is not None:
            results = dump(pair, measures_women, params)
            output_w['fields'] = results['fields']
            output_w['results'] += results['results']
            print output_w['results']
        #dump_game_women_pair_change(pair, params, "change_summary_"+file_name, 'a')
        if measures_midwives is not None:
            results = dump((game, mw), measures_midwives, params)
            output_mw['fields'] = results['fields']
            output_mw['results'] += results['results']
        #print "Dumped results."
    if file_name is not None:
        write_results("women_"+file_name, output_w, 'w')
        write_results("mw_"+file_name, output_mw, 'w')
    return (output_w, output_mw)


def caseload_experiment(file_name="caseload.csv", game_fns=[Game, CaseloadGame], 
    agents=[(ProspectTheorySignaller, ProspectTheoryResponder), (BayesianSignaller, BayesianResponder)],
    measures_women=measures, measures_midwives=measures):
    for pair in agents:
        for game_fn in game_fns:
            game = game_fn()
            game.init_payoffs()
            p = multiprocessing.Process(target=decision_fn_compare, args=(pair[0], pair[1], file_name,), 
                                    kwargs={'game': game,
                                    'measures_midwives': None, 'measures_women': measures})
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
        mw_weights=mw_weights, women_weights=women_weights, measures_women=dumper_w, measures_midwives=dumper_mw, women_priors=women_priors, seeds=seeds, runs=runs)



if __name__ == "__main__":
    #lhs_sampling("lhs_final.csv", "sa_final.txt")
    caseload_experiment("recog_test.csv", [RecognitionGame, CaseloadRecognitionGame], [(RecognitionSignaller, BayesianResponder)])
    #priors_experiment("priors_final.csv")
    #alspac_caseload_experiment("alspac_caseloading_compare.csv")
    #muddy_caseload_experiment("caseloading_compare_breakdown_ref_muddy.csv")
