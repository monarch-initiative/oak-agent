from typing import Optional

import yaml
from linkml.generators import JsonSchemaGenerator
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime.loaders import yaml_loader
from pydantic import BaseModel
from pydantic_ai import RunContext, ModelRetry

from aurelian.agents.linkml.linkml_config import LinkMLDependencies
from aurelian.dependencies.workdir import WorkDir, HasWorkdir


class LinkMLError(ModelRetry):
    pass

class SchemaValidationError(LinkMLError):
    """Base exception for all schema validation errors."""
    def __init__(self, message="Schema validation failed", details=None):
        self.details = details or {}
        super().__init__(message)


class ValidationResult(BaseModel):
    valid: bool
    info_messages: Optional[list[str]] = None


async def validate_then_save_schema(ctx: RunContext[HasWorkdir], schema_as_str: str, save_to_file: str= "schema.yaml") -> ValidationResult:
    """
    Validate a LinkML schema.

    Args:
        ctx: context
        schema_as_str: linkml schema (as yaml) to validate. Do not truncate, always pass the whole schema.
        save_to_file: file name to save the schema to. Defaults to schema.yaml

    Returns:

    """
    print(f"Validating schema: {schema_as_str}")
    msgs = []
    try:
        schema_dict = yaml.safe_load(schema_as_str)
        print("YAML is valid")
    except Exception as e:
        raise SchemaValidationError(f"Schema is not valid yaml: {e}")
    if "id" not in schema_dict:
        raise SchemaValidationError("Schema does not have a top level id")
    if "name" not in schema_dict:
        raise SchemaValidationError("Schema does not have a top level name")
    try:
        schema_obj = yaml_loader.loads(schema_as_str, target_class=SchemaDefinition)
    except Exception as e:
        raise SchemaValidationError(f"Schema does not validate: {e}")
    try:
        gen = JsonSchemaGenerator(schema_obj)
        gen.serialize()
    except Exception as e:
        raise SchemaValidationError(f"Schema does not convert to JSON-Schema: {e}")
    try:
        if save_to_file and schema_as_str:
            msgs.append(f"Writing schema to {save_to_file}")
            workdir = ctx.deps.workdir
            workdir.write_file(save_to_file, schema_as_str)
    except Exception as e:
        raise SchemaValidationError(f"Schema does not validate: {e}")
    return ValidationResult(valid=True, info_messages=msgs)


async def validate_data(ctx: RunContext[LinkMLDependencies], schema: str, data_file: str) -> str:
    """
    Validate data file against a schema.

    This assumes the data file is present in the working directory.
    You can write data to the working directory using the `write_to_file` tool.

    Args:
        ctx:
        schema: the schema (as a YAML string)
        data_file: the name of the data file in the working directory

    Returns:

    """
    print(f"Validating data file: {data_file} using schema: {schema}")
    try:
        schema = yaml_loader.loads(schema, target_class=SchemaDefinition)
    except Exception as e:
        return f"Schema does not validate: {e}"
    try:
        from linkml.validator import validate
        instances = ctx.deps.parse_objects_from_file(data_file)
        for instance in instances:
            print(f"Validating {instance}")
            rpt = validate(instance, schema)
            print(f"Validation report: {rpt}")
            if rpt.results:
                return f"Data does not validate:\n{rpt.results}"
        return f"{len(instances)} instances all validate successfully"
    except Exception as e:
        raise ModelRetry(f"Data does not validate: {e}")