import os

from dotenv import load_dotenv
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

load_dotenv()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
use_api_keys = os.getenv("USE_API_KEYS", "False").lower() in ["true", "1", "yes"]
api_keys_str = os.getenv("API_KEYS", "")
api_keys = api_keys_str.split(",") if api_keys_str else []


def get_api_key(api_key: str = Security(api_key_header)):
    if not use_api_keys:
        return api_key
    elif api_key in api_keys:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing api key"
        )
