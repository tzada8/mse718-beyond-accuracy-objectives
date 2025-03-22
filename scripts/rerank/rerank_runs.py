from utils.datasets.files.rating_file import RatingFile
from utils.datasets.folders.run_folder import RunFolder
from utils.interface.arguments import Arguments
import utils.interface.logging_config
from utils.objectives.distance import Distance


fields = {
    "description": "Reranks recommendations from each run in a directory with a focus on maximizing an objective",
    "example_usage": "python -m scripts.rerank.rerank_runs --runs data/runs --input data/ratings.csv --output results/runs_reranked --objective novelty --k 1000 --tradeoff 0.5",
    "args": [
        {"name": "--runs", "type": str, "description": "The runs input directory or file"},
        {"name": "--input", "type": str, "description": "The movie ratings file"},
        {"name": "--output", "type": str, "description": "The reranked runs output directory"},
        {"name": "--objective", "type": str, "description": "The objective to maximize"},
        {"name": "--k", "type": int, "description": "The top k recommendations to rerank"},
        {"name": "--tradeoff", "type": float, "description": "Tradeoff between relevance and the objective"},
    ]
}


def main(args):
    rating_file = RatingFile(args.input)
    distance = Distance(rating_file.items_rated(), rating_file.num_users)

    runs = RunFolder(args.runs)
    reranked_runs = runs.rerank(args.objective, args.k, args.tradeoff, distance)
    reranked_runs.save(args.output)


if __name__ == "__main__":
    main(Arguments(fields).args)
