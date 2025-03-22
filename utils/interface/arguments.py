import argparse


class Arguments:
    def __init__(self, fields: dict):
        """
        Generate custom commandline arguments based on the provided dictionary
        of fields for running scripts.

        Args:
            fields (dict): A dictionary of arguments.
        """
        parser = argparse.ArgumentParser(
            description=fields["description"],
            epilog=f"Example usage:\n  {fields['example_usage']}",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        for arg in fields["args"]:
            parser.add_argument(
                arg["name"],
                type=arg["type"],
                required=True,
                help=arg["description"],
            )
        self.args = parser.parse_args()
