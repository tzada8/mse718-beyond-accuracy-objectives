import pathlib

import numpy as np

from adjustText import adjust_text
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
from scipy.stats import kendalltau
import seaborn as sns


class Visualizations:
    def __init__(self, df: pd.DataFrame, output_dir: str):
        """
        Create visualizations for a given dataset.

        Args:
            df (pd.DataFrame): The data to be visualized.
            output_dir (str): The base directory to store the generated visualizations.
        """
        self.df = df
        self.palette = "Blues"
        self.alt_palette = "Reds"

        self.output_dir = output_dir
        pathlib.Path(self.output_dir).mkdir(parents=True, exist_ok=True)


    def _kendall_corr(self, data1: pd.Series, data2: pd.Series) -> str:
        """
        Calculates Kendall's Tau and corresponding p-value preparing the text.

        Args:
            data1 (pd.Series): The first set of data.
            data2 (pd.Series): The second set of data.

        Returns:
            str: The textual information containing the Kendall correlation.
        """
        kendall_corr, p_value = kendalltau(data1, data2)
        p_value_text = f"p<0.001" if p_value < 0.001 else f"p={p_value:.3f}"

        corr_text = f"Kendall's Tau={kendall_corr:.2f}\n({p_value_text})"
        return corr_text


    def _custom_sort_order(
        self, x: str, y: str, x_order: list = None, y_order: list = None,
    ) -> pd.DataFrame:
        """
        Applies custom sort ordering for axes if provided.

        Args:
            x (str): The column name for the x-axis.
            y (str): The column name for the y-axis.
            x_order (list): Custom categorical variable ordering if required.
            y_order (list): Custom categorical variable ordering if required.

        Returns:
            pd.DataFrame: Same data with custom sorting applied.
        """
        prep_df = self.df.copy()
        if x_order:
            prep_df[x] = pd.Categorical(prep_df[x], categories=x_order, ordered=True)
        if y_order:
            prep_df[y] = pd.Categorical(prep_df[y], categories=y_order, ordered=True)
        return prep_df


    def _add_axes(self, x: str, y: str, label: str = None, rotate_x: bool = False):
        """
        Adds titles to the axes and a legend if a label is provided.

        Args:
            x (str): The column name for the x-axis.
            y (str): The column name for the y-axis.
            label (str): The column name for the label.
            rotate_x (bool): True if x-axis labels should be rotated. False
            otherwise (default: False).
        """
        plt.xlabel(x)
        plt.ylabel(y)

        # Rotate x labels to improve readability if too cluttered.
        rotate_amt = 45 if rotate_x else 0
        x_ha = "right" if rotate_x else "center"
        plt.xticks(rotation=rotate_amt, ha=x_ha)

        if label:
            plt.legend(title=label)


    def _save_image(self, file_name: str):
        """
        Saves a plot with the provided file name.

        Args:
            file_name (str): The name of the file to be saved.
        """
        output_path = f"{self.output_dir}/{file_name}"
        plt.savefig(output_path, bbox_inches="tight", dpi=1000)
        plt.close()


    def scatter_plot_labelled_points(
        self,
        fig_size: tuple[int, int],
        x: str,
        y: str,
        label: str,
        file_name: str,
        corr_loc: str = "bottom left", # top left, top right, bottom right
    ):
        """
        Plots a scatter plot of the data, with a label for each point.
        Kendall's Tau is also calculated and displayed on the plot.

        Args:
            fig_size (tuple[int, int]): The dimensions of the plot.
            x (str): The column name for the x-axis.
            y (str): The column name for the y-axis.
            label (str): The column name for the label.
            file_name (str): The name of the file being saved.
            corr_loc (str, optional): The location for the correlation box.
        """
        plt.figure(figsize=fig_size)
        sns.scatterplot(x=x, y=y, data=self.df, s=35, color="red")

        # Add label to each point.
        texts = [
            plt.text(row[x], row[y], row[label], fontsize=6.5)
            for _, row in self.df.iterrows()
        ]
        adjust_text(
            texts,
            only_move={"points": "y", "texts": "y"},
            arrowprops=dict(arrowstyle="->", color="black", lw=0.5),
        )

        # Location and text to display Kendall's correlation.
        corr_text = self._kendall_corr(self.df[x], self.df[y])
        corr_pos = corr_loc.split(" ")
        va = corr_pos[0]
        ha = corr_pos[1]
        corr_x = self.df[x].max() if ha == "right" else self.df[x].min()
        corr_y = self.df[y].max() if va == "top" else self.df[y].min()
        plt.text(
            x=corr_x,
            y=corr_y,
            s=corr_text,
            fontsize=8,
            verticalalignment=va,
            horizontalalignment=ha,
            bbox=dict(facecolor="white", alpha=0.5, edgecolor="gray"),
        )

        plt.grid(alpha=0.3)
        self._add_axes(x, y)
        self._save_image(file_name)


    def side_by_side_heatmap(
        self,
        fig_size: tuple[int, int],
        x: str,
        y: str,
        label1: str,
        label2: str,
        file_name: str,
        text_format: str = None,
        x_order: list = None,
        y_order: list = None,
    ):
        """
        Plots 2 heatmaps side-by-side with the same x and y columns, but with
        different values in the cells.

        Args:
            fig_size (tuple[int, int]): The dimensions of the plot.
            x (str): The column name for the x-axis.
            y (str): The column name for the y-axis.
            label1 (str): The column name for the first heatmap.
            label2 (str): The column name for the second heatmap.
            file_name (str): The name of the file being saved.
            text_format (str): Text formatting for each cell if provided.
            x_order (list): Custom categorical variable ordering if required.
            y_order (list): Custom categorical variable ordering if required.
        """
        df = self._custom_sort_order(x, y, x_order, y_order)
        df1 = df.pivot(index=y, columns=x, values=label1)
        df2 = df.pivot(index=y, columns=x, values=label2)

        # Display cell values if provided.
        annot = True
        text_format = text_format
        if text_format is None:
            annot = False
            text_format = None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_size)
        fig.subplots_adjust(wspace=0.01)

        # Plot first heatmap.
        sns.heatmap(
            df1,
            cmap=self.palette,
            annot=annot,
            fmt=text_format,
            ax=ax1,
            cbar=False,
        )
        fig.colorbar(
            ax1.collections[0],
            ax=ax1,
            location="left",
            use_gridspec=False,
            pad=0.2,
            label=label1,
        )

        # Plot second heatmap.
        sns.heatmap(
            df2,
            cmap=self.alt_palette,
            annot=annot,
            fmt=text_format,
            ax=ax2,
            cbar=False,
        )
        fig.colorbar(
            ax2.collections[0],
            ax=ax2,
            location="right",
            use_gridspec=False,
            pad=0.2,
            label=label2,
        )

        # Adjust axes.
        ax2.yaxis.tick_right()
        ax2.tick_params(rotation=0)

        ax1.set_xlabel(x)
        ax1.set_ylabel(None)

        ax2.set_xlabel(x)
        ax2.set_ylabel(None)

        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha="right")

        self._save_image(file_name)


    def line_plot_improvement(
        self,
        fig_size: tuple[int, int],
        x: str,
        l1: str,
        l2: str,
        best_other_l1: float,
        best_other_l2: float,
        indiff_lower: float,
        indiff_upper: float,
        file_name: str,
    ):
        """
        Plots a line graph depicting how much of a shift still resolves in
        improvement.

        Args:
            fig_size (tuple[int, int]): The dimensions of the plot.
            x (str): The column name for the x-axis.
            l1 (str): The column name for the first line.
            l2 (str): The column name for the second line.
            best_other_l1 (float): The best value for l1 from other run.
            best_other_l2 (float): The best value for l2 from other run.
            indiff_lower (float): The lower bound for insignificance.
            indiff_upper (float): The upper bound for insignificance.
            file_name (str): The name of the file being saved.
        """
        # Mappings.
        line_map = {
            f"RRF - {l2}": "#A50F15",
            f"RRF - {l1}": "#08519C",
            "": "#FAFCFD",
            f"Best algorithm - {l2}": "#FB6A4A",
            f"Best algorithm - {l1}": "#6BAED6",
        }
        colour_map = {
            "RRF is better": "#B3D4E6",
            "No difference": "#E8E8E8",
            "Best algorithm is better": "#FBB4B4",
        }

        # Interpolate l1 line.
        l1_interp_func = interp1d(self.df[x], self.df[l1], kind="linear", fill_value="extrapolate")
        l1_intersect_min = l1_interp_func(indiff_lower)
        l1_intersect_max = l1_interp_func(indiff_upper)

        plt.figure(figsize=fig_size)

        # Plot significance ranges.
        plt.axvspan(indiff_upper, 1, color=colour_map["RRF is better"], alpha=0.3)
        plt.axvspan(indiff_lower, indiff_upper, color=colour_map["No difference"], alpha=0.3)
        plt.axvspan(0, indiff_lower, color=colour_map["Best algorithm is better"], alpha=0.3)

        plt.plot(self.df[x], self.df[l2], linestyle="-", label=f"RRF - {l2}", color =line_map[f"RRF - {l2}"])
        plt.plot(self.df[x], self.df[l1], linestyle="-", label=f"RRF - {l1}", color=line_map[f"RRF - {l1}"])
        plt.plot(self.df[x], [best_other_l2] * len(self.df[x]), linestyle="-", label=f"Best algorithm - {l2}", color=line_map[f"Best algorithm - {l2}"])
        plt.plot(self.df[x], [best_other_l1] * len(self.df[x]), linestyle="-", label=f"Best algorithm - {l1}", color=line_map[f"Best algorithm - {l1}"])

        x_shift = 0.012
        y_shift = 0.0075

        # Mark intersections.
        plt.scatter(indiff_lower, l1_intersect_min, color="black", s=25, zorder=3)
        plt.annotate(f"{l1_intersect_min:.2f}", (indiff_lower - x_shift, l1_intersect_min - y_shift), fontsize=7.5)

        plt.scatter(indiff_upper, l1_intersect_max, color="black", s=25, zorder=3)
        plt.annotate(f"{l1_intersect_max:.2f}", (indiff_upper - x_shift, l1_intersect_max - y_shift), fontsize=7.5)

        self._add_axes(x, "Score")
        plt.xticks(self.df[x])
        plt.xlim(0, 1)
        plt.xticks(np.arange(0, 1.1, 0.1))

        # Create custom legend.
        legend_lines = [
            Line2D([0], [0], color=line_map[key], lw=1, label=key) for key in line_map
        ]
        legend_patches = [
            Patch(color=colour_map[key], label=key) for key in colour_map
        ]

        lines_legend = plt.legend(
            handles=legend_lines,
            loc="upper left",
            title="RRF vs Best algorithm",
            title_fontproperties={"weight": "bold", "size": 9},
            alignment="left",
            fontsize=8.5,
        )
        plt.legend(
            handles=legend_patches,
            loc="lower left",
            title="Statistical significance\n(p < 0.01)",
            title_fontproperties={"weight": "bold", "size": 9},
            alignment="left",
            fontsize=8.5,
        )
        plt.gca().add_artist(lines_legend)
        plt.gca().invert_xaxis()

        self._save_image(file_name)
