#!/usr/bin/env python3
"""
FlowState 到 TaskFocusMonitor 的桥接脚本
从 flowstate 获取当前任务和网站数据，传递给 task_focus_monitor.py
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class FlowStateBridge:
    """FlowState 数据桥接器"""
    
    def __init__(self, flowstate_path: str = None):
        """
        初始化桥接器
        
        参数:
            flowstate_path: flowstate 项目路径，默认为 ../flowstate
        """
        if flowstate_path:
            self.flowstate_path = Path(flowstate_path)
        else:
            # 默认路径：从 API/websiteChecker 到 flowstate
            self.flowstate_path = Path(__file__).parent.parent.parent / "flowstate"
        
        self.store_file = self.flowstate_path / "dist" / "store.js"
        self.config_file = self.flowstate_path / "dist" / "config.js"
        
    def get_current_task(self) -> Optional[Dict]:
        """
        获取当前任务信息
        
        返回:
            dict: 任务信息，包含 id, name, resources 等
        """
        try:
            # 使用 flowstate CLI 获取任务列表
            result = self._run_flowstate_command(["task:list"])
            if not result:
                return None
                
            # 解析任务列表，获取最新的任务
            lines = result.strip().split('\n')
            if not lines or not lines[0]:
                return None
                
            # 第一行是最新的任务
            parts = lines[0].split('\t')
            if len(parts) < 3:
                return None
                
            task_id = parts[0]
            task_name = parts[1]
            
            # 获取任务详细信息
            task_detail = self._run_flowstate_command(["task:show", task_id])
            if not task_detail:
                return None
                
            try:
                task_data = json.loads(task_detail)
                return task_data
            except json.JSONDecodeError:
                # 如果解析失败，返回基本信息
                return {
                    "id": task_id,
                    "name": task_name,
                    "resources": []
                }
                
        except Exception as e:
            print(f"获取当前任务失败: {e}")
            return None
    
    def get_current_website(self, use_real_detection: bool = True) -> Optional[Dict]:
        """
        获取当前网站信息
        
        参数:
            use_real_detection: 是否使用真实窗口检测（默认 True）
        
        返回:
            dict: 网站信息，包含 url, title 等
        """
        try:
            if use_real_detection:
                # 使用真实窗口检测
                try:
                    from window_detector import WindowDetector
                    detector = WindowDetector()
                    window_info = detector.get_active_window()
                    
                    if window_info:
                        print(f"[真实检测] 获取到窗口: {window_info.get('title', 'N/A')}")
                        return window_info
                    else:
                        print("[真实检测] 未能获取窗口信息，使用模拟数据")
                        return self._get_mock_website_data()
                except ImportError:
                    print("[警告] window_detector 模块未找到，使用模拟数据")
                    return self._get_mock_website_data()
                except Exception as e:
                    print(f"[真实检测] 检测失败: {e}，使用模拟数据")
                    return self._get_mock_website_data()
            else:
                # 使用模拟数据（开发/测试模式）
                return self._get_mock_website_data()
        except Exception as e:
            print(f"获取当前网站失败: {e}")
            return None
    
    def _get_mock_website_data(self) -> Dict:
        """
        模拟获取当前网站数据（开发环境用）
        """
        # 模拟一些常见的网站
        mock_websites = [
            {
                "url": "https://docs.google.com/document/d/123",
                "title": "Google Docs - 我的文档",
                "app_id": "browser"
            },
            {
                "url": "https://stackoverflow.com/questions/123456",
                "title": "Stack Overflow - Python 问题",
                "app_id": "browser"
            },
            {
                "url": "https://github.com/user/repo",
                "title": "GitHub - 项目仓库",
                "app_id": "browser"
            },
            {
                "url": "https://www.youtube.com/watch?v=123",
                "title": "YouTube - 视频标题",
                "app_id": "browser"
            }
        ]
        
        import random
        return random.choice(mock_websites)
    
    def _run_flowstate_command(self, args: List[str]) -> Optional[str]:
        """
        运行 flowstate CLI 命令
        
        参数:
            args: 命令参数列表
            
        返回:
            str: 命令输出
        """
        try:
            # 构建完整命令
            cmd = ["node", str(self.flowstate_path / "dist" / "cli.js")] + args
            
            # 设置工作目录
            result = subprocess.run(
                cmd,
                cwd=str(self.flowstate_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"FlowState 命令执行失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("FlowState 命令执行超时")
            return None
        except Exception as e:
            print(f"执行 FlowState 命令时出错: {e}")
            return None
    
    def get_task_resources(self, task_id: str) -> List[Dict]:
        """
        获取任务的资源列表
        
        参数:
            task_id: 任务ID
            
        返回:
            list: 资源列表
        """
        try:
            task_detail = self._run_flowstate_command(["task:show", task_id])
            if not task_detail:
                return []
                
            task_data = json.loads(task_detail)
            return task_data.get("resources", [])
            
        except Exception as e:
            print(f"获取任务资源失败: {e}")
            return []
    
    def format_task_for_monitor(self, task: Dict) -> str:
        """
        将任务信息格式化为 task_focus_monitor 可用的格式
        
        参数:
            task: 任务数据
            
        返回:
            str: 格式化的任务描述
        """
        if not task:
            return "未知任务"
            
        task_name = task.get("name", "未知任务")
        resources = task.get("resources", [])
        
        # 构建任务描述
        description = f"任务: {task_name}"
        
        if resources:
            resource_descriptions = []
            for resource in resources:
                if resource.get("kind") == "url":
                    url = resource.get("id", "")
                    title = resource.get("title", "")
                    if title:
                        resource_descriptions.append(f"{title} ({url})")
                    else:
                        resource_descriptions.append(url)
                elif resource.get("kind") == "app":
                    app_id = resource.get("id", "")
                    title = resource.get("title", "")
                    if title:
                        resource_descriptions.append(f"{title} ({app_id})")
                    else:
                        resource_descriptions.append(app_id)
            
            if resource_descriptions:
                description += f"\n相关资源: {', '.join(resource_descriptions[:5])}"  # 只显示前5个资源
        
        return description
    
    def format_website_for_monitor(self, website: Dict) -> Tuple[str, str]:
        """
        将网站信息格式化为 task_focus_monitor 可用的格式
        
        参数:
            website: 网站数据
            
        返回:
            tuple: (url, description)
        """
        if not website:
            return "", ""
            
        url = website.get("url", "")
        title = website.get("title", "")
        app_id = website.get("app_id", "")
        
        description = ""
        if title:
            description = title
        if app_id and app_id != "browser":
            description += f" (应用: {app_id})"
            
        return url, description


def main():
    """主函数 - 演示桥接功能"""
    print("=" * 70)
    print("FlowState 到 TaskFocusMonitor 桥接器")
    print("=" * 70)
    
    # 创建桥接器
    bridge = FlowStateBridge()
    
    # 获取当前任务
    print("1. 获取当前任务...")
    task = bridge.get_current_task()
    if task:
        print(f"   任务ID: {task.get('id', 'N/A')}")
        print(f"   任务名称: {task.get('name', 'N/A')}")
        print(f"   资源数量: {len(task.get('resources', []))}")
        
        # 格式化任务描述
        task_description = bridge.format_task_for_monitor(task)
        print(f"   格式化描述: {task_description}")
    else:
        print("   未找到当前任务")
        return
    
    # 获取当前网站
    print("\n2. 获取当前网站...")
    website = bridge.get_current_website()
    if website:
        print(f"   URL: {website.get('url', 'N/A')}")
        print(f"   标题: {website.get('title', 'N/A')}")
        print(f"   应用: {website.get('app_id', 'N/A')}")
        
        # 格式化网站信息
        url, description = bridge.format_website_for_monitor(website)
        print(f"   格式化URL: {url}")
        print(f"   格式化描述: {description}")
    else:
        print("   未找到当前网站")
        return
    
    # 模拟传递给 task_focus_monitor
    print("\n3. 传递给 TaskFocusMonitor...")
    try:
        from task_focus_monitor import TaskFocusMonitor
        
        # 创建监控器
        monitor = TaskFocusMonitor()
        
        # 设置任务
        monitor.set_task(task_description)
        
        # 检查网站
        if url:
            result = monitor.check_website(url, description if description else None)
            monitor.print_check_result(url, result)
        
    except ImportError:
        print("   错误: 无法导入 task_focus_monitor")
    except Exception as e:
        print(f"   错误: {e}")


if __name__ == "__main__":
    main()