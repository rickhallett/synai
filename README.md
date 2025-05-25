# Synai Prompt & Context Factory (SPCF)

A Python-based utility for managing the creation, personalization, lifecycle, and tracking of prompts and contextual data for the "Synai" AI persona.

## Features

- **User Organization**: Systematically organize all data related to individual users
- **Prompt Automation**: Generate and manage user-specific prompts from templates
- **Context Management**: Aggregate and process user context files
- **Operation Tracking**: SQLite database logging for complete auditability
- **Flexible Pipelines**: Pre-defined workflows for common operations
- **Minimal Dependencies**: Uses only Python standard library

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/synai.git
cd synai

# Initialize the project
python scripts/setup_project.py
```

## Quick Start

### Using the Factory API

```python
from synai_factory import default_factory

# Create a new user
user_id = default_factory.create_user("john@example.com")

# Generate an assessment prompt
assessment_path = default_factory.generate_user_assessment_prompt(user_id)

# Add context files
default_factory.add_context_file(user_id, "background.txt", "User background information...")

# Get aggregated context
context_string = default_factory.get_user_context_string(user_id)

# Prepare designer LLM input
designer_input = default_factory.prepare_designer_llm_input(context_string)

# Process designer output (after LLM call)
seed_path = default_factory.process_designer_llm_output(designer_output, user_id)
```

### Using Command-Line Scripts

```bash
# Onboard a new user
python scripts/onboard_user.py "user@example.com"

# Onboard with context preparation
python scripts/onboard_user.py "user@example.com" --with-context

# Generate seed from designer output
python scripts/generate_seed.py <user_id> designer_output.xml

# List all users
python scripts/list_users.py --detailed
```

## Project Structure

```
synai/
├── base_prompts/              # XML prompt templates
│   ├── synai_assessment.xml   # Initial assessment template
│   └── synai_designer.xml     # Designer mode template
├── data/                      # User data and database
│   ├── users/                 # User-specific directories
│   │   └── [user_id]/
│   │       ├── context/       # User context files
│   │       ├── prompts/       # Generated prompts
│   │       ├── seeds/         # Seed prompts
│   │       ├── feedback/      # User feedback
│   │       └── interaction_dumps/
│   └── spcf.db               # Operations database
├── scripts/                   # Command-line utilities
├── *.py                      # Core modules
└── test_*.py                 # Test files
```

## Core Modules

### `synai_factory.py`
Main entry point providing the `SynaiFactory` class and `default_factory` instance.

### `user_manager.py`
- `create_user(user_identifier)`: Create new user with unique ID
- `get_user_paths(user_id)`: Get all paths for a user

### `prompt_manager.py`
- `load_base_prompt(template_name)`: Load XML templates
- `generate_user_assessment_prompt(user_id)`: Create user-specific prompts
- `save_user_prompt(user_id, filename, content, subfolder)`: Save prompts

### `context_processor.py`
- `get_user_context_string(user_id)`: Aggregate context files

### `llm_orchestrator.py`
- `prepare_designer_llm_input(context)`: Prepare LLM inputs
- `process_designer_llm_output(xml_response, user_id)`: Process LLM outputs

### `db_manager.py`
- `setup_database(db_path)`: Initialize SQLite database
- `log_operation(...)`: Log factory operations
- `get_operations_for_user(user_id)`: Retrieve operation history

### `pipelines.py`
Pre-defined workflows:
- `pipeline_onboard_new_user_no_context(user_identifier, db_path)`
- `pipeline_onboard_user_with_context_to_seed(user_identifier, db_path)`
- `pipeline_process_seed_from_designer_output(user_id, designer_output, db_path)`

## Configuration

Settings can be customized via environment variables (prefix with `SPCF_`):
- `SPCF_DATA_DIR`: Override data directory location
- `SPCF_DB_PATH`: Override database location
- `SPCF_BASE_PROMPTS_DIR`: Override prompt templates location

See `config.py` for all available settings.

## Database Schema

The SQLite database tracks all operations:

```sql
CREATE TABLE operations_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_id TEXT NOT NULL,
    pipeline_name TEXT,
    operation_type TEXT NOT NULL,
    input_params_json TEXT,
    output_ref_json TEXT,
    status TEXT NOT NULL,
    notes TEXT
);
```

## Testing

Run all tests:
```bash
# Individual module tests
python test_utils.py
python test_user_manager.py
python test_prompt_manager.py
python test_context_processor.py
python test_db_manager.py
python test_llm_orchestrator.py
python test_pipelines.py
python test_synai_factory.py
python test_config.py

# Or run all tests with a single script (create if needed)
```

## ACT Framework Integration

Synai implements Acceptance and Commitment Therapy (ACT) principles:

- **ACT Hexaflex Dimensions**: Maps concepts to experiential avoidance, cognitive fusion, etc.
- **Harris Formulation Areas (A-H)**:
  - A: Presenting Problem
  - B: Fusion/Barriers
  - C: Experiential Avoidance
  - D: Values
  - E: Committed Action
  - F: Self-as-Context
  - G: Present Moment Contact
  - H: Strengths/Resources

## Development Workflow

1. **Setup**: Run `scripts/setup_project.py`
2. **Create User**: Use factory API or `scripts/onboard_user.py`
3. **Add Context**: Place files in user's context directory
4. **Generate Prompts**: Use pipelines to process context
5. **Track Operations**: Query database for audit trail

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues or questions, please open an issue on GitHub.