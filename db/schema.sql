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
    followup_comment TEXT, -- Szkic komentarza z linkiem do ręcznego użycia
    utm_tag TEXT UNIQUE, -- np. 'x_20261023_01'
    status TEXT DEFAULT 'scheduled', -- 'draft', 'scheduled', 'published', 'failed'
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    clicks INT DEFAULT 0,
    likes_or_opens INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Kolejka szkiców odpowiedzi (każda odpowiedź zatwierdzana ręcznie)
CREATE TABLE IF NOT EXISTS comments_queue (
    id SERIAL PRIMARY KEY,
    platform TEXT NOT NULL, -- 'linkedin', 'x', 'facebook'
    external_comment_id TEXT UNIQUE,
    post_context TEXT,
    user_comment TEXT,
    ai_reply TEXT,
    reply_at TIMESTAMP WITH TIME ZONE, -- czas ręcznej publikacji po akceptacji
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

-- 6. Lejek klientów (leady) i tenanci — patrz db/migrations/002_leads_tenants.sql
CREATE TABLE IF NOT EXISTS tenants (
  id TEXT PRIMARY KEY, display_name TEXT NOT NULL, plan TEXT DEFAULT 'owner',
  status TEXT DEFAULT 'active' CHECK (status IN ('active','trial','paused','cancelled')),
  config JSONB DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ DEFAULT NOW());
INSERT INTO tenants (id, display_name) VALUES ('default','Marka właściciela') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL DEFAULT 'default' REFERENCES tenants(id),
  name TEXT NOT NULL CHECK (char_length(name) BETWEEN 1 AND 100),
  email TEXT NOT NULL CHECK (char_length(email) <= 254),
  company TEXT CHECK (char_length(company) <= 150),
  service_interest TEXT, message TEXT CHECK (char_length(message) <= 2000),
  source_utm TEXT, consent_at TIMESTAMPTZ NOT NULL, consent_text_version TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','contacted','qualified','proposal','won','lost')),
  value_pln NUMERIC(10,2), next_action TEXT, next_action_at TIMESTAMPTZ, notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE INDEX IF NOT EXISTS idx_leads_tenant_status ON leads(tenant_id, status);

CREATE TABLE IF NOT EXISTS lead_events (
  id BIGSERIAL PRIMARY KEY, lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  event TEXT NOT NULL, from_status TEXT, to_status TEXT, note TEXT, created_at TIMESTAMPTZ DEFAULT NOW());

-- RLS: the public site (anon key) may only INSERT new leads; reading/updating needs the service key.
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS leads_anon_insert ON leads;
CREATE POLICY leads_anon_insert ON leads FOR INSERT TO anon
  WITH CHECK (tenant_id = 'default' AND status = 'new' AND consent_at IS NOT NULL AND value_pln IS NULL AND notes IS NULL);
ALTER TABLE lead_events ENABLE ROW LEVEL SECURITY;

ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS consent_at TIMESTAMPTZ;
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS unsubscribed_at TIMESTAMPTZ;
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';
ALTER TABLE projects ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';
ALTER TABLE content_pipeline ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';
ALTER TABLE content_pipeline ALTER COLUMN id DROP DEFAULT, ALTER COLUMN id TYPE TEXT USING id::text;

