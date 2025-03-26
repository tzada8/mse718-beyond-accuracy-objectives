from typing import Optional

import pandas as pd

from .base_file import BaseFile


class RatingFile(BaseFile):
    def __init__(
        self,
        path: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
    ):
        """
        Initializes a RatingFile object either from a file path or a dataframe.

        Args:
            path (str, optional): The path to the file.
            df (pd.DataFrame, optional): Dataframe containing file data.

        Raises:
            ValueError: If neither `path` or `df` is provided, if both are
            provided, or if data is invalid.
        """
        headers = ["user_id", "movie_id", "rating", "timestamp"]
        sep = ","
        super().__init__(headers, sep, path=path, df=df, header_provided=0)

        self.num_users = len(self.df["user_id"].unique())


    def items_rated(self) -> dict[int, list[int]]:
        """
        Creates a mapping of each item to all the users who rated that item.

        Returns:
            dict[int, list[int]]: Map of items to users who rated it.
        """
        return self.df.groupby("movie_id")["user_id"].apply(list).to_dict()


    def user_ratings(self) -> dict[int, list[int]]:
        """
        Creates a mapping of each user to all the items they rated.

        Returns:
            dict[int, list[int]]: Map of users to items they rated.
        """
        return self.df.groupby("user_id")["movie_id"].apply(list).to_dict()
