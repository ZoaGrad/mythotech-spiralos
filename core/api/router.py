"""Minimal REST router for witness protocol bridging to Supabase edge functions."""

import os
from typing import Any, Dict

import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()

FUNCTIONS_BASE = os.getenv("SUPABASE_FUNCTIONS_URL") or os.getenv("SUPABASE_EDGE_URL")
SUPABASE_REST_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")


def _build_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if SUPABASE_SERVICE_ROLE_KEY:
        headers["apikey"] = SUPABASE_SERVICE_ROLE_KEY
        headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
    return headers


def _functions_url(function_name: str) -> str:
    if not FUNCTIONS_BASE:
        if not SUPABASE_REST_URL:
            raise HTTPException(status_code=500, detail="Supabase configuration missing")
        return f"{SUPABASE_REST_URL.replace('/rest/v1', '')}/functions/v1/{function_name}"
    return f"{FUNCTIONS_BASE.rstrip('/')}/{function_name}"


@router.post("/witness/event")
def post_witness_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Proxy witness events to Supabase edge function."""

    url = _functions_url("witness-event")
    response = requests.post(url, json=payload, headers=_build_headers(), timeout=15)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@router.get("/witness/claim/{claim_id}")
def get_witness_claim(claim_id: str) -> Dict[str, Any]:
    """Fetch witness claim status directly from Supabase."""

    if not SUPABASE_REST_URL:
        raise HTTPException(status_code=500, detail="Supabase URL not configured")

    url = f"{SUPABASE_REST_URL.rstrip('/')}/rest/v1/witness_claims"
    response = requests.get(url, params={"id": f"eq.{claim_id}"}, headers=_build_headers(), timeout=10)
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    if isinstance(data, list) and data:
        return data[0]
    raise HTTPException(status_code=404, detail="Claim not found")
