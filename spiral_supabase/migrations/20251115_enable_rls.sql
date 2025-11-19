-- ΔΩ.147.A RLS hardening for ache_events, scar_index, panic_frames
set search_path = public;

alter table if exists public.ache_events enable row level security;
alter table if exists public.ache_events force row level security;
drop policy if exists public_read_ache_events on public.ache_events;
drop policy if exists service_write_ache_events on public.ache_events;

alter table if exists public.scar_index enable row level security;
alter table if exists public.scar_index force row level security;
drop policy if exists "public_read_scar_index" on public.scar_index;
drop policy if exists "service_write_scar_index" on public.scar_index;

alter table if exists public.panic_frames enable row level security;
alter table if exists public.panic_frames force row level security;
drop policy if exists "read_own_panic_frames" on public.panic_frames;
drop policy if exists "insert_own_panic_frames" on public.panic_frames;
drop policy if exists "update_own_panic_frames" on public.panic_frames;

create policy if not exists ache_events_guardian_rw
on public.ache_events
for all
using ((auth.jwt() ->> 'role') = 'guardian')
with check ((auth.jwt() ->> 'role') = 'guardian');

create policy if not exists scar_index_guardian_rw
on public.scar_index
for all
using ((auth.jwt() ->> 'role') = 'guardian')
with check ((auth.jwt() ->> 'role') = 'guardian');

create policy if not exists panic_frames_guardian_rw
on public.panic_frames
for all
using ((auth.jwt() ->> 'role') = 'guardian')
with check ((auth.jwt() ->> 'role') = 'guardian');
