#!/usr/bin/env python3
"""
专注度计算器 - 基于专注时长和无关网站访问次数计算用户专注度
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class FocusSession:
    session_id: str
    task_id: str
    task_name: str
    start_time: float
    end_time: Optional[float] = None
    total_duration: float = 0.0
    relevant_websites: int = 0
    irrelevant_websites: int = 0
    focus_score: float = 0.0
    website_checks: List[Dict] = None
    
    def __post_init__(self):
        if self.website_checks is None:
            self.website_checks = []


@dataclass
class FocusMetrics:
    total_sessions: int = 0
    total_focus_time: float = 0.0
    average_focus_score: float = 0.0
    best_focus_score: float = 0.0
    worst_focus_score: float = 100.0
    total_relevant_websites: int = 0
    total_irrelevant_websites: int = 0
    focus_efficiency: float = 0.0


class FocusScoreCalculator:
    def __init__(self, data_file: str = "focus_sessions.json"):
        self.data_file = data_file
        self.sessions: List[FocusSession] = []
        self.current_session: Optional[FocusSession] = None
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sessions = [
                    FocusSession(**session_data) 
                    for session_data in data.get('sessions', [])
                ]
        except FileNotFoundError:
            self.sessions = []
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.sessions = []
    
    def save_data(self):
        try:
            data = {
                'sessions': [asdict(session) for session in self.sessions],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def start_session(self, task_id: str, task_name: str) -> str:
        session_id = f"session_{int(time.time())}_{len(self.sessions)}"
        
        self.current_session = FocusSession(
            session_id=session_id,
            task_id=task_id,
            task_name=task_name,
            start_time=time.time()
        )
        
        print(f"✓ 开始专注会话: {task_name}")
        print(f"  会话ID: {session_id}")
        return session_id
    
    def end_session(self) -> Optional[FocusSession]:
        if not self.current_session:
            print("❌ 没有活跃的专注会话")
            return None
        
        self.current_session.end_time = time.time()
        self.current_session.total_duration = (
            self.current_session.end_time - self.current_session.start_time
        )
        
        self.current_session.focus_score = self._calculate_focus_score(
            self.current_session.total_duration,
            self.current_session.relevant_websites,
            self.current_session.irrelevant_websites
        )
        
        self.sessions.append(self.current_session)
        self.save_data()
        
        self._print_session_summary(self.current_session)
        
        ended_session = self.current_session
        self.current_session = None
        
        return ended_session
    
    def record_website_check(self, website_url: str, is_relevant: bool, 
                           confidence: str = "medium", reason: str = ""):
        if not self.current_session:
            print("❌ 没有活跃的专注会话，无法记录网站检查")
            return
        
        check_record = {
            "timestamp": datetime.now().isoformat(),
            "website_url": website_url,
            "is_relevant": is_relevant,
            "confidence": confidence,
            "reason": reason
        }
        
        self.current_session.website_checks.append(check_record)
        
        if is_relevant:
            self.current_session.relevant_websites += 1
        else:
            self.current_session.irrelevant_websites += 1
        
        self.current_session.focus_score = self._calculate_focus_score(
            self.current_session.total_duration,
            self.current_session.relevant_websites,
            self.current_session.irrelevant_websites
        )
        
        print(f"📊 网站检查记录: {website_url}")
        print(f"   相关: {'是' if is_relevant else '否'}")
        print(f"   当前专注度: {self.current_session.focus_score:.1f}")
    
    def _calculate_focus_score(self, duration: float, relevant: int, irrelevant: int) -> float:
        if duration <= 0:
            return 0.0
        
        duration_score = min(40.0, duration / 60.0 * 2)
        
        total_websites = relevant + irrelevant
        if total_websites == 0:
            efficiency_score = 60.0
        else:
            relevance_ratio = relevant / total_websites
            efficiency_score = relevance_ratio * 60.0
        
        distraction_penalty = min(20.0, irrelevant * 2)
        
        final_score = duration_score + efficiency_score - distraction_penalty
        
        return max(0.0, min(100.0, final_score))
    
    def _print_session_summary(self, session: FocusSession):
        duration_minutes = session.total_duration / 60.0
        
        print("\n" + "=" * 70)
        print("🎯 专注会话总结")
        print("=" * 70)
        print(f"任务: {session.task_name}")
        print(f"会话时长: {duration_minutes:.1f} 分钟")
        print(f"相关网站: {session.relevant_websites} 次")
        print(f"无关网站: {session.irrelevant_websites} 次")
        print(f"专注度分数: {session.focus_score:.1f}/100")
        
        if session.focus_score >= 90:
            grade = "🌟 优秀"
        elif session.focus_score >= 80:
            grade = "👍 良好"
        elif session.focus_score >= 70:
            grade = "👌 一般"
        elif session.focus_score >= 60:
            grade = "⚠️ 需要改进"
        else:
            grade = "❌ 需要大幅改进"
        
        print(f"评级: {grade}")
        print("=" * 70 + "\n")
    
    def get_current_session_info(self) -> Optional[Dict]:
        if not self.current_session:
            return None
        
        current_duration = time.time() - self.current_session.start_time
        
        return {
            "session_id": self.current_session.session_id,
            "task_name": self.current_session.task_name,
            "duration_minutes": current_duration / 60.0,
            "relevant_websites": self.current_session.relevant_websites,
            "irrelevant_websites": self.current_session.irrelevant_websites,
            "current_focus_score": self.current_session.focus_score
        }
    
    def get_focus_metrics(self, days: int = 30) -> FocusMetrics:
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        recent_sessions = [
            s for s in self.sessions 
            if s.start_time >= cutoff_time and s.end_time is not None
        ]
        
        if not recent_sessions:
            return FocusMetrics()
        
        total_sessions = len(recent_sessions)
        total_focus_time = sum(s.total_duration for s in recent_sessions)
        focus_scores = [s.focus_score for s in recent_sessions]
        
        return FocusMetrics(
            total_sessions=total_sessions,
            total_focus_time=total_focus_time,
            average_focus_score=sum(focus_scores) / len(focus_scores),
            best_focus_score=max(focus_scores),
            worst_focus_score=min(focus_scores),
            total_relevant_websites=sum(s.relevant_websites for s in recent_sessions),
            total_irrelevant_websites=sum(s.irrelevant_websites for s in recent_sessions),
            focus_efficiency=(
                sum(s.relevant_websites for s in recent_sessions) / 
                max(1, sum(s.relevant_websites + s.irrelevant_websites for s in recent_sessions))
            )
        )
    
    def print_focus_metrics(self, days: int = 30):
        metrics = self.get_focus_metrics(days)
        
        print("\n" + "=" * 70)
        print(f"📈 专注度统计 (最近 {days} 天)")
        print("=" * 70)
        print(f"总会话数: {metrics.total_sessions}")
        print(f"总专注时间: {metrics.total_focus_time / 3600:.1f} 小时")
        print(f"平均专注度: {metrics.average_focus_score:.1f}/100")
        print(f"最佳专注度: {metrics.best_focus_score:.1f}/100")
        print(f"最差专注度: {metrics.worst_focus_score:.1f}/100")
        print(f"相关网站访问: {metrics.total_relevant_websites} 次")
        print(f"无关网站访问: {metrics.total_irrelevant_websites} 次")
        print(f"专注效率: {metrics.focus_efficiency * 100:.1f}%")
        print("=" * 70 + "\n")
    
    def get_session_history(self, limit: int = 10) -> List[Dict]:
        sorted_sessions = sorted(
            [s for s in self.sessions if s.end_time is not None],
            key=lambda x: x.start_time,
            reverse=True
        )
        
        return [
            {
                "session_id": s.session_id,
                "task_name": s.task_name,
                "start_time": datetime.fromtimestamp(s.start_time).strftime("%Y-%m-%d %H:%M:%S"),
                "duration_minutes": s.total_duration / 60.0,
                "focus_score": s.focus_score,
                "relevant_websites": s.relevant_websites,
                "irrelevant_websites": s.irrelevant_websites
            }
            for s in sorted_sessions[:limit]
        ]


def main():
    print("=" * 70)
    print("专注度计算器演示")
    print("=" * 70)
    
    calculator = FocusScoreCalculator()
    
    print("1. 开始专注会话...")
    session_id = calculator.start_session("task_001", "学习Python编程")
    
    print("\n2. 模拟网站访问...")
    test_websites = [
        ("https://docs.python.org", True, "high", "官方文档，与学习相关"),
        ("https://stackoverflow.com", True, "high", "编程问答网站，有助于学习"),
        ("https://github.com", True, "medium", "代码仓库，学习相关"),
        ("https://www.youtube.com", False, "high", "视频网站，容易分心"),
        ("https://www.reddit.com", False, "high", "社交网站，与学习无关"),
        ("https://realpython.com", True, "high", "Python学习网站"),
    ]
    
    for url, is_relevant, confidence, reason in test_websites:
        calculator.record_website_check(url, is_relevant, confidence, reason)
        time.sleep(0.5)
    
    print(f"\n3. 模拟专注时长...")
    time.sleep(2)
    
    print("\n4. 结束专注会话...")
    ended_session = calculator.end_session()
    
    print("\n5. 显示专注度统计...")
    calculator.print_focus_metrics()
    
    print("\n6. 会话历史记录...")
    history = calculator.get_session_history(5)
    for session in history:
        print(f"  {session['start_time']} - {session['task_name']} - 分数: {session['focus_score']:.1f}")


if __name__ == "__main__":
    main()