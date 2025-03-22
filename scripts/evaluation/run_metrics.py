from utils.datasets.files.rating_file import RatingFile
from utils.datasets.files.user_ids_file import UserIdsFile
from utils.datasets.folders.run_folder import RunFolder
from utils.interface.arguments import Arguments
import utils.interface.logging_config
from utils.objectives.distance import Distance


fields = {
    "description": "Evaluates specified metric across runs",
    "example_usage": "python -m scripts.evaluation.run_metrics --runs results/runs_reranked --input data/ratings.csv --users data/user_ids.txt --output results/metrics/metrics.txt --metric novelty --k 100",
    "args": [
        {"name": "--runs", "type": str, "description": "The runs input directory or file"},
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

    runs = RunFolder(args.runs)
    measured_runs = runs.evaluate(args.metric, args.k, distance, user_ids)
    measured_runs.rearrange()
    measured_runs.save(args.output)


if __name__ == "__main__":
    main(Arguments(fields).args)
