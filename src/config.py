import os

class Settings:
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    SESSION_STRING: str = os.getenv("SESSION_STRING", "")
    
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    TARGET_GROUP_ID: int = int(os.getenv("TARGET_GROUP_ID", "0"))

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))

settings = Settings()
