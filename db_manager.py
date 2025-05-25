"""
Database management module for the Synai Prompt & Context Factory (SPCF).

This module handles SQLite database operations for logging all factory
operations, providing traceability and audit capabilities.
"""

import sqlite3
import json
import time
from typing import List, Dict, Optional


def setup_database(db_path: str):
    """
    Set up the SQLite database with required tables.
    
    Creates the operations_log table if it doesn't exist, with columns for:
    - id: Auto-incrementing primary key
    - timestamp: When the operation occurred
    - user_id: The user associated with the operation
    - pipeline_name: The pipeline that ran the operation (optional)
    - operation_type: The type of operation performed
    - input_params_json: JSON string of input parameters (optional)
    - output_ref_json: JSON string of output references (optional)
    - status: The status of the operation (default: SUCCESS)
    - notes: Additional notes about the operation (optional)
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create operations_log table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS operations_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_id TEXT NOT NULL,
        pipeline_name TEXT,
        operation_type TEXT NOT NULL,
        input_params_json TEXT,
        output_ref_json TEXT,
        status TEXT NOT NULL,
        notes TEXT
    )
    ''')
    
    # Create index on user_id for faster queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_user_id ON operations_log(user_id)
    ''')
    
    # Create index on timestamp for chronological queries
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_timestamp ON operations_log(timestamp)
    ''')
    
    conn.commit()
    conn.close()


def log_operation(db_path: str, user_id: str, operation_type: str, 
                 pipeline_name: Optional[str] = None, 
                 input_params: Optional[Dict] = None, 
                 output_ref: Optional[Dict] = None, 
                 status: str = "SUCCESS", 
                 notes: Optional[str] = None):
    """
    Log an operation to the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        user_id (str): The unique identifier for the user
        operation_type (str): The type of operation (e.g., "USER_CREATED", 
                             "PROMPT_GENERATED", etc.)
        pipeline_name (str, optional): The name of the pipeline that ran this operation
        input_params (dict, optional): Input parameters for the operation
        output_ref (dict, optional): Output references from the operation
        status (str): The status of the operation (default: "SUCCESS")
        notes (str, optional): Additional notes about the operation
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Convert dictionaries to JSON strings
    input_params_json = json.dumps(input_params) if input_params else None
    output_ref_json = json.dumps(output_ref) if output_ref else None
    
    # Get current timestamp in ISO format with microseconds for better precision
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + f'.{int(time.time() * 1000000) % 1000000:06d}'
    
    # Insert record
    cursor.execute('''
    INSERT INTO operations_log 
    (timestamp, user_id, pipeline_name, operation_type, input_params_json, 
     output_ref_json, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, user_id, pipeline_name, operation_type, input_params_json, 
          output_ref_json, status, notes))
    
    conn.commit()
    conn.close()


def get_operations_for_user(db_path: str, user_id: str) -> List[Dict]:
    """
    Retrieve all operations for a specific user.
    
    Args:
        db_path (str): Path to the SQLite database file
        user_id (str): The unique identifier for the user
    
    Returns:
        List[Dict]: A list of operation records, sorted by timestamp (newest first).
                   Each record is a dictionary with all operation details,
                   with JSON fields parsed back to Python objects.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM operations_log 
    WHERE user_id = ? 
    ORDER BY timestamp DESC
    ''', (user_id,))
    
    rows = cursor.fetchall()
    
    # Convert rows to list of dictionaries
    operations = []
    for row in rows:
        operation = dict(row)
        
        # Parse JSON strings back to dictionaries
        if operation['input_params_json']:
            operation['input_params'] = json.loads(operation['input_params_json'])
            del operation['input_params_json']
        else:
            operation['input_params'] = None
            del operation['input_params_json']
        
        if operation['output_ref_json']:
            operation['output_ref'] = json.loads(operation['output_ref_json'])
            del operation['output_ref_json']
        else:
            operation['output_ref'] = None
            del operation['output_ref_json']
        
        operations.append(operation)
    
    conn.close()
    return operations