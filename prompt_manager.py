"""
Prompt management module for the Synai Prompt & Context Factory (SPCF).

This module handles loading base prompts, generating user-specific prompts,
and saving prompts to user directories.
"""

import os
import time
from utils import read_file, write_file, generate_hash
from user_manager import get_user_paths


def load_base_prompt(prompt_template_name: str) -> str:
    """
    Load a base prompt template from the base_prompts directory.
    
    Args:
        prompt_template_name (str): The filename of the prompt template 
                                   (e.g., 'synai_assessment.xml')
    
    Returns:
        str: The content of the prompt template
    
    Raises:
        FileNotFoundError: If the prompt template does not exist
    """
    prompt_path = os.path.join('base_prompts', prompt_template_name)
    return read_file(prompt_path)


def generate_user_assessment_prompt(user_id: str) -> str:
    """
    Generate an assessment prompt for a user and return the file path.
    
    This function:
    1. Loads the base assessment prompt template
    2. Generates a unique filename for this user's prompt
    3. Optionally embeds the user_id in the prompt (as a comment)
    4. Saves the prompt to the user's prompts directory
    
    Args:
        user_id (str): The unique identifier for the user
    
    Returns:
        str: The full path to the saved prompt file
    """
    # Load base assessment prompt
    assessment_template = load_base_prompt('synai_assessment.xml')
    
    # Generate unique filename
    timestamp = str(time.time())
    short_hash = generate_hash(user_id + timestamp, length=8)
    filename = f"assessment_prompt_{short_hash}_{int(float(timestamp))}.xml"
    
    # Optional: Embed user_id in XML content as a comment
    # This helps with traceability
    assessment_content = assessment_template.replace(
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<?xml version="1.0" encoding="UTF-8"?>\n<!-- user_id: {user_id} -->'
    )
    
    # Save to user's prompts directory
    user_paths = get_user_paths(user_id)
    prompt_path = os.path.join(user_paths['prompts'], filename)
    write_file(prompt_path, assessment_content)
    
    return prompt_path


def save_user_prompt(user_id: str, prompt_filename: str, prompt_content: str, 
                    subfolder: str = "prompts") -> str:
    """
    Save a prompt to a user's directory and return the file path.
    
    This is a general-purpose function for saving any type of prompt
    to any of the user's subdirectories.
    
    Args:
        user_id (str): The unique identifier for the user
        prompt_filename (str): The filename for the prompt
        prompt_content (str): The content to save
        subfolder (str): The subfolder within the user's directory 
                        (default: "prompts")
    
    Returns:
        str: The full path to the saved file
    
    Raises:
        ValueError: If the specified subfolder is not valid
    """
    user_paths = get_user_paths(user_id)
    
    if subfolder not in user_paths:
        raise ValueError(f"Invalid subfolder: {subfolder}. " +
                        f"Valid options are: {', '.join(user_paths.keys())}")
    
    prompt_path = os.path.join(user_paths[subfolder], prompt_filename)
    write_file(prompt_path, prompt_content)
    
    return prompt_path