#!/bin/bash

# Function to kill processes by port
kill_by_port() {
    local port=$1
    if [ -n "$port" ]; then
        echo "🔍 正在查找并停止占用端口 $port 的进程..."
        local pids=$(lsof -t -i:$port)
        if [ -n "$pids" ]; then
            kill -9 $pids
            echo "✅ 成功停止占用端口 $port 的进程 (PIDs: $pids)"
        else
            echo "🤷‍ 未找到占用端口 $port 的进程"
        fi
    fi
}

# 端口设置
BACKEND_PORT=8000
FRONTEND_PORT=3000

# 停止可能正在运行的旧服务
echo "🛑 正在停止旧服务..."
kill_by_port $BACKEND_PORT
kill_by_port $FRONTEND_PORT
pkill -f "next dev"

# 智能旅游推荐系统启动脚本

echo "🚀 启动智能旅游推荐系统..."

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，请先复制 .env.example 并配置 DeepSeek API Key"
    echo "   cp .env.example .env"
    echo "   然后编辑 .env 文件添加您的 API Key"
    exit 1
fi

# 启动后端服务
echo "📡 启动后端服务..."
cd backend
if [ ! -d ".venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

echo "🤖 启动CrewAI后端服务 (端口 8000)..."
python main.py &
BACKEND_PID=$!

cd ..

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

echo "🌐 启动Next.js前端服务 (端口 3000)..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ 系统启动完成!"
echo "🌐 前端地址: http://localhost:$FRONTEND_PORT"
echo "📡 后端API: http://localhost:$BACKEND_PORT"
echo "📚 API文档: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
