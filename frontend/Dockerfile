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

# 确保 public 目录存在（Next.js 需要）
RUN mkdir -p public

# 构建 Next.js 应用
RUN pnpm run build

# 生产阶段
FROM node:20-slim AS runner

WORKDIR /app

ENV NODE_ENV=production

# 安装 pnpm
RUN npm install -g pnpm

# 复制必要的文件
COPY --from=builder /app/package.json /app/pnpm-lock.yaml ./
COPY --from=builder /app/.next ./.next
# 复制 public 目录（现在肯定存在）
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/tailwind.config.js ./
COPY --from=builder /app/postcss.config.js ./
COPY --from=builder /app/tsconfig.json ./

# 安装生产依赖
RUN pnpm install --frozen-lockfile --prod

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["pnpm", "start"]
