from pathlib import Path
import chromadb

# LlamaIndex Core
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore

# LlamaIndex Local AI Plugins
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# Import your existing config logic
from core.config_loader import load_config, get_dest_dir, DEFAULT_DEST_DIR

def query_codebase():
    # 1. Path setup (same as ingestion)
    try:
        config = load_config()
        dest_dir = get_dest_dir(config)
    except FileNotFoundError:
        dest_dir = Path(DEFAULT_DEST_DIR)
    
    db_path = dest_dir.parent / "chroma_db"

    # 2. Configure Global Settings to point to your WSL Host
    print("Connecting to local WSL AI models...")
    Settings.llm = Ollama(
        model="llama3.2:3b", 
        base_url="http://host.docker.internal:11434",
        request_timeout=600.0,
        context_window=4096,                 # Caps the prompt size inside LlamaIndex
        additional_kwargs={"num_ctx": 4096}  # Caps the actual RAM allocation inside Ollama
    )
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    # 3. Connect to the EXISTING Chroma Vector Database
    print("Connecting to ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=str(db_path))
    # We use get_collection here because we assume it was already created during ingestion
    chroma_collection = chroma_client.get_collection("cpp_coursework")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # 4. Load the index from the vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # 5. Create a Query Engine
    query_engine = index.as_query_engine(
        streaming=True,       # Streams the output like ChatGPT
        similarity_top_k=5    # Fetches the top 5 most relevant chunks to answer your question
    )

    # 6. Interactive Chat Loop
    print("\n✅ RAG System Ready! Ask questions about your C++ codebase (or type 'exit' to quit).")
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
        print("\n" + "-"*50)

if __name__ == "__main__":
    query_codebase()