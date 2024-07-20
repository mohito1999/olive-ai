-- These might be required
-- grant usage on schema extensions to supabase_auth_admin;
-- grant execute on all functions in schema extensions to supabase_auth_admin;

-- https://supabase.com/docs/guides/auth/managing-user-data
create function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.user (id, email, name, organization_id, role, created_by, updated_by)
  values (new.id, new.email, new.raw_user_meta_data ->> 'display_name', new.raw_user_meta_data ->> 'organization_id', new.raw_user_meta_data ->> 'role', new.raw_user_meta_data ->> 'created_by', new.raw_user_meta_data ->> 'created_by');
  return new;
end;
$$;

--bun:split

-- trigger the function every time a user is created
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
