CREATE TABLE IF NOT EXISTS profiles (
    id                       SERIAL PRIMARY KEY,
    uuid                     VARCHAR(255) UNIQUE NOT NULL,
    username                 VARCHAR(255) UNIQUE NOT NULL,
    first_name               VARCHAR(255),
    last_name                VARCHAR(255),
    profile_image            TEXT,
    total_hackathons_attended INT DEFAULT 0,
    total_hackathons_won      INT DEFAULT 0,
    total_projects            INT DEFAULT 0,
    total_merits              INT DEFAULT 0,
    total_funding_received    INT DEFAULT 0,
    ama_enabled               BOOLEAN DEFAULT FALSE,
    raw                       JSONB,
    scraped_at                TIMESTAMPTZ DEFAULT NOW(),
    updated_at                TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_profiles_uuid     ON profiles(uuid);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);
