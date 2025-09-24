import chromadb
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import json # Import the json library

# --- ChromaDB Tool ---
def get_chroma_client():
    """Initializes and returns a ChromaDB client that connects to the running server."""
    client = chromadb.HttpClient(host="chroma", port=8000)
    return client

# --- Google Drive Tool ---
def get_google_drive_service():
    """Initializes and returns a Google Drive API service object."""
    creds_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json_str:
        raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable not set.")
    
    # Use json.loads() which is safer than eval()
    creds_dict = json.loads(creds_json_str) 
    credentials = Credentials.from_service_account_info(creds_dict, scopes=['https://www.googleapis.com/auth/drive.readonly'])
    service = build('drive', 'v3', credentials=credentials)
    return service

def download_file_from_drive(file_id: str) -> io.BytesIO:
    """Downloads a file from Google Drive and returns it as an in-memory binary object."""
    try:
        service = get_google_drive_service()
        
        file_metadata = service.files().get(fileId=file_id, fields='name, mimeType').execute()
        print(f"--- Downloading file: {file_metadata.get('name')} ---")

        request = service.files().get_media(fileId=file_id)
        
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%.")
        
        file_buffer.seek(0)
        
        file_buffer.name = file_metadata.get('name')
        file_buffer.mimeType = file_metadata.get('mimeType')

        return file_buffer

    except Exception as e:
        print(f"An error occurred while downloading from Google Drive: {e}")
        return None