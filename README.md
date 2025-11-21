# LlamaIndex Chat

<div align="center">

一个基于 LlamaIndex 和 FastAPI 构建的现代化多轮对话 Agent 应用，配备优雅的 Next.js 前端界面。

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

</div>

## ✨ 特性

- 🤖 **智能对话 Agent** - 基于 LlamaIndex 构建，支持多轮对话和上下文记忆
- ⚡ **流式响应** - 实时流式输出，提供流畅的交互体验
- 💭 **思考过程可视化** - 展示 AI 的推理过程，增强透明度
- 📝 **Markdown 渲染** - 完整的 Markdown 支持，包括代码语法高亮
- 🎨 **现代化 UI** - 参考 ChatGPT、Claude 等产品的设计，简洁优雅
- 💬 **多会话管理** - 支持多个独立对话会话，历史记录侧边栏
- 🛑 **停止生成** - 随时停止 AI 响应生成
- 🐳 **Docker 支持** - 一键部署，支持开发和生产环境
- 🔧 **灵活配置** - 支持自定义 OpenAI-compatible API 和模型

## 🛠️ 技术栈

### 后端
- **Python 3.12+** - 现代 Python 特性
- **FastAPI** - 高性能异步 Web 框架
- **LlamaIndex** - LLM 应用开发框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证和设置管理

### 前端
- **Next.js 14** - React 全栈框架（App Router）
- **TypeScript** - 类型安全
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Framer Motion** - 流畅的动画效果
- **React Markdown** - Markdown 渲染
- **React Syntax Highlighter** - 代码高亮

### 开发工具
- **uv** - 快速的 Python 包管理器
- **pnpm** - 高效的 Node.js 包管理器
- **Docker & Docker Compose** - 容器化部署
- **Black, Ruff, isort** - 代码格式化和检查

## 🚀 快速开始

### 前置要求

- Python 3.12+
- Node.js 18+ 和 pnpm
- Docker 和 Docker Compose（可选，用于容器化部署）
- [uv](https://github.com/astral-sh/uv)（Python 包管理器）

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd LlamaIndex_chat

# 2. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件设置你的 API 密钥

# 3. 启动服务
docker compose up -d

# 4. 访问应用
# 前端: http://localhost:3001
# 后端: http://localhost:8000
```

### 方式二：本地开发

**启动后端：**

```bash
# 安装依赖
uv sync

# 启动服务
uv run python main.py
```

**启动前端：**

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

访问 `http://localhost:3000` 查看应用。

## ⚙️ 配置

### 环境变量

创建 `.env` 文件或设置环境变量：

```bash
# OpenAI-compatible API 配置
OPENAI_BASE_URL=https://aihubmix.com/v1
OPENAI_API_KEY=your-api-key-here

# 模型配置
MODEL_NAME=gpt-5-mini
TEMPERATURE=0.5
MAX_TOKENS=4000
```

### 配置说明

- `OPENAI_BASE_URL`: OpenAI-compatible API 的基础 URL
- `OPENAI_API_KEY`: API 密钥
- `MODEL_NAME`: 使用的模型名称（如 `gpt-5-mini`, `qwen-plus` 等）
- `TEMPERATURE`: 模型温度参数（0.0-2.0，默认 0.5）
- `MAX_TOKENS`: 最大生成 token 数（可选）

## 📡 API 文档

### POST `/api/chat`

发送聊天消息，支持流式和非流式响应。

**请求体：**
```json
{
  "message": "你好",
  "session_id": "optional-session-id",
  "stream": true
}
```

**流式响应（SSE）：**
```
data: {"type": "thinking", "content": "..."}
data: {"type": "content", "content": "你好"}
data: {"type": "done", "session_id": "..."}
```

**非流式响应：**
```json
{
  "response": "你好！有什么我可以帮助你的吗？",
  "session_id": "uuid-session-id"
}
```

### POST `/api/clear`

清除指定会话的对话历史。

**请求体：**
```json
{
  "session_id": "session-id"
}
```

### GET `/api/conversations`

获取所有会话列表。

### GET `/api/conversation/{session_id}`

获取指定会话的消息历史。

### GET `/health`

健康检查端点。

## 🐳 部署

### Docker 部署

```bash
# 构建并启动
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

### 生产环境

使用生产环境配置：

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 云服务器部署

1. 将代码上传到服务器
2. 安装 Docker 和 Docker Compose
3. 配置环境变量
4. 运行 `docker compose up -d`
5. 配置防火墙开放端口 3001 和 8000

访问：`http://YOUR_SERVER_IP:3001`

## 📁 项目结构

```
LlamaIndex_chat/
├── app/                    # 后端应用
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── agent.py           # LlamaIndex Agent 实现
│   ├── api.py             # FastAPI 路由
│   └── templates/         # HTML 模板
├── frontend/              # Next.js 前端应用
│   ├── app/               # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/        # React 组件
│   │   ├── Header.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── InputArea.tsx
│   │   ├── Sidebar.tsx
│   │   └── SidebarButton.tsx
│   ├── package.json
│   └── Dockerfile
├── main.py                # 后端入口
├── pyproject.toml         # Python 项目配置
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile.backend     # 后端 Dockerfile
└── README.md
```

## 🧑‍💻 开发

### 后端开发

```bash
# 安装开发依赖
uv sync --dev

# 运行代码格式化
uv run black app/ main.py
uv run ruff format app/ main.py
uv run isort app/ main.py

# 运行代码检查
uv run ruff check app/ main.py
```

### 前端开发

```bash
cd frontend

# 安装依赖
pnpm install

# 开发模式
pnpm run dev

# 构建
pnpm run build

# 代码格式化
pnpm run format

# 代码检查
pnpm run lint
```

## 🔍 功能特性详解

### 多轮对话

应用自动维护每个会话的对话历史，支持上下文理解。

### 流式响应

使用 Server-Sent Events (SSE) 实现实时流式输出，提供流畅的打字效果。

### 思考过程

支持显示 AI 的推理过程（如果模型支持），增强交互透明度。

### 会话管理

- 创建新会话
- 查看历史会话列表
- 加载历史对话
- 清除当前会话

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [LlamaIndex](https://www.llamaindex.ai/) - LLM 应用框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [Next.js](https://nextjs.org/) - React 框架

