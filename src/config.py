from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_ID: int
    API_HASH: str
    SESSION_STRING: str = ""
    
    BOT_TOKEN: str
    TARGET_GROUP_ID: int

    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    class Config:
        env_file = ".env"

settings = Settings()
