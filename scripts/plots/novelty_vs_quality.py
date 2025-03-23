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
    results = ResultsFile(args.input)
    results2 = ResultsFile(df=results.df)

    results.filter({"method": "1.0 relevance"})

    visualizations = Visualizations(results.df, args.output)
    visualizations.scatter_plot_labelled_points(
        (5, 5),
        "compatibility-98",
        "novelty",
        "algorithm",
        "novelty-relevance-scatter.png",
        "top right",
    )

    y_order = results2.df[results2.df["method"] == "0.0 relevance"]
    y_order = list(y_order.sort_values(by="novelty")["algorithm"].unique())

    visualizations2 = Visualizations(results2.df, args.output)
    visualizations2.side_by_side_heatmap(
        (20, 6),
        "method",
        "algorithm",
        "novelty",
        "compatibility-98",
        "novelty-relevance-heatmap.png",
        ".2f",
        y_order=y_order,

    )


if __name__ == "__main__":
    main(Arguments(fields).args)
