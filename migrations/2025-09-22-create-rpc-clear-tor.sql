-- SECURITY DEFINER function to clear TOR fields by email
-- This bypasses RLS inside the function while still being safely
-- restricted to updating a single user row by email.

create or replace function public.clear_tor_by_email(target_email text)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  updated_count integer := 0;
begin
  update public.users
  set tor_url = null,
      tor_storage_path = null,
      tor_notes = null,
      tor_uploaded_at = null,
      archetype_analyzed_at = null,
      primary_archetype = null,
      archetype_realistic_percentage = null,
      archetype_investigative_percentage = null,
      archetype_artistic_percentage = null,
      archetype_social_percentage = null,
      archetype_enterprising_percentage = null,
      archetype_conventional_percentage = null,
      career_recommendations = null,
      analysis_results = null
  where email = target_email;

  get diagnostics updated_count = row_count;
  return updated_count > 0;
end;
$$;

-- Allow app roles to execute the function
grant execute on function public.clear_tor_by_email(text) to anon, authenticated, service_role;


