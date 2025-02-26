import json
from pathlib import Path
from collections import defaultdict
import re
from typing import Iterator


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
        for line in f:
            entry = json.loads(line)

            # Only process TestReport entries
            if entry.get('$report_type') != 'TestReport':
                continue

            nodeid = entry['nodeid']

            yield f"## {nodeid}\n"

            outcome = entry.get('outcome')
            duration = entry.get('duration')

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


# Example usage:
if __name__ == '__main__':
    # Assume report.jsonl exists from running:
    # pytest test_examples.py --report-log=report.jsonl

    log_path = Path('report.jsonl')
    markdown = report_md(log_path)

    # Write markdown to file
    with open('docs/unit_tests.md', 'w') as f:
        f.write(markdown)