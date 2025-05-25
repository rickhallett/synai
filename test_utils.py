"""
Test file for utils.py module.
Run this to verify all utility functions work correctly.
"""

import os
import tempfile
from utils import generate_hash, ensure_dir_exists, read_file, write_file, initialize_project


def test_generate_hash():
    """Test the generate_hash function."""
    print("Testing generate_hash...")
    
    # Test default length
    hash1 = generate_hash("test_string")
    assert len(hash1) == 8, f"Expected length 8, got {len(hash1)}"
    
    # Test custom length
    hash2 = generate_hash("test_string", length=16)
    assert len(hash2) == 16, f"Expected length 16, got {len(hash2)}"
    
    # Test consistency
    hash3 = generate_hash("test_string")
    assert hash1 == hash3, "Hash should be consistent for same input"
    
    # Test different inputs produce different hashes
    hash4 = generate_hash("different_string")
    assert hash1 != hash4, "Different inputs should produce different hashes"
    
    print("✓ generate_hash tests passed")


def test_dir_operations():
    """Test directory operations."""
    print("Testing directory operations...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "test_dir")
        
        # Test ensure_dir_exists
        ensure_dir_exists(test_dir)
        assert os.path.exists(test_dir), "Directory should exist"
        
        # Test idempotence
        ensure_dir_exists(test_dir)  # Should not raise error
        assert os.path.exists(test_dir), "Directory should still exist"
        
        # Test nested directories
        nested_dir = os.path.join(tmpdir, "test", "nested", "dir")
        ensure_dir_exists(nested_dir)
        assert os.path.exists(nested_dir), "Nested directory should exist"
    
    print("✓ Directory operations tests passed")


def test_file_operations():
    """Test file read/write operations."""
    print("Testing file operations...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_file.txt")
        test_content = "This is test content\nWith multiple lines\n"
        
        # Test write_file
        write_file(test_file, test_content)
        assert os.path.exists(test_file), "File should exist after writing"
        
        # Test read_file
        read_content = read_file(test_file)
        assert read_content == test_content, "Read content should match written content"
        
        # Test reading non-existent file
        try:
            read_file(os.path.join(tmpdir, "non_existent.txt"))
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected
        
        # Test writing to invalid path (though makedirs should handle most cases)
        try:
            # Try to write to a file with invalid characters (if on Windows)
            if os.name == 'nt':
                write_file(os.path.join(tmpdir, "invalid<>file.txt"), "test")
        except IOError:
            pass  # Expected on some systems
    
    print("✓ File operations tests passed")


def test_initialize_project():
    """Test project initialization."""
    print("Testing project initialization...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Initialize project
        initialize_project()
        
        # Check directories exist
        assert os.path.exists('data'), "data directory should exist"
        assert os.path.exists('data/users'), "data/users directory should exist"
        assert os.path.exists('base_prompts'), "base_prompts directory should exist"
        
        # Test idempotence
        initialize_project()  # Should not raise error
        
        os.chdir(original_dir)
    
    print("✓ Project initialization tests passed")


def main():
    """Run all tests."""
    print("Running utils.py tests...\n")
    
    test_generate_hash()
    test_dir_operations()
    test_file_operations()
    test_initialize_project()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()