"""
Test file for config.py module.
Run this to verify configuration management works correctly.
"""

import os
import tempfile
from config import (
    get_config, get_user_dir_path, get_user_subdir_path,
    is_valid_context_file, is_valid_prompt_file, get_env_override,
    BASE_DIR, DATA_DIR, USERS_DIR, BASE_PROMPTS_DIR, DB_PATH,
    USER_SUBDIRS, OPERATION_TYPES, PIPELINE_NAMES,
    DEFAULT_HASH_LENGTH, SHORT_HASH_LENGTH
)


def test_config_paths():
    """Test configuration paths."""
    print("Testing configuration paths...")
    
    # Test that BASE_DIR is set correctly
    assert os.path.isabs(BASE_DIR), "BASE_DIR should be absolute path"
    assert BASE_DIR.endswith('synai'), "BASE_DIR should end with 'synai'"
    
    # Test other paths are relative to BASE_DIR
    assert DATA_DIR == os.path.join(BASE_DIR, 'data')
    assert USERS_DIR == os.path.join(DATA_DIR, 'users')
    assert BASE_PROMPTS_DIR == os.path.join(BASE_DIR, 'base_prompts')
    assert DB_PATH == os.path.join(DATA_DIR, 'spcf.db')
    
    print("✓ Configuration paths tests passed")


def test_get_config():
    """Test get_config function."""
    print("Testing get_config...")
    
    config = get_config()
    
    # Test required keys exist
    required_keys = [
        'base_dir', 'data_dir', 'users_dir', 'base_prompts_dir',
        'db_path', 'context_file_extensions', 'user_subdirs',
        'operation_types', 'pipeline_names', 'status_success'
    ]
    
    for key in required_keys:
        assert key in config, f"Config should contain '{key}'"
    
    # Test specific values
    assert config['base_dir'] == BASE_DIR
    assert config['context_file_extensions'] == ('.txt', '.md')
    assert len(config['user_subdirs']) == 5
    assert config['default_hash_length'] == 16
    assert config['short_hash_length'] == 8
    
    print("✓ get_config tests passed")


def test_user_path_functions():
    """Test user path helper functions."""
    print("Testing user path functions...")
    
    test_user_id = "test_user_123"
    
    # Test get_user_dir_path
    user_dir = get_user_dir_path(test_user_id)
    assert user_dir == os.path.join(USERS_DIR, test_user_id)
    
    # Test get_user_subdir_path
    for subdir in USER_SUBDIRS:
        subdir_path = get_user_subdir_path(test_user_id, subdir)
        expected = os.path.join(USERS_DIR, test_user_id, subdir)
        assert subdir_path == expected, f"Subdir path for '{subdir}' should match"
    
    # Test invalid subdirectory
    try:
        get_user_subdir_path(test_user_id, "invalid_subdir")
        assert False, "Should raise ValueError for invalid subdirectory"
    except ValueError as e:
        assert "Invalid subdirectory" in str(e)
    
    print("✓ User path functions tests passed")


def test_file_validation_functions():
    """Test file validation functions."""
    print("Testing file validation functions...")
    
    # Test context file validation
    assert is_valid_context_file("test.txt") == True
    assert is_valid_context_file("test.md") == True
    assert is_valid_context_file("test.TXT") == True  # Case insensitive
    assert is_valid_context_file("test.MD") == True
    assert is_valid_context_file("test.pdf") == False
    assert is_valid_context_file("test") == False
    
    # Test prompt file validation
    assert is_valid_prompt_file("prompt.xml") == True
    assert is_valid_prompt_file("prompt.XML") == True  # Case insensitive
    assert is_valid_prompt_file("prompt.txt") == False
    assert is_valid_prompt_file("prompt") == False
    
    print("✓ File validation functions tests passed")


def test_constants():
    """Test configuration constants."""
    print("Testing configuration constants...")
    
    # Test USER_SUBDIRS
    assert len(USER_SUBDIRS) == 5
    assert 'context' in USER_SUBDIRS
    assert 'prompts' in USER_SUBDIRS
    assert 'seeds' in USER_SUBDIRS
    
    # Test OPERATION_TYPES
    assert 'USER_CREATED' in OPERATION_TYPES
    assert OPERATION_TYPES['USER_CREATED'] == 'USER_CREATED'
    assert len(OPERATION_TYPES) >= 7
    
    # Test PIPELINE_NAMES
    assert 'ONBOARD_NO_CONTEXT' in PIPELINE_NAMES
    assert len(PIPELINE_NAMES) == 4
    
    print("✓ Configuration constants tests passed")


def test_env_override():
    """Test environment variable override functionality."""
    print("Testing environment variable overrides...")
    
    # Test with no environment variable set
    default_value = "default_test_value"
    result = get_env_override("TEST_KEY", default_value)
    assert result == default_value, "Should return default when env var not set"
    
    # Test with environment variable set
    os.environ['SPCF_TEST_KEY'] = "env_test_value"
    result = get_env_override("TEST_KEY", default_value)
    assert result == "env_test_value", "Should return env var value when set"
    
    # Clean up
    del os.environ['SPCF_TEST_KEY']
    
    print("✓ Environment variable override tests passed")


def test_config_integration():
    """Test configuration integration with other modules."""
    print("Testing configuration integration...")
    
    # Import a module that might use config
    try:
        from user_manager import create_user
        from utils import ensure_dir_exists
        
        # Ensure we can use config values in practice
        ensure_dir_exists(DATA_DIR)
        ensure_dir_exists(USERS_DIR)
        
        # The modules should work with config values
        assert os.path.exists(DATA_DIR), "DATA_DIR should be created"
        
    except ImportError:
        # If modules aren't available, that's okay for config testing
        pass
    
    print("✓ Configuration integration tests passed")


def main():
    """Run all tests."""
    print("Running config.py tests...\n")
    
    test_config_paths()
    test_get_config()
    test_user_path_functions()
    test_file_validation_functions()
    test_constants()
    test_env_override()
    test_config_integration()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()