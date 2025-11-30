-- Colosseum Profiles Crawler - Database Setup
-- Run in Supabase Dashboard -> SQL Editor

-- OPTION 1: If you want to start fresh (delete all data)
-- Uncomment the line below:
-- DROP TABLE IF EXISTS colosseum_profiles;

-- Create table
CREATE TABLE IF NOT EXISTS colosseum_profiles (
    id SERIAL PRIMARY KEY,
    
    -- API identifiers
    user_id INTEGER,                         -- userId from API (unique identifier)
    username TEXT UNIQUE NOT NULL,           -- e.g., "@dopevelli"
    display_name TEXT,                       -- e.g., "DOPE"
    description TEXT,                        -- Short description from card
    
    -- 1. Location (first)
    location TEXT,                           -- e.g., "Toronto, Kenya"
    
    -- 2. Languages (second)
    languages JSONB DEFAULT '[]'::jsonb,     -- e.g., ["English", "Spanish"]
    
    -- 3. Social media handles (third)
    github_handle TEXT,                      -- GitHub username
    linkedin_handle TEXT,                   -- LinkedIn URL or handle
    twitter_handle TEXT,                     -- Twitter/X username
    telegram_handle TEXT,                   -- Telegram handle
    
    -- 4. I am a roles (fourth)
    i_am_a_roles JSONB DEFAULT '[]'::jsonb,  -- jobRoles from API (e.g., ["Software Engineer", "Backend Developer"])
    
    -- 5. Interested in topics (fifth)
    interested_in_topics JSONB DEFAULT '[]'::jsonb,  -- interestedUseCases from API (e.g., ["DeFi"])
    
    -- 6. About (sixth)
    about TEXT,                              -- Full about text
    
    -- 7. The others (remaining fields)
    tags JSONB DEFAULT '[]'::jsonb,         -- Skills array (e.g., ["Anchor", "Rust", "Typescript"])
    company TEXT,                            -- Company/organization name
    current_position TEXT,                  -- Current job position/role
    is_university_student BOOLEAN DEFAULT FALSE,  -- Whether user is a student
    looking_for_teammates BOOLEAN DEFAULT FALSE,   -- lookingForCollab from API
    project_description TEXT,               -- lookingToBuild from API
    looking_for_roles JSONB DEFAULT '[]'::jsonb,  -- rolesLookingFor from API
    profile_url TEXT,                        -- URL to profile page
    avatar_url TEXT,                         -- Avatar image URL
    account_roles JSONB DEFAULT '[]'::jsonb,  -- accountRoles from profile object
    batches JSONB DEFAULT '[]'::jsonb,       -- batches from profile object
    
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
    
    -- Add social media handles if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='github_handle') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN github_handle TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='linkedin_handle') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN linkedin_handle TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='twitter_handle') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN twitter_handle TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='telegram_handle') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN telegram_handle TEXT;
    END IF;
    
    -- Add user_id if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='user_id') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN user_id INTEGER;
    END IF;
    
    -- Add is_university_student if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='is_university_student') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN is_university_student BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Add current_position if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='current_position') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN current_position TEXT;
    END IF;
    
    -- Add account_roles if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='account_roles') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN account_roles JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Add batches if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='batches') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN batches JSONB DEFAULT '[]'::jsonb;
    END IF;
    
    -- Add scraped_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='colosseum_profiles' AND column_name='scraped_at') THEN
        ALTER TABLE colosseum_profiles ADD COLUMN scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_colosseum_user_id ON colosseum_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_colosseum_username ON colosseum_profiles(username);
CREATE INDEX IF NOT EXISTS idx_colosseum_display_name ON colosseum_profiles(display_name);
CREATE INDEX IF NOT EXISTS idx_colosseum_location ON colosseum_profiles(location);
CREATE INDEX IF NOT EXISTS idx_colosseum_looking_for_teammates ON colosseum_profiles(looking_for_teammates);
CREATE INDEX IF NOT EXISTS idx_colosseum_is_university_student ON colosseum_profiles(is_university_student);
CREATE INDEX IF NOT EXISTS idx_colosseum_tags ON colosseum_profiles USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_colosseum_languages ON colosseum_profiles USING GIN(languages);
CREATE INDEX IF NOT EXISTS idx_colosseum_i_am_a_roles ON colosseum_profiles USING GIN(i_am_a_roles);
CREATE INDEX IF NOT EXISTS idx_colosseum_looking_for_roles ON colosseum_profiles USING GIN(looking_for_roles);
CREATE INDEX IF NOT EXISTS idx_colosseum_interested_in_topics ON colosseum_profiles USING GIN(interested_in_topics);
CREATE INDEX IF NOT EXISTS idx_colosseum_account_roles ON colosseum_profiles USING GIN(account_roles);
CREATE INDEX IF NOT EXISTS idx_colosseum_batches ON colosseum_profiles USING GIN(batches);

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


