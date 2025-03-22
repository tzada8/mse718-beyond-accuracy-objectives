# MSE 718: Novelty Impacting Human Preferences in Movie Recommendations

The purpose of this research is to better understand how novelty/familiarity impacts human interests in the field of movie recommendations.

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

6. Create a new directory at the root called `results`
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
