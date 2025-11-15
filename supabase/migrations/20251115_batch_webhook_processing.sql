-- ΔΩ.147.A batch GitHub webhook processing
set search_path = public;

create unique index if not exists idx_ache_events_source_source_id
    on public.ache_events(source, source_id);

create or replace function public.process_push_batch(
    commits jsonb,
    repository text default null,
    branch_ref text default null
) returns jsonb
language plpgsql
security definer
as $$
declare
    inserted_event_ids uuid[] := '{}';
    avg_ache numeric := 0;
    processed_count integer := 0;
    webhook_id uuid := gen_random_uuid();
begin
    if commits is null or jsonb_typeof(commits) <> 'array' or jsonb_array_length(commits) = 0 then
        return jsonb_build_object(
            'processed_count', 0,
            'ache_event_ids', inserted_event_ids,
            'average_ache', avg_ache,
            'webhook_id', webhook_id
        );
    end if;

    with commit_rows as (
        select
            commit_el ->> 'id' as commit_id,
            commit_el,
            coalesce((commit_el ->> 'ache_level')::numeric, 0) as ache_level
        from jsonb_array_elements(commits) as commit_el
        where commit_el ->> 'id' is not null
    ),
    inserted_ache as (
        insert into public.ache_events (source, source_id, content, ache_level, metadata)
        select
            'github_commit',
            cr.commit_id,
            jsonb_build_object(
                'commit', cr.commit_el,
                'repository', repository,
                'branch_ref', branch_ref
            ),
            cr.ache_level,
            jsonb_build_object('repository', repository)
        from commit_rows cr
        on conflict (source, source_id) do update
            set ache_level = excluded.ache_level,
                content = excluded.content,
                metadata = excluded.metadata
        returning id, source_id, ache_level
    )
    insert into public.scar_index (external_id, external_source, processing_status, scarindex_value, metadata)
    select
        ia.source_id,
        'github_commit',
        'completed',
        ia.ache_level,
        jsonb_build_object('repository', repository, 'branch_ref', branch_ref)
    from inserted_ache ia
    on conflict (external_id) do update
        set processing_status = 'completed',
            scarindex_value = excluded.scarindex_value,
            metadata = excluded.metadata,
            updated_at = now();

    select coalesce(array_agg(id), '{}'),
           coalesce(avg(ache_level), 0),
           count(*)
    into inserted_event_ids, avg_ache, processed_count
    from inserted_ache;

    insert into public.github_webhooks (id, event_type, payload, processed, processed_at)
    values (
        webhook_id,
        'push',
        jsonb_build_object('repository', repository, 'branch_ref', branch_ref, 'commit_count', processed_count),
        true,
        now()
    )
    on conflict (id) do update
        set processed = excluded.processed,
            processed_at = excluded.processed_at,
            payload = excluded.payload;

    return jsonb_build_object(
        'processed_count', processed_count,
        'ache_event_ids', inserted_event_ids,
        'average_ache', avg_ache,
        'webhook_id', webhook_id
    );
end;
$$;
