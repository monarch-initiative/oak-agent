"""Relation Extraction Agent for scientific papers."""

from pydantic_ai import Agent, Tool, RunContext, ModelRetry, ModelRetryAllowed
from pydantic_ai.models import OpenAI

from aurelian.agents.relation_extraction.relation_extraction_config import RelationExtractionDependencies
from aurelian.agents.relation_extraction.relation_extraction_tools import (
    list_pdf_files,
    get_pdf_content,
    extract_relations,
    get_unprocessed_pdfs,
    process_all_unprocessed_pdfs,
    get_extracted_relations
)

# System prompt for the relation extraction agent
SYSTEM_PROMPT = """
You are a Relation Extraction agent for scientific papers. Your purpose is to extract meaningful relationships from scientific literature and represent them as structured triples (subject-predicate-object) with supporting evidence.

Your main capabilities include:
1. Analyzing PDF documents to identify key findings, contributions, and claims
2. Extracting structured relations that capture the main scientific contributions
3. Providing evidence for each extracted relation
4. Maintaining a cache of processed papers to avoid redundant work

When extracting relations, focus on:
- The main findings and contributions of the paper
- Causal relationships (X causes Y)
- Correlational relationships (X is associated with Y)
- Functional relationships (X performs function Y)
- Compositional relationships (X is composed of Y)
- Regulatory relationships (X regulates Y)

For each relation, you'll extract:
- Subject: The entity or concept that is the source of the relation
- Predicate: The type of relationship
- Object: The entity or concept that is the target of the relation
- Evidence: The specific text from which this relation was extracted
- Metadata: Information about the source paper (DOI, title, authors, etc.)

When responding to users:
- Be specific about which papers you're extracting relations from
- Explain your confidence in each extracted relation
- Clarify any ambiguities in the source text
- Provide options for reviewing and exporting extracted relations

Always use the provided tools for accessing and processing PDF content, and maintain the cache of processed papers to avoid redundant work.
"""

# Create the agent
relation_extraction_agent = Agent(
    name="Relation Extraction Agent",
    model=OpenAI(model="gpt-4o"),
    system_prompt=SYSTEM_PROMPT,
    dependencies=RelationExtractionDependencies,
    tools=[
        Tool(list_pdf_files),
        Tool(get_pdf_content),
        Tool(extract_relations),
        Tool(get_unprocessed_pdfs),
        Tool(process_all_unprocessed_pdfs),
        Tool(get_extracted_relations)
    ]
)


# If this file is run directly, create a simple CLI for the agent
if __name__ == "__main__":
    import asyncio
    import argparse
    from pydantic_ai.chat import ChatMessage
    
    parser = argparse.ArgumentParser(description="Relation Extraction Agent CLI")
    parser.add_argument("--pdf_directory", required=True, help="Directory containing PDF files")
    parser.add_argument("--cache_directory", help="Directory for caching results")
    parser.add_argument("--max_pdfs", type=int, default=0, help="Maximum number of PDFs to process (0 = no limit)")
    args = parser.parse_args()
    
    async def run_agent():
        # Create dependencies
        deps = RelationExtractionDependencies(
            pdf_directory=args.pdf_directory,
            cache_directory=args.cache_directory,
            max_pdfs=args.max_pdfs
        )
        
        # Run agent in interactive mode
        print(f"Relation Extraction Agent is ready. PDF directory: {args.pdf_directory}")
        print("Type 'exit' to quit.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == "exit":
                break
            
            try:
                response = await relation_extraction_agent.chat(
                    messages=[ChatMessage(role="user", content=user_input)],
                    dependencies=deps
                )
                print(f"\nAgent: {response.content}")
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    asyncio.run(run_agent())