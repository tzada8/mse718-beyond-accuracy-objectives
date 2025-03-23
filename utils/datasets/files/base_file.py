import os
import pathlib
from typing import Optional, Union

import pandas as pd


class BaseFile:
    def __init__(
        self,
        headers: list[str],
        sep: str,
        path: Optional[str] = None,
        df: Optional[pd.DataFrame] = None,
        output_headers: bool = True,
        header_provided: Optional[Union[str, int]] = "infer",
    ):
        """
        Initializes a BaseFile object either from a file path or a dataframe.

        Args:
            headers (list[str]): The list of columns names.
            sep (str): The separator used if reading from a file.
            path (str, optional): The path to the file.
            df (pd.DataFrame, optional): Dataframe containing file data.
            output_headers (bool, optional): Display headers when saving file.
            header_provided (str, int, optional): If headers in initial file.

        Raises:
            ValueError: If neither `path` or `df` is provided, if both are
            provided, or if data is invalid.
        """
        if path is not None and df is not None:
            ValueError("Both `path` and `df` can not be provided")

        # Read in data either from path or from existing dataframe.
        if path:
            if not os.path.exists(path):
                raise ValueError(f"File does not exist at {path}")

            try:
                self.df = pd.read_csv(
                    path,
                    sep=sep,
                    names=headers,
                    header=header_provided,
                )
            except Exception as e:
                raise ValueError(f"Error reading file at {path}: {e}")
        elif df is not None:
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Provided data must be a pandas DataFrame")
            self.df = df
        else:
            raise ValueError("Either `path` or `df` must be provided")

        self.headers = headers
        self.sep = sep
        self.output_headers = output_headers


    @classmethod
    def combine(cls, files: list["BaseFile"]) -> "BaseFile":
        """
        Combines a list of same type file objects into a single file object.
        Note that BaseFile objects cannot be combined.

        Args:
            files (list[BaseFile]): The list of files to combine.

        Returns:
            BaseFile: The combined file objects.
        """
        dfs = [f.df for f in files]
        combined_df = pd.concat(dfs, ignore_index=True)
        return cls(df=combined_df)


    def filter(self, f: dict[str, str]):
        """
        Applies a mapping of filters in-place.

        Args:
            f (dict[str, str]): Mapping of column name to value filters.
        """
        for column, value in f.items():
            self.df = self.df[self.df[column] == value]


    def save(self, path: str):
        """
        Saves the run at the specified file path.

        Args:
            path (str): The full path to save the file.
        """
        parent_dir = pathlib.Path(path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.df.to_csv(
                path, sep=self.sep, header=self.output_headers, index=False,
            )
        except Exception as e:
            raise ValueError(f"Error saving file at {path}: {e}")
