from pathlib import Path
import chromadb
import os

from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike


from rag.config_loader import get_config, get_backend_root


def query_RAG():
    try:
        config = get_config()
        paths = config.Paths
        llm_config = config.LLM
    except (FileNotFoundError, ValueError):
        print("Config file not found or empty. Exiting...")
        exit(1)

    db_path: Path = get_backend_root() / paths.database_dir

    Settings.llm = OpenAILike(
        model=llm_config.model_name,
        api_base=llm_config.provider.base_url,
        api_key=os.environ.get("LLM_API_KEY"),
        is_chat_model=True,
    )
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print("Connecting to the database...")
    chroma_client = chromadb.PersistentClient(path=str(db_path))
    # We use get_collection here because we assume it was already created during ingestion
    chroma_collection = chroma_client.get_collection("cpp_coursework")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # Load the index from the vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Create a Query Engine
    query_engine = index.as_query_engine(
        streaming=True,  # Streams the output like ChatGPT
        similarity_top_k=5,  # Fetches the top 5 most relevant chunks to answer your question
    )

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
