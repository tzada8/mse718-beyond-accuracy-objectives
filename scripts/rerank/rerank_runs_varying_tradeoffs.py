import numpy as np

from utils.datasets.files.rating_file import RatingFile
from utils.datasets.folders.run_folder import RunFolder
from utils.interface.arguments import Arguments
import utils.interface.logging_config
from utils.objectives.distance import Distance


fields = {
    "description": "Reranks recommendations from each run in a directory with a focus on maximizing an objective across varying tradeoffs",
    "example_usage": "python -m scripts.rerank.rerank_runs_varying_tradeoffs --runs data/runs --input data/ratings.csv --output results/runs-reranked --objective novelty --k 1000 --tradeoffs 11",
    "args": [
        {"name": "--runs", "type": str, "description": "The runs input directory or file"},
        {"name": "--input", "type": str, "description": "The movie ratings file"},
        {"name": "--output", "type": str, "description": "The reranked runs output directory"},
        {"name": "--objective", "type": str, "description": "The objective to maximize"},
        {"name": "--k", "type": int, "description": "The top k recommendations to rerank"},
        {"name": "--tradeoffs", "type": int, "description": "The number of equally spaced tradeoffs from 0-1"},
    ]
}


def main(args):
    rating_file = RatingFile(args.input)
    distance = Distance(rating_file.items_rated(), rating_file.num_users)

    tradeoffs = np.linspace(0, 1, args.tradeoffs)
    for tradeoff in tradeoffs:
        runs = RunFolder(args.runs)
        reranked_runs = runs.rerank(args.objective, args.k, tradeoff, distance)

        tradeoff_str = str(round(tradeoff, 2)).replace(".", "")
        subdir = f"{args.output}/k-{args.k}-tradeoff-{tradeoff_str}"
        reranked_runs.save(subdir)

        # Calculate RRF at each reranked tradeoff.
        RunFolder(runs=[reranked_runs.rrf(args.k)]).save(subdir)


if __name__ == "__main__":
    main(Arguments(fields).args)
