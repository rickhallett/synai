"""
Test file for pipelines.py module.
Run this to verify pipeline functions work correctly.
"""

import os
import tempfile
import sqlite3
from pipelines import (
    pipeline_onboard_new_user_no_context,
    pipeline_onboard_user_with_context_to_seed,
    pipeline_process_seed_from_designer_output,
    pipeline_full_user_onboarding_with_context
)
from db_manager import setup_database, get_operations_for_user
from user_manager import get_user_paths
from utils import ensure_dir_exists, write_file, read_file


def test_pipeline_onboard_new_user_no_context():
    """Test the pipeline_onboard_new_user_no_context function."""
    print("Testing pipeline_onboard_new_user_no_context...")
    
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
        
        # Set up database
        db_path = os.path.join(tmpdir, 'test.db')
        setup_database(db_path)
        
        # Run pipeline
        user_identifier = "test_user_no_context@example.com"
        user_id = pipeline_onboard_new_user_no_context(user_identifier, db_path)
        
        # Verify user was created
        assert len(user_id) == 16, "User ID should be 16 characters"
        user_paths = get_user_paths(user_id)
        assert os.path.exists(user_paths['base']), "User directory should exist"
        
        # Verify assessment prompt was created
        prompts_dir = user_paths['prompts']
        prompt_files = os.listdir(prompts_dir)
        assert len(prompt_files) == 1, "Should have one prompt file"
        assert prompt_files[0].startswith("assessment_prompt_"), "Should be assessment prompt"
        
        # Verify operations were logged
        operations = get_operations_for_user(db_path, user_id)
        assert len(operations) == 2, "Should have 2 operations logged"
        
        # Check operation types (in reverse chronological order)
        assert operations[0]['operation_type'] == "ASSESSMENT_PROMPT_GENERATED"
        assert operations[1]['operation_type'] == "USER_CREATED"
        
        # Check pipeline name is recorded
        assert all(op['pipeline_name'] == "onboard_new_user_no_context" for op in operations)
        
        os.chdir(original_dir)
    
    print("✓ pipeline_onboard_new_user_no_context tests passed")


def test_pipeline_onboard_user_with_context_to_seed():
    """Test the pipeline_onboard_user_with_context_to_seed function."""
    print("Testing pipeline_onboard_user_with_context_to_seed...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        ensure_dir_exists('base_prompts')
        
        # Create designer template
        designer_template = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>designer</mode>
    <context_placeholder>{CONTEXT}</context_placeholder>
</synai>"""
        write_file('base_prompts/synai_designer.xml', designer_template)
        
        # Set up database
        db_path = os.path.join(tmpdir, 'test.db')
        setup_database(db_path)
        
        # Run pipeline - first without context files
        user_identifier = "test_user_with_context@example.com"
        user_id = pipeline_onboard_user_with_context_to_seed(user_identifier, db_path)
        
        # Add context files manually
        user_paths = get_user_paths(user_id)
        write_file(
            os.path.join(user_paths['context'], 'background.txt'),
            "I struggle with anxiety in social situations."
        )
        write_file(
            os.path.join(user_paths['context'], 'goals.md'),
            "# Goals\n- Reduce anxiety\n- Improve relationships"
        )
        
        # Run pipeline again to process context
        # In real usage, this would be a separate call after files are added
        user_id2 = pipeline_onboard_user_with_context_to_seed(user_identifier, db_path)
        
        # Verify operations were logged
        operations = get_operations_for_user(db_path, user_id)
        
        # Should have operations from both runs
        operation_types = [op['operation_type'] for op in operations]
        assert "USER_CREATED" in operation_types
        assert "CONTEXT_AGGREGATED" in operation_types
        assert "DESIGNER_INPUT_PREPARED" in operation_types
        
        # Check for PENDING_LLM status
        designer_ops = [op for op in operations if op['operation_type'] == "DESIGNER_INPUT_PREPARED"]
        assert any(op['status'] == "PENDING_LLM" for op in designer_ops)
        
        os.chdir(original_dir)
    
    print("✓ pipeline_onboard_user_with_context_to_seed tests passed")


def test_pipeline_process_seed_from_designer_output():
    """Test the pipeline_process_seed_from_designer_output function."""
    print("Testing pipeline_process_seed_from_designer_output...")
    
    # Save current directory
    original_dir = os.getcwd()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Set up required directory structure
        ensure_dir_exists('data/users')
        
        # Set up database
        db_path = os.path.join(tmpdir, 'test.db')
        setup_database(db_path)
        
        # Create a user first
        from user_manager import create_user
        user_id = create_user("test_seed_processing_user")
        
        # Mock designer output
        designer_output = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <preloaded_data>
        <concept>Test concept</concept>
    </preloaded_data>
</synai>"""
        
        # Run pipeline
        seed_path = pipeline_process_seed_from_designer_output(
            user_id, designer_output, db_path
        )
        
        # Verify seed was created
        assert os.path.exists(seed_path), "Seed file should exist"
        assert "/seeds/" in seed_path, "Seed should be in seeds directory"
        
        # Verify operation was logged
        operations = get_operations_for_user(db_path, user_id)
        seed_ops = [op for op in operations if op['operation_type'] == "SEED_PROMPT_GENERATED"]
        assert len(seed_ops) == 1, "Should have one seed generation operation"
        assert seed_ops[0]['status'] == "SUCCESS"
        assert seed_ops[0]['output_ref']['seed_path'] == seed_path
        
        # Test with invalid XML
        try:
            pipeline_process_seed_from_designer_output(
                user_id, "<invalid>xml", db_path
            )
            assert False, "Should raise exception for invalid XML"
        except:
            # Check failure was logged
            operations = get_operations_for_user(db_path, user_id)
            failed_ops = [op for op in operations if op['operation_type'] == "SEED_GENERATION_FAILED"]
            assert len(failed_ops) == 1, "Should log failed operation"
            assert failed_ops[0]['status'] == "FAILED"
        
        os.chdir(original_dir)
    
    print("✓ pipeline_process_seed_from_designer_output tests passed")


def test_pipeline_full_user_onboarding():
    """Test the pipeline_full_user_onboarding_with_context function."""
    print("Testing pipeline_full_user_onboarding_with_context...")
    
    # Use actual project directory
    ensure_dir_exists('data/users')
    
    # Set up database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test_full_pipeline.db')
        setup_database(db_path)
        
        # Prepare test data
        user_identifier = "full_pipeline_test_user@example.com"
        context_files = {
            "personal_history.txt": "I have been dealing with anxiety for years.",
            "therapy_goals.md": "# Goals\n1. Reduce anxiety\n2. Improve work-life balance",
            "values.txt": "My core values: Family, Health, Growth"
        }
        
        designer_response = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <version>1.0</version>
    <preloaded_data>
        <profile>
            <anxiety_level>high</anxiety_level>
            <primary_values>["Family", "Health", "Growth"]</primary_values>
        </profile>
    </preloaded_data>
</synai>"""
        
        # Run full pipeline
        result = pipeline_full_user_onboarding_with_context(
            user_identifier, context_files, designer_response, db_path
        )
        
        # Verify all outputs
        assert "user_id" in result
        assert "assessment_path" in result
        assert "seed_path" in result
        
        # Verify files exist
        assert os.path.exists(result["assessment_path"]), "Assessment should exist"
        assert os.path.exists(result["seed_path"]), "Seed should exist"
        
        # Verify context files were created
        user_paths = get_user_paths(result["user_id"])
        for filename in context_files:
            file_path = os.path.join(user_paths['context'], filename)
            assert os.path.exists(file_path), f"Context file {filename} should exist"
        
        # Verify all operations were logged
        operations = get_operations_for_user(db_path, result["user_id"])
        operation_types = [op['operation_type'] for op in operations]
        
        expected_operations = [
            "USER_CREATED",
            "ASSESSMENT_PROMPT_GENERATED",
            "CONTEXT_AGGREGATED",
            "DESIGNER_INPUT_PREPARED",
            "SEED_PROMPT_GENERATED"
        ]
        
        for expected in expected_operations:
            assert expected in operation_types, f"Operation {expected} should be logged"
        
        # All operations should be from the same pipeline
        pipeline_names = set(op['pipeline_name'] for op in operations)
        assert len(pipeline_names) == 1, "All operations should be from same pipeline"
        assert "full_user_onboarding_with_context" in pipeline_names
    
    print("✓ pipeline_full_user_onboarding_with_context tests passed")


def main():
    """Run all tests."""
    print("Running pipelines.py tests...\n")
    
    test_pipeline_onboard_new_user_no_context()
    test_pipeline_onboard_user_with_context_to_seed()
    test_pipeline_process_seed_from_designer_output()
    test_pipeline_full_user_onboarding()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()