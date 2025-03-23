from typing import Optional

import pandas as pd

from .base_file import BaseFile
from .measure_file import MeasureFile
from .quality_file import QualityFile


class ResultsFile(BaseFile):
    def __init__(
        self,
        path: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
    ):
        """
        Initializes a ResultsFile object either from a file path or a dataframe.

        Args:
            path (str, optional): The path to the file.
            df (pd.DataFrame, optional): Dataframe containing file data.

        Raises:
            ValueError: If neither `path` or `df` is provided, if both are
            provided, or if data is invalid.
        """
        headers = ["algorithm", "method", "novelty", "compatibility-98"]
        sep = "\t"
        super().__init__(headers, sep, path=path, df=df, header_provided=0)


    @classmethod
    def generate(
        cls,
        qrel: str,
        measure: str,
        quality: str,
        method: str,
        mfile: MeasureFile,
        qfile: QualityFile,
    ) -> "ResultsFile":
        """
        Initializes a ResultsFile by combining a MeasureFile with a QualityFile.

        Args:
            qrel (str): The particular qrel to evaluate.
            measure (str): The objective measure of interest.
            quality (str): The quality measure of interest.
            method (str): The method being combined.
            mfile (MeasureFile): The measure file containing objectives.
            qfile (QualityFile): The quality file containing relevances.
        """
        mfile.filter({"measure": measure, "user_id": "all"})
        qfile.filter({"measure": quality, "user_id": "all", "qrels": qrel})

        df = pd.merge(mfile.df, qfile.df, on=["algorithm"])
        df = df.rename(
            columns={"score_x": measure, "score_y": quality}
        )
        df["method"] = method
        df = df[["algorithm", "method", measure, quality]]
        return cls(df=df)
