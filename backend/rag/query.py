import os

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore
from utils.config_loader import OverallConfig, get_backend_root, get_config


def initialize_query_engine(config: OverallConfig) -> BaseQueryEngine:
    """
    Initializes everything to be able to query with the RAG model.

    Args:
        config (OverallConfig): The backend configuration

    Returns:
        BaseQueryEngine: a query engine to query with the RAG model.
    """
    paths = config.Paths
    llm_config = config.LLM

    Settings.llm = OpenAILike(
        model=llm_config.model_name,
        api_base=llm_config.provider.base_url,
        api_key=os.environ.get("LLM_API_KEY"),
        is_chat_model=True,
    )
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    db_path = get_backend_root() / paths.database_dir
    print("Connecting to the database...")
    chroma_client = chromadb.PersistentClient(path=str(db_path))
    # We use get_collection here because we assume it was already created during ingestion
    chroma_collection = chroma_client.get_collection("cpp_coursework")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    return index.as_query_engine(streaming=True, similarity_top_k=5)


def query_RAG() -> None:
    """
    Queries the RAG model using the LLM wanted.
    """
    try:
        config = get_config()
    except (FileNotFoundError, ValueError):
        print("Config file not found or empty. Exiting...")
        exit(1)

    # Create a Query Engine
    query_engine = initialize_query_engine(config)

    # Interactive Chat Loop
    print(
        "\n RAG System Ready! Ask questions about your codebase (or type 'exit' to quit)."
    )
    while True:
        user_input = input("\nQuery: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break

        if not user_input.strip():
            continue

        print("\nThinking...\n")
        response = query_engine.query(user_input)

        # Print streamed response chunk by chunk
        response.print_response_stream()
        print("\n" + "-" * 50)


if __name__ == "__main__":
    query_RAG()
