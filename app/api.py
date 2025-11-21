"""FastAPI 路由模块"""

import json
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from app.agent import ConversationAgent
from app.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# 添加 CORS 中间件（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent

# 创建全局 Agent 实例
agent = ConversationAgent()

logger.info(f"应用启动: {settings.APP_NAME} v{settings.APP_VERSION}")


class ChatRequest(BaseModel):
    """聊天请求模型"""

    message: str
    session_id: Optional[str] = "default"
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """聊天响应模型"""

    response: str
    session_id: str


class ClearRequest(BaseModel):
    """清除会话请求模型"""

    session_id: Optional[str] = "default"


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    template_path = BASE_DIR / "app" / "templates" / "index.html"
    with open(template_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    处理聊天请求（支持流式和非流式）

    Args:
        request: 包含用户消息和会话ID的请求

    Returns:
        包含回复和会话ID的响应
    """
    try:
        # 如果没有提供 session_id，生成一个新的
        if not request.session_id or request.session_id == "default":
            session_id = str(uuid.uuid4())
        else:
            session_id = request.session_id

        logger.info(
            f"收到聊天请求，会话ID: {session_id}, 消息长度: {len(request.message)}, 流式: {request.stream}"
        )

        # 检查是否请求流式响应
        use_stream = request.stream if hasattr(request, "stream") else False

        if use_stream:
            # 流式响应
            async def generate():
                try:
                    async for chunk_data in agent.chat_stream(
                        message=request.message,
                        session_id=session_id,
                        system_prompt="你是一个友好、专业的AI助手。请用简洁明了的方式回答用户的问题。",
                    ):
                        # chunk_data 是字典，包含 type 和 content
                        yield f"data: {json.dumps({**chunk_data, 'session_id': session_id}, ensure_ascii=False)}\n\n"
                    yield f"data: {json.dumps({'type': 'done', 'session_id': session_id}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    logger.error(f"流式响应错误: {str(e)}", exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            # 非流式响应（兼容旧版本）
            response_text = agent.chat(
                message=request.message,
                session_id=session_id,
                system_prompt="你是一个友好、专业的AI助手。请用简洁明了的方式回答用户的问题。",
            )

            return ChatResponse(response=response_text, session_id=session_id)
    except Exception as e:
        logger.error(f"处理聊天请求时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@app.post("/api/clear")
async def clear_conversation(request: ClearRequest):
    """
    清除指定会话的对话历史

    Args:
        request: 包含会话ID的请求

    Returns:
        成功消息
    """
    try:
        session_id = request.session_id or "default"
        agent.clear_conversation(session_id=session_id)
        return {"message": "对话历史已清除", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除对话历史时出错: {str(e)}")


@app.get("/api/conversations")
async def list_conversations():
    """
    获取所有会话列表

    Returns:
        会话列表
    """
    try:
        conversations = []
        for session_id, messages in agent.conversations.items():
            if messages:
                # 获取第一条用户消息作为标题
                first_user_msg = next(
                    (
                        msg
                        for msg in messages
                        if hasattr(msg.role, "value") and msg.role.value == "user"
                    ),
                    None,
                )
                if not first_user_msg:
                    first_user_msg = next(
                        (msg for msg in messages if str(msg.role) == "user"), None
                    )
                title = first_user_msg.content[:50] if first_user_msg else "新对话"
                conversations.append(
                    {
                        "session_id": session_id,
                        "title": title,
                        "message_count": len(
                            [
                                m
                                for m in messages
                                if (hasattr(m.role, "value") and m.role.value != "system")
                                or str(m.role) != "system"
                            ]
                        ),
                        "last_updated": "now",  # 可以添加时间戳
                    }
                )
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"获取会话列表时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取会话列表时出错: {str(e)}")


@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str):
    """
    获取指定会话的历史消息

    Args:
        session_id: 会话ID

    Returns:
        会话的历史消息列表
    """
    try:
        history = agent.get_conversation_history(session_id=session_id)

        # 转换为前端需要的格式
        messages = []
        for msg in history:
            # 跳过系统消息
            role = msg.get("role", "")
            if role == "system":
                continue

            # 转换为前端格式
            messages.append(
                {
                    "role": role if role in ["user", "assistant"] else "assistant",
                    "content": msg.get("content", ""),
                }
            )

        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        logger.error(f"获取会话历史时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取会话历史时出错: {str(e)}")


@app.get("/health")
async def health():
    """健康检查端点"""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
