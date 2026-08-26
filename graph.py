
from typing import TypedDict
from langchain_core.documents import Document
from langgraph.graph import END, StateGraph
from langchain_chroma.vectorstores import Chroma
from langchain_ollama import ChatOllama
import datetime

llm: ChatOllama
chromadb: Chroma

class InternalState(TypedDict):
    question: str
    docs: list[Document]
    output: str

def docs_to_str( docs: list[Document] ) -> str:
    return "\n\n".join([ doc.page_content for doc in docs ])

def step_retrieve_docs(state: InternalState):
    return {
        'docs' : chromadb.invoke(state['question'])
    }

def step_answer_question(state: InternalState):
    output: str = llm.invoke(f"""
    Answer the question based on the documents provided.
    Use caveman speech in your reasoning.
    NO MISTAKES!!

    QUESTION:
    {state['question']}
    DOCUMENTS:
    {docs_to_str(state['docs'])}
    """).content

    return {
        'output': output
    }

def step_refine_question(state: InternalState):
    question: str = llm.invoke(f"""
    Rephrase this prompt in order to enhance the Retrieval Augmented Generation's accuracy.
    Make it concrete, precise and formal.
    NO MISTAKES!!

    PROMPT: {state['question']}
    """).content

    return {
        'question': question
    }

def step_validate_output(state: InternalState):
    validity: str = llm.invoke(f"""
    Decide whether the ANSWER answers the QUESTION based on the DOCUMENTS.
    If the ANSWER to the QUESTION is correct based on the DOCUMENTS, say "YES" othervise say "NO" verbatim as your final answer.
    Use caveman speech for reasoning.
    NO MISTAKES!!

    QUESTION:
    {state['question']}

    ANSWER:
    {state['output']}

    DOCUMENTS:
    {docs_to_str(state['docs'])}
    """).content

    if "YES" in validity.upper():
        return 'translate'
    else:
        return 'retrieve'

def step_answer_format(state: InternalState):
    output: str = llm.invoke(f"""
    Here is a DRAFT_ANSWER, make it more refined and human friendly.
    The DRAFT_ANSWER should be as short as possible, answering the QUESTION.
    You may use emojis to make understanding easier.
    You must always use markdown as your output!

    QUESTION:
    {state['question']}

    DRAFT_OUTPUT:
    {state['output']}
    """).content

    return {
        'output': output
    }

def substep_replace_dashes(state: InternalState):
    return {
        'output': state['output'].replace('—', '-')
    }

def substep_add_timestamp(state: InternalState):
    return {
        'output': f"{state['output']}\n\n{str(datetime.datetime.now())}"
    }

def substep_add_header(state: InternalState):
    return {
        'output': f"# {state['question']}\n\n{state['output']}"
    }

def make_graph(_llm: ChatOllama, _chromadb: Chroma):
    global llm
    global chromadb

    _llm, _chromadb = llm, chromadb

    #
    # Finalizer subgraph
    #

    subgraph = StateGraph(InternalState)
    # Nodes
    subgraph.add_node('dash', substep_replace_dashes)
    subgraph.add_node('timestamp', substep_add_timestamp)
    subgraph.add_node('header', substep_add_header)
    # Entry
    subgraph.set_entry_point('dash')
    # Edges
    subgraph.add_edge('dash', 'timestamp')
    subgraph.add_edge('timestamp', 'header')
    subgraph.add_edge('header', END)
    # Compile
    step_finalize = subgraph.compile()

    #
    # Main graph
    #

    graph = StateGraph(InternalState)
    # Nodes
    graph.add_node('retrieve', step_retrieve_docs)
    graph.add_node('answer', step_answer_question)
    graph.add_node('refine_prompt', step_refine_question)
    graph.add_node('translate', step_answer_format)
    graph.add_node('finalize', step_finalize)
    # Entry
    graph.set_entry_point('refine_prompt')
    # Edges
    graph.add_edge('retrieve', 'answer')
    graph.add_edge('refine_prompt', 'retrieve')
    graph.add_edge('translate', 'finalize')
    graph.add_edge('finalize', END)
    graph.add_conditional_edges('answer', step_validate_output)
    # Compile
    graph = graph.compile()

    #
    # Draw graph png (opt)
    #

    png_bytes = graph.get_graph().draw_mermaid_png()

    with open("graph.png", "wb") as f:
        f.write(png_bytes)

    return graph
