"""
Test file for db_manager.py module.
Run this to verify database management functions work correctly.
"""

import os
import tempfile
import time
from db_manager import setup_database, log_operation, get_operations_for_user


def test_setup_database():
    """Test the setup_database function."""
    print("Testing setup_database...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        
        # Test creating new database
        setup_database(db_path)
        assert os.path.exists(db_path), "Database file should be created"
        
        # Test idempotence - running again should not fail
        setup_database(db_path)
        assert os.path.exists(db_path), "Database file should still exist"
        
        # Verify table structure
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if operations_log table exists
        cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='operations_log'
        """)
        result = cursor.fetchone()
        assert result is not None, "operations_log table should exist"
        
        # Check columns
        cursor.execute("PRAGMA table_info(operations_log)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        expected_columns = [
            'id', 'timestamp', 'user_id', 'pipeline_name', 
            'operation_type', 'input_params_json', 'output_ref_json', 
            'status', 'notes'
        ]
        
        for expected in expected_columns:
            assert expected in column_names, f"Column {expected} should exist"
        
        conn.close()
    
    print("✓ setup_database tests passed")


def test_log_operation():
    """Test the log_operation function."""
    print("Testing log_operation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        setup_database(db_path)
        
        # Test logging basic operation
        log_operation(
            db_path=db_path,
            user_id="test_user_123",
            operation_type="USER_CREATED",
            status="SUCCESS"
        )
        
        # Test logging operation with all parameters
        log_operation(
            db_path=db_path,
            user_id="test_user_123",
            operation_type="PROMPT_GENERATED",
            pipeline_name="test_pipeline",
            input_params={"template": "assessment", "version": "1.0"},
            output_ref={"file_path": "/path/to/prompt.xml", "size": 1024},
            status="SUCCESS",
            notes="Test prompt generation"
        )
        
        # Test logging failed operation
        log_operation(
            db_path=db_path,
            user_id="test_user_456",
            operation_type="CONTEXT_AGGREGATION",
            status="FAILED",
            notes="No context files found"
        )
        
        # Verify records were inserted
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM operations_log")
        count = cursor.fetchone()[0]
        assert count == 3, f"Expected 3 records, got {count}"
        conn.close()
    
    print("✓ log_operation tests passed")


def test_get_operations_for_user():
    """Test the get_operations_for_user function."""
    print("Testing get_operations_for_user...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'test.db')
        setup_database(db_path)
        
        # Log operations for multiple users
        # User 1 operations
        log_operation(
            db_path=db_path,
            user_id="user1",
            operation_type="USER_CREATED",
            input_params={"identifier": "user1@test.com"},
            output_ref={"user_id": "user1"}
        )
        
        time.sleep(1)  # Delay to ensure different timestamps
        
        log_operation(
            db_path=db_path,
            user_id="user1",
            operation_type="PROMPT_GENERATED",
            pipeline_name="onboarding",
            output_ref={"prompt_path": "/prompts/assessment.xml"}
        )
        
        # User 2 operations
        log_operation(
            db_path=db_path,
            user_id="user2",
            operation_type="USER_CREATED",
            status="SUCCESS"
        )
        
        # Get operations for user1
        user1_ops = get_operations_for_user(db_path, "user1")
        assert len(user1_ops) == 2, f"Expected 2 operations for user1, got {len(user1_ops)}"
        
        # Verify order (newest first)
        assert user1_ops[0]['operation_type'] == "PROMPT_GENERATED"
        assert user1_ops[1]['operation_type'] == "USER_CREATED"
        
        # Verify JSON parsing
        assert isinstance(user1_ops[1]['input_params'], dict)
        assert user1_ops[1]['input_params']['identifier'] == "user1@test.com"
        assert isinstance(user1_ops[0]['output_ref'], dict)
        assert user1_ops[0]['output_ref']['prompt_path'] == "/prompts/assessment.xml"
        
        # Get operations for user2
        user2_ops = get_operations_for_user(db_path, "user2")
        assert len(user2_ops) == 1, f"Expected 1 operation for user2, got {len(user2_ops)}"
        
        # Get operations for non-existent user
        user3_ops = get_operations_for_user(db_path, "user3")
        assert len(user3_ops) == 0, "Expected 0 operations for non-existent user"
    
    print("✓ get_operations_for_user tests passed")


def test_integration():
    """Test integration of database operations."""
    print("Testing database integration...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, 'integration_test.db')
        setup_database(db_path)
        
        # Simulate a complete user workflow
        user_id = "integration_test_user"
        
        # 1. User creation
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="USER_CREATED",
            pipeline_name="onboard_new_user_no_context",
            input_params={"user_identifier": "test@example.com"},
            output_ref={"user_id": user_id, "directories_created": 5}
        )
        
        time.sleep(0.1)
        
        # 2. Assessment prompt generation
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="ASSESSMENT_PROMPT_GENERATED",
            pipeline_name="onboard_new_user_no_context",
            output_ref={"assessment_path": f"/data/users/{user_id}/prompts/assessment_123.xml"}
        )
        
        time.sleep(0.1)
        
        # 3. Context aggregation
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="CONTEXT_AGGREGATED",
            pipeline_name="onboard_user_with_context_to_seed",
            output_ref={"context_length": 1500, "files_processed": 3}
        )
        
        time.sleep(0.1)
        
        # 4. Designer input preparation
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="DESIGNER_INPUT_PREPARED",
            pipeline_name="onboard_user_with_context_to_seed",
            status="PENDING_LLM",
            output_ref={"designer_input_length": 2000}
        )
        
        time.sleep(0.1)
        
        # 5. Seed prompt generation
        log_operation(
            db_path=db_path,
            user_id=user_id,
            operation_type="SEED_PROMPT_GENERATED",
            pipeline_name="process_seed_from_designer_output",
            input_params={"designer_response_length": 5000},
            output_ref={"seed_path": f"/data/users/{user_id}/seeds/seed_456.xml"}
        )
        
        # Retrieve all operations
        operations = get_operations_for_user(db_path, user_id)
        
        # Verify complete workflow is logged
        assert len(operations) == 5, f"Expected 5 operations, got {len(operations)}"
        
        # Verify operations are in reverse chronological order
        operation_types = [op['operation_type'] for op in operations]
        expected_order = [
            "SEED_PROMPT_GENERATED",
            "DESIGNER_INPUT_PREPARED", 
            "CONTEXT_AGGREGATED",
            "ASSESSMENT_PROMPT_GENERATED",
            "USER_CREATED"
        ]
        assert operation_types == expected_order, f"Operations should be in reverse chronological order. Got: {operation_types}"
        
        # Verify pipeline tracking
        pipelines = [op['pipeline_name'] for op in operations if op['pipeline_name']]
        assert len(set(pipelines)) == 3, "Should have tracked 3 different pipelines"
        
        # Verify status tracking
        statuses = [op['status'] for op in operations]
        assert "PENDING_LLM" in statuses, "Should have tracked PENDING_LLM status"
        assert statuses.count("SUCCESS") == 4, "Should have 4 SUCCESS operations"
    
    print("✓ Integration tests passed")


def main():
    """Run all tests."""
    print("Running db_manager.py tests...\n")
    
    test_setup_database()
    test_log_operation()
    test_get_operations_for_user()
    test_integration()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()