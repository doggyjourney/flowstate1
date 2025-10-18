#!/usr/bin/env python3
"""
FlowState 统一 API 服务器 - 黑客松版本
整合所有功能，提供完整的 REST API，方便前端 UI 集成
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import threading
import time
from datetime import datetime
from enhanced_focus_monitor import EnhancedFocusMonitor
from window_detector import WindowDetector

app = Flask(__name__)
CORS(app)  # 允许跨域，方便前端开发

# 全局状态
monitor = None
detector = WindowDetector()
auto_check_thread = None
auto_check_running = False


# ============================================================================
# 基础接口
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "service": "FlowState Focus Monitor",
        "version": "1.0.0-hackathon",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    return jsonify({
        "platform": detector.platform,
        "detector_type": detector.detector.__class__.__name__,
        "groq_api_configured": bool(os.environ.get("GROQ_API_KEY")),
        "monitoring_active": monitor.monitoring_active if monitor else False
    })


# ============================================================================
# 窗口检测接口
# ============================================================================

@app.route('/api/window/current', methods=['GET'])
def get_current_window():
    """获取当前活动窗口"""
    try:
        window_info = detector.get_active_window()
        
        if window_info:
            return jsonify({
                "success": True,
                "data": window_info,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "无法获取窗口信息"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# 监控控制接口
# ============================================================================

@app.route('/api/monitor/start', methods=['POST'])
def start_monitoring():
    """
    启动监控
    
    请求体:
    {
        "task_name": "学习 Python",
        "task_id": "optional_id",
        "auto_check": true,
        "check_interval": 10
    }
    """
    global monitor, auto_check_running, auto_check_thread
    
    data = request.json or {}
    task_name = data.get('task_name', '未命名任务')
    task_id = data.get('task_id')
    auto_check = data.get('auto_check', True)
    check_interval = data.get('check_interval', 10)
    
    try:
        # 如果已有监控在运行，先停止
        if monitor and monitor.monitoring_active:
            return jsonify({
                "success": False,
                "error": "监控已在运行，请先停止"
            }), 400
        
        # 创建新监控器
        monitor = EnhancedFocusMonitor()
        
        # 启动监控
        success = monitor.start_task_monitoring(
            task_id=task_id,
            task_name=task_name
        )
        
        if not success:
            return jsonify({
                "success": False,
                "error": "监控启动失败"
            }), 500
        
        # 启动自动检测
        if auto_check:
            auto_check_running = True
            auto_check_thread = threading.Thread(
                target=auto_check_worker,
                args=(check_interval,),
                daemon=True
            )
            auto_check_thread.start()
        
        return jsonify({
            "success": True,
            "message": "监控已启动",
            "data": {
                "task_name": task_name,
                "task_id": monitor.current_task_id,
                "auto_check": auto_check,
                "check_interval": check_interval,
                "started_at": datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitoring():
    """停止监控并获取总结"""
    global monitor, auto_check_running
    
    if not monitor or not monitor.monitoring_active:
        return jsonify({
            "success": False,
            "error": "监控未运行"
        }), 400
    
    try:
        # 停止自动检测
        auto_check_running = False
        
        # 结束监控
        summary = monitor.end_task_monitoring()
        
        if summary:
            return jsonify({
                "success": True,
                "message": "监控已停止",
                "data": summary
            })
        else:
            return jsonify({
                "success": False,
                "error": "获取总结失败"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/monitor/status', methods=['GET'])
def get_monitor_status():
    """获取当前监控状态"""
    if not monitor:
        return jsonify({
            "success": True,
            "data": {
                "monitoring_active": False
            }
        })
    
    try:
        status = monitor.get_current_status()
        status['auto_check_running'] = auto_check_running
        
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# 网站检查接口
# ============================================================================

@app.route('/api/check/current', methods=['POST'])
def check_current_website():
    """检查当前打开的网站"""
    if not monitor or not monitor.monitoring_active:
        return jsonify({
            "success": False,
            "error": "监控未运行，请先启动监控"
        }), 400
    
    try:
        result = monitor.check_current_website()
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/check/url', methods=['POST'])
def check_specific_url():
    """
    检查指定 URL
    
    请求体:
    {
        "url": "https://example.com",
        "title": "Example Site"
    }
    """
    if not monitor or not monitor.monitoring_active:
        return jsonify({
            "success": False,
            "error": "监控未运行，请先启动监控"
        }), 400
    
    data = request.json or {}
    url = data.get('url')
    title = data.get('title', url)
    
    if not url:
        return jsonify({
            "success": False,
            "error": "缺少 url 参数"
        }), 400
    
    try:
        # 临时替换获取网站的方法
        original_get = monitor.flowstate_bridge.get_current_website
        
        def temp_get():
            return {
                "url": url,
                "title": title,
                "app_id": "browser"
            }
        
        monitor.flowstate_bridge.get_current_website = temp_get
        result = monitor.check_current_website()
        monitor.flowstate_bridge.get_current_website = original_get
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# 历史记录接口
# ============================================================================

@app.route('/api/history/sessions', methods=['GET'])
def get_sessions():
    """获取所有历史会话"""
    try:
        from focus_score_calculator import FocusScoreCalculator
        
        calc = FocusScoreCalculator()
        sessions = calc.get_all_sessions()
        
        return jsonify({
            "success": True,
            "data": {
                "sessions": sessions,
                "total": len(sessions)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/history/session/<session_id>', methods=['GET'])
def get_session_detail(session_id):
    """获取特定会话详情"""
    try:
        from focus_score_calculator import FocusScoreCalculator
        
        calc = FocusScoreCalculator()
        session = calc.get_session(session_id)
        
        if session:
            return jsonify({
                "success": True,
                "data": session
            })
        else:
            return jsonify({
                "success": False,
                "error": "会话不存在"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# 统计接口
# ============================================================================

@app.route('/api/stats/summary', methods=['GET'])
def get_stats():
    """获取统计摘要"""
    try:
        from focus_score_calculator import FocusScoreCalculator
        
        calc = FocusScoreCalculator()
        sessions = calc.get_all_sessions()
        
        if not sessions:
            return jsonify({
                "success": True,
                "data": {
                    "total_sessions": 0,
                    "total_duration_minutes": 0,
                    "average_focus_score": 0,
                    "total_checks": 0
                }
            })
        
        total_duration = sum(s.get('total_duration', 0) for s in sessions)
        total_checks = sum(
            s.get('relevant_websites', 0) + s.get('irrelevant_websites', 0)
            for s in sessions
        )
        avg_score = sum(s.get('focus_score', 0) for s in sessions) / len(sessions)
        
        return jsonify({
            "success": True,
            "data": {
                "total_sessions": len(sessions),
                "total_duration_minutes": round(total_duration / 60, 1),
                "average_focus_score": round(avg_score, 1),
                "total_checks": total_checks
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/stats/current', methods=['GET'])
def get_current_stats():
    """获取当前会话的实时统计"""
    if not monitor or not monitor.monitoring_active:
        return jsonify({
            "success": False,
            "error": "监控未运行"
        }), 400
    
    try:
        status = monitor.get_current_status()
        
        return jsonify({
            "success": True,
            "data": {
                "task_name": status.get('task_name'),
                "duration_seconds": status.get('duration_seconds', 0),
                "relevant_websites": status.get('relevant_websites', 0),
                "irrelevant_websites": status.get('irrelevant_websites', 0),
                "current_focus_score": status.get('current_focus_score', 0),
                "total_checks": status.get('relevant_websites', 0) + status.get('irrelevant_websites', 0)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# 自动检测工作线程
# ============================================================================

def auto_check_worker(interval):
    """后台自动检测线程"""
    global auto_check_running, monitor
    
    print(f"[自动检测] 已启动，间隔 {interval} 秒")
    
    while auto_check_running:
        try:
            if monitor and monitor.monitoring_active:
                result = monitor.check_current_website()
                
                if result.get("success"):
                    relevance = "✅ 相关" if result['is_relevant'] else "❌ 不相关"
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"{result['website_url'][:50]} - {relevance} - "
                          f"专注度: {result['current_focus_score']:.1f}")
                else:
                    print(f"[自动检测] 失败: {result.get('error', '未知')}")
        except Exception as e:
            print(f"[自动检测] 异常: {e}")
        
        time.sleep(interval)
    
    print("[自动检测] 已停止")


# ============================================================================
# 启动服务器
# ============================================================================

def print_api_docs():
    """打印 API 文档"""
    print("\n" + "=" * 70)
    print("API 端点列表")
    print("=" * 70)
    
    endpoints = [
        ("GET",  "/api/health",              "健康检查"),
        ("GET",  "/api/info",                "系统信息"),
        ("GET",  "/api/window/current",      "获取当前窗口"),
        ("POST", "/api/monitor/start",       "启动监控"),
        ("POST", "/api/monitor/stop",        "停止监控"),
        ("GET",  "/api/monitor/status",      "监控状态"),
        ("POST", "/api/check/current",       "检查当前网站"),
        ("POST", "/api/check/url",           "检查指定 URL"),
        ("GET",  "/api/history/sessions",    "历史会话列表"),
        ("GET",  "/api/history/session/:id", "会话详情"),
        ("GET",  "/api/stats/summary",       "统计摘要"),
        ("GET",  "/api/stats/current",       "当前会话统计"),
    ]
    
    for method, path, desc in endpoints:
        print(f"  {method:4s}  {path:30s}  {desc}")
    
    print("=" * 70 + "\n")


def main():
    """启动服务器"""
    print("=" * 70)
    print("FlowState 专注度监控 - 统一 API 服务器")
    print("黑客松版本 v1.0.0")
    print("=" * 70)
    
    # 环境检查
    if not os.environ.get("GROQ_API_KEY"):
        print("\n⚠️  警告: 未设置 GROQ_API_KEY")
        print("   AI 分析功能将不可用")
        print("   设置: export GROQ_API_KEY='your-key'\n")
    else:
        print("\n✅ GROQ_API_KEY 已配置")
    
    print(f"✅ 平台: {detector.platform}")
    print(f"✅ 检测器: {detector.detector.__class__.__name__}")
    
    # 打印 API 文档
    print_api_docs()
    
    # 启动服务器
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 服务器地址: http://localhost:{port}")
    print(f"📖 API 文档: http://localhost:{port}/api/health")
    print("\n按 Ctrl+C 停止服务器\n")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    # 确保 flask-cors 已安装
    try:
        from flask_cors import CORS
    except ImportError:
        print("正在安装 flask-cors...")
        import subprocess
        subprocess.run(["pip", "install", "flask-cors"], check=True)
        from flask_cors import CORS
    
    main()

