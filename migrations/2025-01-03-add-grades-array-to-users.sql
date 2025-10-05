-- Add grades array column to users table
-- This will store grades as JSONB array for easier frontend management

-- Add grades column as JSONB array
alter table public.users 
add column if not exists grades jsonb default '[]'::jsonb;

-- Create index for better performance on grades queries
create index if not exists idx_users_grades_gin 
on public.users using gin (grades);

-- Add comment for documentation
comment on column public.users.grades is 'Array of grade objects: [{id, subject, courseCode, units, grade, semester}]';

-- Create function to update grades array
create or replace function public.update_user_grades(
  p_user_id bigint,
  p_grades jsonb
)
returns void as $$
begin
  update public.users 
  set grades = p_grades,
      updated_at = now()
  where id = p_user_id;
end;
$$ language plpgsql security definer;

-- Create function to get user grades
create or replace function public.get_user_grades(p_user_id bigint)
returns jsonb as $$
begin
  return (
    select grades 
    from public.users 
    where id = p_user_id
  );
end;
$$ language plpgsql security definer;

-- Grant permissions
grant execute on function public.update_user_grades(bigint, jsonb) to authenticated;
grant execute on function public.get_user_grades(bigint) to authenticated;
