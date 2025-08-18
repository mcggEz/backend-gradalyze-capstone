from typing import Optional
import os
from supabase import create_client, Client


_cached_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Create or return a cached Supabase client.

    Reads configuration from environment variables:
    - SUPABASE_URL
    - SUPABASE_ANON_KEY (or SUPABASE_KEY as fallback)
    """
    global _cached_client
    if _cached_client is not None:
        return _cached_client

    url = (os.getenv("SUPABASE_URL") or "").strip()
    # Prefer service role key on the server; fallback to anon
    key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY") or "").strip()

    if not url or not key:
        raise RuntimeError(
            "Supabase configuration missing. Set SUPABASE_URL and SUPABASE_ANON_KEY in environment/.env"
        )

    _cached_client = create_client(url, key)
    return _cached_client


