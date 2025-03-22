from typing import Optional

import pandas as pd

from .base_file import BaseFile
from .measure_file import MeasureFile
from utils.objectives.distance import Distance
from utils.objectives.measures import Measures
from utils.objectives.rerank import Rerank


class RunFile(BaseFile):
    def __init__(
        self,
        path: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
    ):
        """
        Initializes a RunFile object either from a file path or a dataframe.

        Args:
            path (str, optional): The path to the file.
            df (pd.DataFrame, optional): Dataframe containing file data.

        Raises:
            ValueError: If neither `path` or `df` is provided, if both are
            provided, or if data is invalid.
        """
        headers = ["user_id", "q0", "movie_id", "rank", "score", "algorithm"]
        sep = " "
        super().__init__(headers, sep, path=path, df=df, output_headers=False)

        if self.df.empty or "algorithm" not in self.df.columns:
            raise ValueError("Invalid or empty run file")

        self.algorithm = self.df["algorithm"].iloc[0]


    def _rerank_user_group(
        self,
        user_group: pd.DataFrame,
        method: str,
        k: int,
        tradeoff: float,
        distance: Distance,
    ) -> pd.DataFrame:
        """
        Helper function to rerank the movies for a single user.

        Args:
            user_group (pd.DataFrame): Run data for a single user.
            method (str): The type of method to rerank by.
            k (int): Number of recommendations to rerank.
            tradeoff (float): Amount of relevance to maintain.
            distance (Distance): Defines how item distances are measured.

        Returns:
            pd.DataFrame: The user's reranked results.
        """
        movie_list = list(map(tuple, user_group.to_numpy()))
        reranker = Rerank(movie_list, k, distance)

        # Ensure reranker method exists.
        if not hasattr(reranker, method):
            raise ValueError(f"Invalid method: {method}")

        reranked_movies = getattr(reranker, method)(tradeoff)

        return pd.DataFrame(
            reranked_movies, columns=["movie_id", "score"],
        ).assign(user_id=user_group.name)


    def _add_constant_columns(
        self, df: pd.DataFrame, algorithm: str,
    ) -> pd.DataFrame:
        """
        Adds back constant columns and updates ranking order.

        Args:
            df (pd.DataFrame): The dataframe to add the columns to.
            algorithm (str): Name of algorithm.

        Returns:
            pd.DataFrame: The updated dataframe with the additional columns.
        """
        df["q0"] = "Q0"
        df["algorithm"] = algorithm
        df["rank"] = df.groupby("user_id").cumcount() + 1
        df["movie_id"] = df["movie_id"].astype(int)
        df = df[self.headers]
        return df


    def rerank(
        self, method: str, k: int, tradeoff: float, distance: Distance,
    ) -> "RunFile":
        """
        Reranks the run in terms of a specific method and tradeoff value.

        Args:
            method (str): The type of method to rerank by.
            k (int): Number of recommendations to rerank.
            tradeoff (float): Amount of relevance to maintain.
            distance (Distance): Defines how item distances are measured.

        Returns:
            RunFile: Re-ordered data of the originial run.
        """
        # Rerank each user's recommendations within the run.
        reranked_df = self.df.groupby("user_id")[["movie_id", "score"]].apply(
            self._rerank_user_group, method, k, tradeoff, distance,
        ).reset_index(drop=True)

        algo_name = f"{self.algorithm}-{k}-{tradeoff}"
        reranked_df = self._add_constant_columns(reranked_df, algo_name)
        return RunFile(df=reranked_df)


    def add_rrf_scores(self) -> "RunFile":
        """
        Updates the score column with the calculated RRF scores for all items
        in the run.

        Returns:
            RunFile: Same format as initial RunFile except with update scores.
        """
        k = 60
        rrf_df = self.df.copy()
        rrf_df["score"] = 1 / (rrf_df["rank"] + k)
        return RunFile(df=rrf_df)


    def setup_rrf_file(self, k: int) -> "RunFile":
        """
        Updates an existing RunFile to correctly represent the RRFed data. This
        includes aggregating scores across and reordering.

        Args:
            k (int): Number of recommendations to combine.

        Returns:
            RunFile: The completely formatted RRF RunFile.
        """
        rrf_df = (
            self.df.groupby(["user_id", "movie_id"])["score"].sum()
            .reset_index()
            .sort_values(by=["user_id", "score"], ascending=[True, False])
            .groupby("user_id")
            .head(k)
            .reset_index(drop=True)
        )

        algo_name = "rrf"
        rrf_df = self._add_constant_columns(rrf_df, algo_name)
        return RunFile(df=rrf_df)


    def evaluate(
        self, measure: str, k: int, distance: Distance, user_ids: set[int],
    ) -> MeasureFile:
        """
        Evaluates the run in terms of a specific measure.

        Args:
            measure (str): The type of measure for evaluation.
            k (int): Number of recommendations to measure.
            distance (Distance): Defines how item distances are measured.
            user_ids (set[int]): Set of all users.

        Returns:
            MeasureFile: The measured results of the run.
        """
        # Evaluate each user's recommendations within the run.
        metrics_df = self.df.groupby("user_id")["movie_id"].apply(
            lambda user_group: pd.DataFrame(
                [getattr(Measures(user_group, k, distance), measure)()],
                columns=["score"],
            ).assign(user_id=user_group.name)
        ).reset_index(drop=True)

        # Add default scores of 0 for users missing from run recommendations.
        filled_user_ids = set(metrics_df["user_id"])
        if len(filled_user_ids) != len(user_ids):
            missing_users = user_ids - filled_user_ids
            missing_df = pd.DataFrame(
                {"user_id": list(missing_users), "score": 0}
            )
            metrics_df = pd.concat([metrics_df, missing_df], ignore_index=True)

        # Add constant columns.
        metrics_df["algorithm"] = self.algorithm
        metrics_df["measure"] = measure

        # Calculate average for each metric.
        avg_rows_df = metrics_df.groupby(
            ["algorithm", "measure"]
        )["score"].mean().reset_index()
        avg_rows_df["user_id"] = "all"

        # Combine metric run results.
        results_df = pd.concat([metrics_df, avg_rows_df], ignore_index=True)
        return MeasureFile(df=results_df)
