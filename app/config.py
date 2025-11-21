"""配置管理模块"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置"""

    # OpenAI-like API 配置
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://aihubmix.com/v1")
    OPENAI_API_KEY: str = os.getenv(
        "OPENAI_API_KEY", "sk-f8QpOUajGsi5u5oGE15f2aB93822423694059b8f93083721"
    )

    # 应用配置
    APP_NAME: str = "LlamaIndex Chat"
    APP_VERSION: str = "0.1.0"

    # 模型配置
    # 注意：如果使用自定义模型，需要确保 API 支持该模型名称
    # 可以尝试：qwen-plus, qwen-turbo, qwen-max 等
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-5-mini")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.5"))
    MAX_TOKENS: Optional[int] = (
        int(os.getenv("MAX_TOKENS", "4000")) if os.getenv("MAX_TOKENS") else None
    )


settings = Settings()
