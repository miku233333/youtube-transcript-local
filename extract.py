#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Transcript Extractor (Local Safe Version)
Extract subtitles from YouTube videos using yt-dlp

Author: Ryan (欧启熙) / qibot
License: MIT-0
GitHub: https://github.com/YOUR_USERNAME/youtube-transcript-local
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

class YouTubeTranscriptExtractor:
    """YouTube 字幕提取器"""
    
    def __init__(self, output_dir=None, cache_dir=None):
        """
        初始化提取器
        
        Args:
            output_dir: 輸出目錄
            cache_dir: 緩存目錄
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "transcripts"
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / ".cache"
        
        # 創建目錄
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # yt-dlp 路徑
        self.yt_dlp_path = self._find_yt_dlp()
    
    def _find_yt_dlp(self):
        """查找 yt-dlp 可執行文件"""
        # 嘗試從 PATH 查找
        import shutil
        yt_dlp = shutil.which("yt-dlp")
        if yt_dlp:
            return yt_dlp
        
        # 嘗試常見安裝位置
        common_paths = [
            Path.home() / ".local" / "bin" / "yt-dlp",
            Path("/usr/local/bin/yt-dlp"),
            Path("C:\\Users\\qibot\\AppData\\Roaming\\Python\\Python314\\Scripts\\yt-dlp.exe"),
        ]
        
        for path in common_paths:
            if path.exists():
                return str(path)
        
        # 嘗試通過 pip 安裝
        print("⚠️  未找到 yt-dlp，正在安裝...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        return shutil.which("yt-dlp")
    
    def extract(self, url, lang="en", auto_generate=True):
        """
        提取字幕
        
        Args:
            url: YouTube 視頻 URL
            lang: 首選語言代碼 (e.g., 'en', 'zh-Hans', 'zh-Hant')
            auto_generate: 是否允許自動生成字幕
            
        Returns:
            dict: {
                'success': bool,
                'video_id': str,
                'title': str,
                'subtitle_file': str,
                'content': str,
                'error': str (if failed)
            }
        """
        result = {
            'success': False,
            'video_id': None,
            'title': None,
            'subtitle_file': None,
            'content': None,
            'error': None
        }
        
        try:
            # 提取視頻 ID
            import re
            match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
            if not match:
                result['error'] = "無效的 YouTube URL"
                return result
            
            video_id = match.group(1)
            result['video_id'] = video_id
            
            # 檢查緩存
            cache_file = self.cache_dir / f"{video_id}.info.json"
            if cache_file.exists():
                print(f"✅ 使用緩存: {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                result['title'] = info.get('title', 'Unknown')
            else:
                # 獲取視頻信息
                print(f"🎬 正在獲取視頻信息...")
                info = self._get_video_info(url)
                result['title'] = info.get('title', 'Unknown')
                
                # 保存緩存
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(info, f, ensure_ascii=False, indent=2)
            
            # 提取字幕
            print(f"📝 正在提取字幕 (語言：{lang})...")
            subtitle_file = self._extract_subtitles(url, video_id, lang, auto_generate)
            
            if subtitle_file and subtitle_file.exists():
                result['subtitle_file'] = str(subtitle_file)
                result['content'] = subtitle_file.read_text(encoding='utf-8')
                result['success'] = True
                print(f"✅ 字幕提取成功：{subtitle_file}")
            else:
                result['error'] = "未找到字幕"
                print("⚠️  未找到字幕，可能需要手動提取音頻並使用 Whisper 轉文字")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ 錯誤：{e}")
        
        return result
    
    def _get_video_info(self, url):
        """獲取視頻信息"""
        cmd = [
            self.yt_dlp_path,
            "--dump-json",
            "--no-download",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise Exception(f"yt-dlp 錯誤：{result.stderr}")
        
        return json.loads(result.stdout)
    
    def _extract_subtitles(self, url, video_id, lang, auto_generate):
        """提取字幕"""
        output_template = self.output_dir / f"{video_id}.%(ext)s"
        
        # 構建命令
        cmd = [
            self.yt_dlp_path,
            "--write-sub",
            "--sub-lang", lang,
            "--skip-download",
            "--convert-subs", "srt",
            "-o", str(output_template),
            url
        ]
        
        # 如果允許自動生成字幕
        if auto_generate:
            cmd.insert(2, "--write-auto-sub")
        
        # 執行
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        # 查找字幕文件
        for ext in ['srt', 'vtt']:
            subtitle_file = self.output_dir / f"{video_id}.{lang}.{ext}"
            if subtitle_file.exists():
                return subtitle_file
        
        # 嘗試查找其他語言的字幕
        for file in self.output_dir.glob(f"{video_id}.*.{ext}"):
            return file
        
        return None
    
    def summarize(self, text, max_length=500):
        """
        生成摘要（簡單版本）
        
        Args:
            text: 字幕文本
            max_length: 最大長度
            
        Returns:
            str: 摘要
        """
        # 簡單實現：提取關鍵句
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 過濾時間戳和數字行
        content_lines = []
        for line in lines:
            if not line.isdigit() and '-->' not in line:
                content_lines.append(line)
        
        # 取前 N 個非空行作為摘要
        summary = '\n'.join(content_lines[:20])
        
        return summary


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='YouTube Transcript Extractor - 本地安全的字幕提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python extract.py -u "https://www.youtube.com/watch?v=abc123"
  python extract.py -u "URL" -l zh-Hans
  python extract.py -u "URL" -o ./transcripts
        """
    )
    
    parser.add_argument('-u', '--url', required=True, help='YouTube 視頻 URL')
    parser.add_argument('-l', '--lang', default='zh-Hans', help='首選語言 (默認：zh-Hans)')
    parser.add_argument('-o', '--output', default=None, help='輸出目錄')
    parser.add_argument('--auto-generate', action='store_true', help='允許自動生成字幕')
    parser.add_argument('--no-summarize', action='store_true', help='不生成摘要')
    
    args = parser.parse_args()
    
    # 創建提取器
    extractor = YouTubeTranscriptExtractor(output_dir=args.output)
    
    # 提取字幕
    result = extractor.extract(args.url, args.lang, args.auto_generate)
    
    if result['success']:
        print(f"\n✅ 提取成功!")
        print(f"   標題：{result['title']}")
        print(f"   文件：{result['subtitle_file']}")
        
        # 生成摘要
        if not args.no_summarize:
            print("\n📋 摘要:")
            print("-" * 50)
            summary = extractor.summarize(result['content'])
            print(summary)
            print("-" * 50)
    else:
        print(f"\n❌ 提取失敗：{result['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
