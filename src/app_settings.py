import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    redis_db_url: str = os.environ.get("DATABASE_URL")
