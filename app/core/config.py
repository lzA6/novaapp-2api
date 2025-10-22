import os
import logging
import uuid
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class Credential(BaseModel):
    x_token: str
    x_user_id: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

    APP_NAME: str = "novaapp-2api"
    APP_VERSION: str = "2.0.0"
    DESCRIPTION: str = "一个将 NovaApp.ai 转换为兼容 OpenAI 格式 API 的高性能代理，支持多账号轮询、文本与图像生成。"

    API_MASTER_KEY: Optional[str] = None
    NGINX_PORT: int = 8088
    API_REQUEST_TIMEOUT: int = 300
    POLLING_INTERVAL: int = 2
    POLLING_TIMEOUT: int = 240

    CREDENTIALS: List[Credential] = []

    CHAT_IMAGE_URL: str = "https://api.novaapp.ai/api/chat/image"
    IMAGE_GENERATOR_URL: str = "https://api.novaapp.ai/api/image-generator"
    IMAGE_BASE_URL: str = "https://firebasestorage.googleapis.com/v0/b/chat-ai-prod.appspot.com/o/"

    MODEL_MAPPING: Dict[str, int] = {
        "gpt-4o-mini": 0,
        "gpt-4o": 11,
        "gpt-5": 2,
        "gemini-flash": 10,
        "claude-3.5-sonnet": 15,
        "web-search": 14,
        "nova-dalle3": 4,
    }
    DEFAULT_MODEL: str = "gpt-4o-mini"

    def __init__(self, **values):
        super().__init__(**values)
        i = 1
        while True:
            cred_str = os.getenv(f"NOVAAPP_CREDENTIAL_{i}")
            if cred_str:
                try:
                    x_token, x_user_id = cred_str.split('|')
                    self.CREDENTIALS.append(Credential(x_token=x_token.strip(), x_user_id=x_user_id.strip()))
                except ValueError:
                    logger.warning(f"凭证格式错误 NOVAAPP_CREDENTIAL_{i}，应为 'x_token|x_user_id'。")
                i += 1
            else:
                break
    
        if not self.CREDENTIALS:
            raise ValueError("必须在 .env 文件中至少配置一个有效的 NOVAAPP_CREDENTIAL_1")

settings = Settings()