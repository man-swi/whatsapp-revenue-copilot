import chromadb

def get_chroma_client():
    """Initializes and returns a ChromaDB client that connects to the running server."""
    # We use HttpClient to connect to the chroma service container over the Docker network.
    # 'chroma' is the service name in your docker-compose.yml, and 8000 is the port it exposes.
    client = chromadb.HttpClient(host="chroma", port=8000)
    return client

# We will add more tools here later, like a function to download from Google Drive.