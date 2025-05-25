"""
Test file for context_processor.py module.
Run this to verify context processing functions work correctly.
"""

import os
import tempfile
from context_processor import get_user_context_string
from user_manager import create_user
from utils import write_file, ensure_dir_exists


def test_get_user_context_string_empty():
    """Test get_user_context_string with no context files."""
    print("Testing get_user_context_string with empty context...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Create a test user
        user_id = create_user("test_empty_context_user")
        
        # Get context string (should be empty)
        context_string = get_user_context_string(user_id)
        assert context_string == "", "Context string should be empty when no files exist"
        
        os.chdir(original_dir)
    
    print("✓ Empty context tests passed")


def test_get_user_context_string_single_file():
    """Test get_user_context_string with a single context file."""
    print("Testing get_user_context_string with single file...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Create a test user
        user_id = create_user("test_single_context_user")
        
        # Add a context file
        user_paths = get_user_paths(user_id)
        context_content = "This is my personal context.\nI am interested in ACT therapy."
        write_file(os.path.join(user_paths['context'], 'personal_info.txt'), context_content)
        
        # Get context string
        context_string = get_user_context_string(user_id)
        
        # Verify content
        assert "### Context from personal_info.txt ###" in context_string, "Should have file header"
        assert context_content in context_string, "Should contain file content"
        assert "---" in context_string, "Should have separator line"
        
        os.chdir(original_dir)
    
    print("✓ Single file context tests passed")


def test_get_user_context_string_multiple_files():
    """Test get_user_context_string with multiple context files."""
    print("Testing get_user_context_string with multiple files...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Create a test user
        user_id = create_user("test_multiple_context_user")
        user_paths = get_user_paths(user_id)
        
        # Add multiple context files
        files_content = {
            'background.txt': "I have a background in psychology.",
            'goals.md': "# My Goals\n- Learn about ACT\n- Improve mental health",
            'challenges.txt': "Current challenges:\n1. Anxiety\n2. Work stress"
        }
        
        for filename, content in files_content.items():
            write_file(os.path.join(user_paths['context'], filename), content)
        
        # Get context string
        context_string = get_user_context_string(user_id)
        
        # Verify all files are included (files should be sorted alphabetically)
        assert "### Context from background.txt ###" in context_string
        assert "### Context from challenges.txt ###" in context_string
        assert "### Context from goals.md ###" in context_string
        
        # Verify all content is included
        for content in files_content.values():
            assert content in context_string, f"Content '{content}' should be in aggregated string"
        
        # Verify files are separated
        assert context_string.count("\n\n") >= 2, "Files should be separated by double newlines"
        
        # Verify alphabetical ordering
        background_pos = context_string.find("background.txt")
        challenges_pos = context_string.find("challenges.txt")
        goals_pos = context_string.find("goals.md")
        assert background_pos < challenges_pos < goals_pos, "Files should be in alphabetical order"
        
        os.chdir(original_dir)
    
    print("✓ Multiple files context tests passed")


def test_get_user_context_string_file_types():
    """Test get_user_context_string with different file types."""
    print("Testing get_user_context_string with different file types...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Create a test user
        user_id = create_user("test_filetypes_context_user")
        user_paths = get_user_paths(user_id)
        
        # Add various file types
        write_file(os.path.join(user_paths['context'], 'valid1.txt'), "Text file content")
        write_file(os.path.join(user_paths['context'], 'valid2.md'), "Markdown file content")
        write_file(os.path.join(user_paths['context'], 'ignored.pdf'), "PDF content (ignored)")
        write_file(os.path.join(user_paths['context'], 'ignored.docx'), "DOCX content (ignored)")
        
        # Get context string
        context_string = get_user_context_string(user_id)
        
        # Verify only .txt and .md files are included
        assert "valid1.txt" in context_string, ".txt files should be included"
        assert "valid2.md" in context_string, ".md files should be included"
        assert "ignored.pdf" not in context_string, ".pdf files should be ignored"
        assert "ignored.docx" not in context_string, ".docx files should be ignored"
        
        os.chdir(original_dir)
    
    print("✓ File types tests passed")


def test_get_user_context_string_invalid_user():
    """Test get_user_context_string with invalid user."""
    print("Testing get_user_context_string with invalid user...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Try to get context for non-existent user
        try:
            get_user_context_string("non_existent_user_id")
            assert False, "Should raise ValueError for non-existent user"
        except ValueError as e:
            assert "User directory not found" in str(e), "Error should indicate user not found"
        
        os.chdir(original_dir)
    
    print("✓ Invalid user tests passed")


def test_integration():
    """Test integration with real-world scenario."""
    print("Testing context processor integration...")
    
    # Use actual project directory
    user_id = create_user("integration_test_context_user")
    user_paths = get_user_paths(user_id)
    
    # Create a realistic context scenario
    psychological_background = """Personal Background:
I've been struggling with anxiety for several years, particularly in social situations.
I tend to avoid confrontation and have difficulty expressing my needs.
My values include family, creativity, and personal growth."""
    
    current_situation = """Current Situation:
- Recently started a new job that requires more social interaction
- Feeling overwhelmed by the changes
- Want to develop better coping strategies
- Interested in understanding my patterns of avoidance"""
    
    therapy_goals = """# Therapy Goals

1. **Reduce Anxiety**: Learn techniques to manage anxiety in social situations
2. **Improve Communication**: Develop skills to express needs assertively
3. **Align with Values**: Make decisions that reflect my core values
4. **Build Flexibility**: Develop psychological flexibility through ACT principles"""
    
    # Write context files
    write_file(os.path.join(user_paths['context'], '01_background.txt'), psychological_background)
    write_file(os.path.join(user_paths['context'], '02_current_situation.txt'), current_situation)
    write_file(os.path.join(user_paths['context'], '03_therapy_goals.md'), therapy_goals)
    
    # Get aggregated context
    context_string = get_user_context_string(user_id)
    
    # Verify comprehensive context is created
    assert len(context_string) > 500, "Context should be substantial"
    assert "anxiety" in context_string.lower(), "Should contain key psychological terms"
    assert "values" in context_string.lower(), "Should contain ACT-relevant concepts"
    assert all(f in context_string for f in ['01_background.txt', '02_current_situation.txt', '03_therapy_goals.md'])
    
    print("✓ Integration tests passed")


def main():
    """Run all tests."""
    print("Running context_processor.py tests...\n")
    
    test_get_user_context_string_empty()
    test_get_user_context_string_single_file()
    test_get_user_context_string_multiple_files()
    test_get_user_context_string_file_types()
    test_get_user_context_string_invalid_user()
    test_integration()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    # Import get_user_paths for use in tests
    from user_manager import get_user_paths
    main()