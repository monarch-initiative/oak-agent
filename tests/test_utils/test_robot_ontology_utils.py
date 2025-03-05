import pytest
from aurelian.dependencies.workdir import WorkDir
from aurelian.utils.robot_ontology_utils import run_robot_template_command

from tests import OUTPUT_DIR, INPUT_DIR


@pytest.fixture
def test_workdir() -> WorkDir:
    workdir = WorkDir(location=str(OUTPUT_DIR / "robot_test"))
    for f in workdir.list_file_names():
        workdir.delete_file(f)
    input_workdir = WorkDir(location=str(INPUT_DIR / "robot_test"))
    for f in input_workdir.list_file_names():
        workdir.write_file(f, input_workdir.read_file(f))
    return workdir




def test_robot_ontology_utils(test_workdir):
    run_robot_template_command(
        test_workdir,
        "snacks.csv",
        {"SNK": "http://example.org/snack#"},
        "test_output.owl",
        ["imports.csv"],
    )


def test_robot_ontology_utils_deps(test_workdir):
    run_robot_template_command(
        test_workdir,
        "snacks.csv",
        {"SNK": "http://example.org/snack#"},
        "test_output.owl",
        ["imports.owl"],
    )


def test_robot_ontology_utils_noimport_fails(test_workdir):
    with pytest.raises(Exception):
        run_robot_template_command(
            test_workdir,
            "snacks.csv",
            {"SNK": "http://example.org/snack#"},
            "test_output.owl",
        )

def test_robot_ontology_utils_noprefix_fails(test_workdir):
    with pytest.raises(Exception):
        run_robot_template_command(
            test_workdir,
            "snacks.csv",
            {},
            "test_output.owl",
            ["imports.owl"],
        )