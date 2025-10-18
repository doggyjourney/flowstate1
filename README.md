# FlowState 专注度监控 - 完整测试指导

**版本**: 1.0.0  
**更新**: 2025年10月18日

---

## 📋 测试概览

本指南将带您完成以下测试：

1. ✅ **环境准备测试** - 确保所有依赖正确安装
2. ✅ **后端 API 测试** - 验证 API 服务器功能
3. ✅ **窗口检测测试** - 测试窗口检测功能
4. ✅ **AI 分析测试** - 验证 AI 判断准确性
5. ✅ **前端 UI 测试** - 测试 Web 界面
6. ✅ **完整流程测试** - 端到端测试
7. ✅ **黑客松演示测试** - 准备演示

**预计时间**: 20-30 分钟

---

## 🎯 测试前准备

### 1. 确认项目文件

```bash
cd /path/to/flowstate-focus-monitor

# 检查文件完整性
ls -la backend/
ls -la frontend/
ls -la *.sh *.md
```

**预期结果**:
```
backend/:
  - unified_api_server.py
  - enhanced_focus_monitor.py
  - window_detector.py
  - focus_score_calculator.py
  - flowstate_bridge.py
  - requirements.txt

frontend/:
  - index.html

根目录:
  - start.sh
  - README.md
  - .gitignore
```

### 2. 设置环境变量

```bash
# 设置 Groq API Key
export GROQ_API_KEY='your-groq-api-key-here'

# 验证设置
echo $GROQ_API_KEY
```

**预期结果**: 显示您的 API Key

---

## 📝 测试 1: 环境准备测试

### 目标
验证 Python 环境和依赖安装正确。

### 步骤

#### 1.1 检查 Python 版本

```bash
python3 --version
```

**预期结果**: Python 3.8 或更高版本
```
Python 3.10.x 或 Python 3.11.x 或 Python 3.12.x
```

#### 1.2 创建虚拟环境

```bash
python3 -m venv venv
```

**预期结果**: 创建 `venv/` 目录，无错误信息

**如果报错** `No module named venv`:
```bash
sudo apt update
sudo apt install python3-venv python3-full -y
# 然后重新运行上面的命令
```

#### 1.3 激活虚拟环境

```bash
source venv/bin/activate
```

**预期结果**: 命令提示符前出现 `(venv)`
```
(venv) user@machine:~/flowstate-focus-monitor$
```

#### 1.4 安装依赖

```bash
pip install -r backend/requirements.txt
```

**预期结果**: 成功安装 3 个包
```
Successfully installed flask-x.x.x flask-cors-x.x.x groq-x.x.x
```

#### 1.5 验证安装

```bash
python -c "import flask; import groq; print('✅ 所有依赖安装成功')"
```

**预期结果**:
```
✅ 所有依赖安装成功
```

---

## 📝 测试 2: 后端 API 测试

### 目标
验证 API 服务器可以正常启动和响应。

### 步骤

#### 2.1 启动 API 服务器

```bash
# 确保在虚拟环境中
cd backend
python unified_api_server.py
```

**预期结果**: 服务器成功启动
```
======================================================================
FlowState 专注度监控 - 统一 API 服务器
黑客松版本 v1.0.0
======================================================================

✅ GROQ_API_KEY 已配置
✅ 平台: Linux
✅ 检测器: LinuxDetector

======================================================================
API 端点列表
======================================================================
  GET   /api/health                     健康检查
  POST  /api/monitor/start              启动监控
  ...
======================================================================

🚀 服务器地址: http://localhost:5000
```

**如果看到警告** `⚠️ 警告: 未设置 GROQ_API_KEY`:
```bash
# 停止服务器 (Ctrl+C)
export GROQ_API_KEY='your-key'
# 重新启动
python unified_api_server.py
```

#### 2.2 测试健康检查（新开一个终端）

```bash
# 在新终端中
curl http://localhost:5000/api/health
```

**预期结果**: 返回 JSON
```json
{
  "status": "ok",
  "service": "FlowState Focus Monitor",
  "version": "1.0.0-hackathon",
  "timestamp": "2025-10-18T..."
}
```

#### 2.3 测试系统信息

```bash
curl http://localhost:5000/api/info
```

**预期结果**:
```json
{
  "platform": "Linux",
  "detector_type": "LinuxDetector",
  "groq_api_configured": true,
  "monitoring_active": false
}
```

#### 2.4 测试启动监控

```bash
curl -X POST http://localhost:5000/api/monitor/start \
  -H "Content-Type: application/json" \
  -d '{"task_name": "测试任务"}'
```

**预期结果**:
```json
{
  "success": true,
  "message": "监控已启动",
  "data": {
    "task_name": "测试任务",
    "task_id": "session_...",
    "auto_check": true,
    "check_interval": 10,
    "started_at": "2025-10-18T..."
  }
}
```

#### 2.5 测试监控状态

```bash
curl http://localhost:5000/api/monitor/status
```

**预期结果**:
```json
{
  "success": true,
  "data": {
    "monitoring_active": true,
    "task_name": "测试任务",
    "duration_seconds": ...,
    "relevant_websites": 0,
    "irrelevant_websites": 0,
    "current_focus_score": 100,
    "auto_check_running": true
  }
}
```

#### 2.6 测试停止监控

```bash
curl -X POST http://localhost:5000/api/monitor/stop
```

**预期结果**:
```json
{
  "success": true,
  "message": "监控已停止",
  "data": {
    "session_id": "session_...",
    "task_name": "测试任务",
    "duration_minutes": ...,
    "relevant_websites": ...,
    "irrelevant_websites": ...,
    "focus_score": ...,
    "grade": "..."
  }
}
```

**✅ 测试通过标准**: 所有 API 都返回正确的 JSON，无错误

---

## 📝 测试 3: 窗口检测测试

### 目标
验证窗口检测功能是否正常工作。

### 步骤

#### 3.1 测试窗口检测（API 方式）

```bash
# 确保 API 服务器在运行
curl http://localhost:5000/api/window/current
```

**预期结果（成功）**:
```json
{
  "success": true,
  "data": {
    "url": "https://...",
    "title": "...",
    "app_id": "chrome"
  },
  "timestamp": "..."
}
```

**预期结果（WSL 环境，可能失败）**:
```json
{
  "success": false,
  "error": "无法获取窗口信息"
}
```

**如果失败**: 这是正常的，WSL 无法直接检测 Windows 窗口。

#### 3.2 测试窗口检测（Python 方式）

```bash
# 在虚拟环境中
cd backend
python -c "
from window_detector import WindowDetector
detector = WindowDetector()
window = detector.get_active_window()
print('检测结果:', window)
"
```

**预期结果（成功）**:
```
检测结果: {'url': 'https://...', 'title': '...', 'app_id': '...'}
```

**预期结果（失败）**:
```
检测结果: None
```

**✅ 测试通过标准**: 
- Windows 上运行: 应该成功检测
- WSL 中运行: 失败是正常的，继续测试其他功能

---

## 📝 测试 4: AI 分析测试

### 目标
验证 AI 相关性判断功能。

### 前提条件
- ✅ API 服务器正在运行
- ✅ GROQ_API_KEY 已设置

### 步骤

#### 4.1 启动监控

```bash
curl -X POST http://localhost:5000/api/monitor/start \
  -H "Content-Type: application/json" \
  -d '{"task_name": "学习 Python 编程"}'
```

#### 4.2 测试相关网站判断

```bash
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org", "title": "Python Documentation"}'
```

**预期结果**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "website_url": "https://docs.python.org",
    "website_title": "Python Documentation",
    "is_relevant": true,
    "confidence": "高",
    "reason": "Python 官方文档与学习 Python 编程任务高度相关...",
    "current_focus_score": ...,
    "timestamp": "..."
  }
}
```

**关键检查点**:
- ✅ `is_relevant`: true
- ✅ `confidence`: "高"
- ✅ `reason`: 包含合理的解释

#### 4.3 测试无关网站判断

```bash
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com", "title": "YouTube"}'
```

**预期结果**:
```json
{
  "success": true,
  "data": {
    "success": true,
    "website_url": "https://www.youtube.com",
    "website_title": "YouTube",
    "is_relevant": false,
    "confidence": "高",
    "reason": "YouTube 是视频娱乐平台，与学习 Python 编程无关...",
    "current_focus_score": ...,
    "timestamp": "..."
  }
}
```

**关键检查点**:
- ✅ `is_relevant`: false
- ✅ `confidence`: "高"
- ✅ `reason`: 包含合理的解释

#### 4.4 测试多个网站

测试以下网站，验证 AI 判断的准确性：

**相关网站**（应该判断为 relevant: true）:
```bash
# Stack Overflow
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stackoverflow.com/questions/tagged/python"}'

# GitHub Python 项目
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/python"}'

# Python 教程
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://realpython.com"}'
```

**无关网站**（应该判断为 relevant: false）:
```bash
# Facebook
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.facebook.com"}'

# Twitter
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://twitter.com"}'

# Netflix
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.netflix.com"}'
```

#### 4.5 停止监控并查看总结

```bash
curl -X POST http://localhost:5000/api/monitor/stop
```

**预期结果**: 包含完整的会话总结

**✅ 测试通过标准**: 
- AI 正确判断相关网站（准确率 > 80%）
- AI 正确判断无关网站（准确率 > 90%）
- 提供合理的理由

---

## 📝 测试 5: 前端 UI 测试

### 目标
验证 Web 界面功能正常。

### 步骤

#### 5.1 启动前端服务器

```bash
# 在新终端中
cd /path/to/flowstate-focus-monitor/frontend
python -m http.server 8000
```

**预期结果**:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

#### 5.2 打开浏览器

在浏览器中访问: `http://localhost:8000`

**预期结果**: 看到 FlowState 专注度监控界面

#### 5.3 测试启动页面

**检查点**:
- ✅ 看到标题: "🎯 FlowState 专注度监控"
- ✅ 看到输入框: "请输入您的任务名称"
- ✅ 看到按钮: "开始监控"

**操作**:
1. 在输入框输入: "学习 Python 编程"
2. 点击"开始监控"按钮

**预期结果**: 
- 页面切换到监控页面
- 无错误提示

**如果出现错误**: 检查后端 API 服务器是否在运行

#### 5.4 测试监控页面

**检查点**:
- ✅ 看到大字显示的专注度分数
- ✅ 看到"相关网站"和"无关网站"统计
- ✅ 看到"当前网站"信息
- ✅ 看到"停止监控"按钮

**观察**:
- 专注度分数应该从 100 开始
- 每 3 秒自动更新一次
- 如果有窗口检测，会显示当前网站

#### 5.5 测试手动检查（使用浏览器开发者工具）

按 F12 打开开发者工具，切换到 Console 标签，输入:

```javascript
// 手动触发检查
fetch('http://localhost:5000/api/check/url', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    url: 'https://docs.python.org',
    title: 'Python Docs'
  })
}).then(r => r.json()).then(console.log)
```

**预期结果**: 
- Console 中显示 JSON 响应
- 页面上的统计数字更新

#### 5.6 测试停止监控

**操作**:
1. 点击"停止监控"按钮

**预期结果**:
- 页面切换到总结页面
- 显示最终专注度分数
- 显示评级（优秀/良好/一般/需要改进）
- 显示详细统计

#### 5.7 测试重新开始

**操作**:
1. 点击"重新开始"按钮

**预期结果**:
- 返回启动页面
- 可以输入新任务

**✅ 测试通过标准**: 
- 所有页面正常显示
- 数据实时更新
- 无 JavaScript 错误

---

## 📝 测试 6: 完整流程测试

### 目标
模拟真实使用场景，端到端测试。

### 场景: 学习 Python 的 30 分钟专注会话

#### 6.1 准备

```bash
# 终端 1: 启动后端
cd backend
python unified_api_server.py

# 终端 2: 启动前端
cd frontend
python -m http.server 8000
```

#### 6.2 开始会话

1. 打开浏览器: `http://localhost:8000`
2. 输入任务: "学习 Python 编程"
3. 点击"开始监控"

#### 6.3 模拟浏览行为

使用 curl 或浏览器开发者工具，模拟访问不同网站：

```bash
# 相关网站 1: Python 文档
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org"}'

# 等待 10 秒

# 相关网站 2: Stack Overflow
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stackoverflow.com/questions/tagged/python"}'

# 等待 10 秒

# 无关网站 1: YouTube
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com"}'

# 等待 10 秒

# 相关网站 3: GitHub
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/python"}'

# 等待 10 秒

# 无关网站 2: Facebook
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.facebook.com"}'
```

#### 6.4 观察变化

在浏览器中观察:
- ✅ 相关网站计数增加（应该是 3）
- ✅ 无关网站计数增加（应该是 2）
- ✅ 专注度分数变化（应该下降）

#### 6.5 结束会话

1. 点击"停止监控"
2. 查看总结报告

**预期结果**:
```
专注度分数: 约 70-80 分
评级: 良好
相关网站: 3 次
无关网站: 2 次
```

#### 6.6 查看历史记录

```bash
curl http://localhost:5000/api/history/sessions
```

**预期结果**: 包含刚才的会话记录

**✅ 测试通过标准**: 
- 完整流程无错误
- 数据准确记录
- 分数计算合理

---

## 📝 测试 7: 黑客松演示测试

### 目标
确保演示时一切顺利。

### 步骤

#### 7.1 演示前检查清单

```bash
# 1. 检查环境变量
echo $GROQ_API_KEY

# 2. 检查文件完整性
ls backend/*.py
ls frontend/*.html

# 3. 检查虚拟环境
source venv/bin/activate
pip list | grep -E "flask|groq"

# 4. 测试启动脚本
./start.sh
# 等待启动完成，然后 Ctrl+C 停止
```

#### 7.2 准备演示数据

创建演示脚本:

```bash
# 创建 demo_test.sh
cat > demo_test.sh << 'EOF'
#!/bin/bash

echo "=== 演示测试脚本 ==="

# 启动监控
echo "1. 启动监控..."
curl -X POST http://localhost:5000/api/monitor/start \
  -H "Content-Type: application/json" \
  -d '{"task_name": "学习 Python 编程"}' | jq

sleep 2

# 相关网站
echo -e "\n2. 检查相关网站..."
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://docs.python.org", "title": "Python Docs"}' | jq '.data | {url, is_relevant, confidence, reason}'

sleep 2

# 无关网站
echo -e "\n3. 检查无关网站..."
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com", "title": "YouTube"}' | jq '.data | {url, is_relevant, confidence, reason}'

sleep 2

# 查看状态
echo -e "\n4. 查看当前状态..."
curl http://localhost:5000/api/monitor/status | jq '.data | {task_name, relevant_websites, irrelevant_websites, current_focus_score}'

sleep 2

# 停止监控
echo -e "\n5. 停止监控..."
curl -X POST http://localhost:5000/api/monitor/stop | jq '.data | {task_name, focus_score, grade}'

echo -e "\n=== 演示测试完成 ==="
EOF

chmod +x demo_test.sh
```

#### 7.3 运行演示测试

```bash
# 启动后端
cd backend
python unified_api_server.py &

# 等待启动
sleep 3

# 运行演示
cd ..
./demo_test.sh
```

**预期结果**: 所有步骤成功执行，输出清晰

#### 7.4 UI 演示测试

1. 打开 `http://localhost:8000`
2. 输入任务: "学习 Python 编程"
3. 开始监控
4. 在开发者工具中运行检查脚本
5. 观察数据更新
6. 停止监控
7. 查看报告

**计时**: 整个演示应在 3 分钟内完成

**✅ 测试通过标准**: 
- 演示流程顺畅
- 无卡顿或错误
- 数据展示清晰

---

## 🐛 常见问题排查

### 问题 1: API 服务器无法启动

**症状**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :5000
# 或
netstat -tulpn | grep 5000

# 杀死进程
kill -9 <PID>

# 或更改端口
export PORT=5001
python unified_api_server.py
```

### 问题 2: 无法检测窗口

**症状**: `{"success": false, "error": "无法获取窗口信息"}`

**原因**: WSL 环境限制

**解决**: 使用手动输入模式
```bash
curl -X POST http://localhost:5000/api/check/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 问题 3: AI 分析失败

**症状**: `API key error` 或 `Rate limit exceeded`

**解决**:
```bash
# 检查 API Key
echo $GROQ_API_KEY

# 重新设置
export GROQ_API_KEY='your-correct-key'

# 等待速率限制重置（通常 1 分钟）
```

### 问题 4: 前端无法连接后端

**症状**: 浏览器 Console 显示 `Failed to fetch`

**解决**:
```bash
# 1. 检查后端是否运行
curl http://localhost:5000/api/health

# 2. 检查 CORS 设置
# 确保 unified_api_server.py 中有:
# CORS(app)

# 3. 检查防火墙
sudo ufw allow 5000
```

---

## ✅ 测试完成检查清单

完成所有测试后，确认:

- [ ] ✅ 环境准备测试通过
- [ ] ✅ 后端 API 所有端点正常
- [ ] ✅ 窗口检测功能测试（或确认限制）
- [ ] ✅ AI 分析准确率 > 80%
- [ ] ✅ 前端 UI 所有功能正常
- [ ] ✅ 完整流程测试通过
- [ ] ✅ 黑客松演示准备就绪

---

## 📊 测试报告模板

```markdown
# FlowState 测试报告

**测试日期**: 2025-10-18
**测试人员**: [您的名字]
**测试环境**: WSL Ubuntu 22.04 / Python 3.10

## 测试结果

| 测试项 | 状态 | 备注 |
|:-------|:----:|:-----|
| 环境准备 | ✅ | 所有依赖安装成功 |
| 后端 API | ✅ | 12 个端点全部正常 |
| 窗口检测 | ⚠️ | WSL 限制，使用手动模式 |
| AI 分析 | ✅ | 准确率 90% |
| 前端 UI | ✅ | 所有功能正常 |
| 完整流程 | ✅ | 端到端测试通过 |
| 演示准备 | ✅ | 3 分钟演示流程顺畅 |

## 发现的问题

1. WSL 环境无法检测 Windows 窗口 - 已使用手动输入模式替代
2. 无其他问题

## 结论

系统功能完整，可以用于黑客松演示。
```

---

## 🎉 测试完成！

恭喜！如果您完成了所有测试，说明系统已经准备就绪。

**下一步**:
1. 准备黑客松演示脚本
2. 练习演示流程
3. 准备评委问题回答

**祝您黑客松顺利！** 🚀

