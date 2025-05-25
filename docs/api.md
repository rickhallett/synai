# SPCF API Documentation

## Table of Contents
- [SynaiFactory Class](#synaifactory-class)
- [User Management](#user-management)
- [Prompt Management](#prompt-management)
- [Context Processing](#context-processing)
- [LLM Orchestration](#llm-orchestration)
- [Database Operations](#database-operations)
- [Pipeline Functions](#pipeline-functions)
- [Utility Functions](#utility-functions)
- [Configuration](#configuration)

## SynaiFactory Class

The main interface for all SPCF operations.

### Constructor

```python
factory = SynaiFactory(db_path='data/spcf.db')
```

**Parameters:**
- `db_path` (str): Path to the SQLite database file. Defaults to 'data/spcf.db'.

### Default Instance

```python
from synai_factory import default_factory
```

A pre-configured instance is available for immediate use.

## User Management

### create_user

```python
user_id = factory.create_user(user_identifier)
```

Creates a new user with complete directory structure.

**Parameters:**
- `user_identifier` (str): Human-readable identifier (e.g., email address)

**Returns:**
- `str`: Unique 16-character user ID

**Example:**
```python
user_id = factory.create_user("john.doe@example.com")
# Returns: "a1b2c3d4e5f6g7h8"
```

### get_user_paths

```python
paths = factory.get_user_paths(user_id)
```

Get all directory paths for a user.

**Parameters:**
- `user_id` (str): The unique user identifier

**Returns:**
- `dict`: Dictionary with keys: 'base', 'context', 'prompts', 'seeds', 'feedback', 'interaction_dumps'

**Raises:**
- `ValueError`: If user directory doesn't exist

### get_all_users

```python
users = factory.get_all_users()
```

Get list of all user IDs in the system.

**Returns:**
- `list[str]`: List of user IDs

## Prompt Management

### load_base_prompt

```python
content = factory.load_base_prompt(prompt_template_name)
```

Load a base prompt template from the base_prompts directory.

**Parameters:**
- `prompt_template_name` (str): Filename of the template (e.g., 'synai_assessment.xml')

**Returns:**
- `str`: Content of the prompt template

**Raises:**
- `FileNotFoundError`: If template doesn't exist

### generate_user_assessment_prompt

```python
prompt_path = factory.generate_user_assessment_prompt(user_id)
```

Generate a personalized assessment prompt for a user.

**Parameters:**
- `user_id` (str): The unique user identifier

**Returns:**
- `str`: Path to the generated prompt file

### save_user_prompt

```python
prompt_path = factory.save_user_prompt(user_id, prompt_filename, 
                                      prompt_content, subfolder='prompts')
```

Save a prompt to a user's directory.

**Parameters:**
- `user_id` (str): The unique user identifier
- `prompt_filename` (str): Name for the prompt file
- `prompt_content` (str): Content to save
- `subfolder` (str): Target subdirectory (default: 'prompts')

**Returns:**
- `str`: Path to the saved file

**Raises:**
- `ValueError`: If subfolder is invalid

## Context Processing

### get_user_context_string

```python
context = factory.get_user_context_string(user_id)
```

Aggregate all context files for a user into a single string.

**Parameters:**
- `user_id` (str): The unique user identifier

**Returns:**
- `str`: Concatenated content from all .txt and .md files in context directory

**Raises:**
- `ValueError`: If context directory doesn't exist

### add_context_file

```python
factory.add_context_file(user_id, filename, content)
```

Add a context file for a user.

**Parameters:**
- `user_id` (str): The unique user identifier
- `filename` (str): Name for the context file
- `content` (str): Content to write

## LLM Orchestration

### prepare_designer_llm_input

```python
designer_input = factory.prepare_designer_llm_input(context_string)
```

Prepare input for the Synai Designer LLM.

**Parameters:**
- `context_string` (str): Aggregated user context

**Returns:**
- `str`: Complete prompt ready for LLM processing

### process_designer_llm_output

```python
seed_path = factory.process_designer_llm_output(designer_response, user_id)
```

Process designer LLM output and save as seed prompt.

**Parameters:**
- `designer_response` (str): XML response from designer LLM
- `user_id` (str): The unique user identifier

**Returns:**
- `str`: Path to saved seed prompt

**Raises:**
- `ValueError`: If XML response is invalid

### extract_seed_data

```python
data = factory.extract_seed_data(seed_prompt_path)
```

Extract structured data from a seed prompt file.

**Parameters:**
- `seed_prompt_path` (str): Path to seed prompt XML file

**Returns:**
- `dict` or `None`: Extracted data if found

## Database Operations

### log_operation

```python
factory.log_operation(user_id, operation_type, pipeline_name=None,
                     input_params=None, output_ref=None, 
                     status='SUCCESS', notes=None)
```

Log an operation to the database.

**Parameters:**
- `user_id` (str): The unique user identifier
- `operation_type` (str): Type of operation (e.g., 'USER_CREATED')
- `pipeline_name` (str, optional): Name of the pipeline
- `input_params` (dict, optional): Input parameters as dictionary
- `output_ref` (dict, optional): Output references as dictionary
- `status` (str): Operation status (default: 'SUCCESS')
- `notes` (str, optional): Additional notes

### get_operations_for_user

```python
operations = factory.get_operations_for_user(user_id)
```

Get all logged operations for a user.

**Parameters:**
- `user_id` (str): The unique user identifier

**Returns:**
- `list[dict]`: List of operation records (newest first)

### get_user_summary

```python
summary = factory.get_user_summary(user_id)
```

Get a summary of user data and operations.

**Parameters:**
- `user_id` (str): The unique user identifier

**Returns:**
- `dict`: Summary containing file counts, operation counts, and last activity

## Pipeline Functions

### onboard_new_user_no_context

```python
user_id = factory.onboard_new_user_no_context(user_identifier)
```

Complete onboarding for a new user without context.

**Parameters:**
- `user_identifier` (str): Human-readable identifier

**Returns:**
- `str`: Generated user ID

**Operations:**
1. Creates user directory structure
2. Generates assessment prompt
3. Logs both operations

### onboard_user_with_context_to_seed

```python
user_id = factory.onboard_user_with_context_to_seed(user_identifier)
```

Onboard user and prepare for context-based seed generation.

**Parameters:**
- `user_identifier` (str): Human-readable identifier

**Returns:**
- `str`: Generated user ID

**Operations:**
1. Creates user directory structure
2. Aggregates context (if available)
3. Prepares designer LLM input
4. Logs all operations with PENDING_LLM status

### process_seed_from_designer_output

```python
seed_path = factory.process_seed_from_designer_output(user_id, designer_response)
```

Process designer output into seed prompt.

**Parameters:**
- `user_id` (str): The unique user identifier
- `designer_response` (str): XML response from designer LLM

**Returns:**
- `str`: Path to saved seed prompt

### full_user_onboarding

```python
result = factory.full_user_onboarding(user_identifier, context_files, 
                                     designer_response)
```

Complete end-to-end user onboarding.

**Parameters:**
- `user_identifier` (str): Human-readable identifier
- `context_files` (dict): Dictionary of filename: content
- `designer_response` (str): Designer LLM response

**Returns:**
- `dict`: Contains 'user_id', 'assessment_path', and 'seed_path'

## Utility Functions

### utils.py

#### generate_hash

```python
hash_str = generate_hash(data_string, length=8)
```

Generate a truncated SHA256 hash.

**Parameters:**
- `data_string` (str): String to hash
- `length` (int): Desired output length (default: 8)

**Returns:**
- `str`: Truncated hash string

#### ensure_dir_exists

```python
ensure_dir_exists(path)
```

Create directory if it doesn't exist.

**Parameters:**
- `path` (str): Directory path to create

#### read_file / write_file

```python
content = read_file(path)
write_file(path, content)
```

File I/O operations with error handling.

#### initialize_project

```python
initialize_project()
```

Initialize required directory structure.

## Configuration

### Environment Variables

All settings can be overridden using environment variables with `SPCF_` prefix:

- `SPCF_DATA_DIR`: Override data directory
- `SPCF_DB_PATH`: Override database path
- `SPCF_BASE_PROMPTS_DIR`: Override templates directory

### config.py Constants

```python
from config import (
    BASE_DIR,              # Project root directory
    DATA_DIR,              # Data storage directory
    USERS_DIR,             # User directories location
    BASE_PROMPTS_DIR,      # Template location
    DB_PATH,               # Database file path
    CONTEXT_FILE_EXTENSIONS,  # ('.txt', '.md')
    USER_SUBDIRS,          # List of user subdirectories
    OPERATION_TYPES,       # Standard operation type constants
    PIPELINE_NAMES         # Standard pipeline name constants
)
```

### Helper Functions

```python
# Get user directory path
user_dir = get_user_dir_path(user_id)

# Get user subdirectory
context_dir = get_user_subdir_path(user_id, 'context')

# Validate file types
is_valid = is_valid_context_file('notes.txt')  # True
is_valid = is_valid_prompt_file('prompt.xml')   # True
```