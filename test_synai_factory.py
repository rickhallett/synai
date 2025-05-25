"""
Test file for synai_factory.py module.
Run this to verify the main factory interface works correctly.
"""

import os
import tempfile
from synai_factory import SynaiFactory, default_factory


def test_synai_factory_initialization():
    """Test SynaiFactory initialization."""
    print("Testing SynaiFactory initialization...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test_factory.db')
        
        # Create factory instance
        factory = SynaiFactory(db_path=db_path)
        
        # Verify database was created
        assert os.path.exists(db_path), "Database should be created"
        
        # Verify project structure
        assert os.path.exists('data'), "Data directory should exist"
        assert os.path.exists('data/users'), "Users directory should exist"
        assert os.path.exists('base_prompts'), "Base prompts directory should exist"
    
    print("✓ SynaiFactory initialization tests passed")


def test_factory_user_operations():
    """Test factory user operations."""
    print("Testing factory user operations...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test_factory.db')
        factory = SynaiFactory(db_path=db_path)
        
        # Test user creation
        user_id = factory.create_user("test_factory_user@example.com")
        assert len(user_id) == 16, "User ID should be 16 characters"
        
        # Test get user paths
        paths = factory.get_user_paths(user_id)
        assert 'base' in paths
        assert 'context' in paths
        assert 'prompts' in paths
        
        # Test add context file
        factory.add_context_file(user_id, "test.txt", "Test content")
        context_file = os.path.join(paths['context'], 'test.txt')
        assert os.path.exists(context_file), "Context file should be created"
        
        # Test get context string
        context = factory.get_user_context_string(user_id)
        assert "Test content" in context, "Context should contain file content"
        
        # Test get all users
        users = factory.get_all_users()
        assert user_id in users, "User should be in user list"
    
    print("✓ Factory user operations tests passed")


def test_factory_prompt_operations():
    """Test factory prompt operations."""
    print("Testing factory prompt operations...")
    
    # Use the actual factory since we have base prompts
    user_id = default_factory.create_user("test_prompt_user@example.com")
    
    # Test generate assessment prompt
    assessment_path = default_factory.generate_user_assessment_prompt(user_id)
    assert os.path.exists(assessment_path), "Assessment prompt should be created"
    
    # Test save user prompt
    prompt_path = default_factory.save_user_prompt(
        user_id, "test_prompt.xml", "<test>content</test>"
    )
    assert os.path.exists(prompt_path), "Prompt should be saved"
    
    print("✓ Factory prompt operations tests passed")


def test_factory_pipeline_operations():
    """Test factory pipeline operations."""
    print("Testing factory pipeline operations...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test_pipelines.db')
        factory = SynaiFactory(db_path=db_path)
        
        # Test onboard new user no context
        user_id = factory.onboard_new_user_no_context("pipeline_test_user@example.com")
        assert len(user_id) == 16, "User ID should be created"
        
        # Verify operations were logged
        operations = factory.get_operations_for_user(user_id)
        assert len(operations) >= 2, "Should have at least 2 operations"
        
        # Test full onboarding
        context_files = {
            "background.txt": "Test background",
            "goals.txt": "Test goals"
        }
        designer_response = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <data>{"test": "data"}</data>
</synai>"""
        
        result = factory.full_user_onboarding(
            "full_test_user@example.com",
            context_files,
            designer_response
        )
        
        assert 'user_id' in result
        assert 'assessment_path' in result
        assert 'seed_path' in result
    
    print("✓ Factory pipeline operations tests passed")


def test_factory_utility_methods():
    """Test factory utility methods."""
    print("Testing factory utility methods...")
    
    # Create a user with some data
    user_id = default_factory.create_user("utility_test_user@example.com")
    default_factory.generate_user_assessment_prompt(user_id)
    default_factory.add_context_file(user_id, "test.txt", "Test content")
    
    # Test get user summary
    summary = default_factory.get_user_summary(user_id)
    assert 'user_id' in summary
    assert 'file_counts' in summary
    assert 'total_operations' in summary
    assert summary['file_counts']['prompts'] >= 1
    assert summary['file_counts']['context'] >= 1
    
    # Test logging custom operation
    default_factory.log_operation(
        user_id=user_id,
        operation_type="CUSTOM_TEST",
        notes="Test custom operation"
    )
    
    # Verify it was logged
    operations = default_factory.get_operations_for_user(user_id)
    custom_ops = [op for op in operations if op['operation_type'] == 'CUSTOM_TEST']
    assert len(custom_ops) == 1, "Custom operation should be logged"
    
    print("✓ Factory utility methods tests passed")


def test_default_factory_instance():
    """Test the default factory instance."""
    print("Testing default factory instance...")
    
    # Verify default_factory is available
    assert default_factory is not None, "Default factory should exist"
    
    # Test basic operation
    user_id = default_factory.create_user("default_factory_test@example.com")
    assert len(user_id) == 16, "Should create user through default factory"
    
    print("✓ Default factory instance tests passed")


def main():
    """Run all tests."""
    print("Running synai_factory.py tests...\n")
    
    test_synai_factory_initialization()
    test_factory_user_operations()
    test_factory_prompt_operations()
    test_factory_pipeline_operations()
    test_factory_utility_methods()
    test_default_factory_instance()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()