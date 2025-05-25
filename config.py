"""
Configuration management module for the Synai Prompt & Context Factory (SPCF).

This module defines default paths and settings for the SPCF system.
Future versions may include YAML configuration file support.
"""

import os
from typing import Dict, Tuple, Optional

# Get the base directory (where this config.py file is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Base paths - all relative to BASE_DIR
DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_DIR = os.path.join(DATA_DIR, 'users')
BASE_PROMPTS_DIR = os.path.join(BASE_DIR, 'base_prompts')

# Database settings
DB_FILENAME = 'spcf.db'
DB_PATH = os.path.join(DATA_DIR, DB_FILENAME)

# File extensions
CONTEXT_FILE_EXTENSIONS = ('.txt', '.md')
PROMPT_FILE_EXTENSION = '.xml'

# User directory structure
USER_SUBDIRS = ['context', 'prompts', 'seeds', 'feedback', 'interaction_dumps']

# Hash settings
DEFAULT_HASH_LENGTH = 16  # For user IDs
SHORT_HASH_LENGTH = 8    # For filenames

# Logging settings
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# LLM settings (placeholders for future use)
LLM_TIMEOUT = 300  # seconds
LLM_MAX_RETRIES = 3

# Pipeline settings
PIPELINE_NAMES = {
    'ONBOARD_NO_CONTEXT': 'onboard_new_user_no_context',
    'ONBOARD_WITH_CONTEXT': 'onboard_user_with_context_to_seed',
    'PROCESS_SEED': 'process_seed_from_designer_output',
    'FULL_ONBOARDING': 'full_user_onboarding_with_context'
}

# Operation types for consistent logging
OPERATION_TYPES = {
    'USER_CREATED': 'USER_CREATED',
    'ASSESSMENT_GENERATED': 'ASSESSMENT_PROMPT_GENERATED',
    'CONTEXT_AGGREGATED': 'CONTEXT_AGGREGATED',
    'CONTEXT_FAILED': 'CONTEXT_AGGREGATION_FAILED',
    'DESIGNER_PREPARED': 'DESIGNER_INPUT_PREPARED',
    'SEED_GENERATED': 'SEED_PROMPT_GENERATED',
    'SEED_FAILED': 'SEED_GENERATION_FAILED'
}

# Status values
STATUS_SUCCESS = 'SUCCESS'
STATUS_FAILED = 'FAILED'
STATUS_PENDING = 'PENDING_LLM'


def get_config() -> Dict[str, any]:
    """
    Get the complete configuration as a dictionary.
    
    Returns:
        Dict[str, any]: Dictionary containing all configuration values
    """
    return {
        'base_dir': BASE_DIR,
        'data_dir': DATA_DIR,
        'users_dir': USERS_DIR,
        'base_prompts_dir': BASE_PROMPTS_DIR,
        'db_path': DB_PATH,
        'db_filename': DB_FILENAME,
        'context_file_extensions': CONTEXT_FILE_EXTENSIONS,
        'prompt_file_extension': PROMPT_FILE_EXTENSION,
        'user_subdirs': USER_SUBDIRS,
        'default_hash_length': DEFAULT_HASH_LENGTH,
        'short_hash_length': SHORT_HASH_LENGTH,
        'log_date_format': LOG_DATE_FORMAT,
        'llm_timeout': LLM_TIMEOUT,
        'llm_max_retries': LLM_MAX_RETRIES,
        'pipeline_names': PIPELINE_NAMES,
        'operation_types': OPERATION_TYPES,
        'status_success': STATUS_SUCCESS,
        'status_failed': STATUS_FAILED,
        'status_pending': STATUS_PENDING
    }


def get_user_dir_path(user_id: str) -> str:
    """
    Get the base directory path for a user.
    
    Args:
        user_id (str): The unique user identifier
    
    Returns:
        str: The full path to the user's directory
    """
    return os.path.join(USERS_DIR, user_id)


def get_user_subdir_path(user_id: str, subdir: str) -> str:
    """
    Get a specific subdirectory path for a user.
    
    Args:
        user_id (str): The unique user identifier
        subdir (str): The subdirectory name (e.g., 'context', 'prompts')
    
    Returns:
        str: The full path to the user's subdirectory
    
    Raises:
        ValueError: If the subdirectory name is not valid
    """
    if subdir not in USER_SUBDIRS:
        raise ValueError(f"Invalid subdirectory: {subdir}. " +
                        f"Valid options are: {', '.join(USER_SUBDIRS)}")
    
    return os.path.join(USERS_DIR, user_id, subdir)


def is_valid_context_file(filename: str) -> bool:
    """
    Check if a filename has a valid context file extension.
    
    Args:
        filename (str): The filename to check
    
    Returns:
        bool: True if the file has a valid context extension
    """
    return filename.lower().endswith(CONTEXT_FILE_EXTENSIONS)


def is_valid_prompt_file(filename: str) -> bool:
    """
    Check if a filename has a valid prompt file extension.
    
    Args:
        filename (str): The filename to check
    
    Returns:
        bool: True if the file has a valid prompt extension
    """
    return filename.lower().endswith(PROMPT_FILE_EXTENSION)


# Optional: Environment variable overrides
# This allows users to override settings via environment variables
def get_env_override(key: str, default: any) -> any:
    """
    Get a configuration value with optional environment variable override.
    
    Environment variables should be prefixed with 'SPCF_'.
    For example: SPCF_DATA_DIR, SPCF_DB_PATH
    
    Args:
        key (str): The configuration key
        default: The default value if no override exists
    
    Returns:
        The environment value if set, otherwise the default
    """
    env_key = f"SPCF_{key.upper()}"
    return os.environ.get(env_key, default)


# Apply environment overrides to key paths
DATA_DIR = get_env_override('DATA_DIR', DATA_DIR)
DB_PATH = get_env_override('DB_PATH', DB_PATH)
BASE_PROMPTS_DIR = get_env_override('BASE_PROMPTS_DIR', BASE_PROMPTS_DIR)


# Future: YAML configuration loading (placeholder for v2)
"""
def load_config_from_yaml(config_path: str) -> Dict[str, any]:
    '''
    Load configuration from a YAML file.
    
    This is a placeholder for future implementation.
    
    Args:
        config_path (str): Path to the YAML configuration file
    
    Returns:
        Dict[str, any]: Configuration dictionary
    '''
    # Future implementation would use PyYAML
    # import yaml
    # 
    # try:
    #     with open(config_path, 'r') as file:
    #         yaml_config = yaml.safe_load(file)
    #     
    #     # Merge with defaults
    #     config = get_config()
    #     config.update(yaml_config)
    #     
    #     return config
    # except Exception as e:
    #     print(f"Error loading config from {config_path}: {str(e)}")
    #     return get_config()
    
    # For now, just return defaults
    return get_config()
"""