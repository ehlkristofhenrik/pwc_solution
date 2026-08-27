#!/usr/bin/python3
from langchain.tools import tool
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters.markdown import MarkdownTextSplitter
from langchain_community.document_loaders import (
    DirectoryLoader,
    UnstructuredMarkdownLoader,
)
from langchain_chroma.vectorstores import Chroma
from langchain_ollama.chat_models import ChatOllama
import datetime
from typing import Literal
from typing import TypedDict
from langchain_core.documents import Document
from langgraph.graph import END, StateGraph
import click
import streamlit as st

llm: ChatOllama
chromadb: VectorStoreRetriever

class InternalState(TypedDict):
    question: str
    docs: list[Document]
    output: str


def docs_to_str(docs: list[Document]) -> str:
    """
    Concatenate docs's content to a str
    """
    return "\n\n".join([doc.page_content for doc in docs])


def step_retrieve_docs(state: InternalState):
    """
    Retrieves relevant document pieces
    """
    return {"docs": chromadb.invoke(state["question"])}


def step_answer_question(state: InternalState):
    """
    Generate answer to prompt
    """
    output = llm.invoke(f"""
    Answer the question based on the documents provided.
    Use caveman speech in your reasoning.
    NO MISTAKES!!

    QUESTION:
    {state['question']}
    DOCUMENTS:
    {docs_to_str(state['docs'])}
    """).content

    return {"output": output}


def step_refine_question(state: InternalState):
    """
    Refines prompt for better performance
    """
    question = llm.invoke(f"""
    Rephrase this prompt in order to enhance the Retrieval Augmented Generation's accuracy.
    Make it concrete, precise and formal.
    NO MISTAKES!!

    PROMPT: {state['question']}
    """).content

    return {"question": question}


def step_validate_output(state: InternalState):
    """
    Validates whether the RAG query was successful
    """
    validity = llm.invoke(f"""
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
        return "translate"
    else:
        return "retrieve"


def step_answer_format(state: InternalState):
    """
    Format the answer such that its easy to read
    """
    output = llm.invoke(f"""
    Here is a DRAFT_ANSWER, make it more refined and human friendly.
    The DRAFT_ANSWER should be as short as possible, answering the QUESTION.
    You may use emojis to make understanding easier.
    You must always use markdown as your output!

    QUESTION:
    {state['question']}

    DRAFT_OUTPUT:
    {state['output']}
    """).content

    return {"output": output}


def substep_replace_dashes(state: InternalState):
    """
    Replaces emdash with normal dash
    """
    return {"output": state["output"].replace("—", "-")}


def substep_add_timestamp(state: InternalState):
    """
    Adds timestamp
    """
    return {"output": f"{state['output']}\n\n{str(datetime.datetime.now())}"}


def substep_add_header(state: InternalState):
    """
    Adds markdown header
    """
    return {"output": f"# {state['question']}\n\n{state['output']}"}


@tool
def get_datetime() -> str:
    """
    Returns the current date and time
    """
    return str(datetime.datetime.today())


@tool
def get_usa_gdp() -> float:
    """
    Returns the current USA Gross Domestic Product in Trillion USD
    """
    return 32.3


@tool
def calculate_revenue(
    product: Literal["screwdriver", "toothpaste", "printer", "oilbarrel"],
    count: int,
) -> float:
    """
    Computes the revenue of a product
    """
    match product:
        case "screwdriver":
            return count * 2
        case "toothpaste":
            return count * 10
        case "oilbarrel":
            return count * 99
        case "printer":
            return count * 50
        case _:
            return 0


def main():
    #
    # Streamlit
    #
    st.title("RAG-NAROK")
    query = st.text_input("Query", key='query')
    if st.button("Run"):
        try:
            global llm, chromadb
            # Load the directory's markdown files
            docs: list[Document] = DirectoryLoader(
                "./data", "*.md", loader_cls=UnstructuredMarkdownLoader  # Disallow recursive
            ).load()

            # Split docs zo chunk
            docs = MarkdownTextSplitter().split_documents(docs)

            # Push into vector db
            chromadb = Chroma.from_documents(docs).as_retriever(search_kwargs={"k": 4})

            llm = ChatOllama(
                model="lfm2.5-thinking:1.2b",
                temperature=0,
            )

            # Add tools
            llm.bind_tools([get_datetime, get_usa_gdp, calculate_revenue])

            #
            # Finalizer subgraph
            #

            subgraph = StateGraph(InternalState)
            # Nodes
            subgraph.add_node("dash", substep_replace_dashes)
            subgraph.add_node("timestamp", substep_add_timestamp)
            subgraph.add_node("header", substep_add_header)
            # Entry
            subgraph.set_entry_point("dash")
            # Edges
            subgraph.add_edge("dash", "timestamp")
            subgraph.add_edge("timestamp", "header")
            subgraph.add_edge("header", END)
            # Compile
            step_finalize = subgraph.compile()

            #
            # Main graph
            #

            graph = StateGraph(InternalState)
            # Nodes
            graph.add_node("retrieve", step_retrieve_docs)
            graph.add_node("answer", step_answer_question)
            graph.add_node("refine_prompt", step_refine_question)
            graph.add_node("translate", step_answer_format)
            graph.add_node("finalize", step_finalize)
            # Entry
            graph.set_entry_point("refine_prompt")
            # Edges
            graph.add_edge("retrieve", "answer")
            graph.add_edge("refine_prompt", "retrieve")
            graph.add_edge("translate", "finalize")
            graph.add_edge("finalize", END)
            graph.add_conditional_edges("answer", step_validate_output)
            # Compile
            graph = graph.compile()

            #
            # Draw graph png (opt)
            #

            png_bytes = graph.get_graph().draw_mermaid_png()

            with open("graph.png", "wb") as f:
                f.write(png_bytes)

            res = graph.invoke(
                input={"question": query, "docs": [], "output": ""}
            )

            st.success("Finished query")
            st.write(res)
        except:
            st.error("Does not compute!")

if __name__ == "__main__":
    main()
