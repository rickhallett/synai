#!/usr/bin/env python3
"""
Script to generate a seed prompt from designer LLM output.
This processes the output and saves it as a seed prompt.
"""

import os
import sys
import argparse

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synai_factory import SynaiFactory


def main():
    """Generate seed prompt from designer output."""
    parser = argparse.ArgumentParser(
        description='Generate a seed prompt from designer LLM output'
    )
    parser.add_argument(
        'user_id',
        help='The user ID to generate seed for'
    )
    parser.add_argument(
        'designer_output_file',
        help='Path to file containing designer LLM XML output'
    )
    parser.add_argument(
        '--db-path',
        default='data/spcf.db',
        help='Path to the database file (default: data/spcf.db)'
    )
    parser.add_argument(
        '--extract-data',
        action='store_true',
        help='Extract and display any embedded data from the seed'
    )
    
    args = parser.parse_args()
    
    # Initialize factory
    factory = SynaiFactory(db_path=args.db_path)
    
    print(f"Processing designer output for user: {args.user_id}")
    print("=" * 50)
    
    try:
        # Read designer output
        if not os.path.exists(args.designer_output_file):
            raise FileNotFoundError(f"Designer output file not found: {args.designer_output_file}")
        
        with open(args.designer_output_file, 'r', encoding='utf-8') as f:
            designer_output = f.read()
        
        print(f"\n📄 Read {len(designer_output)} characters from designer output")
        
        # Process the output
        seed_path = factory.process_seed_from_designer_output(args.user_id, designer_output)
        
        print(f"\n✅ Seed prompt generated successfully!")
        print(f"   Saved to: {seed_path}")
        
        # Extract data if requested
        if args.extract_data:
            print("\n🔍 Extracting seed data...")
            data = factory.extract_seed_data(seed_path)
            if data:
                import json
                print(json.dumps(data, indent=2))
            else:
                print("   No structured data found in seed")
        
        # Show user summary
        print("\n📊 User Summary:")
        summary = factory.get_user_summary(args.user_id)
        print(f"   Total operations: {summary['total_operations']}")
        print(f"   Seeds generated: {summary['file_counts'].get('seeds', 0)}")
        
        if summary['last_operation']:
            print(f"   Last operation: {summary['last_operation']['operation_type']}")
            print(f"   Timestamp: {summary['last_operation']['timestamp']}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()