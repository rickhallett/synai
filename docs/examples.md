# SPCF Usage Examples

## Complete User Onboarding Flow

This example demonstrates the full workflow from user creation to seed prompt generation.

```python
from synai_factory import default_factory

# Step 1: Create a new user
user_identifier = "sarah.jones@example.com"
user_id = default_factory.create_user(user_identifier)
print(f"Created user with ID: {user_id}")

# Step 2: Generate initial assessment prompt
assessment_path = default_factory.generate_user_assessment_prompt(user_id)
print(f"Assessment prompt saved at: {assessment_path}")

# Step 3: Add context files
context_files = {
    "personal_background.txt": """
    I've been struggling with anxiety for the past few years, particularly 
    in work situations. I tend to avoid difficult conversations and often 
    procrastinate on challenging tasks.
    """,
    
    "values_exploration.md": """
    # My Core Values
    
    Through reflection, I've identified these as important to me:
    - **Family**: Being present and supportive for my loved ones
    - **Growth**: Continuous learning and self-improvement
    - **Authenticity**: Being true to myself and my beliefs
    - **Health**: Taking care of my physical and mental wellbeing
    """,
    
    "current_challenges.txt": """
    Current challenges I'm facing:
    1. Difficulty speaking up in meetings
    2. Avoiding conflict with my manager
    3. Feeling overwhelmed by project deadlines
    4. Struggling to maintain work-life balance
    """
}

# Add each context file
for filename, content in context_files.items():
    default_factory.add_context_file(user_id, filename, content)
    print(f"Added context file: {filename}")

# Step 4: Aggregate context
context_string = default_factory.get_user_context_string(user_id)
print(f"Aggregated {len(context_string)} characters of context")

# Step 5: Prepare designer LLM input
designer_input = default_factory.prepare_designer_llm_input(context_string)
print("Prepared designer input for LLM processing")

# Step 6: (External) Send designer_input to your LLM service
# designer_response = call_llm_api(designer_input)

# Step 7: Process designer output (mock response for example)
designer_response = """<?xml version="1.0" encoding="UTF-8"?>
<synai>
    <mode>seed</mode>
    <version>1.0</version>
    <preloaded_data>
        <psychological_profile>
            <concepts>
                <concept>
                    <id>work_anxiety_001</id>
                    <type>emotion</type>
                    <content>Anxiety in work situations</content>
                    <act_dimension>experiential_avoidance</act_dimension>
                    <harris_area>C</harris_area>
                    <weight>0.85</weight>
                    <links>["avoidance_pattern_001", "procrastination_001"]</links>
                </concept>
                <concept>
                    <id>avoidance_pattern_001</id>
                    <type>behavior</type>
                    <content>Avoiding difficult conversations</content>
                    <act_dimension>experiential_avoidance</act_dimension>
                    <harris_area>C</harris_area>
                    <weight>0.75</weight>
                </concept>
            </concepts>
            <values>
                <value>
                    <id>family_value_001</id>
                    <content>Being present and supportive for loved ones</content>
                    <harris_area>D</harris_area>
                    <importance>0.9</importance>
                </value>
            </values>
        </psychological_profile>
    </preloaded_data>
</synai>"""

seed_path = default_factory.process_designer_llm_output(designer_response, user_id)
print(f"Seed prompt generated at: {seed_path}")

# Step 8: Get user summary
summary = default_factory.get_user_summary(user_id)
print(f"\nUser Summary:")
print(f"  Total operations: {summary['total_operations']}")
print(f"  Files created: {summary['file_counts']}")
```

## Using Pipelines

### Simple User Onboarding (No Context)

```python
from synai_factory import default_factory

# One-line user creation with assessment prompt
user_id = default_factory.onboard_new_user_no_context("john@example.com")

# Check what was created
summary = default_factory.get_user_summary(user_id)
print(f"Created user {user_id} with {summary['file_counts']['prompts']} prompt(s)")
```

### Context-Based Onboarding

```python
from synai_factory import default_factory

# Create user prepared for context processing
user_id = default_factory.onboard_user_with_context_to_seed("alice@example.com")

# Get the context directory path
paths = default_factory.get_user_paths(user_id)
print(f"Add context files to: {paths['context']}")

# After adding files manually or programmatically...
context = default_factory.get_user_context_string(user_id)
if context:
    designer_input = default_factory.prepare_designer_llm_input(context)
    # Send to LLM...
```

### Full Pipeline with All Data

```python
from synai_factory import default_factory

# Prepare all data upfront
user_identifier = "bob@example.com"
context_files = {
    "history.txt": "Personal history information...",
    "goals.md": "# Therapy Goals\n- Reduce anxiety\n- Improve relationships"
}
designer_response = "<synai>...</synai>"  # From LLM

# Run complete pipeline
result = default_factory.full_user_onboarding(
    user_identifier, 
    context_files, 
    designer_response
)

print(f"User ID: {result['user_id']}")
print(f"Assessment: {result['assessment_path']}")
print(f"Seed: {result['seed_path']}")
```

## Database Operations

### Logging Custom Operations

```python
from synai_factory import default_factory

# Log a custom operation
default_factory.log_operation(
    user_id=user_id,
    operation_type="CUSTOM_ANALYSIS",
    input_params={
        "analysis_type": "sentiment",
        "source": "user_feedback"
    },
    output_ref={
        "result_file": "/path/to/analysis.json",
        "score": 0.85
    },
    status="SUCCESS",
    notes="Sentiment analysis completed successfully"
)
```

### Querying Operation History

```python
from synai_factory import default_factory

# Get all operations for a user
operations = default_factory.get_operations_for_user(user_id)

# Filter by operation type
assessment_ops = [op for op in operations 
                 if op['operation_type'] == 'ASSESSMENT_PROMPT_GENERATED']

# Find failed operations
failed_ops = [op for op in operations if op['status'] == 'FAILED']

# Get operations from specific pipeline
pipeline_ops = [op for op in operations 
               if op['pipeline_name'] == 'onboard_user_with_context_to_seed']

# Display operation timeline
for op in operations[:5]:  # Last 5 operations
    print(f"{op['timestamp']}: {op['operation_type']} - {op['status']}")
```

## Batch Processing

### Process Multiple Users

```python
from synai_factory import default_factory
import csv

# Read user list from CSV
with open('users.csv', 'r') as f:
    reader = csv.DictReader(f)
    users = list(reader)

# Process each user
results = []
for user_data in users:
    try:
        # Create user
        user_id = default_factory.create_user(user_data['email'])
        
        # Add their context
        if 'background' in user_data:
            default_factory.add_context_file(
                user_id, 
                'background.txt', 
                user_data['background']
            )
        
        # Generate assessment
        assessment = default_factory.generate_user_assessment_prompt(user_id)
        
        results.append({
            'email': user_data['email'],
            'user_id': user_id,
            'status': 'success'
        })
        
    except Exception as e:
        results.append({
            'email': user_data['email'],
            'status': 'failed',
            'error': str(e)
        })

# Summary
successful = sum(1 for r in results if r['status'] == 'success')
print(f"Processed {successful}/{len(users)} users successfully")
```

## Working with Templates

### Loading and Customizing Templates

```python
from synai_factory import default_factory

# Load a base template
template_content = default_factory.load_base_prompt('synai_assessment.xml')

# Customize it (example: add session-specific instructions)
import xml.etree.ElementTree as ET

root = ET.fromstring(template_content)
instructions = root.find('.//instructions')
if instructions is not None:
    instructions.text += "\n\nFocus on work-related anxiety for this session."

# Save customized version
custom_content = ET.tostring(root, encoding='unicode')
prompt_path = default_factory.save_user_prompt(
    user_id,
    'custom_assessment.xml',
    custom_content
)
```

## Error Handling

### Robust Pipeline Execution

```python
from synai_factory import default_factory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_onboard_user(user_identifier):
    """Safely onboard a user with comprehensive error handling."""
    try:
        # Try to create user
        user_id = default_factory.create_user(user_identifier)
        logger.info(f"Created user: {user_id}")
        
        try:
            # Generate assessment prompt
            assessment = default_factory.generate_user_assessment_prompt(user_id)
            logger.info(f"Generated assessment: {assessment}")
            
        except Exception as e:
            # Log failure but don't stop
            logger.error(f"Failed to generate assessment: {e}")
            default_factory.log_operation(
                user_id=user_id,
                operation_type="ASSESSMENT_GENERATION_FAILED",
                status="FAILED",
                notes=str(e)
            )
            
        return user_id
        
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        # Log to database if possible
        try:
            default_factory.log_operation(
                user_id="UNKNOWN",
                operation_type="USER_CREATION_FAILED",
                input_params={"identifier": user_identifier},
                status="FAILED",
                notes=str(e)
            )
        except:
            pass  # Database might not be accessible
        raise
```

## Command-Line Script Usage

### Using the Provided Scripts

```bash
# Initialize the system
python scripts/setup_project.py

# Create a simple user
python scripts/onboard_user.py "user@example.com"

# Create user with context preparation
python scripts/onboard_user.py "user@example.com" --with-context

# List all users with details
python scripts/list_users.py --detailed

# Process designer output
python scripts/generate_seed.py abc123def456 designer_output.xml --extract-data
```

### Creating Custom Scripts

```python
#!/usr/bin/env python3
"""Custom script to analyze user patterns."""

import sys
sys.path.append('.')  # Add current directory to path

from synai_factory import default_factory
from collections import Counter

# Get all users
users = default_factory.get_all_users()

# Analyze operation patterns
all_operations = []
for user_id in users:
    ops = default_factory.get_operations_for_user(user_id)
    all_operations.extend(ops)

# Count operation types
op_counts = Counter(op['operation_type'] for op in all_operations)

# Display results
print("Operation Type Analysis:")
for op_type, count in op_counts.most_common():
    print(f"  {op_type}: {count}")

# Find users with most operations
user_op_counts = Counter(op['user_id'] for op in all_operations)
print(f"\nMost active users:")
for user_id, count in user_op_counts.most_common(5):
    print(f"  {user_id}: {count} operations")
```

## Testing Your Implementation

### Unit Test Example

```python
import unittest
from synai_factory import SynaiFactory
import tempfile
import os

class TestSynaiFactory(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.factory = SynaiFactory(db_path=self.db_path)
    
    def test_user_creation_flow(self):
        # Create user
        user_id = self.factory.create_user("test@example.com")
        self.assertEqual(len(user_id), 16)
        
        # Verify paths exist
        paths = self.factory.get_user_paths(user_id)
        for path in paths.values():
            self.assertTrue(os.path.exists(path))
        
        # Add context
        self.factory.add_context_file(user_id, "test.txt", "Test content")
        
        # Get context
        context = self.factory.get_user_context_string(user_id)
        self.assertIn("Test content", context)
        
    def tearDown(self):
        # Clean up
        import shutil
        shutil.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
```