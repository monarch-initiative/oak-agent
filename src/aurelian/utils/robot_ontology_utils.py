from typing import Dict, Optional, List, Tuple

from aurelian.dependencies.workdir import WorkDir

MERGED_IMPORT_PATH = "_imports_.owl"

def run(cmd: str):
    """
    Run a command, raising an error if the command fails,
    returning stdout

    Args:
        cmd:

    Returns:

    """
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        stdout = result.stdout.decode()
        stderr = result.stderr.decode()
        raise Exception(f"Command failed: {cmd}\nError: {stderr}\nOutput: {stdout}")
    return result.stdout.decode()

def parse_component_name(name: str) -> Tuple[str, Optional[str]]:
    """
    Parse file name

    Example:

        >>> parse_component_name("foo.owl")
        ('foo', 'owl')
        >>> parse_component_name("foo")
        ('foo', None)


    Args:
        name:

    Returns:

    """
    parts = name.split(".")
    if len(parts) == 1:
        return name, None
    return ".".join(parts[:-1]), parts[-1]


def depends_on_csv(workdir: WorkDir, name: str) -> Optional[str]:
    base, suffix = parse_component_name(name)
    if not suffix:
        suffix = "owl"
        base = name
    if suffix == "owl":
        for d_suffix in ("tsv", "csv"):
            d_name = f"{base}.{d_suffix}"
            if workdir.check_file_exists(d_name):
                return d_name
    return None

def run_robot_template_command(workdir: WorkDir, template_path: str, prefix_map: Dict[str, str], output_path: Optional[str] = None, import_ontologies: Optional[List[str]] = None) -> str:
    """
    Generate a robot template command

    Args:
        workdir:
        template_path:
        prefix_map:
        output_path:
        import_ontologies:

    Returns:

    """
    if output_path is None:
        output_path = template_path.replace(".csv", ".owl")
    prefixes = " ".join([f"--prefix '{k}: {v}'" for k, v in prefix_map.items()])
    if not import_ontologies:
        import_ontologies = []
    import_owls = []
    for import_ontology in import_ontologies:
        local_name, suffix = parse_component_name(import_ontology)
        if suffix == "owl":
            import_ontology_owl = import_ontology
            if not workdir.check_file_exists(import_ontology_owl):
                depends_on = depends_on_csv(workdir, import_ontology_owl)
                if not workdir.check_file_exists(depends_on):
                    raise Exception(f"Cannot make owl file {import_ontology_owl} as no {depends_on}")
                run_robot_template_command(
                    workdir,
                    depends_on,
                    prefix_map=prefix_map,
                    output_path=import_ontology_owl,
                )
        else:
            if suffix:
                import_ontology_owl = import_ontology.replace(suffix, "owl")
            else:
                import_ontology_owl = import_ontology + ".owl"
            run_robot_template_command(workdir, import_ontology, prefix_map=prefix_map, output_path=import_ontology_owl)
        import_owls.append(import_ontology_owl)
    if import_owls:
        input_opts = [f"--input {owl}" for owl in import_owls]
        cmd = f"cd {workdir.location} && robot merge {' '.join(input_opts)} --output {MERGED_IMPORT_PATH}"
        run(cmd)
        import_ontology_opt = f"--input {MERGED_IMPORT_PATH}"
    else:
        import_ontology_opt = ""
    cmd = f"cd {workdir.location} && robot template {import_ontology_opt} --template {template_path} {prefixes} reason --output {output_path}"
    run(cmd)
    return output_path