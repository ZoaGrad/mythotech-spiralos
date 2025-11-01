-- Core F2 autonomy tables (idempotent)
create table if not exists public.judicial_cases (
  id uuid primary key default gen_random_uuid(),
  subject_id text not null,
  judgment_type text not null,
  priority text not null,
  status text not null default 'pending',
  verdict jsonb,
  created_at timestamptz default now()
);

create table if not exists public.judicial_reports (
  id uuid primary key default gen_random_uuid(),
  timestamp timestamptz not null default now(),
  report jsonb not null
);

-- Enforce RLS
alter table public.judicial_cases enable row level security;
alter table public.judicial_reports enable row level security;

-- Authenticated policies
do $$ begin
  if not exists (select 1 from pg_policies where tablename='judicial_cases' and policyname='authenticated_read_cases') then
    create policy authenticated_read_cases on public.judicial_cases for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename='judicial_cases' and policyname='authenticated_write_cases') then
    create policy authenticated_write_cases on public.judicial_cases for insert, update to authenticated with check (true);
  end if;
  if not exists (select 1 from pg_policies where tablename='judicial_reports' and policyname='authenticated_read_reports') then
    create policy authenticated_read_reports on public.judicial_reports for select to authenticated using (true);
  end if;
  if not exists (select 1 from pg_policies where tablename='judicial_reports' and policyname='authenticated_write_reports') then
    create policy authenticated_write_reports on public.judicial_reports for insert, update to authenticated with check (true);
  end if;
end $$;

-- Seed entry
insert into public.judicial_cases (subject_id, judgment_type, priority)
select 'seed_subject', 'CRISIS_ESCALATION', 'CRITICAL'
where not exists (select 1 from public.judicial_cases);
