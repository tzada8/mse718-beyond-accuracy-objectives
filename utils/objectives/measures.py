from itertools import permutations
import math

from .distance import Distance


class Measures:
    def __init__(
        self,
        user_id: int,
        recs: list[int],
        limit: int,
        distance: Distance,
    ):
        """
        Defines measures for a given recommendation list.

        Args:
            user_id (int): The user's recommendations.
            recs (list[int]): The initial recommendations.
            limit (int): The cutoff point for the number of items.
            distance (Distance): Calculates item distance objectives.
        """
        self.user_id = user_id
        self.recs = recs[:limit]
        self.distance = distance


    def diversity(self) -> float:
        """
        Calculates the recommendation list's level of diversity using the item
        genres.

        Returns:
            float: The diversity score.
        """
        if len(self.recs) == 0:
            return 0.0
        elif len(self.recs) == 1:
            return 1.0

        total_dist = sum(
            self.distance.by_tags(item_i, item_j)
            for item_i, item_j in permutations(self.recs, 2)
        )
        denom = len(self.recs) * (len(self.recs) - 1)
        return total_dist / denom


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


    def serendipity(self) -> float:
        """
        Calculates the recommendation list's level of serendipity using the item
        genres.

        Returns:
            float: The serendipity score.
        """
        if len(self.recs) == 0:
            return 0.0

        total_min_dist = sum(
            self.distance.by_surprise(self.user_id, ranked_item)
            for ranked_item in self.recs
        )
        return total_min_dist / len(self.recs)
