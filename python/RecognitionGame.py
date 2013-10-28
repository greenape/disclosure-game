from Model import *


class RecognitionGame(Game):
        """
        Similar to the standard disclosure game, but the true drinking type
        is only revealed after a referral, which ends the game.
        In addition, signallers can only fuzzily differentiate between responder types.
        Observing a social payoff that could come from any responder type will not allow
        an update.
        Observing one that could come from 2 types is evidence for both.
        Observing a unique response constitutes a type revelation.
        """

        def play_round(self, signaller, receiver):
                """ Play a round of this game between the
                two players.
                """
                signal = signaller.do_signal(receiver)
                act = receiver.respond(signal, opponent=signaller)
                signal_payoff = self.woman_baby_payoff[signaller.player_type][act] + self.woman_social_payoff[signal][receiver.player_type]
                receive_payoff = self.midwife_payoff[signaller.player_type][act]

                #Signaller learns something about the type
                social = self.woman_social_payoff[signal][receiver.player_type]

                target = copy(receiver)

                possible_types = []

                for i in len(self.woman_social_payoff[signal]):
                        if social == self.woman_social_payoff[signal][i]:
                                possible_types.append(i)
                #True type is known
                if len(possible_types) == 1:
                	signaller.update_beliefs(act, receiver, signal_payoff)
                else:
                	signaller.fuzzy_update_beliefs(act, receiver, signal_payoff, possible_types)

                #But the responder doesn't unless they referred
                receiver.rounds -= 1
                if act == 1:
                        receiver.update_beliefs(receive_payoff, signaller)
