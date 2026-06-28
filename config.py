from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model_name: str = "deepseek-chat"
    qweather_key: str = ""
    database_url: str = "sqlite:///data/agent.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
