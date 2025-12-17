"""Storage abstraction layer for Impact Engine."""

from .factory import create_storage
from .base import StorageInterface
from .file import FileStorageBackend
from .s3 import S3StorageBackend

__all__ = ['create_storage', 'StorageInterface', 'FileStorageBackend', 'S3StorageBackend']