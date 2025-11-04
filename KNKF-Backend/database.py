#!/usr/bin/env python3
"""
Database utilities for KNKF Competition Scraper with Supabase integration
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseDatabase:
    """Supabase database integration for KNKF competitions"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.table_name = os.getenv("COMPETITIONS_TABLE", "competitions")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in your .env file."
            )
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("Connected to Supabase database")
    
    def create_table_if_not_exists(self):
        """Create the competitions table if it doesn't exist (SQL to run in Supabase dashboard)"""
        sql_schema = f"""
-- Create competitions table
CREATE TABLE IF NOT EXISTS {self.table_name} (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    organization VARCHAR(255),
    status VARCHAR(100),
    capacity VARCHAR(50),
    start_date DATE,
    end_date DATE,
    url TEXT,
    qualification_required BOOLEAN DEFAULT FALSE,
    competition_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    -- Create unique constraint on name and start_date to prevent duplicates
    UNIQUE(name, start_date)
);

-- Create an index on start_date for better query performance
CREATE INDEX IF NOT EXISTS idx_competitions_start_date ON {self.table_name}(start_date);

-- Create an index on status
CREATE INDEX IF NOT EXISTS idx_competitions_status ON {self.table_name}(status);

-- Create RLS (Row Level Security) policy if needed
-- ALTER TABLE {self.table_name} ENABLE ROW LEVEL SECURITY;
"""
        return sql_schema
    
    def insert_competition(self, competition: Dict) -> Optional[Dict]:
        """Insert a single competition into the database"""
        try:
            # Prepare data for insertion
            data = {
                'name': competition.get('name'),
                'location': competition.get('location'),
                'organization': competition.get('organization'),
                'status': competition.get('status'),
                'capacity': competition.get('capacity'),
                'start_date': competition.get('start_date'),
                'end_date': competition.get('end_date'),
                'url': competition.get('url'),
                'qualification_required': competition.get('qualification_required', False),
                'competition_type': competition.get('competition_type'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            result = self.client.table(self.table_name).insert(data).execute()
            
            if result.data:
                logger.info(f"Inserted competition: {competition.get('name')}")
                return result.data[0]
            else:
                logger.warning(f"Failed to insert competition: {competition.get('name')}")
                return None
                
        except Exception as e:
            logger.error(f"Error inserting competition {competition.get('name', 'Unknown')}: {e}")
            return None
    
    def upsert_competition(self, competition: Dict) -> Optional[Dict]:
        """Insert or update a competition (based on name and start_date)"""
        try:
            # Prepare data for upsert
            data = {
                'name': competition.get('name'),
                'location': competition.get('location'),
                'organization': competition.get('organization'),
                'status': competition.get('status'),
                'capacity': competition.get('capacity'),
                'start_date': competition.get('start_date'),
                'end_date': competition.get('end_date'),
                'url': competition.get('url'),
                'qualification_required': competition.get('qualification_required', False),
                'competition_type': competition.get('competition_type'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}
            
            # Upsert based on name and start_date
            result = self.client.table(self.table_name).upsert(
                data, 
                on_conflict='name,start_date'
            ).execute()
            
            if result.data:
                logger.info(f"Upserted competition: {competition.get('name')}")
                return result.data[0]
            else:
                logger.warning(f"Failed to upsert competition: {competition.get('name')}")
                return None
                
        except Exception as e:
            logger.error(f"Error upserting competition {competition.get('name', 'Unknown')}: {e}")
            return None
    
    def bulk_upsert_competitions(self, competitions: List[Dict]) -> int:
        """Bulk upsert multiple competitions"""
        successful_count = 0
        
        for competition in competitions:
            if self.upsert_competition(competition):
                successful_count += 1
        
        logger.info(f"Successfully upserted {successful_count}/{len(competitions)} competitions")
        return successful_count
    
    def get_all_competitions(self) -> List[Dict]:
        """Retrieve all competitions from the database"""
        try:
            result = self.client.table(self.table_name).select("*").order("start_date").execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error retrieving competitions: {e}")
            return []
    
    def get_upcoming_competitions(self, from_date: str = None) -> List[Dict]:
        """Get upcoming competitions (from today or specified date)"""
        try:
            if not from_date:
                from_date = datetime.now().date().isoformat()
            
            result = self.client.table(self.table_name).select("*").gte(
                "start_date", from_date
            ).order("start_date").execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error retrieving upcoming competitions: {e}")
            return []
    
    def delete_competition(self, competition_id: int) -> bool:
        """Delete a competition by ID"""
        try:
            result = self.client.table(self.table_name).delete().eq("id", competition_id).execute()
            logger.info(f"Deleted competition with ID: {competition_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting competition {competition_id}: {e}")
            return False
    
    def get_competitions_by_type(self, competition_type: str) -> List[Dict]:
        """Get competitions by type (Classic, Equipped, Beginner, etc.)"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                "competition_type", competition_type
            ).order("start_date").execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error retrieving competitions by type {competition_type}: {e}")
            return []
    
    def get_competitions_requiring_qualification(self) -> List[Dict]:
        """Get competitions that require qualification"""
        try:
            result = self.client.table(self.table_name).select("*").eq(
                "qualification_required", True
            ).order("start_date").execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error retrieving qualification competitions: {e}")
            return []


def print_table_schema():
    """Print the SQL schema for creating the competitions table"""
    table_name = os.getenv("COMPETITIONS_TABLE", "competitions")
    
    sql_schema = f"""
-- Create competitions table
CREATE TABLE IF NOT EXISTS {table_name} (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    organization VARCHAR(255),
    status VARCHAR(100),
    capacity VARCHAR(50),
    start_date DATE,
    end_date DATE,
    url TEXT,
    qualification_required BOOLEAN DEFAULT FALSE,
    competition_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    -- Create unique constraint on name and start_date to prevent duplicates
    UNIQUE(name, start_date)
);

-- Create an index on start_date for better query performance
CREATE INDEX IF NOT EXISTS idx_competitions_start_date ON {table_name}(start_date);

-- Create an index on status
CREATE INDEX IF NOT EXISTS idx_competitions_status ON {table_name}(status);

-- Create RLS (Row Level Security) policy if needed
-- ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
"""
    
    print("Run this SQL in your Supabase SQL Editor to create the table:")
    print("=" * 60)
    print(sql_schema)


if __name__ == "__main__":
    # Print table schema
    print_table_schema()
    
    print("\nTo use this module:")
    print("1. Copy .env.example to .env")
    print("2. Fill in your Supabase credentials")
    print("3. Run the SQL schema above in your Supabase dashboard")