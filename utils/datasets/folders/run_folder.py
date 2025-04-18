import logging
import os
import pathlib
from typing import Optional

from tqdm import tqdm

from ..files.run_file import RunFile
from ..files.measure_file import MeasureFile
from utils.objectives.distance import Distance


logger = logging.getLogger(__name__)


class RunFolder:
    def __init__(
        self,
        path: Optional[str] = None,
        runs: Optional[list[RunFile]] = None,
    ):
        """
        Initializes a RunFolder object from a folder/file path, containing many
        RunFile objects.

        Args:
            path (str, optional): The path to the folder or file.
            runs (list[RunFile], optional): List containing RunFiles.

        Raises:
            ValueError: If neither `path` or `runs` is provided, if both are
            provided, or if data is invalid.
        """
        if path is not None and runs is not None:
            ValueError("Both `path` and `runs` can not be provided")

        # Read in data either from path or from existing list.
        if path:
            logger.info(f"Initializing runs from {path}")

            input_path = pathlib.Path(path)
            if input_path.is_file():
                self.runs = [RunFile(path)]
            elif input_path.is_dir():
                self.runs = [
                    RunFile(run) for run in input_path.iterdir() if run.is_file()
                ]
            else:
                raise ValueError(f"{path} is neither a valid file nor directory")
        elif runs is not None:
            if not isinstance(runs, list):
                raise ValueError("Provided data must be a list of RunFiles")
            self.runs = runs
        else:
            raise ValueError("Either `path` or `runs` must be provided")


    def rerank(
        self, method: str, k: int, tradeoff: float, distance: Distance,
    ) -> "RunFolder":
        """
        Reranks all RunFiles in the RunFolder.

        Args:
            method (str): The type of method to rerank by.
            k (int): Number of recommendations to rerank.
            tradeoff (float): Amount of relevance to maintain.
            distance (Distance): Defines how item distances are measured.

        Returns:
            RunFile: A new RunFolder instance with reranked RunFiles.
        """
        tradeoff_disp = round(1 - tradeoff, 2)
        logger.info(f"Reranking {k} items per user with {tradeoff_disp} {method}")
        reranked_runs = [
            run.rerank(method, k, tradeoff, distance)
            for run in tqdm(self.runs)
        ]
        return RunFolder(runs=reranked_runs)


    def evaluate(
        self, measure: str, k: int, distance: Distance, user_ids: set[int],
    ) -> MeasureFile:
        """
        Evaluates all RunFiles in the RunFolder.

        Args:
            measure (str): The type of measure for evaluation.
            k (int): Number of recommendations to measure.
            distance (Distance): Defines how item distances are measured.
            user_ids (set[int]): Set of all users.

        Returns:
            MeasureFile: The measured results across all runs.
        """
        logger.info(f"Measuring top {k} items per user for {measure}")
        measured_runs = [
            run.evaluate(measure, k, distance, user_ids)
            for run in tqdm(self.runs)
        ]
        return MeasureFile.combine(measured_runs)


    def rrf(self, k: int) -> RunFile:
        """
        Performs reciprocal rank fusion (RRF) across all runs.

        Args:
            k (int): Number of recommendations to combine.

        Returns:
            RunFile: A single RunFile of the combined runs.
        """
        logger.info(f"Performing RRF to combine top {k} items per user")
        rrf_runs = [run.add_rrf_scores() for run in tqdm(self.runs)]
        rrf_file = RunFile.combine(rrf_runs)
        return rrf_file.setup_rrf_file(k)


    def save(self, path: str):
        """
        Saves the runs at the specified folder path.

        Args:
            path (str): The directory to save the runs.
        """
        logger.info(f"Saving runs to {path}")
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        for run in self.runs:
            run.save(f"{path}/{run.algorithm}.results")
