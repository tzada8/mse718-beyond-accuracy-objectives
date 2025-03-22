from utils.datasets.folders.run_folder import RunFolder
from utils.interface.arguments import Arguments
import utils.interface.logging_config


fields = {
    "description": "Performs reciprocal rank fusion (RRF) for all runs in a single directory",
    "example_usage": "python -m scripts.rerank.rrf --runs data/runs --output results/runs-reranked/rrf.results --k 1000",
    "args": [
        {"name": "--runs", "type": str, "description": "The runs input directory"},
        {"name": "--output", "type": str, "description": "The RRF run output file"},
        {"name": "--k", "type": int, "description": "The top k recommendations to combine"},
    ]
}


def main(args):
    runs = RunFolder(args.runs)
    rrf_run = runs.rrf(args.k)
    rrf_run.save(args.output)


if __name__ == "__main__":
    main(Arguments(fields).args)
