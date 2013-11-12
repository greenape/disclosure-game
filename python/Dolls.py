from Model import *

class Doll(object):
    """
    Doll, as in russian doll. A doll is a container for a set of agent brains.
    One brain controls general behaviour, other brains control responses to
    specific other agents.
    Calling a method or attribute of the doll will, in general, attempt to call
    that on the general agent.
    """
    def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1], child_fn=BayesianSignaller):
        self.children = {}
        self.child_fn = child_fn
        self.children[None] = child_fn(player_type, signals, responses)

    def __str__(self):
        return "doll_%s" % (str(self.child_fn()))

    def __getattr__(self, name):
        if name in {"children", "child_fn"}:
            return super(DollSignaller).__getattr__(name)
        try:
            return getattr(self.children[None], name)
        except AttributeError:
            # Default behaviour
            raise AttributeError, name

    def __setattr__(self, name, value):
        if name in {"children", "child_fn"}:
            return object.__setattr__(self, name, value)
        try:
            setattr(self.children[None], name, value)
        except AttributeError:
            # Default behaviour
            raise AttributeError

class DollSignaller(Doll):
    """
    A signalling agent that is actually a collection, one agent takes
    responsibility for general action, and an agent per opponent.
    """

    def current_type_distribution(self, opponent=None):
        return self.children[opponent].current_type_distribution()

    def current_signal_risk(self, opponent=None):
        return self.children[opponent].current_signal_risk()

    def current_response_belief(self, opponent=None):
        return self.children[opponent].current_response_belief()

    def round_signal(self, rounds, opponent=None):
        return self.children[opponent].round_signal(rounds)

    def round_response_belief(self, rounds, opponent=None):
        return self.children[opponent].round_response_belief(rounds)

    def update_beliefs(self, response, midwife, payoff, midwife_type=None):
        # We know you...
        if midwife in self.children:
            self.children[midwife].update_beliefs(response, midwife, payoff, midwife_type)
        else:
            # Hullo stranger
            child = self.child_fn(self.player_type)
            baby_payoffs = [[0] for x in self.signals]
            baby_payoffs[self.player_type] = list(self.baby_payoffs)

            type_weights = list(self.type_weights)
            response_weights = list(self.response_weights)

            for signal in self.signals:
                type_weights[signal] += self.type_matches[signal]
                for i_response in self.responses:
                    response_weights[signal][i_response] += self.response_signal_matches[signal][i_response]
            child.init_payoffs(baby_payoffs, self.social_payoffs, type_weights, response_weights)
            #Append the last signal
            child.log_signal(self.signal_log[len(self.signal_log) - 1])

            child.update_beliefs(response, midwife, payoff, midwife_type)
            self.children[midwife] = child
        #Update the general child
        self.children[None].update_beliefs(response, midwife, payoff, midwife_type)

    def do_signal(self, opponent=None):
        if opponent in self.children:
            #print "Recognised this one:", opponent
            signal = self.children[opponent].do_signal(opponent)
            #print "Signal was %d" % signal
            self.rounds += 1
            self.log_signal(signal, opponent)
        else:
            signal = self.children[None].do_signal(opponent)
        return signal

class DollResponder(Doll):
    """
    """

    def respond(self, signal, opponent=None):
        if opponent in self.children:
            self.signal_log.append(signal)
            self.signal_matches[signal] += 1.
            response = self.children[opponent].respond(signal, opponent)
            self.response_log.append(response)
            self.rounds += 1
        else:
            response = self.children[None].respond(signal, opponent)
        return response

    def update_beliefs(self, payoff, signaller, signal, signaller_type=None):
        if signaller in self.children:
            self.children[signaller].update_beliefs(payoff, signaller, signal, signaller_type)
        else:
            # Hello newbie, let's make you a memory..
            child = self.child_fn(self.player_type)
            # Type weights
            child.init_payoffs(self.payoffs, self.type_weights)
            # Bring you up to date
            for i in range(len(self.payoff_log)):
                s = Signaller(self.type_log[i])
                child.update_beliefs(self.payoff_log[i], s, self.signal_log[i])
                children[signaller] = child
        self.children[None].update_beliefs(payoff, signaller, signal, signaller_type)