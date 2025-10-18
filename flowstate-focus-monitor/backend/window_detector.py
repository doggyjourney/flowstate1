#!/usr/bin/env python3
"""
真实窗口检测器 - 支持多平台
用于获取当前活动窗口的信息（URL、标题等）
"""

import os
import sys
import subprocess
import re
from typing import Optional, Dict
import platform


class WindowDetector:
    """窗口检测器基类"""
    
    def __init__(self):
        self.platform = platform.system()
        self.detector = self._get_detector()
    
    def _get_detector(self):
        """根据平台选择合适的检测器"""
        if self.platform == "Windows":
            return WindowsDetector()
        elif self.platform == "Darwin":
            return MacOSDetector()
        elif self.platform == "Linux":
            return LinuxDetector()
        else:
            return ManualInputDetector()
    
    def get_active_window(self) -> Optional[Dict]:
        """获取当前活动窗口信息"""
        return self.detector.get_active_window()


class WindowsDetector:
    """Windows 平台检测器"""
    
    def get_active_window(self) -> Optional[Dict]:
        """使用 PowerShell 获取活动窗口"""
        try:
            # PowerShell 脚本获取活动窗口标题
            ps_script = """
            Add-Type @"
                using System;
                using System.Runtime.InteropServices;
                public class Win32 {
                    [DllImport("user32.dll")]
                    public static extern IntPtr GetForegroundWindow();
                    [DllImport("user32.dll")]
                    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
                }
"@
            $handle = [Win32]::GetForegroundWindow()
            $title = New-Object System.Text.StringBuilder 256
            [void][Win32]::GetWindowText($handle, $title, 256)
            $title.ToString()
            """
            
            result = subprocess.run(
                ["powershell.exe", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                title = result.stdout.strip()
                url = self._extract_url_from_title(title)
                
                return {
                    "url": url,
                    "title": title,
                    "app_id": self._get_app_from_title(title)
                }
        except Exception as e:
            print(f"Windows 检测失败: {e}")
        
        return None
    
    def _extract_url_from_title(self, title: str) -> Optional[str]:
        """从窗口标题中提取 URL"""
        # 常见浏览器标题格式: "页面标题 - Google Chrome"
        # 或 "页面标题 - Mozilla Firefox"
        
        # 尝试匹配 URL 模式
        url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, title)
            if match:
                url = match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
        
        # 如果没有找到 URL，返回 None
        return None
    
    def _get_app_from_title(self, title: str) -> str:
        """从标题推断应用"""
        title_lower = title.lower()
        
        if 'chrome' in title_lower:
            return 'chrome'
        elif 'firefox' in title_lower:
            return 'firefox'
        elif 'edge' in title_lower:
            return 'edge'
        elif 'safari' in title_lower:
            return 'safari'
        else:
            return 'unknown'


class MacOSDetector:
    """macOS 平台检测器"""
    
    def get_active_window(self) -> Optional[Dict]:
        """使用 AppleScript 获取活动窗口"""
        try:
            # 获取活动应用
            app_script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            app_result = subprocess.run(
                ["osascript", "-e", app_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            app_name = app_result.stdout.strip()
            
            # 获取窗口标题
            title_script = f'tell application "{app_name}" to get name of front window'
            title_result = subprocess.run(
                ["osascript", "-e", title_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            title = title_result.stdout.strip()
            
            # 如果是浏览器，尝试获取 URL
            url = None
            if app_name.lower() in ['google chrome', 'safari', 'firefox']:
                url_script = f'tell application "{app_name}" to get URL of active tab of front window'
                url_result = subprocess.run(
                    ["osascript", "-e", url_script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if url_result.returncode == 0:
                    url = url_result.stdout.strip()
            
            return {
                "url": url,
                "title": title,
                "app_id": app_name.lower().replace(' ', '_')
            }
        except Exception as e:
            print(f"macOS 检测失败: {e}")
        
        return None


class LinuxDetector:
    """Linux 平台检测器（X11）"""
    
    def get_active_window(self) -> Optional[Dict]:
        """使用 xdotool 获取活动窗口"""
        try:
            # 获取活动窗口 ID
            window_id = subprocess.run(
                ["xdotool", "getactivewindow"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if window_id.returncode != 0:
                return None
            
            wid = window_id.stdout.strip()
            
            # 获取窗口标题
            title_result = subprocess.run(
                ["xdotool", "getwindowname", wid],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            title = title_result.stdout.strip()
            
            # 获取窗口类名（应用名）
            class_result = subprocess.run(
                ["xdotool", "getwindowclassname", wid],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            app_name = class_result.stdout.strip()
            
            # 尝试从标题提取 URL
            url = self._extract_url_from_title(title)
            
            return {
                "url": url,
                "title": title,
                "app_id": app_name.lower()
            }
        except Exception as e:
            print(f"Linux 检测失败: {e}")
        
        return None
    
    def _extract_url_from_title(self, title: str) -> Optional[str]:
        """从窗口标题中提取 URL"""
        url_patterns = [
            r'https?://[^\s]+',
            r'www\.[^\s]+',
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, title)
            if match:
                url = match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
        
        return None


class ManualInputDetector:
    """手动输入检测器（后备方案）"""
    
    def __init__(self):
        self.last_url = None
        self.last_title = None
    
    def get_active_window(self) -> Optional[Dict]:
        """提示用户手动输入当前网站"""
        print("\n" + "=" * 70)
        print("无法自动检测窗口，请手动输入当前网站信息")
        print("=" * 70)
        
        url = input("请输入当前网站 URL (或按 Enter 跳过): ").strip()
        
        if not url:
            # 如果用户跳过，返回上次的数据或模拟数据
            if self.last_url:
                print(f"使用上次的 URL: {self.last_url}")
                return {
                    "url": self.last_url,
                    "title": self.last_title or self.last_url,
                    "app_id": "browser"
                }
            else:
                print("使用模拟数据")
                return {
                    "url": "https://example.com",
                    "title": "Example Website",
                    "app_id": "browser"
                }
        
        if not url.startswith('http'):
            url = 'https://' + url
        
        title = input("请输入页面标题 (可选，按 Enter 跳过): ").strip()
        
        self.last_url = url
        self.last_title = title or url
        
        return {
            "url": url,
            "title": title or url,
            "app_id": "browser"
        }


def test_detector():
    """测试窗口检测器"""
    print("=" * 70)
    print("窗口检测器测试")
    print("=" * 70)
    
    detector = WindowDetector()
    
    print(f"\n当前平台: {detector.platform}")
    print(f"使用检测器: {detector.detector.__class__.__name__}")
    
    print("\n获取当前活动窗口...")
    window_info = detector.get_active_window()
    
    if window_info:
        print("\n✅ 检测成功:")
        print(f"   URL: {window_info.get('url', 'N/A')}")
        print(f"   标题: {window_info.get('title', 'N/A')}")
        print(f"   应用: {window_info.get('app_id', 'N/A')}")
    else:
        print("\n❌ 检测失败")
    
    return window_info


if __name__ == "__main__":
    test_detector()

