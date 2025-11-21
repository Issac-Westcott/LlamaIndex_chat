"""LlamaIndex Agent 模块"""

import logging
from typing import AsyncGenerator, Dict, List, Optional

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class ConversationAgent:
    """支持多轮对话的 Agent"""

    def __init__(self):
        """初始化 Agent"""
        # 使用 OpenAILike（实际是 OpenAI 类）连接自定义的 OpenAI-compatible API
        # api_base 指定了模型供应商的 API 地址
        self.llm = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            api_base=settings.OPENAI_BASE_URL,  # 自定义 API 基础 URL
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )
        # 存储每个会话的对话历史
        self.conversations: Dict[str, List[ChatMessage]] = {}

    def chat(
        self, message: str, session_id: str = "default", system_prompt: Optional[str] = None
    ) -> str:
        """
        处理用户消息并返回回复

        Args:
            message: 用户消息
            session_id: 会话ID，用于维护多轮对话上下文
            system_prompt: 系统提示词

        Returns:
            Agent 的回复
        """
        # 获取或创建会话历史
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            # 如果有系统提示词，添加到对话历史
            if system_prompt:
                self.conversations[session_id].append(
                    ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
                )

        # 添加用户消息
        self.conversations[session_id].append(ChatMessage(role=MessageRole.USER, content=message))

        # 调用 LLM 生成回复
        try:
            response = self.llm.chat(messages=self.conversations[session_id])

            # 获取回复内容
            assistant_message = response.message.content

            # 添加助手回复到对话历史
            self.conversations[session_id].append(
                ChatMessage(role=MessageRole.ASSISTANT, content=assistant_message)
            )

            logger.info(
                f"会话 {session_id} 收到回复，历史长度: {len(self.conversations[session_id])}"
            )
            return assistant_message
        except Exception as e:
            logger.error(f"LLM 调用失败: {str(e)}", exc_info=True)
            # 移除刚添加的用户消息，避免历史记录不一致
            if (
                self.conversations[session_id]
                and self.conversations[session_id][-1].role == MessageRole.USER
            ):
                self.conversations[session_id].pop()
            raise

    def clear_conversation(self, session_id: str = "default"):
        """清除指定会话的对话历史"""
        if session_id in self.conversations:
            del self.conversations[session_id]

    async def chat_stream(
        self, message: str, session_id: str = "default", system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        流式处理用户消息并返回回复

        Args:
            message: 用户消息
            session_id: 会话ID，用于维护多轮对话上下文
            system_prompt: 系统提示词

        Yields:
            Agent 回复的文本片段
        """
        # 获取或创建会话历史
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            # 如果有系统提示词，添加到对话历史
            if system_prompt:
                self.conversations[session_id].append(
                    ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
                )

        # 添加用户消息
        self.conversations[session_id].append(ChatMessage(role=MessageRole.USER, content=message))

        # 调用 LLM 流式生成回复
        try:
            full_response = ""
            thinking_content = ""
            # astream_chat 返回协程，需要先 await 得到 AsyncGenerator
            stream = await self.llm.astream_chat(messages=self.conversations[session_id])
            async for chat_response in stream:
                # chat_response 是 ChatResponse 对象
                if hasattr(chat_response, "message") and chat_response.message:
                    # 检查是否有思考过程（reasoning）
                    if hasattr(chat_response, "raw") and chat_response.raw:
                        # 尝试从 raw 中提取思考过程
                        raw_data = chat_response.raw
                        if isinstance(raw_data, dict):
                            if "reasoning" in raw_data:
                                thinking_content = raw_data.get("reasoning", "")
                                if thinking_content:
                                    yield {"type": "thinking", "content": thinking_content}

                    if hasattr(chat_response.message, "content") and chat_response.message.content:
                        current_content = chat_response.message.content
                        # 只发送新增的内容（增量）
                        if len(current_content) > len(full_response):
                            new_content = current_content[len(full_response) :]
                            full_response = current_content
                            yield {"type": "content", "content": new_content}

            # 添加完整的助手回复到对话历史
            if full_response:
                self.conversations[session_id].append(
                    ChatMessage(role=MessageRole.ASSISTANT, content=full_response)
                )
                logger.info(
                    f"会话 {session_id} 流式回复完成，历史长度: {len(self.conversations[session_id])}"
                )
        except Exception as e:
            logger.error(f"LLM 流式调用失败: {str(e)}", exc_info=True)
            # 移除刚添加的用户消息，避免历史记录不一致
            if (
                self.conversations[session_id]
                and self.conversations[session_id][-1].role == MessageRole.USER
            ):
                self.conversations[session_id].pop()
            raise

    def get_conversation_history(self, session_id: str = "default") -> List[Dict]:
        """获取对话历史（用于调试或显示）"""
        if session_id not in self.conversations:
            return []

        history = []
        for msg in self.conversations[session_id]:
            history.append(
                {
                    "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role),
                    "content": msg.content,
                }
            )
        return history
