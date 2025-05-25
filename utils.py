"""
Utility functions for the Synai Prompt & Context Factory (SPCF).

This module provides core utilities for file operations, directory management,
and hashing functions used throughout the SPCF system.
"""

import hashlib
import os


def generate_hash(data_string: str, length: int = 8) -> str:
    """
    Generate a truncated SHA256 hash from the input string.
    
    Args:
        data_string (str): The string to hash
        length (int): The desired length of the truncated hash (default: 8)
    
    Returns:
        str: A truncated hash string of the specified length
    """
    hash_obj = hashlib.sha256(data_string.encode())
    return hash_obj.hexdigest()[:length]


def ensure_dir_exists(path: str):
    """
    Create directory if it doesn't exist.
    
    Args:
        path (str): The directory path to create
    """
    os.makedirs(path, exist_ok=True)


def read_file(path: str) -> str:
    """
    Read file content with error handling.
    
    Args:
        path (str): The file path to read
    
    Returns:
        str: The content of the file
    
    Raises:
        FileNotFoundError: If the file does not exist
    """
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")


def write_file(path: str, content: str):
    """
    Write content to file with error handling.
    
    Args:
        path (str): The file path to write to
        content (str): The content to write
    
    Raises:
        IOError: If there's an error writing to the file
    """
    try:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        raise IOError(f"Error writing to file {path}: {str(e)}")


def initialize_project():
    """
    Initialize the project directory structure.
    
    Creates the following directories:
    - data/
    - data/users/
    - base_prompts/
    """
    ensure_dir_exists('data')
    ensure_dir_exists('data/users')
    ensure_dir_exists('base_prompts')
    print("Project directory structure initialized.")