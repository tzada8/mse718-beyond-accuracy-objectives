import pathlib
import re

from utils.datasets.files.measure_file import MeasureFile
from utils.datasets.files.quality_file import QualityFile
from utils.datasets.files.results_file import ResultsFile
from utils.interface.arguments import Arguments
import utils.interface.logging_config


fields = {
    "description": "Combines metric and quality scores into a single file for plotting",
    "example_usage": "python -m scripts.evaluation.combine_results --metric_dir results/metrics/novelty --quality_dir results/metrics/compatibility --output results/metrics/combined_interest.txt --qrel interest --measure novelty --quality compatibility-98",
    "args": [
        {"name": "--metric_dir", "type": str, "description": "The metric input directory"},
        {"name": "--quality_dir", "type": str, "description": "The quality input directory"},
        {"name": "--output", "type": str, "description": "The combined output file"},
        {"name": "--qrel", "type": str, "description": "The particular qrel to evaluate"},
        {"name": "--measure", "type": str, "description": "The particular measure to evaluate"},
        {"name": "--quality", "type": str, "description": "The particular quality to evaluate"},
    ]
}


def decode_file_name(file_name: str) -> str:
    match = re.search(r"-(\d{2,3})\.txt$", file_name)
    if match:
        str_num = str(match.group(1))
        decimal = int(str_num) / (10 ** (len(str_num) - 1))
        formatted_number = f"{decimal:.2f}"
        return f"{formatted_number} relevance"
    return "Invalid file name"


def main(args):
    dir1 = sorted(pathlib.Path(args.metric_dir).iterdir())
    dir2 = sorted(pathlib.Path(args.quality_dir).iterdir())

    files = []
    for metr_path, qual_path in zip(dir1, dir2):
        method = decode_file_name(str(metr_path))

        mfile = MeasureFile(metr_path)
        qfile = QualityFile(qual_path)
        res_file = ResultsFile.generate(
            args.qrel, args.measure, args.quality, method, mfile, qfile,
        )
        files.append(res_file)

    combined_file = ResultsFile.combine(files)
    combined_file.save(args.output)


if __name__ == "__main__":
    main(Arguments(fields).args)
