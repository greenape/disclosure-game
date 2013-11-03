from Model import *


class ReferralGame(Game):
        """
        Similar to the standard disclosure game, but the true drinking type
        is only revealed after a referral, which ends the game.
        """
        def name(self):
                return "referral"

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
                if act == 1:
                        receiver.update_beliefs(receive_payoff, signaller)
                        signaller.is_finished = True
                else:
                        receiver.rounds -= 1


class CaseloadReferralGame(CaseloadGame, ReferralGame):
        """
        Identical with the regular referral game, but uses caseloading to assign
        women to midwives.
        """
