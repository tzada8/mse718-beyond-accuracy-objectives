import pathlib

from tqdm import tqdm

from utils.datasets.files.rating_file import RatingFile
from utils.datasets.files.run_file import RunFile
from utils.interface.arguments import Arguments
from utils.objectives.distance import Distance


fields = {
    "description": "Reranks runs to maximize an objective",
    "args": [
        {"name": "--runs", "type": str, "description": "The runs input directory"},
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

    for run in tqdm(pathlib.Path(args.runs).iterdir()):
        run_file = RunFile(run)
        reranked_run_file = run_file.rerank(
            args.objective, args.k, args.tradeoff, distance,
        )
        reranked_run_path = f"{args.output}/{reranked_run_file.algorithm}.results"
        reranked_run_file.save(reranked_run_path)


"""
This script reranks the recommendations from each run with a focus on
maximizing an objective. An example usage of the script from the root directory
includes:

python -m scripts.rerank.rerank_runs --runs data/runs --input data/ratings.csv --output results/runs-reranked --objective novelty --k 1000 --tradeoff 0.5
"""
if __name__ == "__main__":
    main(Arguments(fields).args)
