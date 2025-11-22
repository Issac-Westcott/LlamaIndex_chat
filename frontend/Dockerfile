# 前端 Dockerfile
FROM node:20-slim AS base

# 安装 pnpm
RUN npm install -g pnpm

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建阶段
FROM base AS builder

# 设置构建时环境变量
ARG NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# 确保 public 目录存在（Next.js 需要）
RUN mkdir -p public

# 构建 Next.js 应用（standalone 模式）
RUN pnpm run build

# 生产阶段
FROM node:20-slim AS runner

WORKDIR /app

ENV NODE_ENV=production
# 运行时环境变量
ENV NEXT_PUBLIC_API_URL=http://backend:8000

# 复制 standalone 输出
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# 暴露端口（容器内部监听 3000）
EXPOSE 3000

# 启动命令
CMD ["node", "server.js"]
