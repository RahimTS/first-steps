import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()

@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "first-steps")
    debug_mode: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    env: str = os.getenv("ENV", "local")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = os.getenv("PORT", 8000)
    mongo_uri: str = os.getenv("MONGO_URI")
    mongo_db: str = os.getenv("MONGO_DB")


settings = Settings()

