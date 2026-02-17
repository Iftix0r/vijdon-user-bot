try:
    from src.config_local import *
except ImportError:
    pass

class Settings:
    API_ID: int = globals().get("API_ID", 0)
    API_HASH: str = globals().get("API_HASH", "")
    SESSION_STRING: str = globals().get("SESSION_STRING", "")
    
    BOT_TOKEN: str = globals().get("BOT_TOKEN", "")
    TARGET_GROUP_ID: int = globals().get("TARGET_GROUP_ID", 0)

    OPENAI_API_KEY: str = globals().get("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = globals().get("OPENAI_MODEL", "gpt-3.5-turbo")

settings = Settings()
