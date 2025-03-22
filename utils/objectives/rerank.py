from .distance import Distance


class Rerank:
    # Specify default alpha value for relevance.
    tradeoff = 0.5

    def __init__(
            self, recs: list[list[int, float]], limit: int, distance: Distance,
        ):
        """
        Defines rerankers for a given recommendation list.

        Args:
            recs (list[list[int, float]]): The initial item recs and their scores.
            limit (int): The cutoff point for the number of items.
            distance (Distance): Calculates item distance objectives.
        """
        # Precompute relevance weights by standardizing initial recommendations.
        recs_std = Distance.standardize(recs, 1)

        # Precompute and standardize novelty scores.
        novelty_scores = [(item, distance.by_rarity(item)) for item, _ in recs]
        novelty_std = Distance.standardize(novelty_scores, 1)

        self.recs_set = set(recs_std)
        self.novelty_std = dict(novelty_std)

        # Ensure limit does not surpass list length.
        self.limit = limit
        if len(self.recs_set) < self.limit:
            self.limit = len(self.recs_set)


    def _full_objective(
        self,
        alpha: float,
        rel: float,
        obj_fn: callable,
        item: int,
        recs: list[tuple[int, float]],
    ) -> float:
        """
        Calculates the reranking objective for an item.
        
        Args:
            alpha (float): Controls the tradeoff between relevance and the objective.
            rel (float): The relevance level.
            obj_fn (callable): Function used to calculate reranker objective.
            item (int): The objective function being calculated for this item.
            recs (list[tuple[int, float]]): The current list of reranked recommendations.

        Returns:
            float: The full objective value for the particular item.

        """
        relevance_weight = alpha * rel
        objective_weight = (1 - alpha) * obj_fn(item, recs)
        full_obj = relevance_weight + objective_weight
        return full_obj


    def _f_objective(self, objective_fn: callable, alpha: float) -> list[tuple[int, float]]:
        """
        Helper function for reranking a recommendation list by an objective.
        Reranker variations are a combination of its current relevance and the
        reranker objective.

        Args:
            objective_fn (callable): Function used to calculate reranker objective.
            alpha (float): Controls the tradeoff between relevance and the objective.

        Returns:
            list[tuple[int, float]]: Pairs of items and scores to maximize the objective.
        """
        initial_recs = self.recs_set.copy()
        reranked_recs = []

        while len(initial_recs) > 0 and len(reranked_recs) < self.limit:
            # Treat first value as initial best.
            best_item, rel_level = next(iter(initial_recs))
            best_score = self._full_objective(
                alpha, rel_level, objective_fn, best_item, reranked_recs,
            )

            # Calculate f-objective for each item in candidate list.
            for new_item, rel in initial_recs:
                full_obj = self._full_objective(
                    alpha, rel, objective_fn, new_item, reranked_recs,
                )

                # Update item that results in the best score.
                if full_obj > best_score:
                    best_item = new_item
                    rel_level = rel
                    best_score = full_obj

            # Transfer item from candidate list to recommendation list.
            reranked_recs.append((best_item, best_score))
            initial_recs.remove((best_item, rel_level))

        return reranked_recs


    def novelty(self, alpha: float = tradeoff) -> list[tuple[int, float]]:
        """
        Reranks with a focus on maximizing novelty. The reranking algorithm
        bases distances off the fraction of users who rated the item.

        Args:
            alpha (float): Controls the tradeoff between relevance and novelty.

        Returns:
            list[tuple[int, float]]: Pairs of items and scores to maximize novelty.
        """
        def objective(item: int, _) -> float:
            return self.novelty_std[item]

        return self._f_objective(objective, alpha)
