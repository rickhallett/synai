"""
Context processing module for the Synai Prompt & Context Factory (SPCF).

This module handles the aggregation of user context files into a single
string that can be used for LLM processing.
"""

import os
from utils import read_file
from user_manager import get_user_paths


def get_user_context_string(user_id: str) -> str:
    """
    Aggregate all context files for a user into a single string.
    
    This function reads all text and markdown files from the user's
    context directory and concatenates them with headers indicating
    the source file.
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        str: The aggregated context string with all file contents.
             Returns empty string if no context files are found.
    
    Raises:
        ValueError: If the context directory does not exist for the user
    """
    user_paths = get_user_paths(user_id)
    context_dir = user_paths['context']
    
    if not os.path.exists(context_dir):
        raise ValueError(f"Context directory not found for user_id: {user_id}")
    
    # Get all text and markdown files
    context_files = [
        f for f in os.listdir(context_dir) 
        if f.endswith(('.txt', '.md')) and os.path.isfile(os.path.join(context_dir, f))
    ]
    
    if not context_files:
        return ""  # No context files found
    
    # Sort files for consistent ordering
    context_files.sort()
    
    # Concatenate file contents with headers
    aggregated_context = []
    for filename in context_files:
        file_path = os.path.join(context_dir, filename)
        content = read_file(file_path)
        
        # Add header with filename and separator
        header = f"### Context from {filename} ###"
        separator = "-" * len(header)
        
        aggregated_context.append(f"{header}\n{separator}\n{content}")
    
    return "\n\n".join(aggregated_context)