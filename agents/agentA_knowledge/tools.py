import chromadb

def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client."""
    # The 'path' is where the database files will be stored inside the Docker container.
    # The Docker volume we created in docker-compose.yml maps this to our local ./data/chroma folder.
    client = chromadb.PersistentClient(path="/data/chroma_db")
    return client

# We will add more tools here later, like a function to download from Google Drive.