-- =====================================================================
-- BAZA DANYCH WIRTUALNEJ AGENCJI AI (SUPABASE SQL EDITOR)
-- Koszt: 0,00 zł w darmowym planie Supabase
-- =====================================================================

-- 1. Pamięć strategiczna i wagi stylów (Dział Statystyczny aktualizuje tę tabelę!)
CREATE TABLE IF NOT EXISTS agent_strategy (
    id SERIAL PRIMARY KEY,
    persona_name TEXT UNIQUE, -- np. 'analityk_danych', 'kontrowersyjny_ekspert', 'case_study'
    system_prompt TEXT,
    posts_count INT DEFAULT 0,
    total_clicks INT DEFAULT 0,
    conversions INT DEFAULT 0,
    effectiveness_score FLOAT DEFAULT 1.0, -- Wyliczane przez Agenta Analityka (Multi-Armed Bandit)
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Wstawienie 3 początkowych stylów (person)
INSERT INTO agent_strategy (persona_name, system_prompt, effectiveness_score)
VALUES 
    ('analityk_danych', 'Jesteś chłodnym, precyzyjnym inżynierem i analitykiem. Operujesz konkretnymi liczbami, architekturą, benchmarkami i wyliczeniami. Zero lania wody.', 1.0),
    ('case_study', 'Jesteś praktykiem biznesowym. Pokazujesz realne case studies, problem klienta, krok po kroku rozwiązanie i wymierne rezultaty.', 1.0),
    ('kontrowersyjny_ekspert', 'Jesteś bezkompromisowym ekspertem. Podważasz powszechne mity i hype rynkowy, wskazujesz ukryte koszty i błędy popełniane przez większość firm.', 1.0)
ON CONFLICT (persona_name) DO NOTHING;

-- 2. Kolejka treści (Blog, Social Media, Newsletter)
CREATE TABLE IF NOT EXISTS content_pipeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel TEXT NOT NULL, -- 'blog', 'x', 'linkedin', 'newsletter', 'fb_group'
    persona_used TEXT REFERENCES agent_strategy(persona_name),
    title TEXT,
    body TEXT NOT NULL,
    followup_comment TEXT, -- Link wrzucany w 1. komentarzu z opóźnieniem (Anti-Ban!)
    utm_tag TEXT UNIQUE, -- np. 'x_20261023_01'
    status TEXT DEFAULT 'scheduled', -- 'draft', 'scheduled', 'published', 'failed'
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    clicks INT DEFAULT 0,
    likes_or_opens INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Kolejka komentarzy (Human-like delay 15-45 min)
CREATE TABLE IF NOT EXISTS comments_queue (
    id SERIAL PRIMARY KEY,
    platform TEXT NOT NULL, -- 'linkedin', 'x', 'facebook'
    external_comment_id TEXT UNIQUE,
    post_context TEXT,
    user_comment TEXT,
    ai_reply TEXT,
    reply_at TIMESTAMP WITH TIME ZONE NOT NULL, -- Losowy czas: now() + 15..95 min
    status TEXT DEFAULT 'pending', -- 'pending', 'replied', 'ignored'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Baza subskrybentów Newslettera (Własne leady)
CREATE TABLE IF NOT EXISTS subscribers (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    source_utm TEXT, -- Skąd przyszedł użytkownik (który agent go przyciągnął!)
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indeksy dla maksymalnej wydajności zapytań
CREATE INDEX IF NOT EXISTS idx_content_pipeline_status ON content_pipeline(status, scheduled_for);
CREATE INDEX IF NOT EXISTS idx_comments_queue_status ON comments_queue(status, reply_at);
CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers(is_active);
-- 5. Tabela Projektów / Klientów Platformy (Wielodostępność - Multi-Tenancy)
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY, -- unikalny identyfikator, np. 'proj_client_1', 'proj_fitness_app'
    user_id TEXT, -- ID klienta z Twojego systemu płatności / autoryzacji
    product_name TEXT NOT NULL,
    website_url TEXT NOT NULL,
    tagline TEXT,
    category TEXT,
    target_audience TEXT,
    primary_problem_solved TEXT,
    industry_keywords JSONB DEFAULT '[]'::jsonb,
    key_features JSONB DEFAULT '[]'::jsonb,
    cms_config JSONB DEFAULT '{
        "owner_authorized": false,
        "publish_mode": "require_approval",
        "cms_type": "github_markdown"
    }'::jsonb,
    subscription_status TEXT DEFAULT 'active', -- 'active', 'trial', 'paused', 'cancelled'
    subscription_plan TEXT DEFAULT 'pro', -- 'starter', 'pro', 'enterprise'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_run_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(subscription_status);
