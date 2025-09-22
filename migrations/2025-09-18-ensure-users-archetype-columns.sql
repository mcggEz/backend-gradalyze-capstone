-- Ensure archetype columns exist on users table and are nullable
alter table if exists public.users
  add column if not exists tor_storage_path text,
  add column if not exists tor_uploaded_at timestamptz,
  add column if not exists primary_archetype text,
  add column if not exists archetype_analyzed_at timestamptz,
  add column if not exists archetype_realistic_percentage numeric,
  add column if not exists archetype_investigative_percentage numeric,
  add column if not exists archetype_artistic_percentage numeric,
  add column if not exists archetype_social_percentage numeric,
  add column if not exists archetype_enterprising_percentage numeric,
  add column if not exists archetype_conventional_percentage numeric,
  add column if not exists certificate_paths text[] default '{}'::text[],
  add column if not exists certificate_urls text[] default '{}'::text[],
  add column if not exists certificates_count int default 0,
  add column if not exists latest_certificate_path text,
  add column if not exists latest_certificate_url text,
  add column if not exists latest_certificate_uploaded_at timestamptz;

-- RLS helper policy (adjust for your auth schema): allow service role to write
-- Note: replace 'service_role' check with your auth mechanism if different
-- This assumes using service role key server-side; Supabase treats it as bypassing RLS automatically.
