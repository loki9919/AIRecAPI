from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader, APIKeyQuery
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api-key", auto_error=False)

def get_api_key(
    api_key_header: str = Security(api_key_header),
    api_key_query: str = Security(api_key_query)
) -> str:
    if api_key_header in settings.API_KEYS:
        return api_key_header
    if api_key_query in settings.API_KEYS:
        return api_key_query
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")
