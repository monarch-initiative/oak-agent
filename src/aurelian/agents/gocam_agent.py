import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from bioservices import UniProt
from linkml_store import Client
from linkml_store.api import Collection
from pydantic_ai import Agent, RunContext, AgentRunError

from aurelian.agents.uniprot_agent import normalize_uniprot_id
from aurelian.utils.async_utils import run_sync
from aurelian.utils.data_utils import flatten
from aurelian.utils.pubmed_utils import get_pmid_text
from aurelian.utils.search_utils import web_search

HANDLE = "mongodb://localhost:27017/gocams"
DB_NAME = "gocams"
COLLECTION_NAME = "main"

u = UniProt(verbose=False)


@dataclass
class GOCamDependencies:
    max_results: int = field(default=10)
    _collection: Optional[Collection] = None

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            client = Client()
            client.attach_database(HANDLE, alias=DB_NAME)
            db = client.databases[DB_NAME]
            self._collection = db.get_collection(COLLECTION_NAME)
        return self._collection

gocam_agent = Agent(
    model="openai:gpt-4o",
    deps_type=GOCamDependencies,
    result_type=str,
    system_prompt=(
        "You are an expert molecular biologist with access to the GO-CAM database."
        "You can provide information on gene functions, pathways, and models."
        "When giving your response, stick to communicating the information provided"
        " in the response. You may extemporize and fill in gaps with your own knowledge,"
        " but always be clear about what information came from the call vs your"
        " own knowledge.\n"
        "When providing results in markdown, you should generally include CURIEs/IDs, and you"
        " can hyperlink these as https://bioregistry.io/{curie}. Note that GO-CAM IDs"
        "should be hyperlinked as https://bioregistry.io/go.model:{uuid}."
    )
)

@gocam_agent.tool
def search(ctx: RunContext[GOCamDependencies], query: str) -> List[Dict]:
    """
    Performs a retrieval search over the GO-CAM database.

    The query can be any text, such as name of a pathway, genes, or
    a complex sentence.

    The objects returned are summaries of GO-CAM models; they do not contain full
    details. Use `lookup_gocam` to retrieve full details of a model.

    This tool uses a retrieval method that is not guaranteed to always return
    complete results, and some results may be less relevant than others.
    You MAY use your judgment in filtering these.
    """
    print(f"SEARCH: {query}")
    qr = ctx.deps.collection.search(query, index_name="llm", limit=ctx.deps.max_results)
    objs = []
    for score, row in qr.ranked_rows:
        obj = flatten(row)
        obj["relevancy_score"] = score
        objs.append(obj)
        print(f"RESULT: {obj}")
    return objs

@gocam_agent.tool
def lookup_gocam(ctx: RunContext[GOCamDependencies], model_id: str) -> Dict:
    """
    Performs a lookup of a GO-CAM model by its ID, and returns the model.
    """
    print(f"LOOKUP: {model_id}")
    if ":" in model_id:
        parts = model_id.split(":")
        if parts[0] != "gomodel":
            model_id = f"gomodel:{parts[1]}"
    else:
        model_id = f"gomodel:{model_id}"
    qr = ctx.deps.collection.find({"id": model_id})
    if not qr.rows:
        return None
        #raise ValueError(f"Could not find model with ID {model_id}")
    return qr.rows[0]


# TODO: this is copy-pasted from uniprot_agent.py
@gocam_agent.tool
def lookup_uniprot_entry(ctx: RunContext[GOCamDependencies], uniprot_acc: str) -> str:
    """
    Lookup the Uniprot entry for a given Uniprot accession number.

    This can be used to obtain further information about a protein in
    a GO-CAM.

    Args:
        uniprot_acc: The Uniprot accession
    Returns:
        detailed functional and other info about the protein
    """
    uniprot_acc = normalize_uniprot_id(uniprot_acc)
    print(f"LOOKUP UNIPROT: {uniprot_acc}")
    return u.retrieve(uniprot_acc, frmt="txt")


@gocam_agent.tool
def lookup_pmid(ctx: RunContext[GOCamDependencies], pmid: str) -> str:
    """
    Lookup the text of a PubMed ID, using its PMID.

    Note that assertions in GO-CAMs may reference PMIDs, so this tool
    is useful for validating assertions. A common task is to align
    the text of a PMID with the text of an assertion, or extracting text
    snippets from the publication that support the assertion.

    Returns: full text if available, otherwise abstract
    """
    print(f"LOOKUP PMID: {pmid}")
    return get_pmid_text(pmid)


@gocam_agent.tool
def search_web(ctx: RunContext[GOCamDependencies], query: str) -> str:
    """
    Search the web using a text query.

    Note, this will not retrieve the full content, for that you
    should use `retrieve_web_page`.

    Returns: matching web pages plus summaries
    """
    print(f"Web Search: {query}")
    return web_search(query)

@gocam_agent.tool
def retrieve_web_page(ctx: RunContext[GOCamDependencies], url: str) -> str:
    """
    Fetch the contents of a web page.

    Returns:
        The contents of the web page.
    """
    print(f"Fetch URL: {url}")
    import aurelian.utils.search_utils as su
    return su.retrieve_web_page(url)


def ui():
    import gradio as gr
    deps = GOCamDependencies()

    def get_info(query: str):
        print(f"QUERY: {query}")
        #result = my_run_sync(query, deps)
        #result = gocam_agent.run_sync(query, deps=deps)
        result = run_sync(lambda: gocam_agent.run_sync(query, deps=deps))
        return result.data

    demo = gr.Interface(
        fn=get_info,
        inputs=gr.Textbox(label="Ask about any GO-CAMs",
                          placeholder="What is the function of caspase genes in apoptosis pathways?"),
        outputs=gr.Textbox(label="GO-CAM Information"),
        title="GO-CAM AI Assistant",
        description="Ask me anything about GO-CAMs and I will try to provide you with the information you need.",
    )
    return demo

def chat(**kwargs):
    import gradio as gr
    deps = GOCamDependencies()

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(lambda: gocam_agent.run_sync(query, deps=deps, **kwargs))
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        title="GO-CAM AI Assistant",
        examples=[
            ["What is the function of caspase genes in apoptosis pathways?"],
            ["What models involve autophagy?"],
            [("find the wikipedia article on the integrated stress response pathway,"
              " download it, and summarize the genes and what they do."
              " then find similar GO-CAMs, look up their details,"
              " and compare them to the reviews"
              )
            ],
            ["Examine models for antimicrobial resistance, look for commonalities in genes"],
        ]
    )
