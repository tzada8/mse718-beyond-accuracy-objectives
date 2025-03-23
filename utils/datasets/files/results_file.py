from typing import Optional

import pandas as pd

from .base_file import BaseFile
from .measure_file import MeasureFile
from .quality_file import QualityFile


class ResultsFile(BaseFile):
    def __init__(
        self,
        qrel: str,
        measure: str,
        quality: str,
        method: str,
        path: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
        mfile: MeasureFile = None,
        qfile: QualityFile = None,
    ):
        """
        Initializes a ResultsFile by combining a MeasureFile with a QualityFile.

        Args:
            qrel (str): The particular qrel to evaluate.
            measure (str): The objective measure of interest.
            quality (str): The quality measure of interest.
            method (str): The method being combined.
            path (str, optional): The path to the file.
            df (pd.DataFrame, optional): Dataframe containing file data.
            mfile (MeasureFile, optional): The measure file containing objectives.
            qfile (QualityFile, optional): The quality file containing relevances.

        Raises:
            ValueError: If neither `path` or `df` is provided, if both are
            provided, or if data is invalid.
        """
        headers = ["algorithm", "method", measure, quality]
        sep = "\t"

        self.qrel = qrel
        self.measure = measure
        self.quality = quality
        self.method = method

        if mfile is not None and qfile is not None:
            mfile.filter({"measure": self.measure, "user_id": "all"})
            qfile.filter({"measure": self.quality, "user_id": "all", "qrels": qrel})

            df = pd.merge(mfile.df, qfile.df, on=["algorithm"])
            df = df.rename(
                columns={"score_x": self.measure, "score_y": self.quality}
            )
            df["method"] = method
            df = df[headers]
            print(df)

        super().__init__(headers, sep, path=path, df=df)


    @classmethod
    def combine(cls, files: list["ResultsFile"]) -> "ResultsFile":
        """
        Combines a list of ResultFiles into a single file object.

        Args:
            files (list[ResultFile]): The list of files to combine.

        Returns:
            ResultFile: The combined file objects.
        """
        dfs = [f.df for f in files]
        combined_df = pd.concat(dfs, ignore_index=True)
        first_file = files[0]
        return cls(
            first_file.qrel,
            first_file.measure,
            first_file.quality,
            first_file.method,
            df=combined_df,
        )