from typing import Optional

import pandas as pd

from .base_file import BaseFile


class MeasureFile(BaseFile):
    def __init__(
        self,
        path: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
    ):
        """
        Initializes a MeasureFile object either from a file path or a dataframe.

        Args:
            path (str, optional): The path to the file.
            df (pd.DataFrame, optional): Dataframe containing file data.

        Raises:
            ValueError: If neither `path` or `df` is provided, if both are
            provided, or if data is invalid.
        """
        headers = ["algorithm", "measure", "user_id", "score"]
        sep = "\t"
        super().__init__(headers, sep, path=path, df=df)


    def rearrange(self):
        """
        Rearranges this MeasureFile's data in-place. This includes re-ordering
        the columns and sorting the data.
        """
        self.df["score"] = self.df["score"].round(4)
        self.df = self.df[self.headers]
        self.df = self.df.sort_values(by=["algorithm", "measure", "user_id"])
