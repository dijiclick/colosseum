-- Colosseum Profiles Crawler - Database Setup
-- Run in Supabase Dashboard -> SQL Editor

-- OPTION 1: If you want to start fresh (delete all data)
-- Uncomment the line below:
-- DROP TABLE IF EXISTS colosseum_profiles;

-- Create table
CREATE TABLE IF NOT EXISTS colosseum_profiles (
    id SERIAL PRIMARY KEY,
    
    -- Basic profile info (from listing card)
    username TEXT UNIQUE NOT NULL,           -- e.g., "@dopevelli"
    display_name TEXT,                       -- e.g., "DOPE"
    description TEXT,                        -- Short description from card
    location TEXT,                           -- e.g., "Toronto"
    
    -- Arrays stored as JSONB
    tags JSONB DEFAULT '[]'::jsonb,         -- Role tags like ["PRODUCT MANAGER", "MARKETER"]
    languages JSONB DEFAULT '[]'::jsonb,     -- e.g., ["English", "Spanish"]
    
    -- Detailed profile info (from detail view)
    company TEXT,                            -- e.g., "LOOP"
    looking_for_teammates BOOLEAN DEFAULT FALSE,
    project_description TEXT,               -- From "Looking for teammates" section
    
    -- Role and topic arrays
    i_am_a_roles JSONB DEFAULT '[]'::jsonb,  -- Roles user has (e.g., ["PRODUCT DESIGNER", "VISUAL DESIGNER"])
    looking_for_roles JSONB DEFAULT '[]'::jsonb,  -- Roles user is looking for
    interested_in_topics JSONB DEFAULT '[]'::jsonb,  -- Topics of interest (e.g., ["DEFI", "PAYMENTS"])
    
    -- Additional info
    about TEXT,                              -- Full about text
    profile_url TEXT,                        -- URL to profile page
    avatar_url TEXT,                         -- Avatar image URL
    
    -- Metadata
    source_url TEXT,                         -- Original URL where profile was found
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add columns if table already exists (for updates)
DO $$ 
BEGIN
    -- Add company if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='company') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN company TEXT;
    END IF;
    
    -- Add looking_for_teammates if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='looking_for_teammates') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN looking_for_teammates BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Add project_description if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='project_description') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN project_description TEXT;
    END IF;
    
    -- Add i_am_a_roles if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='i_am_a_roles') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN i_am_a_roles JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Add looking_for_roles if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='looking_for_roles') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN looking_for_roles JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Add interested_in_topics if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='interested_in_topics') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN interested_in_topics JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Add about if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='about') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN about TEXT;
    END IF;
    
    -- Add profile_url if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='profile_url') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN profile_url TEXT;
    END IF;
    
    -- Add avatar_url if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='avatar_url') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN avatar_url TEXT;
    END IF;
    
    -- Add scraped_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='scraped_at') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_colosseum_username ON colosseum_profiles(username);
CREATE INDEX IF NOT EXISTS idx_colosseum_display_name ON colosseum_profiles(display_name);
CREATE INDEX IF NOT EXISTS idx_colosseum_location ON colosseum_profiles(location);
CREATE INDEX IF NOT EXISTS idx_colosseum_looking_for_teammates ON colosseum_profiles(looking_for_teammates);
CREATE INDEX IF NOT EXISTS idx_colosseum_tags ON colosseum_profiles USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_colosseum_languages ON colosseum_profiles USING GIN(languages);
CREATE INDEX IF NOT EXISTS idx_colosseum_i_am_a_roles ON colosseum_profiles USING GIN(i_am_a_roles);
CREATE INDEX IF NOT EXISTS idx_colosseum_looking_for_roles ON colosseum_profiles USING GIN(looking_for_roles);
CREATE INDEX IF NOT EXISTS idx_colosseum_interested_in_topics ON colosseum_profiles USING GIN(interested_in_topics);

-- Auto-update timestamp function
CREATE OR REPLACE FUNCTION update_colosseum_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
DROP TRIGGER IF EXISTS trg_update_colosseum_timestamp ON colosseum_profiles;
CREATE TRIGGER trg_update_colosseum_timestamp
    BEFORE UPDATE ON colosseum_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_colosseum_updated_at();

-- Enable RLS
ALTER TABLE colosseum_profiles ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for anon key)
DROP POLICY IF EXISTS "allow_select_colosseum" ON colosseum_profiles;
DROP POLICY IF EXISTS "allow_insert_colosseum" ON colosseum_profiles;
DROP POLICY IF EXISTS "allow_update_colosseum" ON colosseum_profiles;
DROP POLICY IF EXISTS "allow_delete_colosseum" ON colosseum_profiles;

CREATE POLICY "allow_select_colosseum" ON colosseum_profiles FOR SELECT USING (true);
CREATE POLICY "allow_insert_colosseum" ON colosseum_profiles FOR INSERT WITH CHECK (true);
CREATE POLICY "allow_update_colosseum" ON colosseum_profiles FOR UPDATE USING (true);
CREATE POLICY "allow_delete_colosseum" ON colosseum_profiles FOR DELETE USING (true);

-- Verify structure
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'colosseum_profiles' 
ORDER BY ordinal_position;

