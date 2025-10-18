# FlowState 专注度监控系统

> 使用 AI 实时监控您的专注度，帮助您保持高效工作和学习。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ 功能特点

- 🔍 **实时窗口检测** - 自动获取当前打开的网站
- 🤖 **AI 智能判断** - 使用 Groq AI 判断网站是否与任务相关
- 📊 **专注度计算** - 多维度评分系统（0-100 分）
- 📈 **历史记录** - 完整的会话记录和统计
- 🌐 **Web 界面** - 简洁美观的用户界面
- 🔌 **REST API** - 完整的 API 接口，易于集成

---

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Groq API Key（[免费获取](https://console.groq.com)）

### 安装

1. **克隆或下载项目**

```bash
cd flowstate-focus-monitor
```

2. **设置 API Key**

```bash
export GROQ_API_KEY='your-groq-api-key'
```

3. **启动系统**

```bash
chmod +x start.sh
./start.sh
```

4. **打开浏览器**

访问: http://localhost:8000

---

## 📖 使用说明

### 1. 启动监控

- 在 Web 界面输入任务名称（如："学习 Python 编程"）
- 点击"开始监控"按钮

### 2. 自动检测

- 系统每 10 秒自动检测当前打开的网站
- AI 判断网站是否与任务相关
- 实时更新专注度分数

### 3. 查看结果

- 实时查看专注度分数和统计
- 点击"停止监控"查看完整报告
- 包含详细的会话总结和评级

---

## 🏗️ 项目结构

```
flowstate-focus-monitor/
├── backend/                       # 后端代码
│   ├── unified_api_server.py     # API 服务器
│   ├── enhanced_focus_monitor.py # 监控核心
│   ├── window_detector.py        # 窗口检测
│   ├── focus_score_calculator.py # 分数计算
│   ├── flowstate_bridge.py       # FlowState 集成
│   └── requirements.txt          # Python 依赖
├── frontend/                      # 前端代码
│   └── index.html                # Web UI
├── data/                          # 数据目录
│   └── focus_sessions.json       # 会话记录（自动生成）
├── start.sh                       # 启动脚本
└── README.md                      # 项目说明
```

---

## 🔧 技术栈

### 后端

- **Python 3.8+**
- **Flask** - Web 框架
- **Groq API** - AI 模型（llama-3.3-70b）

### 前端

- **HTML5**
- **CSS3** - 响应式设计
- **JavaScript** - 原生 JS，无框架依赖

### 窗口检测

- **Windows**: PowerShell
- **macOS**: AppleScript
- **Linux**: xdotool

---

## 📡 API 文档

### 基础端点

| 端点 | 方法 | 功能 |
|:-----|:----:|:-----|
| `/api/health` | GET | 健康检查 |
| `/api/info` | GET | 系统信息 |
| `/api/window/current` | GET | 获取当前窗口 |

### 监控端点

| 端点 | 方法 | 功能 |
|:-----|:----:|:-----|
| `/api/monitor/start` | POST | 启动监控 |
| `/api/monitor/stop` | POST | 停止监控 |
| `/api/monitor/status` | GET | 监控状态 |

### 检查端点

| 端点 | 方法 | 功能 |
|:-----|:----:|:-----|
| `/api/check/current` | POST | 检查当前网站 |
| `/api/check/url` | POST | 检查指定 URL |

### 历史端点

| 端点 | 方法 | 功能 |
|:-----|:----:|:-----|
| `/api/history/sessions` | GET | 历史会话列表 |
| `/api/history/session/:id` | GET | 会话详情 |
| `/api/stats/summary` | GET | 统计摘要 |

完整 API 文档请参考后端代码注释。

---

## 🎯 使用场景

- 📚 **学生** - 学习时保持专注，避免分心
- 💻 **开发者** - 工作时提高效率，减少干扰
- 🏠 **远程工作者** - 监控工作状态，提升生产力
- 👥 **团队** - 追踪团队整体专注度（需扩展）

---

## 🔒 隐私说明

- ✅ 所有数据本地存储
- ✅ 仅 URL 和标题发送给 AI API
- ✅ 不收集个人隐私信息
- ✅ 用户可随时删除历史记录

---

## 🐛 故障排除

### 问题 1: 无法检测窗口

**原因**: 系统权限不足或工具未安装

**解决**:
- **Linux**: 安装 xdotool: `sudo apt install xdotool`
- **macOS**: 授予终端辅助功能权限
- **Windows**: 以管理员身份运行

### 问题 2: API Key 错误

**原因**: 未设置或设置错误

**解决**:
```bash
export GROQ_API_KEY='your-actual-api-key'
```

### 问题 3: 端口被占用

**原因**: 5000 或 8000 端口被其他程序占用

**解决**:
```bash
# 修改 unified_api_server.py 中的端口
# 或停止占用端口的程序
```

---

## 🚧 未来计划

- [ ] 浏览器扩展（Chrome/Firefox）
- [ ] 桌面应用（Electron）
- [ ] 移动端支持
- [ ] 团队协作功能
- [ ] 数据可视化图表
- [ ] 本地 AI 模型支持
- [ ] 多任务并行追踪

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 👥 作者

FlowState Team

---

## 🙏 致谢

- [Groq](https://groq.com) - 提供高速 AI 推理
- [Flask](https://flask.palletsprojects.com) - Web 框架
- 所有开源贡献者

---

**如有问题，请提交 Issue 或联系我们！** 📧

