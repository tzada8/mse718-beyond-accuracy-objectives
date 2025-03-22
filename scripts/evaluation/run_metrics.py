import pathlib

from tqdm import tqdm

from utils.datasets.measure_file import MeasureFile
from utils.datasets.rating_file import RatingFile
from utils.datasets.run_file import RunFile
from utils.datasets.user_ids_file import UserIdsFile
from utils.interface.arguments import Arguments
from utils.objectives.distance import Distance

fields = {
    "description": "Evaluates specified metric across runs",
    "args": [
        {"name": "--runs", "type": str, "description": "The runs input directory"},
        {"name": "--input", "type": str, "description": "The movie ratings file"},
        {"name": "--users", "type": str, "description": "The list of users file"},
        {"name": "--output", "type": str, "description": "The metric runs output file"},
        {"name": "--metric", "type": str, "description": "The metric to evaluate"},
        {"name": "--k", "type": int, "description": "The top k recommendations to evaluate"},
    ]
}

def main(args):
    rating_file = RatingFile(args.input)
    distance = Distance(rating_file.items_rated(), rating_file.num_users)

    user_ids = UserIdsFile(args.users).user_ids

    results = None
    for run in tqdm(pathlib.Path(args.runs).iterdir()):
        run_file = RunFile(run)
        measured_run_file = run_file.evaluate(
            args.metric, args.k, distance, user_ids,
        )
        results = measured_run_file.combine(results)

    results.rearrange()
    results.save(args.output)


"""
This script evaluates the specified metric for each run. An example usage of the
script from the root directory includes:

python -m scripts.evaluation.run_metrics --runs results/runs-reranked --input data/ratings.csv --users data/user_ids.txt --output results/metrics/metrics.txt --metric novelty --k 100
"""
if __name__ == "__main__":
    main(Arguments(fields).args)
