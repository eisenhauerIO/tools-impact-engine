"""Storage factory for creating storage backends."""

from .url_parser import parse_storage_url, normalize_to_file_url
from .file import FileStorageBackend
from .s3 import S3StorageBackend

def create_storage(storage_url: str):
    """Create storage backend from URL or path."""
    # Convert local paths to file:// URLs
    if "://" not in storage_url:
        storage_url = normalize_to_file_url(storage_url)
    
    parsed = parse_storage_url(storage_url)
    
    if parsed["scheme"] == "file":
        return FileStorageBackend(storage_url)
    elif parsed["scheme"] == "s3":
        return S3StorageBackend(storage_url)
    else:
        raise ValueError(f"Unsupported scheme: {parsed['scheme']}")