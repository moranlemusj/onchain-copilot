from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_api_key: str
    alchemy_api_key: str
    etherscan_api_key: str | None = None

    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/text-embedding-004"
    alchemy_network: str = "eth-mainnet"
    vector_store_dir: str = ".chroma"

    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "onchain-copilot"


settings = Settings()
