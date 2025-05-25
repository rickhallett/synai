# SPCF Architecture Documentation

## System Overview

The Synai Prompt & Context Factory (SPCF) is designed as a modular, extensible system for managing AI persona interactions. The architecture emphasizes separation of concerns, minimal dependencies, and comprehensive audit trails.

## Design Principles

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Minimal Dependencies**: Uses only Python standard library
3. **Extensibility**: Easy to add new pipelines and operations
4. **Auditability**: Complete operation logging in SQLite
5. **Simplicity**: Clear interfaces and predictable behavior

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SynaiFactory (Main API)                  │
├─────────────────────────────────────────────────────────────┤
│                          Pipelines                           │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ User Manager │Prompt Manager│Context Proc. │LLM Orchestrator│
├──────────────┴──────────────┴──────────────┴───────────────┤
│                      Database Manager                        │
├─────────────────────────────────────────────────────────────┤
│                    Utilities & Config                        │
└─────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

### Core Modules

#### `synai_factory.py`
- **Purpose**: Unified API interface
- **Responsibilities**:
  - Initialize system components
  - Provide convenient access to all operations
  - Manage default configuration
- **Key Classes**: `SynaiFactory`

#### `user_manager.py`
- **Purpose**: User lifecycle management
- **Responsibilities**:
  - Create unique user identifiers
  - Initialize user directory structure
  - Provide path resolution for user data
- **Key Functions**: `create_user()`, `get_user_paths()`

#### `prompt_manager.py`
- **Purpose**: Prompt template and generation management
- **Responsibilities**:
  - Load base prompt templates
  - Generate user-specific prompts
  - Save prompts to appropriate locations
- **Key Functions**: `load_base_prompt()`, `generate_user_assessment_prompt()`

#### `context_processor.py`
- **Purpose**: User context aggregation
- **Responsibilities**:
  - Read context files (.txt, .md)
  - Aggregate multiple files into single string
  - Maintain file headers for clarity
- **Key Functions**: `get_user_context_string()`

#### `llm_orchestrator.py`
- **Purpose**: LLM interaction preparation
- **Responsibilities**:
  - Prepare inputs for LLM calls
  - Process LLM outputs
  - Validate XML responses
  - Extract structured data
- **Key Functions**: `prepare_designer_llm_input()`, `process_designer_llm_output()`

### Infrastructure Modules

#### `db_manager.py`
- **Purpose**: Persistence and audit logging
- **Responsibilities**:
  - Initialize SQLite database
  - Log all operations with metadata
  - Query operation history
- **Key Functions**: `setup_database()`, `log_operation()`, `get_operations_for_user()`

#### `pipelines.py`
- **Purpose**: Orchestrate multi-step workflows
- **Responsibilities**:
  - Define standard operation sequences
  - Ensure proper logging at each step
  - Handle errors gracefully
- **Key Functions**: Various pipeline functions

#### `utils.py`
- **Purpose**: Common utility functions
- **Responsibilities**:
  - File I/O operations
  - Directory management
  - Hash generation
- **Key Functions**: `ensure_dir_exists()`, `generate_hash()`

#### `config.py`
- **Purpose**: Centralized configuration
- **Responsibilities**:
  - Define system constants
  - Manage paths
  - Support environment overrides
- **Key Constants**: `BASE_DIR`, `DATA_DIR`, `USER_SUBDIRS`

## Data Flow Patterns

### User Creation Flow
```
User Identifier → create_user() → Generate Hash → Create Directories → Return User ID
                                         ↓
                                  Log Operation
```

### Context Processing Flow
```
User ID → Get Paths → Read Context Files → Aggregate Content → Return String
                              ↓
                      Filter by Extension
```

### Prompt Generation Flow
```
User ID → Load Template → Embed Metadata → Generate Filename → Save Prompt → Return Path
                                                    ↓
                                             Log Operation
```

### Designer Pipeline Flow
```
Context String → Prepare Input → [External LLM] → Process Output → Save Seed → Return Path
                      ↓                                   ↓              ↓
                Log Prepared                    Validate XML      Log Generated
```

## Directory Structure

### Project Layout
```
synai/
├── Core Modules (*.py)
├── Test Modules (test_*.py)
├── Configuration (config.py)
├── Scripts (scripts/)
├── Documentation (docs/)
├── Base Templates (base_prompts/)
└── User Data (data/)
```

### User Data Structure
```
data/users/[user_id]/
├── context/           # Input context files
├── prompts/          # Generated prompts
├── seeds/            # Seed prompts from designer
├── feedback/         # User feedback files
└── interaction_dumps/# Interaction logs
```

## Database Schema

### operations_log Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| timestamp | TEXT | ISO format timestamp with microseconds |
| user_id | TEXT | User identifier |
| pipeline_name | TEXT | Pipeline that executed operation |
| operation_type | TEXT | Type of operation performed |
| input_params_json | TEXT | JSON-encoded input parameters |
| output_ref_json | TEXT | JSON-encoded output references |
| status | TEXT | SUCCESS, FAILED, or PENDING_LLM |
| notes | TEXT | Additional human-readable notes |

### Indexes
- `idx_user_id`: For efficient user-based queries
- `idx_timestamp`: For chronological queries

## Extension Points

### Adding New Operations

1. Define operation type in `config.py`:
```python
OPERATION_TYPES['MY_OPERATION'] = 'MY_OPERATION'
```

2. Implement operation function:
```python
def my_operation(user_id: str, **kwargs):
    # Implementation
    result = do_something()
    
    # Log operation
    log_operation(
        db_path=db_path,
        user_id=user_id,
        operation_type='MY_OPERATION',
        output_ref={'result': result}
    )
    
    return result
```

3. Add to factory or pipeline as needed

### Adding New Pipelines

1. Define pipeline in `pipelines.py`:
```python
def pipeline_my_workflow(user_identifier: str, db_path: str):
    # Step 1: Create user
    user_id = create_user(user_identifier)
    log_operation(...)
    
    # Step 2: Custom operation
    result = my_operation(user_id)
    log_operation(...)
    
    return result
```

2. Add to `SynaiFactory` class:
```python
def my_workflow(self, user_identifier: str):
    return pipeline_my_workflow(user_identifier, self.db_path)
```

### Adding New File Types

1. Update `config.py`:
```python
CONTEXT_FILE_EXTENSIONS = ('.txt', '.md', '.json')
```

2. Update `context_processor.py` if special handling needed

## Error Handling Strategy

### Principle: Fail Fast with Clear Messages

- **File Operations**: Raise `FileNotFoundError` or `IOError`
- **User Operations**: Raise `ValueError` for invalid inputs
- **Database Operations**: Let SQLite exceptions bubble up
- **Pipeline Operations**: Log failures to database when possible

### Error Propagation

```
Operation Function
    ↓ (try)
Execute Operation
    ↓ (except)
Log Failure → Re-raise Exception
    ↓
Pipeline Handler
    ↓
User/API
```

## Performance Considerations

### Current Design (Optimized for < 10,000 users)

- **File System**: Direct file I/O
- **Database**: SQLite with indexes
- **Memory**: Loads full files into memory
- **Concurrency**: Single-threaded operations

### Scaling Considerations

For larger deployments, consider:

1. **Database**: PostgreSQL for concurrent access
2. **File Storage**: Object storage (S3, etc.)
3. **Caching**: Redis for frequently accessed data
4. **Processing**: Async operations with queues
5. **API**: REST/GraphQL interface

## Security Considerations

### Current Implementation

- **User IDs**: SHA256 hashed identifiers
- **File Access**: OS-level permissions
- **Database**: Local SQLite file
- **No Network**: All operations are local

### Production Recommendations

1. **Authentication**: Add user authentication layer
2. **Authorization**: Implement role-based access
3. **Encryption**: Encrypt sensitive context data
4. **Audit Trail**: Enhanced logging with user actions
5. **Input Validation**: Stricter validation on all inputs

## Testing Strategy

### Unit Tests
- Each module has corresponding test file
- Tests focus on individual function behavior
- Mock external dependencies when needed

### Integration Tests
- Pipeline tests verify multi-step workflows
- Database tests verify persistence
- File system tests use temporary directories

### Test Coverage Goals
- Core functionality: 100%
- Error paths: 90%+
- Edge cases: Documented and tested

## Future Architecture Considerations

### Microservices Architecture
```
┌─────────┐     ┌─────────┐     ┌──────────┐
│   API   │────▶│Pipeline │────▶│   LLM    │
│ Gateway │     │ Service │     │ Service  │
└─────────┘     └─────────┘     └──────────┘
     │               │                 │
     ▼               ▼                 ▼
┌─────────┐     ┌─────────┐     ┌──────────┐
│  User   │     │Context  │     │ Prompt   │
│ Service │     │ Service │     │ Service  │
└─────────┘     └─────────┘     └──────────┘
```

### Event-Driven Architecture
- Use message queues for async operations
- Event sourcing for complete audit trail
- CQRS for read/write optimization

### Container Architecture
- Docker containers for each service
- Kubernetes for orchestration
- Helm charts for deployment