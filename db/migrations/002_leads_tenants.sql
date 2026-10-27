-- 002: tenants, leads (client pipeline), lead_events + consent columns.
-- Run once in Supabase SQL Editor (idempotent). Fresh installs: db/schema.sql already contains this.
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
