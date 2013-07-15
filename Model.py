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
	def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
		self.player_type = player_type
		self.decision_function = decision_function
		self.signals = signals
		self.responses = responses
		self.payoff_log = []
		self.signal_log = []
		self.response_log = []
		self.type_log = []


	def respond(self, signal, opponent):
		"""
		Make a judgement about somebody based on
		the signal they sent.
		"""
		self.signal_log.append(signal)
		resp = random.choice(self.responses)
		self.response_log.append(resp)
		return resp

	def do_signal(self, opponent):
		""" Report own consumption based on
		decision function.
		"""
		sig = random.choice(self.signals)
		self.signal_log.append(sig)
		return sig


	def update_beliefs(self, payoff, signaller_type):
		""" Update the agent's beliefs about
		the frequency of other types and so on.
		"""
		self.payoff_log.append(payoff)

class Signaller(Agent):

	def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
		# Given own type, there are always 6 possible payoffs for a given signal.
		# 2 for each of the three midwife types, per signal.
		self.payoff_belief = dict([(signal, {}) for signal in self.signals])
		super(Signaller, self).__init__(player_type, signals, responses)

	def init_payoff_belief(self, payoffs):
		#Only interested in payoffs for own type
		payoffs = payoffs[self.player_type]
		#Interested in payoffs per signal
		for signal_i, payoff_set in self.payoff_belief.items():
			for midwife_type in range(3):
				for i in range(2):
					#Payoff for this signal with this midwife type
					payoff = payoffs[midwife_type][signal_i][i]
					if payoff in payoff_set:
						payoff_set[payoff][0] += 1/6.
					else:
						payoff_set[payoff] = [1/6.]

	def update_beliefs(self, payoff, signaller_type):
		""" Women have belief about the state of the world,
		and how likely refer or not actions are on the part
		of the responder, i.e. P(Payoff | Signal) = P(Signal | Payoff)P(Payoff) / P(Signal | Payoff)P(Payoff) + ..
		"""
		self.payoff_log.append(payoff)
		rounds = len(self.type_log)
		for signal_i, payoffs in self.payoff_belief.items():
			signal_matches = [x == signal_i for x in self.signal_log]
			payoff_matches = {}
			for payoff, belief in payoffs.items():
				payoff_matches[payoff] = [x == payoff for x in self.payoff_log]

			for payoff, belief in payoffs.items():
				#Othey payoffs
				other_payoffs = filter(lambda x: x != payoff, payoffs.keys())
				# Update given recent payoff using bayes rule
				#print "Payoff matches", payoff_matches
				
				#print "Signal matches", signal_matches

				matched_pairs = zip(payoff_matches[payoff], signal_matches)

				# Rounds where we got this payoff having sent the signal count(Signal | Payoff)
				signal_payoff_matches = [a and b for a, b in matched_pairs]
				# Other payoffs and this signal
				signal_payoff_others = {}
				for x in other_payoffs:
					matched_pairs = zip(payoff_matches[x], signal_matches)
					signal_payoff_others[x] = [a and b for a, b in matched_pairs]
				

				# Rounds where we sent this signal
				signal_matches_count = float(signal_matches.count(True))

				#print "Payoff-Signal matches", signal_payoff_matches

				#P(Payoff) in this state of the world
				p_payoff = self.payoff_belief[signal_i][payoff][0]
				p_signal_payoff = 0.
				p_signal_not_payoff = 0.
				p_payoff_signal = self.payoff_belief[signal_i][payoff][rounds - 1]
			
				if signal_matches_count > 0:
					print "Updating payoff belief for signal", signal_i, "payoff", payoff,". Signal happened",signal_matches_count," times"
					print "Got both",signal_payoff_matches.count(True),"times."
					#P(Signal | Payoff)
					p_signal_payoff = signal_payoff_matches.count(True) / signal_matches_count
					print "P(Signal|Payoff)=",p_signal_payoff
					#P(Signal | -Payoff)
					p_signal_not_payoff = 0.
					for key, matches in signal_payoff_others.items():
						p_signal_not_payoff += (matches.count(True) / signal_matches_count) * self.payoff_belief[signal_i][key][0]
					print "P(Signal|-Payoff)=",p_signal_not_payoff
					# Probability that this signal actually leads to this payoff (P(Payoff | Signal))
					p_payoff_signal = p_signal_payoff*p_payoff / (p_signal_payoff*p_payoff + p_signal_not_payoff)
				self.payoff_belief[signal_i][payoff].append(p_payoff_signal)

class LyingSignaller(Signaller):

	def do_signal(own_type):
		""" A decision function that always returns a
		type other than its own as a signal.
		"""
		types = filter(lambda x: x != own_type, self.signals)
		return random.choice(types)


class Responder(Agent):

	def __init__(self, player_type=1, signals=[0, 1, 2], responses=[0, 1]):
		# Belief that a particular signal means a state
		self.signal_belief = dict([(y, dict([(x, [1/3.]) for x in self.signals])) for y in self.signals])
		super(Responder, self).__init__(player_type, signals, responses)

	def update_beliefs(self, payoff, signaller_type):
		""" Update beliefs about the meaning of signals, essentially the
		belief that the State of the world is S based on s.
		i.e. P(Type | signal) = P(signal | Type)P(Type) / P(signal | Type)P(Type) + P(signal | -Type)P(-Type)
		"""
		self.type_log.append(signaller_type)
		rounds = len(self.type_log)

		type_matches = []
		for player_type in self.signals:
			type_matches.append([x == player_type for x in self.type_log])

		for signal_i, types in self.signal_belief.items():
			signal_matches = [x == signal_i for x in self.signal_log]
			for player_type, belief in types.items():
				other_types = filter(lambda x: x != player_type, self.signals)
				# Update given recent signal using bayes rule
				#Both together
				matched_pairs = zip(type_matches[player_type], signal_matches)
				signal_type_matches = [a and b for a, b in matched_pairs]
				signal_type_other_matches = {}
				#Other types and this signal
				for x in other_types:
					matched_pairs = zip(type_matches[x], signal_matches)
					signal_type_other_matches[x] = [a and b for a, b in matched_pairs]

				type_matches_count = float(type_matches.count(True))
				signal_matches_count = float(signal_matches.count(True))

				#P(Type) Might be wise to assume this is known
				p_type = self.signal_belief[signal_i][player_type][0]
				p_signal_type = 0.
				p_signal_not_type = 0.
				p_type_signal = self.signal_belief[signal_i][player_type][rounds - 1]
				#P(Signal | Type)
				print "Seen this type", type_matches_count,"times."
				print "Seen this signal", signal_matches_count,"times."
				print "Saw this type and signal together", signal_type_matches.count(True), "times"
				if signal_matches_count > 0:
					p_signal_type = signal_type_matches.count(True) / signal_matches_count
				#P(Signal | -Type)
					p_signal_type_other = 0.
					for key, matches in signal_type_other_matches.items():
						p_signal_type_other += (matches.count(True) / signal_matches_count) * p_type
				# Probability that the signal actually meant this type (P(Type | Signal))
					print "Probability of signalling this type - ", p_signal_type
					print "Probability of signalling other type - ",p_signal_type_other
					p_type_signal = p_signal_type*p_type / (p_signal_type*p_type + p_signal_type_other)
				print "Updating signal ", signal_i, " type ", player_type
				self.signal_belief[signal_i][player_type].append(p_type_signal)



class Game:
	def __init__(self, num_rounds=1, baby_payoff=100, referral_cost=50, heavy_cost=3,
	 moderate_cost=2, light_cost=1, moderate_judge=1, harsh_judge=2):
		""" A multistage game played by two agents.
		"""
		self.signal_log = []
		self.act_log = []
		self.disclosure_log = []
		self.payoff = [[[[0, 0] for y in range(3)] for z in range(3)] for i in range(3)]
		self.midwife_payoff = [[0, 0] for x in range(3)]
		self.num_rounds = num_rounds
		#Payoff for a baby
		self.baby_payoff = baby_payoff
		self.no_baby_payoff = -baby_payoff
		self.mid_baby_payoff = baby_payoff / 2
		#Cost for referring
		self.referral_cost = referral_cost
		#Basic social cost of drinking types
		self.heavy_cost = heavy_cost
		self.moderate_cost = moderate_cost
		self.light_cost = light_cost
		#Type multipliers
		self.harsh_judge = harsh_judge
		self.moderate_judge = moderate_judge

	def init_payoffs(self):
		#Midwife payoffs
		#Light drinker
		self.midwife_payoff[0][0] = self.baby_payoff
		self.midwife_payoff[0][1] = self.baby_payoff - self.referral_cost

		#Moderate drinker
		self.midwife_payoff[1][0] = self.mid_baby_payoff
		self.midwife_payoff[1][1] = self.baby_payoff - self.referral_cost

		#Heavy drinker
		self.midwife_payoff[2][0] = self.no_baby_payoff
		self.midwife_payoff[2][1] = self.baby_payoff - self.referral_cost

		#Woman's payoff
		#[woman type][midwife type][signal][action]
		#Light drinkers
		#Non-judgemental midwife
		self.payoff[0][0][0][0] = self.baby_payoff - self.light_cost
		self.payoff[0][0][0][1] = self.baby_payoff - self.light_cost
		self.payoff[0][0][1][0] = self.baby_payoff - self.moderate_cost
		self.payoff[0][0][1][1] = self.baby_payoff - self.moderate_cost
		self.payoff[0][0][2][0] = self.baby_payoff - self.heavy_cost
		self.payoff[0][0][2][1] = self.baby_payoff - self.heavy_cost

		#Moderately judgemental midwife
		self.payoff[0][1][0][0] = self.baby_payoff - self.light_cost * self.moderate_judge
		self.payoff[0][1][0][1] = self.baby_payoff - self.light_cost * self.moderate_judge
		self.payoff[0][1][1][0] = self.baby_payoff - self.moderate_cost * self.moderate_judge
		self.payoff[0][1][1][1] = self.baby_payoff - self.moderate_cost * self.moderate_judge
		self.payoff[0][1][2][0] = self.baby_payoff - self.heavy_cost * self.moderate_judge
		self.payoff[0][1][2][1] = self.baby_payoff - self.heavy_cost * self.moderate_judge

		#Very judgemental midwife
		self.payoff[0][2][0][0] = self.baby_payoff - self.light_cost * self.harsh_judge
		self.payoff[0][2][0][1] = self.baby_payoff - self.light_cost * self.harsh_judge
		self.payoff[0][2][1][0] = self.baby_payoff - self.moderate_cost * self.harsh_judge
		self.payoff[0][2][1][1] = self.baby_payoff - self.moderate_cost * self.harsh_judge
		self.payoff[0][2][2][0] = self.baby_payoff - self.heavy_cost * self.harsh_judge
		self.payoff[0][2][2][1] = self.baby_payoff - self.heavy_cost * self.harsh_judge

		#Moderate drinkers
		#Non-judgemental midwife
		self.payoff[1][0][0][0] = self.mid_baby_payoff - self.light_cost
		self.payoff[1][0][0][1] = self.baby_payoff - self.light_cost
		self.payoff[1][0][1][0] = self.mid_baby_payoff - self.moderate_cost
		self.payoff[1][0][1][1] = self.baby_payoff - self.moderate_cost
		self.payoff[1][0][2][0] = self.mid_baby_payoff - self.heavy_cost
		self.payoff[1][0][2][1] = self.baby_payoff - self.heavy_cost

		#Moderately judgemental midwife
		self.payoff[1][1][0][0] = self.mid_baby_payoff - self.light_cost * self.moderate_judge
		self.payoff[1][1][0][1] = self.baby_payoff - self.light_cost * self.moderate_judge
		self.payoff[1][1][1][0] = self.mid_baby_payoff - self.moderate_cost * self.moderate_judge
		self.payoff[1][1][1][1] = self.baby_payoff - self.moderate_cost * self.moderate_judge
		self.payoff[1][1][2][0] = self.mid_baby_payoff - self.heavy_cost * self.moderate_judge
		self.payoff[1][1][2][1] = self.baby_payoff - self.heavy_cost * self.moderate_judge

		#Very judgemental midwife
		self.payoff[1][2][0][0] = self.mid_baby_payoff - self.light_cost * self.harsh_judge
		self.payoff[1][2][0][1] = self.baby_payoff - self.light_cost * self.harsh_judge
		self.payoff[1][2][1][0] = self.mid_baby_payoff - self.moderate_cost * self.harsh_judge
		self.payoff[1][2][1][1] = self.baby_payoff - self.moderate_cost * self.harsh_judge
		self.payoff[1][2][2][0] = self.mid_baby_payoff - self.heavy_cost * self.harsh_judge
		self.payoff[1][2][2][1] = self.baby_payoff - self.heavy_cost * self.harsh_judge

		#Heavy drinkers
		#Non-judgemental midwife
		self.payoff[2][0][0][0] = - self.light_cost
		self.payoff[2][0][0][1] = self.baby_payoff - self.light_cost
		self.payoff[2][0][1][0] = - self.moderate_cost
		self.payoff[2][0][1][1] = self.baby_payoff - self.moderate_cost
		self.payoff[2][0][2][0] =  - self.heavy_cost
		self.payoff[2][0][2][1] = self.baby_payoff - self.heavy_cost

		#Moderately judgemental midwife
		self.payoff[2][1][0][0] =  self.no_baby_payoff - self.light_cost * self.moderate_judge
		self.payoff[2][1][0][1] = self.baby_payoff - self.light_cost * self.moderate_judge
		self.payoff[2][1][1][0] = self.no_baby_payoff - self.moderate_cost * self.moderate_judge
		self.payoff[2][1][1][1] = self.baby_payoff - self.moderate_cost * self.moderate_judge
		self.payoff[2][1][2][0] = self.no_baby_payoff - self.heavy_cost * self.moderate_judge
		self.payoff[2][1][2][1] = self.baby_payoff - self.heavy_cost * self.moderate_judge

		#Very judgemental midwife
		self.payoff[2][2][0][0] = self.no_baby_payoff - self.light_cost * self.harsh_judge
		self.payoff[2][2][0][1] = self.baby_payoff - self.light_cost * self.harsh_judge
		self.payoff[2][2][1][0] = self.no_baby_payoff - self.moderate_cost * self.harsh_judge
		self.payoff[2][2][1][1] = self.baby_payoff - self.moderate_cost * self.harsh_judge
		self.payoff[2][2][2][0] = self.no_baby_payoff - self.heavy_cost * self.harsh_judge
		self.payoff[2][2][2][1] = self.baby_payoff - self.heavy_cost * self.harsh_judge


	def play_round(self, signaller, receiver):
		""" Play a round of this game between the
		two players.
		"""
		signal = signaller.do_signal(receiver)
		act = receiver.respond(signal, signaller)
		signaller.response_log.append(act)
		signal_payoff = self.payoff[signaller.player_type][receiver.player_type][signal][act]
		receive_payoff = self.midwife_payoff[signaller.player_type][act]
		self.signal_log.append(signal)
		self.act_log.append(act)
		signaller.update_beliefs(signal_payoff, receiver.player_type)
		receiver.update_beliefs(receive_payoff, signaller.player_type)
		# Log honesty of signal
		self.disclosure_log.append(signal == signaller.player_type)

	def play_game(self, signaller, receiver):
		signaller.init_payoffs(self.payoff)
		for r in range(self.num_rounds):
			self.play_round(signaller, receiver)




