from pathlib import Path

MIGRATIONS = {
    "external_witness": Path("spiral_supabase/migrations/12_external_witness_table.sql"),
    "external_quarantine": Path("spiral_supabase/migrations/12_external_quarantine_table.sql"),
    "external_views": Path("spiral_supabase/migrations/12_external_views.sql"),
}


def _load(path: Path) -> str:
    assert path.exists(), f"missing migration {path}"
    return path.read_text()


def test_external_witness_table_schema_locked():
    content = _load(MIGRATIONS["external_witness"])
    assert "external_witness_events" in content
    assert "timestamptz" in content
    assert "trust_score" in content


def test_external_quarantine_table_schema_locked():
    content = _load(MIGRATIONS["external_quarantine"])
    assert "external_quarantine" in content
    assert "quarantined_at" in content
    assert "jsonb" in content


def test_external_view_exists_and_projects_required_fields():
    content = _load(MIGRATIONS["external_views"])
    assert "external_scarindex_view" in content
    assert "external_witness_events" in content
    assert "trust_score" in content
