# Chemistry Agent

The Chemistry Agent provides a natural language interface for working with chemical structures, reactions, and molecular properties. It can process SMILES strings, render chemical structures, calculate molecular properties, and assist with chemical analysis tasks.

## Features

- Process SMILES strings and render molecular structures
- Calculate common molecular properties and descriptors
- Convert between different chemical formats
- Search for chemical compounds by name or structure
- Analyze chemical reactions and transformations
- Generate high-quality visualizations of molecules

## Usage

### Python API

```python
from aurelian.agents.chemistry import chemistry_agent, get_config

# Initialize dependencies
deps = get_config()

# Process a chemical query
result = await chemistry_agent.run(
    "Draw the structure of caffeine and calculate its molecular weight",
    deps=deps
)

# Get the analysis results
print(result.data)
```

### Command Line Interface

```bash
aurelian chemistry "Draw the structure of caffeine and calculate its molecular weight"
```

### Gradio Interface

```python
from aurelian.agents.chemistry import chat

# Launch Gradio interface
interface = chat()
interface.launch()
```

## Tools

The Chemistry Agent provides the following tools:

### process_smiles

Processes a SMILES string to generate a molecular structure and calculate basic properties.

### draw_molecule

Creates a visual representation of a molecule from its SMILES string.

### calculate_descriptors

Calculates detailed molecular descriptors and properties for a given molecule.

### search_pubchem

Searches PubChem for compounds matching a name or partial structure.

## Examples

### Example 1: Analyzing a molecule

```
Draw the structure of aspirin and calculate its molecular weight
```

### Example 2: Converting chemical representations

```
Convert "caffeine" to a SMILES string
```

### Example 3: Comparing molecules

```
Compare the structures and properties of ibuprofen and paracetamol
```