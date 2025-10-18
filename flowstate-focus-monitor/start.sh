#!/bin/bash

echo "🚀 启动 FlowState 专注度监控系统"
echo "=================================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 检查并安装依赖..."
pip install -q -r backend/requirements.txt

# 检查 API Key
if [ -z "$GROQ_API_KEY" ]; then
    echo ""
    echo "⚠️  警告: 未设置 GROQ_API_KEY"
    echo "   AI 分析功能将不可用"
    echo "   设置方法: export GROQ_API_KEY='your-key'"
    echo ""
    read -p "是否继续（将使用模拟模式）? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 启动后端
echo ""
echo "🚀 启动后端服务器..."
cd backend
python unified_api_server.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🌐 启动前端服务器..."
cd frontend
python -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 系统已启动！"
echo "=================================="
echo "📡 后端 API: http://localhost:5000"
echo "🌐 前端 UI:  http://localhost:8000"
echo "=================================="
echo ""
echo "在浏览器中打开: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务器"

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务器..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ 已停止"
    exit 0
}

# 捕获中断信号
trap cleanup INT TERM

# 等待
wait

