from game import *

class ReferralGame(Game):
        """
        Similar to the standard disclosure game, but the true drinking type
        is only revealed after a referral, which ends the game.
        """
        def name(self):
                return "referral_no_inform"

        ##@profile
        def play_round(self, signaller, receiver):
                """ Play a round of this game between the
                two players.
                """
                signal = signaller.do_signal(receiver)
                if signaller.rounds == self.num_appointments:
                        signaller.is_finished = True
                act = receiver.respond(signal, opponent=signaller)
                signal_payoff = self.woman_baby_payoff[signaller.player_type][act] + self.woman_social_payoff[signal][receiver.player_type]
                receive_payoff = self.midwife_payoff[signaller.player_type][act]

                #Signaller learns the true type
                signaller.update_counts(act, receiver, signal_payoff)
                signaller.update_beliefs()
                signaller.accrued_payoffs += signal_payoff
                receiver.accrued_payoffs += receive_payoff
                #But the responder doesn't unless they referred
                if act == 1:
                        receiver.update_beliefs(receive_payoff, signaller, signal)
                        signaller.is_finished = True
                elif signaller.rounds == self.num_appointments:
                        signaller.is_finished = True
                        #receiver.update_beliefs(receive_payoff, signaller, signal)


class CaseloadReferralGame(CaseloadGame, ReferralGame):
        """
        Identical with the regular referral game, but uses caseloading to assign
        women to midwives.
        """
