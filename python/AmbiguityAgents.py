from RecognitionAgents import *


class AmbiguitySignaller(RecognitionSignaller):
    """
    A class of signaller that uses the Fryer model for resolving ambiguity
    in observations.
    """

    def fuzzy_update_beliefs(self, response, midwife, payoff, possible_types):
        """
        This class of agent uses their existing beliefs to resolve
        the ambiguity of the possible types by finding the maximum
        likelihood and assuming this is the truth.
        """

        max_type = random.choice(possible_types)
        current = self.individual_current_type_distribution(midwife)
        likelihood = current[max_type]
        for t in possible_types:
            if current[t] > likelihood:
                likelihood = current[t]
                max_type = t
        #print "Possible types were", possible_types,"resolved to",max_type,"with p", likelihood
        super(AmbiguitySignaller, self).update_beliefs(response, midwife, payoff, midwife_type=max_type)
