import os

from dotenv import load_dotenv
from pydantic import PostgresDsn, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class DatabaseBase:
    @property
    def url(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.database,
        ))

    @property
    def url_alembic(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.database,
        ))


class MyBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )


class Server(MyBaseSettings):
    host: str = '0.0.0.0'
    port: int = 8000
    api_url: str = f'http://{host}:{port}/api/v1'

    class Config:
        env_prefix = 'SERVER_'


class Telegram(MyBaseSettings):
    token: str

    class Config:
        env_prefix = 'BOT_'


class PostgresProd(MyBaseSettings, DatabaseBase):
    host: str
    port: int
    user: str
    password: str
    database: str

    class Config:
        env_prefix = 'POSTGRES_'


class PostgresTest(MyBaseSettings, DatabaseBase):
    host: str
    port: int
    user: str
    password: str
    database: str

    class Config:
        env_prefix = 'POSTGRES_TEST_'


class App(BaseSettings):
    title: str = 'CRM'


class Settings(BaseModel):
    server: Server = Server()
    telegram_bot: Telegram = Telegram()
    db_prod: PostgresProd = PostgresProd()
    db_test: PostgresTest = PostgresTest()
    app: App = App()


settings = Settings()

if __name__ == '__main__':
    json = settings.model_dump()
    print(json)
