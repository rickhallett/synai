"""
Test file for user_manager.py module.
Run this to verify user management functions work correctly.
"""

import os
import shutil
import tempfile
from user_manager import create_user, get_user_paths


def test_create_user():
    """Test the create_user function."""
    print("Testing create_user...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create required data structure
        os.makedirs('data/users', exist_ok=True)
        
        # Test creating a user
        user_id1 = create_user("test_user_1")
        assert len(user_id1) == 16, f"Expected user_id length 16, got {len(user_id1)}"
        
        # Verify directory structure
        user_path = os.path.join('data', 'users', user_id1)
        assert os.path.exists(user_path), "User directory should exist"
        
        # Verify all subdirectories exist
        subdirs = ['context', 'prompts', 'seeds', 'feedback', 'interaction_dumps']
        for subdir in subdirs:
            subdir_path = os.path.join(user_path, subdir)
            assert os.path.exists(subdir_path), f"Subdirectory {subdir} should exist"
        
        # Test creating another user with same identifier - should get different ID
        user_id2 = create_user("test_user_1")
        assert user_id1 != user_id2, "Same identifier should produce different IDs due to timestamp"
        
        # Test creating user with different identifier
        user_id3 = create_user("test_user_2")
        assert user_id3 != user_id1, "Different identifiers should produce different IDs"
        assert user_id3 != user_id2, "Different identifiers should produce different IDs"
        
        os.chdir(original_dir)
    
    print("✓ create_user tests passed")


def test_get_user_paths():
    """Test the get_user_paths function."""
    print("Testing get_user_paths...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create required data structure
        os.makedirs('data/users', exist_ok=True)
        
        # Create a user first
        user_id = create_user("test_user")
        
        # Test getting user paths
        paths = get_user_paths(user_id)
        
        # Verify all expected keys are present
        expected_keys = ['base', 'context', 'prompts', 'seeds', 'feedback', 'interaction_dumps']
        for key in expected_keys:
            assert key in paths, f"Key '{key}' should be in paths dictionary"
        
        # Verify paths are correct
        assert paths['base'] == os.path.join('data', 'users', user_id)
        assert paths['context'] == os.path.join('data', 'users', user_id, 'context')
        assert paths['prompts'] == os.path.join('data', 'users', user_id, 'prompts')
        assert paths['seeds'] == os.path.join('data', 'users', user_id, 'seeds')
        assert paths['feedback'] == os.path.join('data', 'users', user_id, 'feedback')
        assert paths['interaction_dumps'] == os.path.join('data', 'users', user_id, 'interaction_dumps')
        
        # Test with non-existent user
        try:
            get_user_paths("non_existent_user_id")
            assert False, "Should raise ValueError for non-existent user"
        except ValueError as e:
            assert "User directory not found" in str(e), "Error message should indicate user not found"
        
        os.chdir(original_dir)
    
    print("✓ get_user_paths tests passed")


def test_integration():
    """Test the integration of user management functions."""
    print("Testing user management integration...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create required data structure
        os.makedirs('data/users', exist_ok=True)
        
        # Create multiple users
        users = []
        for i in range(3):
            user_id = create_user(f"integration_test_user_{i}")
            users.append(user_id)
        
        # Verify all users have correct structure
        for user_id in users:
            paths = get_user_paths(user_id)
            
            # Verify all paths exist
            for path_key, path_value in paths.items():
                assert os.path.exists(path_value), f"Path {path_key} should exist at {path_value}"
        
        # Verify all user IDs are unique
        assert len(set(users)) == len(users), "All user IDs should be unique"
        
        os.chdir(original_dir)
    
    print("✓ Integration tests passed")


def main():
    """Run all tests."""
    print("Running user_manager.py tests...\n")
    
    test_create_user()
    test_get_user_paths()
    test_integration()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()