from dataclasses import dataclass
import os


@dataclass
class AuthSettings:
    client_id: str = os.getenv("CLIENT_ID")
    client_secret: str = os.getenv("CLIENT_SECRET")
    domain: str = os.getenv("DOMAIN")

AUTH_SETTINGS = AuthSettings()