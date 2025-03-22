import math

from .distance import Distance


class Measures:
    def __init__(self, recs: list[int], limit: int, distance: Distance):
        """
        Defines measures for a given recommendation list.

        Args:
            recs (list[int]): The initial recommendations.
            limit (int): The cutoff point for the number of items.
            distance (Distance): Calculates item distance objectives.
        """
        self.recs = recs[:limit]
        self.distance = distance


    def novelty(self) -> float:
        """
        Calculates the recommendation list's level of novelty using the number
        of times items are rated.

        Returns:
            float: The novelty score.
        """
        if len(self.recs) == 0:
            return 0.0

        fraction_rated = sum(
            self.distance.by_rarity(item) for item in self.recs
        )
        factor = -math.log2(1 / self.distance.num_users) * len(self.recs)
        return (1 / factor) * fraction_rated
