-- ΔΩ: SCHEMA INITIATION // TABLE: ATTESTATIONS
-- Storage for Sovereign Work Energy

create table public.attestations (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  
  -- The Physics of the Work
  volume int not null default 0, -- Lines of code, message count, etc.
  complexity float not null default 1.0, -- 1.0 to 10.0
  entropy float not null default 0.1, -- 0.0 to 1.0 (Penalty)
  
  -- Metadata
  source text default 'manual', -- 'github', 'discord', 'manual'
  description text,
  
  -- Calculated WI (Optional, can be computed on fly, but good to store)
  final_wi_score float generated always as (
    case 
      when volume <= 0 then 0
      else (volume * power(greatest(0.1, least(complexity, 10.0)), 1.5)) * (1.0 / (1.0 + (entropy * 4)))
    end
  ) stored
);

-- Enable Row Level Security (Sovereign Access Only)
alter table public.attestations enable row level security;

-- Policy: Allow full access to the Architect (Service Role)
create policy "Allow Service Role Full Access"
on public.attestations
for all
using ( true )
with check ( true );
