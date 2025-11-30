"""
Database Handler for Colosseum Profiles
Manages all database operations for storing Colosseum profile data.
"""

from supabase import create_client, Client
from typing import Dict, Any, Optional, List, Set
import json

from config import SUPABASE_URL, SUPABASE_KEY


class ColosseumDatabase:
    """Supabase database handler for Colosseum profiles."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.table_name = "colosseum_profiles"
        print(f"Connected to Supabase: {SUPABASE_URL}")
    
    def insert_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Insert or update a single profile in the database.
        Uses username as unique identifier for upsert logic.
        
        Args:
            profile_data: Dictionary with profile fields
            
        Returns:
            True if successful, False otherwise
        """
        try:
            username = profile_data.get("username")
            if not username:
                print("    Error: No username in profile data")
                return False
            
            # Convert list fields to JSONB format if they're lists
            profile_data = self._prepare_profile_data(profile_data)
            
            # Check if profile already exists
            existing = self.client.table(self.table_name)\
                .select("id")\
                .eq("username", username)\
                .execute()
            
            if existing.data:
                # Update existing record
                self.client.table(self.table_name)\
                    .update(profile_data)\
                    .eq("username", username)\
                    .execute()
                print(f"    Updated: {username}")
            else:
                # Insert new record
                self.client.table(self.table_name)\
                    .insert(profile_data)\
                    .execute()
                print(f"    Inserted: {username}")
            
            return True
            
        except Exception as e:
            print(f"    Database error: {e}")
            return False
    
    def _prepare_profile_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare profile data for database insertion.
        Ensures JSONB fields are in the correct format (lists/dicts, not strings).
        Removes any fields not in the database schema.
        """
        prepared = data.copy()
        
        # Remove internal fields that aren't in the database
        internal_fields = ['card_index']
        for field in internal_fields:
            prepared.pop(field, None)
        
        # Fields that should be JSONB arrays
        jsonb_fields = ['tags', 'languages', 'i_am_a_roles', 'looking_for_roles', 'interested_in_topics']
        
        for field in jsonb_fields:
            if field in prepared:
                value = prepared[field]
                # Supabase Python client expects lists/dicts directly, not JSON strings
                if value is None:
                    prepared[field] = []
                elif isinstance(value, str):
                    # If it's a string, try to parse it as JSON
                    try:
                        prepared[field] = json.loads(value)
                    except:
                        prepared[field] = []
                # If it's already a list, keep it as is
        
        return prepared
    
    def insert_batch(self, profiles: List[Dict[str, Any]]) -> int:
        """
        Insert multiple profiles.
        
        Args:
            profiles: List of profile dictionaries
            
        Returns:
            Count of successful inserts/updates
        """
        success_count = 0
        for profile in profiles:
            if self.insert_profile(profile):
                success_count += 1
        return success_count
    
    def get_existing_usernames(self) -> Set[str]:
        """
        Get all existing usernames to avoid re-scraping.
        
        Returns:
            Set of usernames already in database
        """
        try:
            result = self.client.table(self.table_name)\
                .select("username")\
                .execute()
            return {row["username"] for row in result.data if row.get("username")}
        except Exception as e:
            print(f"Error fetching existing usernames: {e}")
            return set()
    
    def get_profile_count(self) -> int:
        """
        Get total number of profiles in database.
        
        Returns:
            Total count of profiles
        """
        try:
            result = self.client.table(self.table_name)\
                .select("id", count="exact")\
                .execute()
            return result.count or 0
        except Exception as e:
            print(f"Error getting count: {e}")
            return 0
    
    def get_profiles_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Get all profiles for a specific location.
        
        Args:
            location: Location string
            
        Returns:
            List of profile dictionaries
        """
        try:
            result = self.client.table(self.table_name)\
                .select("*")\
                .eq("location", location)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error fetching profiles: {e}")
            return []
    
    def get_profiles_looking_for_teammates(self) -> List[Dict[str, Any]]:
        """
        Get all profiles that are looking for teammates.
        
        Returns:
            List of profile dictionaries
        """
        try:
            result = self.client.table(self.table_name)\
                .select("*")\
                .eq("looking_for_teammates", True)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error fetching profiles: {e}")
            return []
    
    def delete_profile(self, username: str) -> bool:
        """
        Delete a profile by username.
        
        Args:
            username: Username of the profile to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.table(self.table_name)\
                .delete()\
                .eq("username", username)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test database connection.
        
        Returns:
            True if connection is working
        """
        try:
            self.client.table(self.table_name).select("id").limit(1).execute()
            print("Database connection successful!")
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

