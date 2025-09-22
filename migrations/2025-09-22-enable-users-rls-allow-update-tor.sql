-- Enable RLS on users and allow signed-in users to select and update
-- their own profile (by matching auth.email() to users.email).
-- This is required so the backend (when using anon/auth key) can
-- clear TOR-related fields when the user clicks Remove.

-- Ensure RLS is enabled
alter table public.users enable row level security;

-- Basic grants (Supabase usually sets these, but include for clarity)
grant usage on schema public to anon, authenticated, service_role;
grant select, update on table public.users to authenticated;

-- Allow selecting own row by email
do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'users' and policyname = 'select own profile by email'
  ) then
    create policy "select own profile by email"
      on public.users
      for select
      to authenticated
      using (auth.email() = email);
  end if;
end$$;

-- Allow updating own row by email (used to clear TOR fields)
do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'users' and policyname = 'update own tor by email'
  ) then
    create policy "update own tor by email"
      on public.users
      for update
      to authenticated
      using (auth.email() = email)
      with check (auth.email() = email);
  end if;
end$$;

-- NOTE:
-- If your project stores the auth UID in a column (e.g., users.auth_user_id),
-- consider swapping email-based matching for UID matching:
--   using (auth.uid() = auth_user_id) with check (auth.uid() = auth_user_id)
-- This file assumes you match via email.


