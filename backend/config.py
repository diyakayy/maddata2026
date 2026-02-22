from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tam.db")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")  # Legacy, no longer used
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")            # Free — https://console.groq.com

settings = Settings()
