from pathlib import Path
import os

from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.core.schema import BaseNode
from llama_index.core.node_parser import CodeSplitter
from tree_sitter_languages import get_parser

from rag.config_loader import load_config, get_backend_root
from rag.sync_repos import sync_repos
from rag.splitters import FileSplitter


def ingest_file(file_path: Path) -> list[BaseNode] | None:
    config = next(
        (
            split_config.value
            for split_config in FileSplitter
            if file_path.suffix in split_config.value.extensions
        ),
        None,
    )
    if config is None:
        return None

    reader = SimpleDirectoryReader(input_files=[str(file_path)])
    documents = reader.load_data()
    return config.splitter.get_nodes_from_documents(documents)


def ingest_repos() -> None:
    try:
        config = load_config()
        paths = config.Paths
        llm_config = config.LLM
    except (FileNotFoundError, ValueError):
        print("Config file not found or empty. Exiting...")
        exit(1)

    # Configuration of LLM and embedding models
    Settings.llm = OpenAILike(
        model=llm_config.model_name,
        api_base=llm_config.provider.base_url,
        api_key=os.environ.get("LLM_API_KEY"),
        is_chat_model=True,
    )
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Configuration of Database
    db_path: Path = get_backend_root() / paths.database_dir
    db_path.mkdir(parents=True, exist_ok=True)

    chroma_client = chromadb.PersistentClient(path=str(db_path))
    chroma_collection = chroma_client.get_or_create_collection("cpp_coursework")

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    sync_results = sync_repos()
    failed_syncs = [result for result in sync_results if not result.success]
    if failed_syncs:
        print(
            f"Warning: {len(failed_syncs)} repo(s) failed to sync: {[result.repo_name for result in failed_syncs]}"
        )

    files_to_ingest = [
        Path(file)
        for result in sync_results
        if result.success
        for file in result.changed_files
    ]

    if not files_to_ingest:
        print("No files to ingest.")
        return

    all_nodes = []
    for file_path in files_to_ingest:
        # Delete existing chunks for files being re-ingested
        chroma_collection.delete(where={"file_path": {"$eq": str(file_path)}})

        nodes = ingest_file(file_path)
        if nodes is None:
            # print(f"Skipping {file_path.name} — no splitter for {file_path.suffix}")
            continue
        all_nodes.extend(nodes)

    if not all_nodes:
        print("No nodes to index.")
        return

    print("Indexing nodes into database...")
    VectorStoreIndex(
        nodes=all_nodes, storage_context=storage_context, show_progress=True
    )
    print("Indexing complete! The database is ready.")


if __name__ == "__main__":
    ingest_repos()
