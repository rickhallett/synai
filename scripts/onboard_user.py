#!/usr/bin/env python3
"""
Script to onboard a new user to the Synai system.
Can be used with or without context files.
"""

import os
import sys
import argparse

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synai_factory import SynaiFactory


def main():
    """Onboard a new user."""
    parser = argparse.ArgumentParser(
        description='Onboard a new user to the Synai system'
    )
    parser.add_argument(
        'user_identifier',
        help='Human-readable identifier for the user (e.g., email)'
    )
    parser.add_argument(
        '--db-path',
        default='data/spcf.db',
        help='Path to the database file (default: data/spcf.db)'
    )
    parser.add_argument(
        '--with-context',
        action='store_true',
        help='Prepare for context-based seed generation'
    )
    
    args = parser.parse_args()
    
    # Initialize factory
    factory = SynaiFactory(db_path=args.db_path)
    
    print(f"Onboarding user: {args.user_identifier}")
    print("=" * 50)
    
    try:
        if args.with_context:
            # Onboard with context preparation
            user_id = factory.onboard_user_with_context_to_seed(args.user_identifier)
            print(f"\n✅ User created with ID: {user_id}")
            print("\n📁 Context directory created at:")
            print(f"   {factory.get_user_paths(user_id)['context']}")
            print("\n📝 Next steps:")
            print("   1. Add context files to the context directory")
            print("   2. Run the designer LLM with the prepared input")
            print("   3. Use generate_seed.py to process the designer output")
        else:
            # Simple onboarding
            user_id = factory.onboard_new_user_no_context(args.user_identifier)
            print(f"\n✅ User created with ID: {user_id}")
            print("\n📄 Assessment prompt generated at:")
            
            # Get the assessment prompt path
            user_paths = factory.get_user_paths(user_id)
            prompts_dir = user_paths['prompts']
            prompt_files = [f for f in os.listdir(prompts_dir) if f.startswith('assessment_')]
            if prompt_files:
                print(f"   {os.path.join(prompts_dir, prompt_files[0])}")
        
        # Show summary
        print("\n📊 User Summary:")
        summary = factory.get_user_summary(user_id)
        print(f"   Total operations: {summary['total_operations']}")
        print(f"   File counts: {summary['file_counts']}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()