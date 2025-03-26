from utils.datasets.files.results_file import ResultsFile
from utils.plots.visualizations import Visualizations
from utils.interface.arguments import Arguments
import utils.interface.logging_config


fields = {
    "description": "Creates several plots comparing rrf to the best run",
    "example_usage": "python -m scripts.plots.rrf_vs_best_run --input results/metrics/combined_interest.txt --output results/plots",
    "args": [
        {"name": "--input", "type": str, "description": "The metrics input file"},
        {"name": "--output", "type": str, "description": "The plots output directory"},
    ]
}


def main(args):
    results = ResultsFile(args.input)

    # Tradeoffs leading to insignificant results.
    indiff_lower = 0.51
    indiff_upper = 0.69

    # Best run scores.
    best_run_compat = 0.2894
    best_run_novelty = 0.2791

    results.filter({"algorithm": "RRF"})
    results.df["method"] = results.df["method"].str.replace(" relevance", "").astype(float)
    results.df = results.df.rename(
        columns={"method": "RRF tradeoff", "novelty": "novelty", "compatibility-98": "compatibility"}
    )

    visualizations = Visualizations(results.df, args.output)
    visualizations.line_plot_improvement(
        (5, 4),
        "RRF tradeoff",
        "novelty",
        "compatibility",
        best_run_novelty,
        best_run_compat,
        indiff_lower,
        indiff_upper,
        "rrf-improvement.png",
    )


if __name__ == "__main__":
    main(Arguments(fields).args)
