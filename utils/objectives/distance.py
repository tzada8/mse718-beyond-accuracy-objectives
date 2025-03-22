import math
import statistics


class Distance:
    def __init__(self, rated: dict[int, list[int]], num_users: int):
        """
        Defines distance metrics for a given dataset.

        Args:
            rated (dict[int, list[int]]): A mapping of items to all the users that rated it.
            num_users (int): The total number of users in the dataset.
        """
        self.rated = rated
        self.num_users = num_users


    @staticmethod
    def standardize(data: list[tuple], idx: int) -> list[tuple]:
        """
        Standardizes a list of scores using the equation x' = (x - mu) / sigma.

        Args:
            scores (list[tuple]]): The list of scores to be standardized.
            idx (int): Which index of the tuple should be standardized.

        Returns:
            list[tuple]: The same initial list, except with the elements at the
            specified index being standardized.
        """
        default_sigma = 0

        scores = [score[idx] for score in data]
        mu = statistics.mean(scores)
        sigma = default_sigma if len(scores) < 2 else statistics.stdev(scores)

        # If all same values, then all standardized values should be the same.
        scores_std = [
            t[:idx] + ((t[idx] - mu) / sigma,) + t[idx+1:] if len(t) > idx else t
            for t in data
        ] if sigma > default_sigma else [
            t[:idx] + (0,) + t[idx+1:] if len(t) > idx else t
            for t in data
        ]
        return scores_std


    def by_rarity(self, item: int) -> float:
        """
        Finds the fraction of users who rated the item to determine how
        novel the item is. The logarithm emphasizes the novelty of the
        most rare items.

        Args:
            item (int): The item.

        Returns:
            float: The novelty of the item.
        """
        return -math.log2(len(self.rated[item]) / self.num_users)
