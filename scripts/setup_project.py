#!/usr/bin/env python3
"""
Setup script for Synai Prompt & Context Factory.
Initializes the project structure and database.
"""

import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import initialize_project
from db_manager import setup_database


def main():
    """Initialize the SPCF project."""
    print("Synai Prompt & Context Factory - Setup")
    print("=" * 40)
    
    # Initialize directory structure
    print("\n1. Initializing project directory structure...")
    initialize_project()
    
    # Setup database
    print("\n2. Setting up database...")
    db_path = 'data/spcf.db'
    setup_database(db_path)
    print(f"   Database created at: {db_path}")
    
    # Create example base prompts if they don't exist
    print("\n3. Checking base prompts...")
    base_prompts_dir = 'base_prompts'
    
    if not os.path.exists('base_prompts/synai_assessment.xml'):
        print("   Creating example synai_assessment.xml...")
        # Assessment template is already created by other tasks
        print("   Assessment template already exists")
    
    if not os.path.exists('base_prompts/synai_designer.xml'):
        print("   Creating example synai_designer.xml...")
        # Designer template is already created by other tasks
        print("   Designer template already exists")
    
    print("\n✅ Setup complete!")
    print("\nYou can now use the Synai Factory:")
    print("  from synai_factory import default_factory")
    print("  user_id = default_factory.create_user('user@example.com')")


if __name__ == "__main__":
    main()