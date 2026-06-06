from pathlib import Path
import chromadb

# LlamaIndex Core
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.core.node_parser import CodeSplitter


from tree_sitter_languages import get_parser

# LlamaIndex Local AI Plugins
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# Import your existing config logic
from core.config_loader import load_config, get_dest_dir, DEFAULT_DEST_DIR


def build_index():
    # 1. Load directory paths using your config_loader
    try:
        config = load_config()
        dest_dir = get_dest_dir(config)
    except FileNotFoundError:
        print("Config file not found. Using default paths.")
        dest_dir = Path(DEFAULT_DEST_DIR)

    # 2. Configure Global Settings to point to your WSL Host!
    print("Connecting to local WSL AI models...")
    Settings.llm = Ollama(
        model="llama3.2:3b",
        base_url="http://host.docker.internal:11434",
        request_timeout=120.0,
    )
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # 3. Setup the Chroma Vector Database
    db_path = dest_dir.parent / "chroma_db"
    db_path.mkdir(parents=True, exist_ok=True)

    # create db file
    chroma_client = chromadb.PersistentClient(path=str(db_path))

    chroma_collection = chroma_client.get_or_create_collection("cpp_coursework")
    # give collection to LlamaIndex
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    # create storage context for LlamaIndex
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 4. Load C++ Documents from the synced repos
    print(f"Loading documents from {dest_dir}...")
    reader = SimpleDirectoryReader(
        input_dir=str(dest_dir),
        recursive=True,
        required_exts=[".cpp", ".hpp", ".c", ".h"],
    )
    documents = reader.load_data()
    print(f"Loaded {len(documents)} C/C++ files.")

    cpp_parser = get_parser("cpp")

    # 5. Split code using the Tree-sitter CodeSplitter
    print("Chunking code structurally (this might take a minute)...")
    cpp_splitter = CodeSplitter(
        language="cpp",
        parser=cpp_parser,
        chunk_lines=40,
        chunk_lines_overlap=15,
        max_chars=1500,
    )

    # 6. Extract nodes (chunks) from documents
    nodes = cpp_splitter.get_nodes_from_documents(documents)
    print(f"Created {len(nodes)} structural code chunks.")

    # 7. Embed and Index into Chroma
    print("Embedding chunks into ChromaDB...")
    index = VectorStoreIndex(
        nodes=nodes, storage_context=storage_context, show_progress=True
    )

    print("✅ Indexing complete! Your local vector database is ready.")


if __name__ == "__main__":
    build_index()
