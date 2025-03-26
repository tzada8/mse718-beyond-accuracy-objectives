import json


class MovieMappingFile:
    def __init__(self, path: str):
        """
        Initializes a MovieMappingFile object either from a file path.

        Args:
            path (str): The path to the file.
        """
        with open(path, "r") as f:
            map = json.load(f)
        self.map = {int(k) if k.isdigit() else k: v for k, v in map.items()}


    def genres_map(self) -> dict[int, set[str]]:
        """
        Converts the entire mapping file to just a mapping of genres.

        Returns:
            dict[int, set[str]]: Map of items to set of genres.
        """
        return {k: set(v["genres"]) for k, v in self.map.items()}
