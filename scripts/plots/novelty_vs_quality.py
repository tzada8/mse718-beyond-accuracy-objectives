from utils.datasets.files.results_file import ResultsFile
from utils.plots.visualizations import Visualizations
from utils.interface.arguments import Arguments
import utils.interface.logging_config


fields = {
    "description": "Creates several plots comparing novelty to quality",
    "example_usage": "python -m scripts.plots.novelty_vs_quality --input results/metrics/combined_interest.txt --output results/plots",
    "args": [
        {"name": "--input", "type": str, "description": "The metrics input file"},
        {"name": "--output", "type": str, "description": "The plots output directory"},
    ]
}


def main(args):
    improved_method_col = "Tradeoff"
    improved_novelty_col = "Novelty"
    improved_compat_col = "Compatibility (p=0.98)"

    results = ResultsFile(args.input)
    results.df = results.df.rename(
        columns={
            "method": improved_method_col,
            "novelty": improved_novelty_col,
            "compatibility-98": improved_compat_col,
        }
    )
    results2 = ResultsFile(df=results.df)

    results.filter({improved_method_col: "1.00 relevance"})

    visualizations = Visualizations(results.df, args.output)
    visualizations.scatter_plot_labelled_points(
        (4, 4),
        improved_compat_col,
        improved_novelty_col,
        "algorithm",
        "novelty-relevance-scatter.png",
        "top right",
    )

    y_order = results2.df[results2.df[improved_method_col] == "1.00 relevance"]
    y_order = list(y_order.sort_values(by=improved_compat_col, ascending=False)["algorithm"].unique())

    visualizations2 = Visualizations(results2.df, args.output)
    visualizations2.side_by_side_heatmap(
        (20, 6),
        improved_method_col,
        "algorithm",
        improved_novelty_col,
        improved_compat_col,
        "novelty-relevance-heatmap.png",
        y_order=y_order,
    )


if __name__ == "__main__":
    main(Arguments(fields).args)
