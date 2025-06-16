from dataclasses import dataclass, field
import os
from pathlib import Path
from dotenv import load_dotenv

env_file_path = Path(__file__).parent / ".env.local"
load_dotenv(env_file_path)


@dataclass
class AuthOption:
    id: str
    name: str
    client_id: str
    client_secret: str
    domain: str
    type: str


@dataclass
class AuthSettings:
    options: dict[str, AuthOption] | None = field(default_factory=dict)


AUTH_SETTINGS = AuthSettings()

auth_option_index = 0
id = os.getenv(f"AUTH_OPTION_{auth_option_index}_ID")
while id:
    type = os.getenv(f"AUTH_OPTION_{auth_option_index}_TYPE")
    name = os.getenv(f"AUTH_OPTION_{auth_option_index}_NAME")
    client_id = os.getenv(f"AUTH_OPTION_{auth_option_index}_CLIENT_ID")
    client_secret = os.getenv(
        f"AUTH_OPTION_{auth_option_index}_CLIENT_SECRET")
    domain = os.getenv(f"AUTH_OPTION_{auth_option_index}_DOMAIN")
    AUTH_SETTINGS.options[id] = AuthOption(
        id, name, client_id, client_secret, domain, type)
    auth_option_index += 1
    id = os.getenv(f"AUTH_OPTION_{auth_option_index}_ID")