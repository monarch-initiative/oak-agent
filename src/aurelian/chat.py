from typing import Callable

from aurelian.utils.async_utils import run_sync


def get_chatbot(query_func: Callable, **kwargs):
    import gradio as gr

    def get_info(query: str, history: List[str]) -> str:
        print(f"QUERY: {query}")
        print(f"HISTORY: {history}")
        if history:
            query += "## History"
            for h in history:
                query += f"\n{h}"
        result = run_sync(query_func)
        return result.data

    return gr.ChatInterface(
        fn=get_info,
        type="messages",
        **kwargs,
    )
