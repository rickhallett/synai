"""
Test file for prompt_manager.py module.
Run this to verify prompt management functions work correctly.
"""

import os
import tempfile
import time
from prompt_manager import load_base_prompt, generate_user_assessment_prompt, save_user_prompt
from user_manager import create_user
from utils import write_file, ensure_dir_exists


def test_load_base_prompt():
    """Test the load_base_prompt function."""
    print("Testing load_base_prompt...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create base_prompts directory and test prompt
        ensure_dir_exists('base_prompts')
        test_prompt_content = """<?xml version="1.0" encoding="UTF-8"?>
<test>
    <content>This is a test prompt</content>
</test>"""
        write_file('base_prompts/test_prompt.xml', test_prompt_content)
        
        # Test loading existing prompt
        loaded_content = load_base_prompt('test_prompt.xml')
        assert loaded_content == test_prompt_content, "Loaded content should match original"
        
        # Test loading non-existent prompt
        try:
            load_base_prompt('non_existent.xml')
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError as e:
            assert "File not found" in str(e), "Error should indicate file not found"
        
        os.chdir(original_dir)
    
    print("✓ load_base_prompt tests passed")


def test_generate_user_assessment_prompt():
    """Test the generate_user_assessment_prompt function."""
    print("Testing generate_user_assessment_prompt...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        ensure_dir_exists('base_prompts')
        
        # Create test assessment template
        assessment_template = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>assessment</mode>
    <content>Test assessment prompt</content>
</synai>"""
        write_file('base_prompts/synai_assessment.xml', assessment_template)
        
        # Create a test user
        user_id = create_user("test_assessment_user")
        
        # Generate assessment prompt
        prompt_path = generate_user_assessment_prompt(user_id)
        
        # Verify file was created
        assert os.path.exists(prompt_path), "Prompt file should exist"
        
        # Verify file is in correct location
        assert f"data/users/{user_id}/prompts/" in prompt_path, "Prompt should be in user's prompts directory"
        
        # Verify filename format
        filename = os.path.basename(prompt_path)
        assert filename.startswith("assessment_prompt_"), "Filename should start with 'assessment_prompt_'"
        assert filename.endswith(".xml"), "Filename should end with '.xml'"
        
        # Verify content includes user_id comment
        saved_content = read_file(prompt_path)
        assert f"<!-- user_id: {user_id} -->" in saved_content, "Content should include user_id comment"
        assert "<mode>assessment</mode>" in saved_content, "Content should include original template data"
        
        # Test generating multiple prompts for same user
        time.sleep(0.1)  # Ensure different timestamp
        prompt_path2 = generate_user_assessment_prompt(user_id)
        assert prompt_path != prompt_path2, "Multiple prompts should have different filenames"
        
        os.chdir(original_dir)
    
    print("✓ generate_user_assessment_prompt tests passed")


def test_save_user_prompt():
    """Test the save_user_prompt function."""
    print("Testing save_user_prompt...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Create a test user
        user_id = create_user("test_save_prompt_user")
        
        # Test saving to default prompts folder
        test_content = "<test>Prompt content</test>"
        filename = "test_prompt.xml"
        saved_path = save_user_prompt(user_id, filename, test_content)
        
        assert os.path.exists(saved_path), "Saved file should exist"
        assert saved_path.endswith(f"prompts/{filename}"), "File should be in prompts directory"
        
        # Verify content
        saved_content = read_file(saved_path)
        assert saved_content == test_content, "Saved content should match original"
        
        # Test saving to different subfolders
        for subfolder in ['seeds', 'feedback', 'interaction_dumps']:
            test_filename = f"test_{subfolder}.xml"
            test_content = f"<test>{subfolder} content</test>"
            saved_path = save_user_prompt(user_id, test_filename, test_content, subfolder=subfolder)
            
            assert os.path.exists(saved_path), f"File should exist in {subfolder}"
            assert f"{subfolder}/{test_filename}" in saved_path, f"File should be in {subfolder} directory"
            
            saved_content = read_file(saved_path)
            assert saved_content == test_content, "Saved content should match"
        
        # Test invalid subfolder
        try:
            save_user_prompt(user_id, "test.xml", "content", subfolder="invalid_folder")
            assert False, "Should raise ValueError for invalid subfolder"
        except ValueError as e:
            assert "Invalid subfolder" in str(e), "Error should indicate invalid subfolder"
        
        os.chdir(original_dir)
    
    print("✓ save_user_prompt tests passed")


def test_integration():
    """Test integration of prompt management functions."""
    print("Testing prompt management integration...")
    
    # Use the actual project directory with the real assessment template
    original_dir = os.getcwd()
    
    # Create a test user
    user_id = create_user("integration_test_prompt_user")
    
    # Generate assessment prompt using real template
    prompt_path = generate_user_assessment_prompt(user_id)
    assert os.path.exists(prompt_path), "Assessment prompt should be created"
    
    # Load and verify it contains expected ACT content
    content = read_file(prompt_path)
    assert "Acceptance and Commitment Therapy" in content, "Should contain ACT reference"
    assert f"<!-- user_id: {user_id} -->" in content, "Should contain user_id comment"
    
    # Save additional prompts to different folders
    seed_content = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <preloaded_data>Test seed data</preloaded_data>
</synai>"""
    
    seed_path = save_user_prompt(user_id, "test_seed.xml", seed_content, subfolder="seeds")
    assert os.path.exists(seed_path), "Seed prompt should be saved"
    
    print("✓ Integration tests passed")


def main():
    """Run all tests."""
    print("Running prompt_manager.py tests...\n")
    
    test_load_base_prompt()
    test_generate_user_assessment_prompt()
    test_save_user_prompt()
    test_integration()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    # Import read_file for use in tests
    from utils import read_file
    main()