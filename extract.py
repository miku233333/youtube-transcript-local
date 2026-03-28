#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Transcript Extractor (Local Safe Version)
Extract subtitles from YouTube videos using yt-dlp

Author: Ryan (欧启熙) / qibot
License: MIT-0
GitHub: https://github.com/miku233333/youtube-transcript-local
Version: 2.0.0 (P0 Upgrade - Error Handling + Logging + Tests)
"""

import os
import sys
import json
import argparse
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

# 修復 Windows 編碼問題
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# ==================== 日誌配置 ====================

class LogFormatter(logging.Formatter):
    """自定義日誌格式器，支持彩色輸出"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    設置結構化日誌系統
    
    Args:
        verbose: 是否啟用 DEBUG 級別
        log_file: 可選的日誌文件路徑
    
    Returns:
        配置好的 logger 實例
    """
    logger = logging.getLogger('youtube_transcript')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # 清除現有 handlers
    logger.handlers.clear()
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = LogFormatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件處理器（可選）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# ==================== 錯誤分類系統 ====================

class TranscriptError(Exception):
    """字幕提取錯誤基類"""
    def __init__(self, message: str, error_code: str = "UNKNOWN", details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式，便於 JSON 序列化"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': datetime.now().isoformat()
        }


class URLValidationError(TranscriptError):
    """URL 驗證錯誤"""
    def __init__(self, message: str = "Invalid YouTube URL", url: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="URL_VALIDATION_FAILED",
            details={'url': url}
        )


class NetworkError(TranscriptError):
    """網絡錯誤"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            details={'original_error': str(original_error) if original_error else None}
        )


class SubtitleNotFoundError(TranscriptError):
    """字幕未找到錯誤"""
    def __init__(self, video_id: str, lang: str, auto_generate: bool = False):
        message = f"No subtitles found for video {video_id} (lang: {lang})"
        if auto_generate:
            message += " (including auto-generated)"
        super().__init__(
            message=message,
            error_code="SUBTITLE_NOT_FOUND",
            details={'video_id': video_id, 'lang': lang, 'auto_generate': auto_generate}
        )


class YTDLLError(TranscriptError):
    """yt-dlp 執行錯誤"""
    def __init__(self, message: str, stderr: Optional[str] = None, returncode: int = -1):
        super().__init__(
            message=message,
            error_code="YT_DLP_ERROR",
            details={'stderr': stderr, 'returncode': returncode}
        )


class FileIOError(TranscriptError):
    """文件 IO 錯誤"""
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="FILE_IO_ERROR",
            details={'file_path': file_path}
        )


class CacheError(TranscriptError):
    """緩存錯誤"""
    def __init__(self, message: str, cache_file: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details={'cache_file': cache_file}
        )


# ==================== 用戶友好錯誤提示 ====================

ERROR_MESSAGES = {
    "URL_VALIDATION_FAILED": {
        "user": "❌ 無效的 YouTube 連結，請檢查是否正確",
        "tech": "URL 格式驗證失敗",
        "suggestion": "請確保連結格式為：https://www.youtube.com/watch?v=VIDEO_ID"
    },
    "NETWORK_ERROR": {
        "user": "🌐 網絡連接問題，請檢查網絡後重試",
        "tech": "網絡請求失敗",
        "suggestion": "檢查網絡連接，或嘗試使用代理"
    },
    "SUBTITLE_NOT_FOUND": {
        "user": "📝 未找到字幕，該視頻可能沒有可用字幕",
        "tech": "字幕文件不存在",
        "suggestion": "嘗試其他語言，或使用音頻提取 + Whisper 識別"
    },
    "YT_DLP_ERROR": {
        "user": "⚙️ 字幕提取工具執行失敗",
        "tech": "yt-dlp 命令執行錯誤",
        "suggestion": "檢查 yt-dlp 是否已安裝，或嘗試更新：pip install -U yt-dlp"
    },
    "FILE_IO_ERROR": {
        "user": "📁 文件讀寫失敗",
        "tech": "文件系統操作錯誤",
        "suggestion": "檢查文件權限和磁盤空間"
    },
    "CACHE_ERROR": {
        "user": "💾 緩存操作失敗",
        "tech": "緩存文件讀寫錯誤",
        "suggestion": "嘗試刪除緩存目錄後重試"
    },
    "UNKNOWN": {
        "user": "⚠️ 發生未知錯誤",
        "tech": "未分類的錯誤",
        "suggestion": "請查看詳細日誌或提交 issue"
    }
}


def get_user_friendly_error(error: TranscriptError) -> str:
    """
    獲取用戶友好的錯誤提示
    
    Args:
        error: TranscriptError 實例
    
    Returns:
        格式化的用戶友好錯誤消息
    """
    error_info = ERROR_MESSAGES.get(error.error_code, ERROR_MESSAGES["UNKNOWN"])
    
    output = [
        error_info["user"],
        "",
        f"技術細節：{error_info['tech']}",
        f"建議：{error_info['suggestion']}",
    ]
    
    if error.details:
        output.append("")
        output.append("詳細信息:")
        for key, value in error.details.items():
            if value is not None:
                output.append(f"  - {key}: {value}")
    
    return "\n".join(output)


# ==================== 核心提取器類 ====================

class YouTubeTranscriptExtractor:
    """YouTube 字幕提取器（P0 升級版）"""
    
    def __init__(
        self, 
        output_dir: Optional[str] = None, 
        cache_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化提取器
        
        Args:
            output_dir: 輸出目錄路徑
            cache_dir: 緩存目錄路徑
            logger: 自定義 logger，不提供則使用默認
        """
        self.logger = logger or setup_logging()
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "transcripts"
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / ".cache"
        
        self.logger.debug(f"初始化輸出目錄：{self.output_dir}")
        self.logger.debug(f"初始化緩存目錄：{self.cache_dir}")
        
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("目錄初始化成功")
        except Exception as e:
            raise FileIOError(f"無法創建目錄：{e}", str(self.output_dir))
        
        self.yt_dlp_path = self._find_yt_dlp()
    
    def _find_yt_dlp(self) -> str:
        """查找 yt-dlp 可執行文件"""
        import shutil
        
        # 嘗試從 PATH 查找
        yt_dlp = shutil.which("yt-dlp")
        if yt_dlp:
            self.logger.debug(f"找到 yt-dlp: {yt_dlp}")
            return yt_dlp
        
        # 嘗試常見路徑
        common_paths: List[Path] = [
            Path.home() / ".local" / "bin" / "yt-dlp",
            Path("/usr/local/bin/yt-dlp"),
            Path("/opt/homebrew/bin/yt-dlp"),
        ]
        
        if sys.platform == 'win32':
            common_paths.append(
                Path.home() / "AppData" / "Roaming" / "Python" / "Python314" / "Scripts" / "yt-dlp.exe"
            )
        
        for path in common_paths:
            if path.exists():
                self.logger.debug(f"找到 yt-dlp: {path}")
                return str(path)
        
        # 自動安裝
        self.logger.warning("yt-dlp 未找到，正在安裝...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            self.logger.info("yt-dlp 安裝成功")
            yt_dlp = shutil.which("yt-dlp")
            if yt_dlp:
                return yt_dlp
        except subprocess.CalledProcessError as e:
            raise YTDLLError("無法安裝 yt-dlp", str(e))
        
        raise YTDLLError("無法找到或安裝 yt-dlp")
    
    def _validate_url(self, url: str) -> str:
        """
        驗證 YouTube URL 並提取 video_id
        
        Args:
            url: YouTube 視頻 URL
        
        Returns:
            video_id
        
        Raises:
            URLValidationError: URL 無效時
        """
        import re
        
        patterns = [
            r'v=([a-zA-Z0-9_-]{11})',  # Standard: youtube.com/watch?v=VIDEO_ID
            r'youtu\.be/([a-zA-Z0-9_-]{11})',  # Short: youtu.be/VIDEO_ID
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',  # Embed
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',  # Old format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                self.logger.debug(f"驗證成功，video_id: {video_id}")
                return video_id
        
        self.logger.error(f"URL 驗證失敗：{url}")
        raise URLValidationError(url=url)
    
    def _get_video_info(self, url: str) -> Dict[str, Any]:
        """
        獲取視頻信息
        
        Args:
            url: YouTube 視頻 URL
        
        Returns:
            視頻信息字典
        
        Raises:
            YTDLLError: yt-dlp 執行失敗時
            NetworkError: 網絡錯誤時
        """
        self.logger.info("正在獲取視頻信息...")
        
        cmd = [self.yt_dlp_path, "--dump-json", "--no-download", url]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.error(f"yt-dlp 執行失敗：{result.stderr}")
                raise YTDLLError("獲取視頻信息失敗", result.stderr, result.returncode)
            
            info = json.loads(result.stdout)
            self.logger.info(f"獲取成功：{info.get('title', 'Unknown')}")
            return info
            
        except subprocess.TimeoutExpired:
            raise NetworkError("請求超時", TimeoutError())
        except json.JSONDecodeError as e:
            raise YTDLLError(f"JSON 解析失敗：{e}")
        except Exception as e:
            if "Connection" in str(e) or "Network" in str(e):
                raise NetworkError(f"網絡錯誤：{e}", e)
            raise
    
    def _extract_subtitles(
        self, 
        url: str, 
        video_id: str, 
        lang: str, 
        auto_generate: bool = False
    ) -> Optional[Path]:
        """
        提取字幕
        
        Args:
            url: YouTube 視頻 URL
            video_id: 視頻 ID
            lang: 語言代碼
            auto_generate: 是否允許自動生成字幕
        
        Returns:
            字幕文件路徑，失敗返回 None
        
        Raises:
            YTDLLError: yt-dlp 執行失敗時
        """
        self.logger.info(f"正在提取字幕 (lang: {lang}, auto: {auto_generate})...")
        
        output_template = self.output_dir / f"{video_id}.%(ext)s"
        
        cmd = [
            self.yt_dlp_path,
            "--write-sub",
            "--sub-lang", lang,
            "--skip-download",
            "--convert-subs", "srt",
            "-o", str(output_template),
            url
        ]
        
        if auto_generate:
            cmd.insert(2, "--write-auto-sub")
            self.logger.debug("已啟用自動生成字幕")
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                timeout=120
            )
            
            if result.returncode != 0:
                self.logger.warning(f"yt-dlp 警告：{result.stderr}")
            
            # 查找生成的字幕文件
            for ext in ['srt', 'vtt']:
                subtitle_file = self.output_dir / f"{video_id}.{lang}.{ext}"
                if subtitle_file.exists():
                    self.logger.info(f"找到字幕文件：{subtitle_file}")
                    return subtitle_file
            
            # 嘗試其他格式
            for file in self.output_dir.glob(f"{video_id}.*"):
                if file.suffix in ['.srt', '.vtt']:
                    self.logger.info(f"找到替代字幕文件：{file}")
                    return file
            
            self.logger.warning("未找到字幕文件")
            return None
            
        except subprocess.TimeoutExpired:
            self.logger.error("字幕提取超時")
            raise YTDLLError("字幕提取超時", returncode=-1)
        except Exception as e:
            self.logger.error(f"字幕提取失敗：{e}")
            raise
    
    def extract(
        self, 
        url: str, 
        lang: str = "en", 
        auto_generate: bool = True
    ) -> Dict[str, Any]:
        """
        提取字幕（主接口）
        
        Args:
            url: YouTube 視頻 URL
            lang: 語言代碼 (default: "en")
            auto_generate: 是否允許自動生成字幕 (default: True)
        
        Returns:
            提取結果字典：
            {
                'success': bool,
                'video_id': str,
                'title': str,
                'subtitle_file': str,
                'content': str,
                'error': dict or None
            }
        """
        self.logger.info(f"開始提取：{url}")
        
        result: Dict[str, Any] = {
            'success': False,
            'video_id': None,
            'title': None,
            'subtitle_file': None,
            'content': None,
            'error': None
        }
        
        try:
            # 1. 驗證 URL
            video_id = self._validate_url(url)
            result['video_id'] = video_id
            
            # 2. 檢查緩存
            cache_file = self.cache_dir / f"{video_id}.info.json"
            if cache_file.exists():
                self.logger.info(f"使用緩存：{cache_file}")
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    result['title'] = info.get('title', 'Unknown')
                except Exception as e:
                    self.logger.warning(f"緩存讀取失敗：{e}，重新獲取")
                    cache_file.unlink(missing_ok=True)
                    info = self._get_video_info(url)
                    result['title'] = info.get('title', 'Unknown')
            else:
                info = self._get_video_info(url)
                result['title'] = info.get('title', 'Unknown')
                
                # 保存緩存
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(info, f, ensure_ascii=False, indent=2)
                    self.logger.debug(f"緩存已保存：{cache_file}")
                except Exception as e:
                    self.logger.warning(f"緩存保存失敗：{e}")
            
            # 3. 提取字幕
            subtitle_file = self._extract_subtitles(url, video_id, lang, auto_generate)
            
            if subtitle_file and subtitle_file.exists():
                result['subtitle_file'] = str(subtitle_file)
                result['content'] = subtitle_file.read_text(encoding='utf-8')
                result['success'] = True
                self.logger.info(f"提取成功：{subtitle_file}")
            else:
                error = SubtitleNotFoundError(video_id, lang, auto_generate)
                result['error'] = error.to_dict()
                self.logger.warning(get_user_friendly_error(error))
            
        except TranscriptError as e:
            self.logger.error(f"提取失敗：{e.error_code} - {e.message}")
            result['error'] = e.to_dict()
        except Exception as e:
            self.logger.exception(f"未知錯誤：{e}")
            error = TranscriptError(str(e), "UNKNOWN")
            result['error'] = error.to_dict()
        
        return result
    
    def summarize(self, text: str, max_lines: int = 20) -> str:
        """
        生成摘要（去除時間軸）
        
        Args:
            text: 字幕內容
            max_lines: 最大行數
        
        Returns:
            摘要文本
        """
        self.logger.debug(f"生成摘要 (max_lines: {max_lines})")
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        content_lines = []
        
        for line in lines:
            # 過濾時間軸和數字行
            if not line.isdigit() and '-->' not in line:
                content_lines.append(line)
        
        summary = '\n'.join(content_lines[:max_lines])
        self.logger.debug(f"摘要生成完成，{len(content_lines)} 行")
        return summary


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='YouTube Transcript Extractor (P0 Upgrade)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -u https://www.youtube.com/watch?v=VIDEO_ID
  %(prog)s -u VIDEO_ID -l zh-Hans --verbose
  %(prog)s -u VIDEO_ID -o ./output --log-file ./logs/extract.log
        """
    )
    
    parser.add_argument('-u', '--url', required=True, help='YouTube URL 或 VIDEO_ID')
    parser.add_argument('-l', '--lang', default='zh-Hans', help='語言代碼 (default: zh-Hans)')
    parser.add_argument('-o', '--output', default=None, help='輸出目錄')
    parser.add_argument('--auto-generate', action='store_true', help='允許自動生成字幕')
    parser.add_argument('--no-summarize', action='store_true', help='跳過摘要')
    parser.add_argument('--verbose', '-v', action='store_true', help='啟用詳細日誌')
    parser.add_argument('--log-file', default=None, help='日誌文件路徑')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式輸出結果')
    
    args = parser.parse_args()
    
    # 設置日誌
    logger = setup_logging(verbose=args.verbose, log_file=args.log_file)
    logger.info("YouTube Transcript Extractor v2.0.0 (P0 Upgrade)")
    
    try:
        extractor = YouTubeTranscriptExtractor(
            output_dir=args.output,
            logger=logger
        )
        
        result = extractor.extract(
            args.url, 
            args.lang, 
            args.auto_generate
        )
        
        if args.json:
            # JSON 輸出（適合程序調用）
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif result['success']:
            print("\n✅ 提取成功!")
            print(f"  標題：{result['title']}")
            print(f"  文件：{result['subtitle_file']}")
            
            if not args.no_summarize:
                print("\n📝 摘要:")
                print("-" * 50)
                summary = extractor.summarize(result['content'])
                print(summary)
                print("-" * 50)
        else:
            error = TranscriptError(
                result['error']['message'],
                result['error']['error_code'],
                result['error'].get('details')
            )
            print("\n" + get_user_friendly_error(error))
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\n用戶中斷")
        print("\n⚠️  操作已取消")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"程序異常：{e}")
        error = TranscriptError(str(e), "UNKNOWN")
        print("\n" + get_user_friendly_error(error))
        sys.exit(1)


if __name__ == '__main__':
    main()
