from utils.datasets.files.measure_file import MeasureFile
from utils.datasets.files.quality_file import QualityFile
from utils.datasets.files.results_file import ResultsFile
from utils.plots.visualizations import Visualizations
from utils.interface.arguments import Arguments
import utils.interface.logging_config


fields = {
    "description": "Creates a plot comparing an objective to quality",
    "example_usage": "python -m scripts.plots.objective_vs_quality --objective results/metrics/diversity.txt --quality results/metrics/compatibility/p2_cranfield_k_100_tradeoff_10.txt --output results/plots/objectives --measure diversity",
    "args": [
        {"name": "--objective", "type": str, "description": "The objective input file"},
        {"name": "--quality", "type": str, "description": "The quality input file"},
        {"name": "--output", "type": str, "description": "The plots output directory"},
        {"name": "--measure", "type": str, "description": "The particular measure to evaluate"},
    ]
}


def main(args):
    mfile = MeasureFile(args.objective)
    qfile = QualityFile(args.quality)
    results = ResultsFile.generate(
        "interest",
        args.measure,
        "compatibility-98",
        "1.00 relevance",
        mfile,
        qfile,
    )

    improved_method_col = "Tradeoff"
    improved_col = f"{args.measure}".capitalize()
    improved_compat_col = "Compatibility (p=0.98)"

    results.df = results.df.rename(
        columns={
            "method": improved_method_col,
            args.measure: improved_col,
            "compatibility-98": improved_compat_col,
        }
    )
    results.filter({improved_method_col: "1.00 relevance"})
    results.df[[improved_col, improved_compat_col]] = results.df[[improved_col, improved_compat_col]].astype(float)

    visualizations = Visualizations(results.df, args.output)
    visualizations.scatter_plot_labelled_points(
        (5, 5),
        improved_compat_col,
        improved_col,
        "algorithm",
        f"{args.measure}-relevance-scatter.png",
        "top right",
    )


if __name__ == "__main__":
    main(Arguments(fields).args)
