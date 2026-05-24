

"""

Acquirer Matcher — ranks best acquirers for a given opportunity.

"""



from typing import Dict, List

from runtime_core.acquirers.dataset import AcquirerDataset

from runtime_core.acquirers.scoring import AcquirerScorer





class AcquirerMatcher:

    """Finds and ranks best acquirers."""



    def __init__(self):

        self.dataset = AcquirerDataset()

        self.scorer = AcquirerScorer()



    def match(self, context: Dict, top_n: int = 5) -> List[Dict]:

        domain = context.get("domain")



        # Filter dataset

        if domain:

            candidates = self.dataset.filter_by_sector(domain)

        else:

            candidates = self.dataset.get_all()



        # Score all

        scored = [self.scorer.score(a, context) for a in candidates]



        # Sort by fit

        ranked = sorted(scored, key=lambda x: x["fit"], reverse=True)



        return ranked[:top_n]

