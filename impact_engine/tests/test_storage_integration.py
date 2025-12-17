"""Integration tests for storage backends."""

import pytest
import tempfile
import json
from pathlib import Path
from impact_engine.storage import create_storage, FileStorageBackend, S3StorageBackend

class TestStorageFactory:
    """Tests for storage factory functionality."""
    
    def test_create_file_storage_from_path(self):
        """Test creating file storage from local path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = create_storage(tmpdir)
            assert isinstance(storage, FileStorageBackend)
            assert storage.base_url == f"file://{tmpdir}"
    
    def test_create_file_storage_from_file_url(self):
        """Test creating file storage from file:// URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_url = f"file://{tmpdir}"
            storage = create_storage(file_url)
            assert isinstance(storage, FileStorageBackend)
            assert storage.base_url == file_url
    
    def test_create_s3_storage_from_url(self):
        """Test creating S3 storage from s3:// URL."""
        storage = create_storage("s3://test-bucket/prefix")
        assert isinstance(storage, S3StorageBackend)
        assert storage.bucket == "test-bucket"
        assert storage.prefix == "prefix"
    
    def test_create_s3_storage_without_prefix(self):
        """Test creating S3 storage without prefix."""
        storage = create_storage("s3://test-bucket")
        assert isinstance(storage, S3StorageBackend)
        assert storage.bucket == "test-bucket"
        assert storage.prefix == ""

class TestFileStorageBackend:
    """Tests for file storage backend."""
    
    def test_store_and_load_json(self):
        """Test storing and loading JSON data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = create_storage(tmpdir)
            
            test_data = {"key": "value", "number": 42}
            stored_url = storage.store_json("test.json", test_data)
            
            # Verify URL format
            assert stored_url.startswith("file://")
            assert "test.json" in stored_url
            
            # Load and verify data
            loaded_data = storage.load_json("test.json")
            assert loaded_data == test_data
    
    def test_tenant_isolation(self):
        """Test that different tenants have isolated storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = create_storage(tmpdir)
            
            # Store data for tenant A
            data_a = {"tenant": "A", "value": 100}
            storage.store_json("data.json", data_a, tenant_id="tenant_a")
            
            # Store data for tenant B
            data_b = {"tenant": "B", "value": 200}
            storage.store_json("data.json", data_b, tenant_id="tenant_b")
            
            # Verify isolation
            loaded_a = storage.load_json("data.json", tenant_id="tenant_a")
            loaded_b = storage.load_json("data.json", tenant_id="tenant_b")
            
            assert loaded_a == data_a
            assert loaded_b == data_b
            assert loaded_a != loaded_b
    
    def test_default_tenant(self):
        """Test default tenant behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = create_storage(tmpdir)
            
            test_data = {"default": True}
            storage.store_json("test.json", test_data)  # No tenant_id specified
            
            # Should be accessible with default tenant
            loaded_data = storage.load_json("test.json", tenant_id="default")
            assert loaded_data == test_data
            
            # Should also be accessible without specifying tenant
            loaded_data_implicit = storage.load_json("test.json")
            assert loaded_data_implicit == test_data
    
    def test_nested_paths(self):
        """Test storing files in nested directory structures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = create_storage(tmpdir)
            
            test_data = {"nested": True}
            stored_url = storage.store_json("jobs/job_123/results.json", test_data, "tenant_x")
            
            # Verify file was created in correct nested structure
            assert "jobs/job_123/results.json" in stored_url
            
            # Verify data can be loaded
            loaded_data = storage.load_json("jobs/job_123/results.json", "tenant_x")
            assert loaded_data == test_data

class TestS3StorageBackend:
    """Tests for S3 storage backend (mocked)."""
    
    def test_store_and_load_json(self):
        """Test storing and loading JSON data in mocked S3."""
        storage = create_storage("s3://test-bucket/impact-engine")
        
        test_data = {"s3_test": True, "value": 42}
        stored_url = storage.store_json("test.json", test_data)
        
        # Verify S3 URL format
        assert stored_url.startswith("s3://test-bucket/")
        assert "impact-engine" in stored_url
        assert "test.json" in stored_url
        
        # Load and verify data
        loaded_data = storage.load_json("test.json")
        assert loaded_data == test_data
    
    def test_s3_tenant_isolation(self):
        """Test tenant isolation in S3 backend."""
        storage = create_storage("s3://test-bucket/prefix")
        
        # Store data for different tenants
        data_1 = {"tenant": "company_1"}
        data_2 = {"tenant": "company_2"}
        
        url_1 = storage.store_json("config.json", data_1, "company_1")
        url_2 = storage.store_json("config.json", data_2, "company_2")
        
        # URLs should be different
        assert url_1 != url_2
        assert "company_1" in url_1
        assert "company_2" in url_2
        
        # Data should be isolated
        loaded_1 = storage.load_json("config.json", "company_1")
        loaded_2 = storage.load_json("config.json", "company_2")
        
        assert loaded_1 == data_1
        assert loaded_2 == data_2
    
    def test_s3_mock_directory_structure(self):
        """Test that S3 mock creates expected directory structure."""
        storage = create_storage("s3://my-bucket/data")
        
        storage.store_json("test.json", {"test": True}, "tenant_abc")
        
        # Verify mock directory exists
        mock_path = Path(".mock_s3/my-bucket/data/tenants/tenant_abc/test.json")
        assert mock_path.exists()
        
        # Verify content
        with open(mock_path, 'r') as f:
            content = json.load(f)
        assert content == {"test": True}

class TestURLParsing:
    """Tests for URL parsing functionality."""
    
    def test_parse_local_paths(self):
        """Test parsing various local path formats."""
        from impact_engine.storage.url_parser import parse_storage_url
        
        # Relative path
        result = parse_storage_url("./data")
        assert result == {"scheme": "file", "path": "./data"}
        
        # Absolute path
        result = parse_storage_url("/tmp/data")
        assert result == {"scheme": "file", "path": "/tmp/data"}
        
        # File URL
        result = parse_storage_url("file:///app/data")
        assert result == {"scheme": "file", "path": "/app/data"}
    
    def test_parse_s3_urls(self):
        """Test parsing S3 URLs."""
        from impact_engine.storage.url_parser import parse_storage_url
        
        # S3 with prefix
        result = parse_storage_url("s3://bucket/prefix/path")
        assert result == {"scheme": "s3", "bucket": "bucket", "prefix": "prefix/path"}
        
        # S3 without prefix
        result = parse_storage_url("s3://bucket")
        assert result == {"scheme": "s3", "bucket": "bucket", "prefix": ""}
    
    def test_normalize_file_urls(self):
        """Test file URL normalization."""
        from impact_engine.storage.url_parser import normalize_to_file_url
        
        assert normalize_to_file_url("./data") == "file://./data"
        assert normalize_to_file_url("/tmp/data") == "file:///tmp/data"

class TestStorageIntegrationWithEngine:
    """Integration tests with the main engine."""
    
    def test_engine_with_file_storage(self):
        """Test engine works with file storage URL."""
        # This would require mocking the full engine pipeline
        # For now, just test that storage creation works
        storage = create_storage("./test_data")
        assert isinstance(storage, FileStorageBackend)
    
    def test_engine_with_s3_storage(self):
        """Test engine works with S3 storage URL."""
        # This would require mocking the full engine pipeline
        # For now, just test that storage creation works
        storage = create_storage("s3://test-bucket/impact-engine")
        assert isinstance(storage, S3StorageBackend)

class TestErrorHandling:
    """Tests for error handling in storage operations."""
    
    def test_unsupported_scheme(self):
        """Test error handling for unsupported URL schemes."""
        with pytest.raises(ValueError, match="Unsupported scheme"):
            create_storage("ftp://example.com/data")
    
    def test_file_not_found(self):
        """Test error handling when loading non-existent files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = create_storage(tmpdir)
            
            with pytest.raises(FileNotFoundError):
                storage.load_json("nonexistent.json")
    
    def test_invalid_json(self):
        """Test error handling for invalid JSON data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = create_storage(tmpdir)
            
            # Create invalid JSON file manually
            invalid_file = Path(tmpdir) / "tenants/default/invalid.json"
            invalid_file.parent.mkdir(parents=True, exist_ok=True)
            invalid_file.write_text("invalid json content")
            
            with pytest.raises(json.JSONDecodeError):
                storage.load_json("invalid.json")