import pathlib
import re

import pandas as pd
import scipy.stats as stats
from tqdm import tqdm

from utils.datasets.files.quality_file import QualityFile
from utils.interface.arguments import Arguments
import utils.interface.logging_config


fields = {
    "description": "Creates several plots comparing rrf to the best run",
    "example_usage": "python -m scripts.plots.rrf_significance --best_run results/metrics/compatibility/p2_cranfield_k_100_tradeoff_08.txt --rrf results/metrics/rrf-101/compatibility --output results/plots/rrf-101/rrf_significance.txt --metric compatibility-98",
    "args": [
        {"name": "--best_run", "type": str, "description": "The compatibility file containing the best run data"},
        {"name": "--rrf", "type": str, "description": "The directory containing all RRF rerankings"},
        {"name": "--output", "type": str, "description": "The plots output file"},
        {"name": "--metric", "type": str, "description": "The relevance metric to evaluate"},
    ]
}


def decode_file_name(file_name: str) -> str:
    match = re.search(r"_(\d{2,3})\.txt$", file_name)
    if match:
        str_num = str(match.group(1))
        decimal = int(str_num) / (10 ** (len(str_num) - 1))
        formatted_number = f"{decimal:.2f}"
        return f"{formatted_number} relevance"
    return "Invalid file name"


def main(args):
    best_run = QualityFile(args.best_run)
    best_run.filter({"qrels": "interest", "algorithm": "EASE", "measure": args.metric})
    best_run.df = best_run.df[best_run.df["user_id"] != "all"]
    best_run.df["score"] = best_run.df["score"].astype(float)

    headers = ["RRF tradeoff", "best run score", "RRF score", "% improvement", "p-value", "sig (< 0.01)"]
    results_df = pd.DataFrame(columns=headers)

    for rrf_path in tqdm(pathlib.Path(args.rrf).iterdir()):
        tradeoff = decode_file_name(str(rrf_path))

        rrf = QualityFile(rrf_path)
        rrf.filter({"qrels": "interest", "algorithm": "RRF", "measure": args.metric})
        rrf.df = rrf.df[rrf.df["user_id"] != "all"]
        rrf.df["score"] = rrf.df["score"].astype(float)

        # Calculate statistic.
        _, p_value = stats.ttest_rel(best_run.df["score"], rrf.df["score"])
        best_score = best_run.df["score"].mean()
        rrf_score = rrf.df["score"].mean()
        improvement = (rrf_score - best_score) / best_score
        sig = "Yes" if p_value < 0.01 else "No"

        results_df.loc[len(results_df)] = [tradeoff, best_score, rrf_score, improvement, p_value, sig]

    # Save results.
    results_df = results_df.sort_values(by="RRF tradeoff")
    results_df.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main(Arguments(fields).args)
