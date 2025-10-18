#!/bin/bash

# FlowState 快速测试脚本
# 自动测试所有核心功能

set -e  # 遇到错误立即退出

echo "======================================================================="
echo "FlowState 专注度监控 - 快速测试"
echo "======================================================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_step() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${YELLOW}测试: ${test_name}${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ 通过${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# 等待函数
wait_for_server() {
    echo "等待服务器启动..."
    for i in {1..10}; do
        if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
            echo "服务器已就绪"
            return 0
        fi
        sleep 1
    done
    echo "服务器启动超时"
    return 1
}

echo ""
echo "======================================================================="
echo "第 1 部分: 环境检查"
echo "======================================================================="

test_step "Python 版本" "python3 --version"
test_step "虚拟环境" "[ -d venv ] || python3 -m venv venv"
test_step "激活虚拟环境" "source venv/bin/activate && python --version"
test_step "安装依赖" "source venv/bin/activate && pip install -q -r backend/requirements.txt"
test_step "验证 Flask" "source venv/bin/activate && python -c 'import flask'"
test_step "验证 Groq" "source venv/bin/activate && python -c 'import groq'"
test_step "检查 API Key" "[ -n \"\$GROQ_API_KEY\" ]"

echo ""
echo "======================================================================="
echo "第 2 部分: 后端 API 测试"
echo "======================================================================="

# 启动后端服务器
echo "启动后端服务器..."
source venv/bin/activate
cd backend
python unified_api_server.py > /tmp/flowstate_api.log 2>&1 &
API_PID=$!
cd ..

# 等待服务器启动
if ! wait_for_server; then
    echo "无法启动服务器，查看日志:"
    cat /tmp/flowstate_api.log
    exit 1
fi

test_step "健康检查" "curl -s http://localhost:5000/api/health | grep -q '\"status\":\"ok\"'"
test_step "系统信息" "curl -s http://localhost:5000/api/info | grep -q '\"platform\"'"
test_step "启动监控" "curl -s -X POST http://localhost:5000/api/monitor/start -H 'Content-Type: application/json' -d '{\"task_name\":\"测试任务\"}' | grep -q '\"success\":true'"

sleep 2

test_step "监控状态" "curl -s http://localhost:5000/api/monitor/status | grep -q '\"monitoring_active\":true'"
test_step "检查 URL" "curl -s -X POST http://localhost:5000/api/check/url -H 'Content-Type: application/json' -d '{\"url\":\"https://docs.python.org\",\"title\":\"Python Docs\"}' | grep -q '\"success\":true'"

sleep 2

test_step "停止监控" "curl -s -X POST http://localhost:5000/api/monitor/stop | grep -q '\"success\":true'"
test_step "历史会话" "curl -s http://localhost:5000/api/history/sessions | grep -q '\"success\":true'"
test_step "统计摘要" "curl -s http://localhost:5000/api/stats/summary | grep -q '\"success\":true'"

echo ""
echo "======================================================================="
echo "第 3 部分: 窗口检测测试"
echo "======================================================================="

test_step "窗口检测 API" "curl -s http://localhost:5000/api/window/current | grep -q '\"success\"'" || echo "注意: WSL 环境可能无法检测窗口"

echo ""
echo "======================================================================="
echo "第 4 部分: AI 分析测试"
echo "======================================================================="

if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  跳过 AI 测试: 未设置 GROQ_API_KEY${NC}"
else
    # 启动新的监控会话
    curl -s -X POST http://localhost:5000/api/monitor/start -H 'Content-Type: application/json' -d '{"task_name":"学习 Python"}' > /dev/null
    
    sleep 2
    
    test_step "AI 判断相关网站" "curl -s -X POST http://localhost:5000/api/check/url -H 'Content-Type: application/json' -d '{\"url\":\"https://docs.python.org\",\"title\":\"Python Docs\"}' | grep -q '\"is_relevant\":true'"
    
    sleep 2
    
    test_step "AI 判断无关网站" "curl -s -X POST http://localhost:5000/api/check/url -H 'Content-Type: application/json' -d '{\"url\":\"https://www.youtube.com\",\"title\":\"YouTube\"}' | grep -q '\"is_relevant\":false'"
    
    # 停止监控
    curl -s -X POST http://localhost:5000/api/monitor/stop > /dev/null
fi

echo ""
echo "======================================================================="
echo "第 5 部分: 前端测试"
echo "======================================================================="

test_step "前端文件存在" "[ -f frontend/index.html ]"
test_step "前端 HTML 有效" "grep -q 'FlowState' frontend/index.html"

# 启动前端服务器
echo "启动前端服务器..."
cd frontend
python -m http.server 8000 > /tmp/flowstate_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2

test_step "前端服务器响应" "curl -s http://localhost:8000 | grep -q 'FlowState'"

echo ""
echo "======================================================================="
echo "清理"
echo "======================================================================="

echo "停止服务器..."
kill $API_PID 2>/dev/null || true
kill $FRONTEND_PID 2>/dev/null || true

echo ""
echo "======================================================================="
echo "测试总结"
echo "======================================================================="

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "${GREEN}通过: $TESTS_PASSED${NC}"
echo -e "${RED}失败: $TESTS_FAILED${NC}"
echo "总计: $TOTAL_TESTS"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=======================================================================${NC}"
    echo -e "${GREEN}🎉 所有测试通过！系统已准备就绪！${NC}"
    echo -e "${GREEN}=======================================================================${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}=======================================================================${NC}"
    echo -e "${RED}⚠️  有 $TESTS_FAILED 个测试失败，请检查错误信息${NC}"
    echo -e "${RED}=======================================================================${NC}"
    exit 1
fi

