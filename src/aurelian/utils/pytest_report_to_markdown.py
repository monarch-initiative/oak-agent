import json
from pathlib import Path
from collections import defaultdict
import re
from typing import Iterator

import click


def report_md(log_path: str) -> str:
    return '\n'.join(list(report_md_iter(log_path)))

def report_md_iter(log_path: str) -> Iterator[str]:
    """
    Parse pytest-reportlog output into structured format.

    Args:
        log_path:

    Returns:

    """

    with open(log_path) as f:
        outcome = None
        duration = None
        for line in f:
            entry = json.loads(line)

            # Only process TestReport entries
            if entry.get('$report_type') != 'TestReport':
                continue

            nodeid = entry['nodeid']
            outcome = entry.get('outcome')
            duration = entry.get('duration')

            if not outcome:
                continue

            yield f"## {nodeid}\n"



            for p in entry.get('user_properties', []):
                k = p[0]
                v = p[1]

                yield f"### {k}\n\n"
                yield f"{v}\n"

        yield "## Stats\n\n"
        if outcome:
            yield f"* Outcome: {outcome}\n"
        if duration:
            yield f"* Duration: {duration}\n"



@click.command()
@click.argument("log_path", type=click.Path(exists=True))
def main(log_path: str):
    markdown = report_md(log_path)
    print(markdown)

if __name__ == "__main__":
    main()