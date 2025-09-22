-- Storage RLS policies so authenticated users can upload/delete
-- to the 'certificates' and 'tor' buckets using anon/auth keys.

-- Enable RLS on storage.objects (usually enabled by default)
alter table storage.objects enable row level security;

-- Certificates bucket policies
do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname='storage' and tablename='objects' and policyname='certificates insert'
  ) then
    create policy "certificates insert"
      on storage.objects
      for insert
      to authenticated
      with check (bucket_id = 'certificates');
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname='storage' and tablename='objects' and policyname='certificates update'
  ) then
    create policy "certificates update"
      on storage.objects
      for update
      to authenticated
      using (bucket_id = 'certificates')
      with check (bucket_id = 'certificates');
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname='storage' and tablename='objects' and policyname='certificates delete'
  ) then
    create policy "certificates delete"
      on storage.objects
      for delete
      to authenticated
      using (bucket_id = 'certificates');
  end if;
end$$;

-- TOR bucket policies
do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname='storage' and tablename='objects' and policyname='tor insert'
  ) then
    create policy "tor insert"
      on storage.objects
      for insert
      to authenticated
      with check (bucket_id = 'tor');
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname='storage' and tablename='objects' and policyname='tor update'
  ) then
    create policy "tor update"
      on storage.objects
      for update
      to authenticated
      using (bucket_id = 'tor')
      with check (bucket_id = 'tor');
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname='storage' and tablename='objects' and policyname='tor delete'
  ) then
    create policy "tor delete"
      on storage.objects
      for delete
      to authenticated
      using (bucket_id = 'tor');
  end if;
end$$;


