import random

def generate_players():
	""" Generate players for a game.
	"""
	return (Agent(None), Agent(None))

class Agent:
	"""
	An agent who plays a game, according to their
	type, and some decision rule.
	Players are one of three types.
	0 = low
	1 = middle
	2 = high

	Players have two possible response moves.
	0 = refer
	1 = not refer
	"""
	def __init__(self, decision_function, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
		self.player_type = player_type
		self.decision_function = decision_function
		self.signals = signals
		self.responses = responses
		self.payoff_log = []
		self.signal_log = []
		self.response_log = []

	def respond(self, signal, opponent):
		"""
		Make a judgement about somebody based on
		the signal they sent.
		"""
		self.signal_log.append(signal)
		if self.decision_function is None:
			resp = random.choice(self.responses)
			self.response_log.append(resp)
			return resp

	def signal(self, opponent):
		""" Report own consumption based on
		decision function.
		"""
		if self.decision_function is None:
			sig = random.choice(self.signals)
			self.signal_log.append(sig)
			return sig


	def update_beliefs(self, payoff):
		""" Update the agent's beliefs about
		the frequency of other types and so on.
		"""
		self.payoff_log.append(payoff)




class Game:
	def __init__(self, num_rounds=1, baby_payoff=100, referal_cost=50, heavy_cost=3,
	 moderate_cost=2, light_cost=1):
		""" A multistage game played by two agents.
		"""
		self.signal_log = []
		self.act_log = []
		self.payoff = [[[[[(0, 0), (0,0)] for x in range(2)] for y in range(3)] for z in range(3)] for i in range(3)]
		self.num_rounds = num_rounds
		#Payoff for a baby
		self.baby_payoff = baby_payoff
		#Cost for referring
		self.referal_cost = referal_cost
		#Basic social cost of drinking types
		self.heavy_cost = heavy_cost
		self.moderate_cost = moderate_cost
		self.light_cost = light_cost

	def init_payoffs(self):
		#Light drinkers
		#Non-judgemental midwife
		self.payoff[0][0][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[0][0][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[0][0][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[0][0][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[0][0][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[0][0][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Moderately judgemental midwife
		self.payoff[0][1][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[0][1][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[0][1][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[0][1][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[0][1][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[0][1][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Very judgemental midwife
		self.payoff[0][2][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[0][2][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[0][2][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[0][2][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[0][2][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[0][2][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Moderate drinkers
		#Non-judgemental midwife
		self.payoff[1][0][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[1][0][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[1][0][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[1][0][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[1][0][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[1][0][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Moderately judgemental midwife
		self.payoff[1][1][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[1][1][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[1][1][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[1][1][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[1][1][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[1][1][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Very judgemental midwife
		self.payoff[1][2][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[1][2][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[1][2][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[1][2][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[1][2][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[1][2][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Heavy drinkers
		#Non-judgemental midwife
		self.payoff[2][0][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[2][0][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[2][0][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[2][0][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[2][0][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[2][0][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Moderately judgemental midwife
		self.payoff[2][1][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[2][1][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[2][1][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[2][1][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[2][1][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[2][1][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)

		#Very judgemental midwife
		self.payoff[2][2][0][0] = (self.baby_payoff - self.light_cost, self.baby_payoff)
		self.payoff[2][2][0][1] = (self.baby_payoff - self.light_cost, self.baby_payoff - self.referal_cost)
		self.payoff[2][2][1][0] = (self.baby_payoff - self.moderate_cost, self.baby_payoff)
		self.payoff[2][2][1][1] = (self.baby_payoff - self.moderate_cost, self.baby_payoff - self.referal_cost)
		self.payoff[2][2][2][0] = (self.baby_payoff - self.heavy_cost, self.baby_payoff)
		self.payoff[2][2][2][1] = (self.baby_payoff - self.heavy_cost, self.baby_payoff - self.referal_cost)


	def play_round(self, signaller, receiver):
		""" Play a round of this game between the
		two players.
		"""
		signal = signaller.signal(receiver)
		act = receiver.respond(signal, signaller)
		signaller.response_log.append(act)
		round_payoff = self.payoff[signaller.player_type][receiver.player_type][signal][act]
		self.signal_log.append(signal)
		self.act_log.append(act)
		signaller.update_beliefs(round_payoff)
		receiver.update_beliefs(round_payoff)

	def play_game(self, signaller, receiver):
		for r in range(self.num_rounds):
			self.play_round(signaller, receiver)

