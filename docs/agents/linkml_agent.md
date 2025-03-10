# LinkML Agent

The LinkML Agent assists with creating, validating, and working with LinkML schemas. It provides tools for schema development, validation, code generation, and data transformation using the LinkML (Linked Data Modeling Language) framework.

## Features

- Assist with LinkML schema design and development
- Validate YAML data against LinkML schemas
- Generate code and artifacts from schemas
- Transform data between JSON, YAML, RDF, and other formats
- Explain LinkML concepts and best practices
- Troubleshoot schema and validation issues

## Usage

### Python API

```python
from aurelian.agents.linkml import linkml_agent, get_config

# Initialize dependencies
deps = get_config()

# Query about LinkML
result = await linkml_agent.run(
    "How do I define an enumeration in LinkML?",
    deps=deps
)

# Get the response
print(result.data)
```

### Command Line Interface

```bash
aurelian linkml "How do I define an enumeration in LinkML?"
```

### Gradio Interface

```python
from aurelian.agents.linkml import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The LinkML Agent provides the following tools:

### validate_schema

Validates a LinkML schema for correctness.

### generate_python

Generates Python classes from a LinkML schema.

### validate_data

Validates data against a LinkML schema.

### transform_data

Transforms data between different formats (YAML, JSON, RDF, etc.).

## Examples

### Example 1: Creating a schema

```
Help me create a LinkML schema for a person with name, age, and address
```

### Example 2: Validating a schema

```
Is this schema valid?
```
```yaml
classes:
  Person:
    attributes:
      name:
        required: true
      age:
        range: integer
```

### Example 3: Generating code

```
Generate Python classes for this schema:
```
```yaml
classes:
  Person:
    attributes:
      name:
        required: true
      age:
        range: integer
```