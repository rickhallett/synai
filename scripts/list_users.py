#!/usr/bin/env python3
"""
Script to list all users and their summaries.
"""

import os
import sys
import argparse

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synai_factory import SynaiFactory


def main():
    """List all users in the system."""
    parser = argparse.ArgumentParser(
        description='List all users in the Synai system'
    )
    parser.add_argument(
        '--db-path',
        default='data/spcf.db',
        help='Path to the database file (default: data/spcf.db)'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed information for each user'
    )
    
    args = parser.parse_args()
    
    # Initialize factory
    factory = SynaiFactory(db_path=args.db_path)
    
    print("Synai System - User List")
    print("=" * 50)
    
    # Get all users
    users = factory.get_all_users()
    
    if not users:
        print("\n📭 No users found in the system.")
        return
    
    print(f"\n📊 Total users: {len(users)}")
    print()
    
    for i, user_id in enumerate(users, 1):
        print(f"{i}. User ID: {user_id}")
        
        if args.detailed:
            summary = factory.get_user_summary(user_id)
            
            if 'error' not in summary:
                print(f"   📁 Files:")
                for dir_name, count in summary['file_counts'].items():
                    if count > 0:
                        print(f"      - {dir_name}: {count} file(s)")
                
                print(f"   📈 Operations: {summary['total_operations']}")
                if summary['operation_types']:
                    print("   📋 Operation breakdown:")
                    for op_type, count in summary['operation_types'].items():
                        print(f"      - {op_type}: {count}")
                
                if summary['last_operation']:
                    print(f"   ⏰ Last activity: {summary['last_operation']['timestamp']}")
                    print(f"      Type: {summary['last_operation']['operation_type']}")
            else:
                print(f"   ❌ Error getting summary: {summary['error']}")
        
        print()


if __name__ == "__main__":
    main()