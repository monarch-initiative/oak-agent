"""Scientific Knowledge Extraction Agent for extracting structured knowledge from scientific papers."""

from pydantic_ai import Agent, Tool, RunContext, ModelRetry, ModelRetryAllowed
from pydantic_ai.models import OpenAI

from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_config import ScientificKnowledgeExtractionDependencies
from aurelian.agents.scientific_knowledge_extraction.scientific_knowledge_extraction_tools import (
    list_pdf_files,
    get_pdf_content,
    extract_knowledge,
    get_unprocessed_pdfs,
    process_all_unprocessed_pdfs,
    get_extracted_knowledge,
    map_assertion_to_ontology,
    map_all_assertions_to_ontology,
    export_assertions_as_rdf
)

# System prompt for the Scientific Knowledge Extraction agent
SYSTEM_PROMPT = """
You are a Scientific Knowledge Extraction agent. Your purpose is to extract meaningful scientific knowledge from research literature and represent it as structured assertions (subject-predicate-object) with supporting evidence and ground them to standard ontologies.

Your main capabilities include:
1. Analyzing PDF documents to identify key findings, contributions, and claims
2. Extracting structured assertions that capture the main scientific contributions
3. Providing evidence for each extracted assertion with full provenance
4. Mapping extracted assertions to standard ontology terms
5. Maintaining a cache of processed papers to avoid redundant work
6. Exporting assertions in RDF format with full provenance

When extracting knowledge, focus on:
- The main findings and contributions of the paper
- Causal relationships (X causes Y)
- Correlational relationships (X is associated with Y)
- Functional relationships (X performs function Y)
- Compositional relationships (X is composed of Y)
- Regulatory relationships (X regulates Y)

For each assertion, you'll extract and map to ontology:
- Subject: The entity or concept that is the source of the assertion
- Predicate: The type of relationship
- Object: The entity or concept that is the target of the assertion
- Evidence: The specific text from which this assertion was extracted
- Metadata: Information about the source paper (DOI, title, authors, etc.)
- Ontology IDs: When possible, map each element to a standard ontology term

The ontology mapping process connects extracted terms to:
- Gene Ontology (GO) for biological processes, cellular components, molecular functions
- ChEBI for chemical entities
- Disease Ontology (DOID) for diseases
- Protein Ontology (PR) for proteins
- Uberon for anatomical entities
- Relation Ontology (RO) for relationship types

When responding to users:
- Be specific about which papers you're extracting knowledge from
- Explain your confidence in each extracted assertion
- Clarify any ambiguities in the source text
- Highlight successful ontology mappings
- Provide options for reviewing and exporting extracted knowledge

Always maintain complete provenance tracking for all extracted assertions, ensuring that each assertion is linked back to its specific evidence in the source paper.
"""

# Create the agent
scientific_knowledge_extraction_agent = Agent(
    name="Scientific Knowledge Extraction Agent",
    model=OpenAI(model="gpt-4o"),
    system_prompt=SYSTEM_PROMPT,
    dependencies=ScientificKnowledgeExtractionDependencies,
    tools=[
        Tool(list_pdf_files),
        Tool(get_pdf_content),
        Tool(extract_knowledge),
        Tool(get_unprocessed_pdfs),
        Tool(process_all_unprocessed_pdfs),
        Tool(get_extracted_knowledge),
        Tool(map_assertion_to_ontology),
        Tool(map_all_assertions_to_ontology),
        Tool(export_assertions_as_rdf)
    ]
)


# If this file is run directly, create a simple CLI for the agent
if __name__ == "__main__":
    import asyncio
    import argparse
    from pydantic_ai.chat import ChatMessage
    
    parser = argparse.ArgumentParser(description="Scientific Knowledge Extraction Agent CLI")
    parser.add_argument("--pdf_directory", required=True, help="Directory containing PDF files")
    parser.add_argument("--cache_directory", help="Directory for caching results")
    parser.add_argument("--max_pdfs", type=int, default=0, help="Maximum number of PDFs to process (0 = no limit)")
    args = parser.parse_args()
    
    async def run_agent():
        # Create dependencies
        deps = ScientificKnowledgeExtractionDependencies(
            pdf_directory=args.pdf_directory,
            cache_directory=args.cache_directory,
            max_pdfs=args.max_pdfs
        )
        
        # Run agent in interactive mode
        print(f"Scientific Knowledge Extraction Agent is ready. PDF directory: {args.pdf_directory}")
        print("Type 'exit' to quit.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                break
            
            try:
                response = await scientific_knowledge_extraction_agent.chat(
                    messages=[ChatMessage(role="user", content=user_input)],
                    dependencies=deps
                )
                print(f"\nAgent: {response.content}")
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    asyncio.run(run_agent())