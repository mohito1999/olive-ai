-- https://supabase.com/docs/guides/auth/managing-user-data
create function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.user (auth_provider, auth_provider_id, email, name, organization_id, role, created_by, updated_by)
  values ('SUPABASE', new.id, new.email, new.raw_user_meta_data ->> 'name', new.raw_user_meta_data ->> 'organization_id', new.raw_user_meta_data ->> 'role', new.raw_user_meta_data ->> 'created_by', new.raw_user_meta_data ->> 'created_by');
  return new;
end;
$$;

--bun:split

-- trigger the function every time a user is created
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
