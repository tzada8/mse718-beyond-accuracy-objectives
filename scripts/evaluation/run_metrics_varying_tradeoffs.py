import pathlib

from utils.datasets.files.rating_file import RatingFile
from utils.datasets.files.user_ids_file import UserIdsFile
from utils.datasets.folders.run_folder import RunFolder
from utils.interface.arguments import Arguments
import utils.interface.logging_config
from utils.objectives.distance import Distance


fields = {
    "description": "Evaluates specified metric across runs for each subdirectory in the provided directory",
    "example_usage": "python -m scripts.evaluation.run_metrics_varying_tradeoffs --runs results/runs_reranked --input data/ratings.csv --users data/user_ids.txt --output results/metrics --metric novelty --k 100",
    "args": [
        {"name": "--runs", "type": str, "description": "The runs main directory"},
        {"name": "--input", "type": str, "description": "The movie ratings file"},
        {"name": "--users", "type": str, "description": "The list of users file"},
        {"name": "--output", "type": str, "description": "The metric runs output directory"},
        {"name": "--metric", "type": str, "description": "The metric to evaluate"},
        {"name": "--k", "type": int, "description": "The top k recommendations to evaluate"},
    ]
}


def main(args):
    rating_file = RatingFile(args.input)
    distance = Distance(rating_file.items_rated(), {}, {}, rating_file.num_users)

    user_ids = UserIdsFile(args.users).user_ids

    for run_dir in pathlib.Path(args.runs).iterdir():
        dir_name = str(run_dir).split("/")[-1]

        runs = RunFolder(run_dir)
        measured_runs = runs.evaluate(args.metric, args.k, distance, user_ids)
        measured_runs.rearrange()

        measured_runs_path = f"{args.output}/{args.metric}/metric_{dir_name}.txt"
        measured_runs.save(measured_runs_path)


if __name__ == "__main__":
    main(Arguments(fields).args)
