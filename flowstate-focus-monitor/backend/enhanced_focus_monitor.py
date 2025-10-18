#!/usr/bin/env python3
"""
增强版专注度监控器 - 集成FlowState和专注度计算
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from groq import Groq
from focus_score_calculator import FocusScoreCalculator
from flowstate_bridge import FlowStateBridge


class EnhancedFocusMonitor:
    def __init__(self, api_key=None, flowstate_path=None):
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        
        self.focus_calculator = FocusScoreCalculator()
        self.flowstate_bridge = FlowStateBridge(flowstate_path)
        
        self.current_task = None
        self.current_session = None
        self.monitoring_active = False
    
    def start_task_monitoring(self, task_id: str = None, task_name: str = None):
        try:
            if task_id and task_name:
                self.current_task = {"id": task_id, "name": task_name}
            else:
                task_data = self.flowstate_bridge.get_current_task()
                if not task_data:
                    print("❌ 未找到当前任务，请先在FlowState中创建任务")
                    return False
                self.current_task = task_data
            
            self.current_session = self.focus_calculator.start_session(
                self.current_task["id"], self.current_task["name"]
            )
            
            self.monitoring_active = True
            
            print(f"🎯 开始监控任务: {self.current_task['name']}")
            print(f"   任务ID: {self.current_task['id']}")
            print(f"   会话ID: {self.current_session}")
            print("   现在将监控您的网站访问情况...\n")
            
            return True
            
        except Exception as e:
            print(f"❌ 启动任务监控失败: {e}")
            return False
    
    def check_current_website(self) -> Dict:
        if not self.monitoring_active or not self.current_task:
            return {"success": False, "error": "没有活跃的监控会话"}
        
        try:
            website_data = self.flowstate_bridge.get_current_website()
            if not website_data:
                return {"success": False, "error": "无法获取当前网站信息"}
            
            result = self._analyze_website_with_ai(
                website_data["url"], website_data.get("title", ""), self.current_task
            )
            
            self.focus_calculator.record_website_check(
                website_url=website_data["url"],
                is_relevant=result["is_relevant"],
                confidence=result["confidence"],
                reason=result["reason"]
            )
            
            return {
                "success": True,
                "website_url": website_data["url"],
                "website_title": website_data.get("title", ""),
                "is_relevant": result["is_relevant"],
                "confidence": result["confidence"],
                "reason": result["reason"],
                "current_focus_score": self.focus_calculator.get_current_session_info()["current_focus_score"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"检查网站失败: {e}"}
    
    def _analyze_website_with_ai(self, url: str, title: str, task: Dict) -> Dict:
        try:
            task_name = task.get("name", "未知任务")
            resources = task.get("resources", [])
            
            task_description = f"任务: {task_name}"
            if resources:
                resource_descriptions = []
                for resource in resources[:3]:
                    if resource.get("kind") == "url":
                        url_info = resource.get("id", "")
                        title_info = resource.get("title", "")
                        if title_info:
                            resource_descriptions.append(f"{title_info} ({url_info})")
                        else:
                            resource_descriptions.append(url_info)
                    elif resource.get("kind") == "app":
                        app_id = resource.get("id", "")
                        title_info = resource.get("title", "")
                        if title_info:
                            resource_descriptions.append(f"{title_info} ({app_id})")
                        else:
                            resource_descriptions.append(app_id)
                
                if resource_descriptions:
                    task_description += f"\n相关资源: {', '.join(resource_descriptions)}"
            
            website_info = f"URL: {url}"
            if title:
                website_info += f"\n标题: {title}"
            
            prompt = f"""我正在执行的任务是：{task_description}

现在我想打开以下网站：
{website_info}

请判断这个网站是否与我的任务主题相关。

判断标准：
1. 如果网站内容直接有助于完成任务，判定为"相关"
2. 如果网站是娱乐、社交、购物等与任务无关的内容，判定为"不相关"
3. 如果网站是搜索引擎、工具类网站，需要根据任务判断

请按以下格式回答：
判断：相关 / 不相关
置信度：高 / 中 / 低
理由：[简短说明为什么相关或不相关]

只回答以上内容，不要添加其他说明。"""

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的任务专注度助手，帮助用户判断网站是否与当前任务相关，从而保持专注。"
                    },
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                max_tokens=512
            )
            
            response_content = chat_completion.choices[0].message.content
            return self._parse_ai_response(response_content)
            
        except Exception as e:
            return {
                "is_relevant": False,
                "confidence": "low",
                "reason": f"AI分析失败: {str(e)}"
            }
    
    def _parse_ai_response(self, response_content: str) -> Dict:
        is_relevant = "相关" in response_content and "不相关" not in response_content.split("\n")[0]
        
        confidence = "medium"
        if "高" in response_content:
            confidence = "high"
        elif "低" in response_content:
            confidence = "low"
        
        reason = response_content
        lines = response_content.split("\n")
        for line in lines:
            if "理由" in line:
                reason = line.replace("理由：", "").replace("理由:", "").strip()
                break
        
        return {
            "is_relevant": is_relevant,
            "confidence": confidence,
            "reason": reason
        }
    
    def end_task_monitoring(self) -> Optional[Dict]:
        if not self.monitoring_active:
            print("❌ 没有活跃的监控会话")
            return None
        
        ended_session = self.focus_calculator.end_session()
        
        if ended_session:
            print("\n" + "=" * 70)
            print("🎯 任务监控结束总结")
            print("=" * 70)
            print(f"任务: {ended_session.task_name}")
            print(f"专注时长: {ended_session.total_duration / 60.0:.1f} 分钟")
            print(f"相关网站: {ended_session.relevant_websites} 次")
            print(f"无关网站: {ended_session.irrelevant_websites} 次")
            print(f"专注度分数: {ended_session.focus_score:.1f}/100")
            
            if ended_session.focus_score >= 90:
                grade = "🌟 优秀"
            elif ended_session.focus_score >= 80:
                grade = "👍 良好"
            elif ended_session.focus_score >= 70:
                grade = "👌 一般"
            elif ended_session.focus_score >= 60:
                grade = "⚠️ 需要改进"
            else:
                grade = "❌ 需要大幅改进"
            
            print(f"评级: {grade}")
            print("=" * 70 + "\n")
            
            self.current_task = None
            self.current_session = None
            self.monitoring_active = False
            
            return {
                "task_name": ended_session.task_name,
                "duration_minutes": ended_session.total_duration / 60.0,
                "focus_score": ended_session.focus_score,
                "relevant_websites": ended_session.relevant_websites,
                "irrelevant_websites": ended_session.irrelevant_websites,
                "grade": grade
            }
        
        return None
    
    def get_current_status(self) -> Dict:
        if not self.monitoring_active:
            return {"monitoring_active": False, "message": "没有活跃的监控会话"}
        
        session_info = self.focus_calculator.get_current_session_info()
        if session_info:
            return {
                "monitoring_active": True,
                "task_name": self.current_task["name"],
                "duration_minutes": session_info["duration_minutes"],
                "current_focus_score": session_info["current_focus_score"],
                "relevant_websites": session_info["relevant_websites"],
                "irrelevant_websites": session_info["irrelevant_websites"]
            }
        
        return {"monitoring_active": True, "message": "状态信息获取失败"}
    
    def print_focus_history(self, days=30):
        self.focus_calculator.print_focus_metrics(days)
    
    def get_focus_history(self, limit=10):
        return self.focus_calculator.get_session_history(limit)


def main():
    print("=" * 70)
    print("增强版专注度监控器")
    print("=" * 70)
    print("功能：集成FlowState任务管理和专注度计算")
    print()
    
    monitor = EnhancedFocusMonitor()
    
    print("1. 尝试从FlowState获取当前任务...")
    task_data = monitor.flowstate_bridge.get_current_task()
    
    if task_data:
        print(f"   找到任务: {task_data.get('name', 'N/A')}")
        print(f"   任务ID: {task_data.get('id', 'N/A')}")
        
        if monitor.start_task_monitoring():
            print("\n2. 开始监控...")
            
            print("\n3. 模拟网站检查...")
            for i in range(3):
                result = monitor.check_current_website()
                if result["success"]:
                    print(f"   检查 {i+1}: {result['website_url']}")
                    print(f"   相关: {'是' if result['is_relevant'] else '否'}")
                    print(f"   当前专注度: {result['current_focus_score']:.1f}")
                time.sleep(1)
            
            print("\n4. 结束监控...")
            monitor.end_task_monitoring()
            
            print("\n5. 专注度历史记录...")
            monitor.print_focus_history()
    
    else:
        print("   未找到FlowState任务，请先创建任务")
        print("   或者手动提供任务信息进行测试")
        
        print("\n2. 创建测试任务...")
        if monitor.start_task_monitoring("test_task_001", "测试专注度监控"):
            print("\n3. 模拟网站检查...")
            time.sleep(2)
            monitor.end_task_monitoring()


if __name__ == "__main__":
    main()