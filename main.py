#!/usr/bin/python3
from langchain.tools import tool
from langchain_text_splitters.markdown import MarkdownTextSplitter
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_chroma.vectorstores import Chroma
from langchain_ollama.chat_models import ChatOllama
import datetime
from typing import Literal
from graph import make_graph

@tool
def get_datetime() -> str:
    """
    Returns the current date and time
    """
    return str( datetime.datetime.today() )

@tool
def get_usa_gdp() -> float:
    """
    Returns the current USA Gross Domestic Product in Trillion USD
    """
    return 32.3

@tool
def calculate_revenue(product: Literal["screwdriver", "toothpaste", "printer", "oilbarrel"], count: int) -> float:
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

if __name__ == '__main__':
    # Load the directory's markdown files
    docs = DirectoryLoader(
        "./data",
        "*.md", # Disallow recursive
        loader_cls = UnstructuredMarkdownLoader
    ).load()

    # Split docs zo chunk
    docs = MarkdownTextSplitter() \
        .split_documents( docs )

    # Push into vector db
    chromadb = Chroma.from_documents( docs ) \
        .as_retriever(
            search_kwargs = { 'k': 4 }
        )

    llm = ChatOllama(
        model = "lfm2.5-thinking:1.2b",
        temperature = 0,
    )

    llm.bind_tools([
        get_datetime,
        get_usa_gdp,
        calculate_revenue
    ])

    agent = make_graph()

    res = agent.invoke(
        input = {
            'question': 'What is the name of the company?',
            'docs': [],
            'output': ''
        }, config = {
            'llm': llm,
            'vectordb': chromadb
        }
    )

    print(res)
