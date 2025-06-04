from pathlib import Path
from dotenv import load_dotenv

env_file_path = Path(__file__).parent / '.env.local'
load_dotenv(env_file_path)