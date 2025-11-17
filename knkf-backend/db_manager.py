#!/usr/bin/env python3
"""
Database management CLI for KNKF Competition Scraper
"""

import argparse
import json
from datetime import datetime
from database import SupabaseDatabase, print_table_schema


def list_competitions(args):
    """List competitions from the database"""
    db = SupabaseDatabase()
    
    if args.upcoming:
        competitions = db.get_upcoming_competitions()
        print(f"🔮 Upcoming Competitions ({len(competitions)} found)")
    elif args.type:
        competitions = db.get_competitions_by_type(args.type)
        print(f"🎯 {args.type} Competitions ({len(competitions)} found)")
    elif args.qualification:
        competitions = db.get_competitions_requiring_qualification()
        print(f"👑 Qualification Required Competitions ({len(competitions)} found)")
    else:
        competitions = db.get_all_competitions()
        print(f"🏋️‍♀️ All Competitions ({len(competitions)} found)")
    
    print("=" * 60)
    
    for i, comp in enumerate(competitions, 1):
        print(f"\n{i}. 🏆 {comp['name']}")
        if comp['start_date'] and comp['end_date']:
            if comp['start_date'] == comp['end_date']:
                print(f"   📅 Date: {comp['start_date']}")
            else:
                print(f"   📅 Dates: {comp['start_date']} to {comp['end_date']}")
        if comp['location']:
            print(f"   📍 Location: {comp['location']}")
        if comp['organization']:
            print(f"   🏢 Organization: {comp['organization']}")
        if comp['competition_type']:
            print(f"   🎯 Type: {comp['competition_type']}")
        if comp['status']:
            print(f"   ✅ Status: {comp['status']}")
        if comp['qualification_required']:
            print(f"   👑 Qualification Required: Yes")
        if comp['url']:
            print(f"   🔗 More info: {comp['url']}")
        print(f"   🆔 Database ID: {comp['id']}")
    
    if not competitions:
        print("No competitions found in the database.")


def export_competitions(args):
    """Export competitions to JSON"""
    db = SupabaseDatabase()
    competitions = db.get_all_competitions()
    
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'total_competitions': len(competitions),
        'competitions': competitions
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Exported {len(competitions)} competitions to {args.output}")


def delete_competition(args):
    """Delete a competition by ID"""
    db = SupabaseDatabase()
    
    if db.delete_competition(args.id):
        print(f"✅ Deleted competition with ID: {args.id}")
    else:
        print(f"❌ Failed to delete competition with ID: {args.id}")


def main():
    parser = argparse.ArgumentParser(description='KNKF Competition Database Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Schema command
    schema_parser = subparsers.add_parser('schema', help='Print database schema')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List competitions from database')
    list_parser.add_argument('--upcoming', action='store_true', help='Show only upcoming competitions')
    list_parser.add_argument('--type', choices=['Classic', 'Equipped', 'Beginner', 'Powerlifting'], 
                           help='Filter by competition type')
    list_parser.add_argument('--qualification', action='store_true', 
                           help='Show only competitions requiring qualification')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export competitions to JSON')
    export_parser.add_argument('--output', '-o', default='exported_competitions.json',
                             help='Output filename (default: exported_competitions.json)')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a competition by ID')
    delete_parser.add_argument('id', type=int, help='Competition ID to delete')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'schema':
            print_table_schema()
        elif args.command == 'list':
            list_competitions(args)
        elif args.command == 'export':
            export_competitions(args)
        elif args.command == 'delete':
            delete_competition(args)
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file with SUPABASE_URL and SUPABASE_KEY")
        print("2. Created the competitions table in Supabase")


if __name__ == "__main__":
    main()