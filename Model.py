def generate_players():
	""" Generate players for a game.
	"""

class Agent:
	"""
	An agent who plays a game, according to their
	type, and some decision rule.
	"""
	def __init__(self, player_type=1, decision_function):
		self.player_type = player_type
		self.decision_function = decision_function

	def respond(self, signal):
		"""
		Make a judgement about somebody based on
		the signal they sent.
		"""

	def signal(self):
		""" Report own consumption based on
		decision function.
		"""

	def update_beliefs(self, signal):
		""" Update the agent's beliefs about
		the frequency of other types and so on.
		"""

class Response:
	""" A response to a signal.
	Consists of a function to perform on the signaller
	and a 
	"""
	def __init__(self):



class Game:
	def __init__(self, num_rounds=1):
		""" A multistage game played by two agents.
		"""
		self.signal_log = []
		self.act_log = []
		self.payoff = [[[[[]]]]]
		self.num_rounds = num_rounds

	def play_round(self, signaller, receiver):
		""" Play a round of this game between the
		two players.
		"""
		signal = signaller.signal()
		act = receiver.respond(signal)
		round_payoff = self.payoff[signaller.player_type][receiver.player_type][signal][act]

