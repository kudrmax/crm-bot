import os
from typing import Dict

from dotenv import load_dotenv
from pydantic import PostgresDsn, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class MyBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )


class Server(MyBaseSettings):
    api_url: str = f'http://api:8000/api/v2'  # 'http://api:8000/api/v2'

    class Config:
        env_prefix = 'SERVER_'


class Telegram(MyBaseSettings):
    token: str

    class Config:
        env_prefix = 'BOT_'


class Settings(BaseModel):
    server: Server = Server()
    telegram_bot: Telegram = Telegram()


settings = Settings()

if __name__ == '__main__':
    json = settings.model_dump()
    print(json)
