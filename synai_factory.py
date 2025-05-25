"""
Synai Prompt & Context Factory (SPCF) - Main Module

This is the primary entry point for the SPCF system, providing a unified
interface to all factory operations.
"""

import os
from typing import Dict, List, Optional

# Import all modules
from utils import ensure_dir_exists, initialize_project, read_file, write_file, generate_hash
from user_manager import create_user, get_user_paths
from prompt_manager import load_base_prompt, generate_user_assessment_prompt, save_user_prompt
from context_processor import get_user_context_string
from llm_orchestrator import prepare_designer_llm_input, process_designer_llm_output, extract_seed_data
from db_manager import setup_database, log_operation, get_operations_for_user
from pipelines import (
    pipeline_onboard_new_user_no_context,
    pipeline_onboard_user_with_context_to_seed,
    pipeline_process_seed_from_designer_output,
    pipeline_full_user_onboarding_with_context
)

# Default paths
DEFAULT_DB_PATH = 'data/spcf.db'


class SynaiFactory:
    """
    Main class for Synai Prompt & Context Factory operations.
    
    This class provides a unified interface to all SPCF functionality,
    making it easy to use the factory in other applications.
    """
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """
        Initialize the Synai Factory.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        # Initialize project structure if needed
        initialize_project()
        
        # Ensure database directory exists
        ensure_dir_exists(os.path.dirname(db_path))
        
        # Setup database
        setup_database(db_path)
        
        self.db_path = db_path
    
    # User management methods
    def create_user(self, user_identifier: str) -> str:
        """Create a new user and return the user_id."""
        return create_user(user_identifier)
    
    def get_user_paths(self, user_id: str) -> Dict[str, str]:
        """Get all paths for a user."""
        return get_user_paths(user_id)
    
    # Prompt management methods
    def load_base_prompt(self, prompt_template_name: str) -> str:
        """Load a base prompt template."""
        return load_base_prompt(prompt_template_name)
    
    def generate_user_assessment_prompt(self, user_id: str) -> str:
        """Generate an assessment prompt for a user."""
        return generate_user_assessment_prompt(user_id)
    
    def save_user_prompt(self, user_id: str, prompt_filename: str, 
                        prompt_content: str, subfolder: str = "prompts") -> str:
        """Save a prompt to a user's directory."""
        return save_user_prompt(user_id, prompt_filename, prompt_content, subfolder)
    
    # Context processing methods
    def get_user_context_string(self, user_id: str) -> str:
        """Get aggregated context string for a user."""
        return get_user_context_string(user_id)
    
    def add_context_file(self, user_id: str, filename: str, content: str):
        """Add a context file for a user."""
        user_paths = get_user_paths(user_id)
        file_path = os.path.join(user_paths['context'], filename)
        write_file(file_path, content)
    
    # LLM orchestration methods
    def prepare_designer_llm_input(self, context_string: str) -> str:
        """Prepare input for the Synai Designer LLM."""
        return prepare_designer_llm_input(context_string)
    
    def process_designer_llm_output(self, designer_llm_response_xml_str: str, 
                                   user_id: str) -> str:
        """Process Synai Designer output and save as seed prompt."""
        return process_designer_llm_output(designer_llm_response_xml_str, user_id)
    
    def extract_seed_data(self, seed_prompt_path: str) -> Optional[dict]:
        """Extract structured data from a seed prompt."""
        return extract_seed_data(seed_prompt_path)
    
    # Database operations
    def log_operation(self, user_id: str, operation_type: str, 
                     pipeline_name: Optional[str] = None, 
                     input_params: Optional[Dict] = None, 
                     output_ref: Optional[Dict] = None, 
                     status: str = "SUCCESS", 
                     notes: Optional[str] = None):
        """Log an operation to the database."""
        return log_operation(
            self.db_path, user_id, operation_type, pipeline_name,
            input_params, output_ref, status, notes
        )
    
    def get_operations_for_user(self, user_id: str) -> List[Dict]:
        """Get all operations for a user."""
        return get_operations_for_user(self.db_path, user_id)
    
    def get_all_users(self) -> List[str]:
        """Get a list of all user IDs in the system."""
        users_dir = 'data/users'
        if not os.path.exists(users_dir):
            return []
        return [d for d in os.listdir(users_dir) 
                if os.path.isdir(os.path.join(users_dir, d))]
    
    # Pipeline methods
    def onboard_new_user_no_context(self, user_identifier: str) -> str:
        """Onboard a new user without context."""
        return pipeline_onboard_new_user_no_context(user_identifier, self.db_path)
    
    def onboard_user_with_context_to_seed(self, user_identifier: str) -> str:
        """Onboard a user with context and prepare for seed generation."""
        return pipeline_onboard_user_with_context_to_seed(user_identifier, self.db_path)
    
    def process_seed_from_designer_output(self, user_id: str, 
                                         designer_llm_response_xml_str: str) -> str:
        """Process designer output and create seed prompt."""
        return pipeline_process_seed_from_designer_output(
            user_id, designer_llm_response_xml_str, self.db_path
        )
    
    def full_user_onboarding(self, user_identifier: str, 
                            context_files: Dict[str, str],
                            designer_llm_response: str) -> Dict[str, str]:
        """Complete end-to-end user onboarding."""
        return pipeline_full_user_onboarding_with_context(
            user_identifier, context_files, designer_llm_response, self.db_path
        )
    
    # Utility methods
    def get_user_summary(self, user_id: str) -> Dict:
        """Get a summary of user data and operations."""
        try:
            user_paths = get_user_paths(user_id)
            operations = get_operations_for_user(self.db_path, user_id)
            
            # Count files in each directory
            file_counts = {}
            for key, path in user_paths.items():
                if key != 'base' and os.path.exists(path):
                    file_counts[key] = len(os.listdir(path))
            
            # Get operation summary
            operation_types = {}
            for op in operations:
                op_type = op['operation_type']
                operation_types[op_type] = operation_types.get(op_type, 0) + 1
            
            return {
                'user_id': user_id,
                'file_counts': file_counts,
                'total_operations': len(operations),
                'operation_types': operation_types,
                'last_operation': operations[0] if operations else None
            }
        except Exception as e:
            return {'error': str(e)}


# Create a default instance for easy import
default_factory = SynaiFactory()


def main():
    """
    Main entry point for command-line usage.
    This is a placeholder for future CLI implementation.
    """
    print("Synai Prompt & Context Factory v1.0")
    print("Use the SynaiFactory class or import default_factory for programmatic access.")
    print("\nExample usage:")
    print("  from synai_factory import default_factory")
    print("  user_id = default_factory.create_user('john@example.com')")
    print("  default_factory.generate_user_assessment_prompt(user_id)")


if __name__ == "__main__":
    main()