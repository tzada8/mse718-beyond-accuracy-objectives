import math
import statistics


class Distance:
    def __init__(
        self,
        rated: dict[int, list[int]],
        tags: dict[int, set[str]],
        user_ratings: dict[int, list[int]],
        num_users: int,
    ):
        """
        Defines distance metrics for a given dataset.

        Args:
            rated (dict[int, list[int]]): A mapping of items to all the users that rated it.
            tags (dict[int, set[str]]): A mapping of items to its genres.
            user_ratings (dict[int, list[int]]): A mapping of users to their rated items.
            num_users (int): The total number of users in the dataset.
        """
        self.rated = rated
        self.tags = tags
        self.user_ratings = user_ratings
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


    def by_tags(self, item_i: int, item_j: int) -> float:
        """
        Finds the distance between items based on tags.

        Args:
            item_i (int): The first item.
            item_j (int): The second item.

        Returns:
            float: The distance between the two items.
        """
        item_i_tags = self.tags[item_i]
        item_j_tags = self.tags[item_j]

        similar_tags = item_i_tags & item_j_tags
        all_tags = item_i_tags | item_j_tags
        num_total_tags = max(len(all_tags), 1)
        return 1 - (len(similar_tags) / num_total_tags)


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


    def by_surprise(self, user_id: int, item: int) -> float:
        """
        Finds the amount of surprise of an item being recommended.

        Args:
            user_id (int): The user.
            item (int): The item.

        Returns:
            float: The surprise of the item.
        """
        return min(
            self.by_tags(item, rated_item)
            for rated_item in self.user_ratings[user_id]
        )
