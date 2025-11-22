
-- File: core/guardian/sql/guardian_views.sql
-- Create a read‑only SQL runner for Edge usage (locks to SELECT‑only via SECURITY DEFINER body).

CREATE OR REPLACE FUNCTION public.raw_sql(query text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result json;
BEGIN
  -- Enforce SELECT‑only to keep this safe.
  IF left(trim(lower(query)), 6) <> 'select' THEN
    RAISE EXCEPTION 'raw_sql only permits SELECT queries';
  END IF;

  EXECUTE format('WITH r AS (%s) SELECT json_agg(r) FROM r', query) INTO result;
  RETURN COALESCE(result, '[]'::json);
END;
$$;

REVOKE ALL ON FUNCTION public.raw_sql(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.raw_sql(text) TO anon, authenticated, service_role;
