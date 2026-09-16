from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    embedding_model: str = "gemini-embedding-001"
    llm_model: str = "gemini-2.5-flash"
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 4
    vector_store_dir: str = "vectorstore"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
