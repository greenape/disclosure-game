from Model import *


class ReferralGame(Game):
        """
        Similar to the standard disclosure game, but the true drinking type
        is only revealed after a referral, which ends the game.
        """

        def play_round(self, signaller, receiver):
                """ Play a round of this game between the
                two players.
                """
                signal = signaller.do_signal(receiver)
                act = receiver.respond(signal, opponent=signaller)
                signal_payoff = self.woman_baby_payoff[signaller.player_type][act] + self.woman_social_payoff[signal][receiver.player_type]
                receive_payoff = self.midwife_payoff[signaller.player_type][act]

                #Signaller learns the true type
                signaller.update_beliefs(act, receiver, signal_payoff)
                #But the responder doesn't unless they referred
                receiver.rounds -= 1
                if act == 1:
                        receiver.update_beliefs(receive_payoff, signaller)
                else:
                        signaller.finished += 1
