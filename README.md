# MSE 718: Diversity, Serendipity, and Novelty Impacting Human Preferences in Movie Recommendations

The purpose of this research is to better understand how diversity, serendipity, and novelty impact human interests in the field of movie recommendations.

## Getting Started

### Data Setup

1. Create a new directory at the root called `data`
    ```
    mkdir data
    ```

2. Attain permission and access to the dataset: [MovieLens-32M Extension](https://uwaterlooir.github.io/datasets/ml-32m-extension)

3. Follow the steps in the [ml-32m-extension](https://github.com/UWaterlooIR/ml-32m-extension) repository to prepare the dataset

4. Manually add the generated `ratings.csv` file and `interest.qrels` into the `data` directory

5. Manually add the run results from the 22 different algorithms into the `data` directory

6. At this point, the folder structure should look like:
    ```
    data
    ├── runs
    │   ├── ADMMSLIM.results
    │   ├── Bias.results
    │   └── ...
    │── interest.qrels
    │── ratings.csv
    └── user_ids.txt
    ```

7. Create a new directory at the root called `results`. This will be where all file/plot outputs are stored 
    ```
    mkdir results
    ```

### Environment Setup

1. Create a local virtual environment
    ```
    python3 -m venv .venv
    ```

2. Activate the virtual environment
    ```
    source .venv/bin/activate
    ```

3. Install `requirements` dependencies
    ```
    pip install -r requirements.txt
    ```

## Scripts

Note that all scripts should be run from the root directory.

### Generate RRF Run

1. The following script generates an RRF run based on the initial runs
    ```
    python -m scripts.rerank.rrf --runs data/runs --output results/runs_reranked/rrf.results --k 1000
    ```

### Rerank Runs

1. The following script reranks runs to introduce varying levels of novelty
    ```
    python -m scripts.rerank.rerank_runs_varying_tradeoffs --runs data/runs --input data/ratings.csv --output results/runs_reranked --objective novelty --k 1000 --tradeoffs 11
    ```
    OR
    ```
    python -m scripts.rerank.rerank_runs_varying_tradeoffs --runs results/runs_reranked/rrf.results --input data/ratings.csv --output results/runs_reranked --objective novelty --k 1000 --tradeoffs 11
    ```

### Evaluate Runs

1. The following script evaluates the quality/relevance of a all runs within a directory recommendations
    ```
    scripts/evaluation/calculate_compatibility.sh results/metrics/compatibility results/runs_reranked
    ```

2. The following script evaluates the novelty of each run's recommendations
    ```
    python -m scripts.evaluation.run_metrics_varying_tradeoffs --runs results/runs_reranked --input data/ratings.csv --users data/user_ids.txt --output results/metrics --metric novelty --k 100
    ```
3. The following script evaluates the diversity or serendipity of each run's recommendations
    ```
    python -m scripts.plots.objective_vs_quality --objective results/metrics/diversity.txt --quality results/metrics/compatibility/p2_cranfield_k_100_tradeoff_10.txt --output results/plots/objectives --measure diversity
    ```

4. The following script combines the quality and novelty scores for plotting
    ```
    python -m scripts.evaluation.combine_results --metric_dir results/metrics/novelty --quality_dir results/metrics/compatibility --output results/metrics/combined_interest.txt --qrel interest --measure novelty --quality compatibility-98
    ```

### Visualizations

1. The following script plots the relationship between relevance and novelty
    ```
    python -m scripts.plots.novelty_vs_quality --input results/metrics/combined_interest.txt --output results/plots
    ```

2. The following script plots the relationship between relevance and diversity/serendipity
    ```
    python -m scripts.plots.objective_vs_quality --objective results/metrics/diversity.txt --quality results/metrics/compatibility/p2_cranfield_k_100_tradeoff_10.txt --output results/plots/objectives --measure diversity
    ```

3. The following script plots the RRF run to the best run to determine amount of possible novelty improvement
    ```
    python -m scripts.plots.rrf_vs_best_run --input results/metrics/combined_interest.txt --output results/plots
    ```

4. The following script compares the best run to varying RRF tradeoffs to determine the significance distribution
    ```
    python -m scripts.plots.rrf_significance --best_run results/metrics/compatibility/p2_cranfield_k_100_tradeoff_08.txt --rrf results/metrics/rrf-101/compatibility --output results/plots/rrf-101/rrf_significance.txt --metric compatibility-98
    ```
