from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Server Settings
    API_PORT: int = 5000
    DEBUG_MODE: bool = True
    HOST: str = "0.0.0.0"

    # Agent Settings
    AGENT_TIMEOUT: int = 300
    RESEARCH_AGENT_THREADS: int = 5

    # API Keys
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str

    # Database Settings
    FAISS_INDEX_PATH: str = "./db/faiss_index"
    SQLITE_DB_PATH: str = "./db/prd_database.db"

    # Vector Settings
    VECTOR_DIM: int = 768

    class Config:
        env_file = "config/.env"

    def validate_api_keys(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY is required") 