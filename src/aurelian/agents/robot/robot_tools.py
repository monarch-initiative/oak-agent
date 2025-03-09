from typing import Optional, List

from pydantic_ai import RunContext, ModelRetry

from aurelian.agents.robot.assets import ROBOT_ONTOLOGY_AGENT_CONTENTS_DIR
from aurelian.agents.robot.robot_config import RobotDependencies
from aurelian.utils.robot_ontology_utils import run_robot_template_command


async def write_and_compile_template(ctx: RunContext[RobotDependencies], template: str, save_to_file: str= "core.csv", import_ontologies: Optional[List[str]] = None) -> str:
    """
    Adds a template to the file system and compile it to OWL

    Args:
        ctx: context
        template: robot template as string. Do not truncate, always pass the whole template, including header.
        save_to_file: file name to save the templates to. Defaults to core.csv. Only written if file compiles to OWL
        import_ontologies: list of ontologies to import. These should be files in the working directory.

    Returns:

    """
    print(f"Validating template: {template}")
    try:
        ctx.deps.workdir.write_file(save_to_file, template)
        output_path = run_robot_template_command(
            ctx.deps.workdir,
            save_to_file,
            import_ontologies=import_ontologies,
            prefix_map=ctx.deps.prefix_map,
            output_path=None,
        ),
        if save_to_file and template:
            ctx.deps.workdir.write_file(save_to_file, template)
    except Exception as e:
        raise ModelRetry(f"Template does not compile: {e}")
    return f"Template compiled to {output_path}"


async def fetch_documentation(ctx: RunContext[RobotDependencies]) -> str:
    """
    Fetch the documentation for the robot ontology agent.

    Args:
        ctx: context

    Returns:
        str: documentation
    """
    return open(ROBOT_ONTOLOGY_AGENT_CONTENTS_DIR / "template.md").read()
