import json
from pathlib import Path
from collections import defaultdict
import re


def parse_reportlog(log_path: str):
    """Parse pytest-reportlog output into structured format."""
    tests = defaultdict(dict)

    with open(log_path) as f:
        for line in f:
            entry = json.loads(line)

            # Only process TestReport entries
            if entry.get('$report_type') != 'TestReport':
                continue

            nodeid = entry['nodeid']

            # Store test outcome
            if 'outcome' in entry:
                tests[nodeid]['outcome'] = entry['outcome']

            # Store duration
            if 'duration' in entry:
                tests[nodeid]['duration'] = entry['duration']

            # Convert user_properties to dict
            if 'user_properties' in entry:
                props = dict(entry['user_properties'])
                tests[nodeid]['properties'] = props

            # Store parameters from nodeid
            # Extract from something like: test_search_ontology[sqlite:obo:bfo-3D spatial-10-expected0]
            if '[' in nodeid:
                param_str = nodeid[nodeid.index('[') + 1:nodeid.rindex(']')]
                # You might want to customize this parsing based on your parameter format
                tests[nodeid]['parameters'] = param_str

    return tests


def generate_markdown(tests):
    """Convert test results to markdown documentation."""
    md = []
    md.append("# Test Results Documentation\n")

    # Group tests by their base function name
    test_groups = defaultdict(list)
    for nodeid, data in tests.items():
        # Split nodeid into parts: path::function[params]
        base_name = nodeid.split('::')[1].split('[')[0] if '[' in nodeid else nodeid.split('::')[1]
        test_groups[base_name].append((nodeid, data))

    for base_name, group in test_groups.items():
        md.append(f"## {base_name}\n")

        # Create table for all test runs
        md.append("### Test Runs\n")

        # Headers: Parameters, Properties, Duration, Outcome
        md.append('| Parameters | Properties | Duration (s) | Outcome |')
        md.append('|------------|------------|-------------|---------|')

        for nodeid, data in group:
            # Extract parameters from nodeid
            params = nodeid.split('[')[1].rstrip(']') if '[' in nodeid else ''

            # Format properties
            props = data.get('properties', {})
            props_str = '; '.join(f"{k}: {v}" for k, v in props.items())

            # Format duration
            duration = f"{data.get('duration', 0):.3f}"

            row = [
                params,
                props_str,
                duration,
                data.get('outcome', '')
            ]

            md.append('| ' + ' | '.join(str(cell) for cell in row) + ' |')

        md.append('')
    return '\n'.join(md)

# Example usage:
if __name__ == '__main__':
    # Assume report.jsonl exists from running:
    # pytest test_examples.py --report-log=report.jsonl

    log_path = Path('report.jsonl')
    tests = parse_reportlog(log_path)
    markdown = generate_markdown(tests)

    # Write markdown to file
    with open('docs/unit_tests.md', 'w') as f:
        f.write(markdown)