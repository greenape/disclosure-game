from CarryingGame import CarryingReferralGame
from Model import measures_women, measures_midwives, random_expectations
import random
from math import copysign
import operator
try:
    import scoop
    scoop.worker
    scoop_on = True
except:
    scoop_on = False
    pass

class CarryingInformationGame(CarryingReferralGame):
    """
    A game type identical with the carrying referral game, but where some information
    is shared on each round, according to a parameter controlling what percentage of the
    population to share to (chosen at random), and how biased towards sharing 'dramatic'
    information people are.
    """
    def __init__(self, baby_payoff=2, no_baby_payoff=2, mid_baby_payoff=1,referral_cost=1, harsh_high=2,
     harsh_mid=1, harsh_low=0, mid_high=1, mid_mid=0, mid_low=0, low_high=0,low_mid=0,low_low=0, randomise_payoffs=False,
     type_weights=[[10., 1., 1.], [1., 10., 1.], [1., 1., 10.]], rounds=100, measures_women=measures_women(),
     measures_midwives=measures_midwives(), params=None, mw_share_width=0, mw_share_bias=-1, women_share_width=0, women_share_bias=1,
     num_appointments=12):
        super(CarryingInformationGame, self).__init__(baby_payoff, no_baby_payoff, mid_baby_payoff, referral_cost, harsh_high,
            harsh_mid, harsh_low, mid_high, mid_mid, mid_low, low_high, low_mid, low_low, randomise_payoffs, type_weights,
            rounds, measures_women, measures_midwives, params)
        self.mw_share_bias = mw_share_bias
        self.mw_share_width = mw_share_width
        self.women_share_bias = women_share_bias
        self.women_share_width = women_share_width
        self.num_appointments = num_appointments

    def __str__(self):
        return "sharing_%s" % super(CarryingInformationGame, self).__unicode__()

    def play_game(self, players, file_name=""):
        if scoop_on:
            scoop.logger.debug("Worker %s playing a game." % (scoop.worker[0]))
        women, midwives = players
        player_dist = self.get_distribution(women)

        rounds = self.rounds
        birthed = []
        random.shuffle(women)
        num_midwives = len(midwives)
        women_res = self.measures_women.dump(women, self.rounds, self)
        mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        women_memories = []
        for i in range(rounds):
            players = [women.pop() for j in range(num_midwives)]
            random.shuffle(midwives)
            map(self.play_round, players, midwives)
            for x in midwives:
                x.finished += 1
            for woman in players:
                if self.all_played([woman], self.num_appointments):
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = self.random_player(player_dist, woman)#type(woman)(player_type=woman.player_type)
                    new_woman.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff,
                        random_expectations(), [random_expectations(breadth=2) for x in range(3)])
                    new_woman.started = i
                    new_woman.finished = i
                    women.insert(0, new_woman)
                    women_res.add_results(self.measures_women.dump([woman, new_woman], self.rounds, self))
                    women_memories.append(woman.get_memory())
                    del woman
                else:
                    women.insert(0, woman)
                    woman.finished += 1
            # Share information
            if scoop_on:
                scoop.logger.debug("Worker %s prepping share." % (scoop.worker[0]))
            #Midwives
            self.share_midwives(midwives)

            #Women
            self.share_women(women, women_memories)

            #if scoop_on:
            #    scoop.logger.debug("Worker %s played %d rounds." % (scoop.worker[0], i))
        women_res = self.measures_women.dump(women, self.rounds, self)
        mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        del women
        del midwives
        women_res.write_db("%s_women" % file_name)
        mw_res.write_db("%s_mw" % file_name)
        if scoop_on:
            scoop.logger.debug("Worker %s completed a game." % (scoop.worker[0]))
        return None

    def share_midwives(self, midwives):
        #Collect memories
            mw_memories = map(lambda x: x.shareable, midwives)
            mw_memories = filter(lambda x: x is not None, mw_memories)
            #print mw_memories
            #Sort them according to the threshold sign
            if self.mw_share_bias == 0:
                mw_memories.shuffle()
            elif copysign(1, self.mw_share_bias) == 1:
                mw_memories.sort(key=operator.itemgetter(1), reverse=True)
            elif copysign(1, self.mw_share_bias) == -1:
                mw_memories.sort(key=operator.itemgetter(1))
            #Weight them by position in the sort
            mw_memories = self.n_most(self.mw_share_bias, mw_memories)
            #print mw_memories
            #Choose one by weighted random choice
            #memory = self.weighted_random_choice(mw_memories)
            #print "Memory is", memory, "worst was", mw_memories[len(mw_memories) - 1]
            for memory in mw_memories:
                possibles = filter(lambda x: hash(x) != memory[0], midwives)
                #Share it
                self.disseminate_midwives(memory[2], self.share_to(possibles, self.mw_share_width))
                #And null it
                lucky = filter(lambda x: hash(x) == memory[0], midwives)[0]
                lucky.shareable = None

    def share_women(self, women, women_memories):
        #Sort them according to the threshold sign
            if self.women_share_bias == 0:
                women_memories.shuffle()
            elif copysign(1, self.women_share_bias) == 1:
                women_memories.sort(key=operator.itemgetter(0), reverse=True)
            elif copysign(1, self.women_share_bias) == -1:
                women_memories.sort(key=operator.itemgetter(0))
            #Weight them by position in the sort
            memories = self.n_most(self.women_share_bias, women_memories)
            #Choose one by weighted random choice
            #memory = self.weighted_random_choice(tmp_memories)
            #Share it
            for memory in memories:
                self.disseminate_women(memory[1], self.share_to(women, self.women_share_width))
                #And null it
                women_memories.remove(memory)

    def disseminate_midwives(self, memory, recepients):
        if scoop_on:
            scoop.logger.debug("Sharing a memory to midwives.")
        if memory is None:
            return
        player_type, signals = memory
        print "Sharing to midwives.", memory
        tmp_signaller = type(recepients[0])(player_type=player_type)
        for recepient in recepients:
            for signal, response in signals:
                recepient.remember(tmp_signaller, signal, response)
                recepient.update_beliefs(None, tmp_signaller, signal, signaller_type=player_type)

    def disseminate_women(self, memory, recepients):
        if scoop_on:
            scoop.logger.debug("Sharing a memory to women.")
        print "Sharing to women.", memory
        if memory is None:
            return
        for recepient in recepients:
            for mem in memory:
                pt, signal, response, payoff = mem
                tmp_signaller = type(recepients[0])(player_type=pt)
                recepient.exogenous_update(signal, response, tmp_signaller, payoff, midwife_type=pt)

    def share_to(self, pop, fraction):
        """
        Choose some percentage of the population to share to at random.
        """
        size = len(pop)
        k = int(round(size * fraction))
        return random.sample(pop, k)

    def weighted_random_choice(self, choices):
        total = sum(w for c, w in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w in choices:
            if upto + w > r:
                return c
            upto += w

    def n_most(self, threshold, memories):
        num = int(round(len(memories)*(1 - abs(threshold))))
        return memories[0:num]


class CaseloadSharingGame(CarryingInformationGame):
    def __str__(self):
        return "caseload_%s" % super(CaseloadSharingGame, self).__unicode__()


    def play_game(self, players, file_name=""):
        if scoop_on:
            scoop.logger.debug("Worker %s playing a game." % (scoop.worker[0]))
        women, midwives = players
        player_dist = self.get_distribution(women)

        rounds = self.rounds
        birthed = []
        random.shuffle(women)
        num_midwives = len(midwives)
        women_res = self.measures_women.dump(women, self.rounds, self)
        mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        women_memories = []
        caseloads = {}
        num_women = len(women)
        num_midwives = len(midwives)
        load = num_women / num_midwives
        random.shuffle(women)
        for midwife in midwives:
            caseloads[midwife] = []
            for i in range(load):
                caseloads[midwife].append(women.pop())
         # Assign leftovers at random
        while len(women) > 0:
            caseloads[random.choice(midwives)].append(women.pop())

        for i in range(rounds):
            players = [caseloads[midwife].pop() for midwife in midwives]
            random.shuffle(midwives)
            map(self.play_round, players, midwives)
            for x in midwives:
                x.finished += 1
            for j in range(len(players)):
                woman = players[j]
                women = caseloads[midwives[j]]
                if self.all_played([woman], self.num_appointments):
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = self.random_player(player_dist, woman)#type(woman)(player_type=woman.player_type)
                    new_woman.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff,
                        random_expectations(), [random_expectations(breadth=2) for x in range(3)])
                    new_woman.started = i
                    new_woman.finished = i
                    women.insert(0, new_woman)
                    women_res.add_results(self.measures_women.dump([woman, new_woman], self.rounds, self))
                    women_memories.append(woman.get_memory())
                    del woman
                else:
                    women.insert(0, woman)
                    woman.finished += 1
            # Share information
            if scoop_on:
                scoop.logger.debug("Worker %s prepping share." % (scoop.worker[0]))
            #Midwives
            self.share_midwives(midwives)

            #Women
            self.share_women(reduce(lambda x, y: x + y, caseloads.values()), women_memories)

            #if scoop_on:
            #    scoop.logger.debug("Worker %s played %d rounds." % (scoop.worker[0], i))
        women_res = self.measures_women.dump(women, self.rounds, self)
        mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        del women
        del midwives
        women_res.write_db("%s_women" % file_name)
        mw_res.write_db("%s_mw" % file_name)
        if scoop_on:
            scoop.logger.debug("Worker %s completed a game." % (scoop.worker[0]))
        return None


        women, midwives = players
        player_dist = self.get_distribution(women)

        rounds = self.rounds
        birthed = []
        random.shuffle(women)
        num_midwives = len(midwives)
        women_res = self.measures_women.dump(women, self.rounds, self)
        mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        caseloads = {}
        num_women = len(women)
        num_midwives = len(midwives)
        load = num_women / num_midwives
        random.shuffle(women)
        for midwife in midwives:
            caseloads[midwife] = []
            for i in range(load):
                caseloads[midwife].append(women.pop())
         # Assign leftovers at random
        while len(women) > 0:
            caseloads[random.choice(midwives)].append(women.pop())

        for i in range(rounds):
            players = [caseloads[midwife].pop() for midwife in midwives]
            random.shuffle(midwives)
            map(self.play_round, players, midwives)
            for x in midwives:
                x.finished += 1
            for j in range(len(players)):
                woman = players[j]
                women = caseloads[midwives[j]]
                if self.all_played([woman], self.num_appointments):
                    woman.is_finished = True
                    # Add a new naive women back into the mix
                    new_woman = self.random_player(player_dist, woman)#type(woman)(player_type=woman.player_type)
                    new_woman.init_payoffs(self.woman_baby_payoff, self.woman_social_payoff,
                        random_expectations(), [random_expectations(breadth=2) for x in range(3)])
                    new_woman.started = i
                    new_woman.finished = i
                    women.insert(0, new_woman)
                    women_res.add_results(self.measures_women.dump([woman, new_woman], self.rounds, self))
                    birthed.append(woman)
                else:
                    women.insert(0, woman)
                    woman.finished += 1
            # Share information
            #Midwives
            mw_memories = map(lambda x: self.should_share(x, self.mw_share_bias), midwives)
            for owner, memory in mw_memories:
                possibles = filter(lambda x: hash(x) != owner, midwives)
                self.share(memory, self.share_to(possibles, self.mw_share_width))
            w_memories = []
            new_birthed = []
            women = reduce(lambda x, y: x + y, caseloads.values())
            while len(birthed) > 0:
                woman = birthed.pop()
                mem = self.should_share(woman, self.women_share_bias)
                if mem is None:
                    new_birthed.append(woman)
                else:
                    self.share(mem, self.share_to(women, self.women_share_width))
            birthed = new_birthed



            #if scoop_on:
            #    scoop.logger.debug("Worker %s played %d rounds." % (scoop.worker[0], i))
        women = reduce(lambda x, y: x + y, caseloads.values())
        women_res = self.measures_women.dump(women, self.rounds, self)
        mw_res = self.measures_midwives.dump(midwives, self.rounds, self)
        del women
        del midwives
        women_res.write_db("%s_women" % file_name)
        mw_res.write_db("%s_mw" % file_name)
        if scoop_on:
            scoop.logger.debug("Worker %s completed a game." % (scoop.worker[0]))
        return None    


