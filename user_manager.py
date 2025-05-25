"""
User management module for the Synai Prompt & Context Factory (SPCF).

This module handles user creation, identification, and path retrieval
for organizing user-specific data within the SPCF system.
"""

import os
import time
from utils import ensure_dir_exists, generate_hash


def create_user(user_identifier: str) -> str:
    """
    Create a new user with the given identifier and return the user_id.
    
    Creates a unique user_id by hashing the user_identifier combined with 
    the current timestamp, then creates the complete user directory structure.
    
    Args:
        user_identifier (str): A human-readable identifier for the user
                              (e.g., "john_doe_email")
    
    Returns:
        str: The generated unique user_id
    """
    # Generate unique user_id using hash of identifier + timestamp
    timestamp = str(time.time())
    user_id = generate_hash(user_identifier + timestamp, length=16)
    
    # Create user directory structure
    user_base_path = os.path.join('data', 'users', user_id)
    ensure_dir_exists(user_base_path)
    
    # Create subdirectories
    subdirs = ['context', 'prompts', 'seeds', 'feedback', 'interaction_dumps']
    for subdir in subdirs:
        ensure_dir_exists(os.path.join(user_base_path, subdir))
    
    return user_id


def get_user_paths(user_id: str) -> dict:
    """
    Return a dictionary of all standard paths for a user.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        dict: A dictionary containing all user-specific paths:
              - base: The user's base directory
              - context: Directory for user context files
              - prompts: Directory for generated prompts
              - seeds: Directory for seed prompts
              - feedback: Directory for user feedback
              - interaction_dumps: Directory for interaction logs
    
    Raises:
        ValueError: If the user directory does not exist
    """
    user_base_path = os.path.join('data', 'users', user_id)
    
    if not os.path.exists(user_base_path):
        raise ValueError(f"User directory not found for user_id: {user_id}")
    
    paths = {
        'base': user_base_path,
        'context': os.path.join(user_base_path, 'context'),
        'prompts': os.path.join(user_base_path, 'prompts'),
        'seeds': os.path.join(user_base_path, 'seeds'),
        'feedback': os.path.join(user_base_path, 'feedback'),
        'interaction_dumps': os.path.join(user_base_path, 'interaction_dumps')
    }
    
    return paths