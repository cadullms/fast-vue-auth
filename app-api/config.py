from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

env_file_path = Path(__file__).parent / ".env.local"
load_dotenv(env_file_path)


@dataclass
class AuthSettings:
    client_id: str = os.getenv("CLIENT_ID")
    client_secret: str = os.getenv("CLIENT_SECRET")
    domain: str = os.getenv("DOMAIN")


AUTH_SETTINGS = AuthSettings()
