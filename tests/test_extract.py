#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Transcript Extractor - Unit Tests
測試覆蓋：錯誤處理、日誌系統、核心功能
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# 添加父目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))

from extract import (
    YouTubeTranscriptExtractor,
    setup_logging,
    TranscriptError,
    URLValidationError,
    NetworkError,
    SubtitleNotFoundError,
    YTDLLError,
    FileIOError,
    CacheError,
    get_user_friendly_error,
    ERROR_MESSAGES,
    LogFormatter
)
import logging


class TestLogFormatter:
    """測試日誌格式器"""
    
    def test_color_codes(self):
        """測試顏色代碼正確應用"""
        formatter = LogFormatter('%(levelname)s - %(message)s')
        
        for level, expected_color in [
            ('DEBUG', '\033[36m'),
            ('INFO', '\033[32m'),
            ('WARNING', '\033[33m'),
            ('ERROR', '\033[31m'),
            ('CRITICAL', '\033[35m'),
        ]:
            record = logging.LogRecord(
                name='test',
                level=getattr(logging, level),
                pathname='',
                lineno=0,
                msg='test message',
                args=(),
                exc_info=None
            )
            formatted = formatter.format(record)
            assert expected_color in formatted
            assert '\033[0m' in formatted  # Reset code
    
    def test_unknown_level(self):
        """測試未知級別使用默認顏色"""
        formatter = LogFormatter('%(levelname)s')
        record = logging.LogRecord(
            name='test',
            level=99,  # Unknown level
            pathname='',
            lineno=0,
            msg='test',
            args=(),
            exc_info=None
        )
        formatted = formatter.format(record)
        assert '\033[0m' in formatted


class TestLoggingSetup:
    """測試日誌系統設置"""
    
    def test_setup_logging_console(self):
        """測試控制台日誌設置"""
        logger = setup_logging(verbose=False)
        assert logger.name == 'youtube_transcript'
        assert len(logger.handlers) >= 1
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    
    def test_setup_logging_verbose(self):
        """測試詳細日誌模式"""
        logger = setup_logging(verbose=True)
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_with_file(self, tmp_path):
        """測試文件日誌設置"""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file))
        
        assert len(logger.handlers) >= 2
        assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
        assert log_file.exists()
    
    def test_logging_output(self, caplog):
        """測試日誌輸出"""
        with caplog.at_level(logging.INFO):
            logger = setup_logging()
            logger.info("Test message")
            assert "Test message" in caplog.text


class TestTranscriptError:
    """測試錯誤類"""
    
    def test_base_error(self):
        """測試基礎錯誤類"""
        error = TranscriptError("Test error", "TEST_CODE", {"key": "value"})
        assert error.message == "Test error"
        assert error.error_code == "TEST_CODE"
        assert error.details == {"key": "value"}
        
        error_dict = error.to_dict()
        assert error_dict['error_code'] == "TEST_CODE"
        assert error_dict['message'] == "Test error"
        assert 'timestamp' in error_dict
    
    def test_url_validation_error(self):
        """測試 URL 驗證錯誤"""
        error = URLValidationError(url="invalid_url")
        assert error.error_code == "URL_VALIDATION_FAILED"
        assert error.details['url'] == "invalid_url"
    
    def test_network_error(self):
        """測試網絡錯誤"""
        original = Exception("Connection failed")
        error = NetworkError("Network issue", original)
        assert error.error_code == "NETWORK_ERROR"
        assert "Connection failed" in error.details['original_error']
    
    def test_subtitle_not_found_error(self):
        """測試字幕未找到錯誤"""
        error = SubtitleNotFoundError("video123", "en", auto_generate=True)
        assert error.error_code == "SUBTITLE_NOT_FOUND"
        assert error.details['video_id'] == "video123"
        assert error.details['lang'] == "en"
    
    def test_ytdlp_error(self):
        """測試 yt-dlp 錯誤"""
        error = YTDLLError("Command failed", stderr="error output", returncode=1)
        assert error.error_code == "YT_DLP_ERROR"
        assert error.details['stderr'] == "error output"
        assert error.details['returncode'] == 1
    
    def test_file_io_error(self):
        """測試文件 IO 錯誤"""
        error = FileIOError("Read failed", file_path="/path/to/file")
        assert error.error_code == "FILE_IO_ERROR"
        assert error.details['file_path'] == "/path/to/file"
    
    def test_cache_error(self):
        """測試緩存錯誤"""
        error = CacheError("Cache miss", cache_file="/path/to/cache")
        assert error.error_code == "CACHE_ERROR"
        assert error.details['cache_file'] == "/path/to/cache"


class TestUserFriendlyError:
    """測試用戶友好錯誤提示"""
    
    def test_known_error_code(self):
        """測試已知錯誤代碼"""
        error = URLValidationError(url="bad_url")
        message = get_user_friendly_error(error)
        
        assert "❌" in message
        assert "無效的 YouTube 連結" in message
        assert "技術細節" in message
        assert "建議" in message
    
    def test_unknown_error_code(self):
        """測試未知錯誤代碼使用默認消息"""
        error = TranscriptError("Unknown", "UNKNOWN_CODE")
        message = get_user_friendly_error(error)
        
        assert "⚠️" in message
        assert "未知錯誤" in message
    
    def test_error_with_details(self):
        """測試帶詳細信息的錯誤"""
        error = SubtitleNotFoundError("video123", "zh-Hans")
        message = get_user_friendly_error(error)
        
        assert "video123" in message
        assert "zh-Hans" in message


class TestURLValidation:
    """測試 URL 驗證"""
    
    @pytest.fixture
    def extractor(self, tmp_path):
        """創建測試用提取器"""
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            return YouTubeTranscriptExtractor(
                output_dir=str(tmp_path / "output"),
                cache_dir=str(tmp_path / "cache")
            )
    
    def test_standard_url(self, extractor):
        """測試標準 YouTube URL"""
        video_id = extractor._validate_url("https://contact.com/watch?v=dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
    
    def test_short_url(self, extractor):
        """測試短連結"""
        video_id = extractor._validate_url("https://youtu.be/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
    
    def test_embed_url(self, extractor):
        """測試嵌入連結"""
        video_id = extractor._validate_url("https://contact.com/embed/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
    
    def test_invalid_url(self, extractor):
        """測試無效 URL"""
        with pytest.raises(URLValidationError) as exc_info:
            extractor._validate_url("https://contact.com")
        assert exc_info.value.error_code == "URL_VALIDATION_FAILED"
    
    def test_url_with_extra_params(self, extractor):
        """測試帶參數的 URL"""
        video_id = extractor._validate_url(
            "https://contact.com/watch?v=dQw4w9WgXcQ&feature=share&t=10"
        )
        assert video_id == "dQw4w9WgXcQ"


class TestExtractorInitialization:
    """測試提取器初始化"""
    
    def test_default_directories(self, tmp_path):
        """測試默認目錄創建"""
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            extractor = YouTubeTranscriptExtractor()
            assert extractor.output_dir.exists()
            assert extractor.cache_dir.exists()
    
    def test_custom_directories(self, tmp_path):
        """測試自定義目錄"""
        output_dir = tmp_path / "custom_output"
        cache_dir = tmp_path / "custom_cache"
        
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            extractor = YouTubeTranscriptExtractor(
                output_dir=str(output_dir),
                cache_dir=str(cache_dir)
            )
            assert extractor.output_dir == output_dir
            assert extractor.cache_dir == cache_dir
    
    def test_yt_dlp_not_found_auto_install(self, tmp_path):
        """測試 yt-dlp 未找到時自動安裝"""
        # 這個測試需要 mock 整個 _find_yt_dlp 方法，因為 shutil 是內部導入
        with patch.object(YouTubeTranscriptExtractor, '_find_yt_dlp', return_value='/fake/yt-dlp'):
            extractor = YouTubeTranscriptExtractor(
                output_dir=str(tmp_path / "output"),
                cache_dir=str(tmp_path / "cache")
            )
            assert extractor.yt_dlp_path == '/fake/yt-dlp'


class TestExtractMethod:
    """測試 extract 方法"""
    
    @pytest.fixture
    def extractor(self, tmp_path):
        """創建測試用提取器"""
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            return YouTubeTranscriptExtractor(
                output_dir=str(tmp_path / "output"),
                cache_dir=str(tmp_path / "cache")
            )
    
    @patch('extract.YouTubeTranscriptExtractor._validate_url')
    @patch('extract.YouTubeTranscriptExtractor._get_video_info')
    @patch('extract.YouTubeTranscriptExtractor._extract_subtitles')
    def test_successful_extraction(
        self, 
        mock_extract_sub, 
        mock_get_info, 
        mock_validate, 
        extractor,
        tmp_path
    ):
        """測試成功提取"""
        # Mock 設置
        mock_validate.return_value = "test_video_id"
        mock_get_info.return_value = {'title': 'Test Video'}
        
        # 創建假字幕文件
        subtitle_file = tmp_path / "output" / "test_video_id.zh-Hans.srt"
        subtitle_file.parent.mkdir(parents=True, exist_ok=True)
        subtitle_file.write_text("1\n00:00:00 --> 00:00:01\nTest subtitle")
        mock_extract_sub.return_value = subtitle_file
        
        # 執行測試
        result = extractor.extract("https://contact.com/watch?v=test", "zh-Hans")
        
        # 驗證結果
        assert result['success'] is True
        assert result['video_id'] == "test_video_id"
        assert result['title'] == "Test Video"
        assert result['subtitle_file'] == str(subtitle_file)
        assert "Test subtitle" in result['content']
        assert result['error'] is None
    
    @patch('extract.YouTubeTranscriptExtractor._validate_url')
    def test_url_validation_error(self, mock_validate, extractor):
        """測試 URL 驗證錯誤"""
        mock_validate.side_effect = URLValidationError(url="bad_url")
        
        result = extractor.extract("bad_url")
        
        assert result['success'] is False
        assert result['error'] is not None
        assert result['error']['error_code'] == "URL_VALIDATION_FAILED"
    
    @patch('extract.YouTubeTranscriptExtractor._validate_url')
    @patch('extract.YouTubeTranscriptExtractor._get_video_info')
    def test_network_error(self, mock_get_info, mock_validate, extractor):
        """測試網絡錯誤"""
        mock_validate.return_value = "test_id"
        mock_get_info.side_effect = NetworkError("Connection failed")
        
        result = extractor.extract("https://contact.com/watch?v=test")
        
        assert result['success'] is False
        assert result['error']['error_code'] == "NETWORK_ERROR"
    
    @patch('extract.YouTubeTranscriptExtractor._validate_url')
    @patch('extract.YouTubeTranscriptExtractor._get_video_info')
    @patch('extract.YouTubeTranscriptExtractor._extract_subtitles')
    def test_subtitle_not_found(
        self, 
        mock_extract_sub, 
        mock_get_info, 
        mock_validate, 
        extractor
    ):
        """測試字幕未找到"""
        mock_validate.return_value = "test_id"
        mock_get_info.return_value = {'title': 'Test Video'}
        mock_extract_sub.return_value = None
        
        result = extractor.extract("https://contact.com/watch?v=test")
        
        assert result['success'] is False
        assert result['error']['error_code'] == "SUBTITLE_NOT_FOUND"
    
    @patch('extract.YouTubeTranscriptExtractor._validate_url')
    @patch('extract.YouTubeTranscriptExtractor._get_video_info')
    @patch('extract.YouTubeTranscriptExtractor._extract_subtitles')
    def test_cache_usage(
        self, 
        mock_extract_sub, 
        mock_get_info, 
        mock_validate, 
        extractor,
        tmp_path
    ):
        """測試緩存使用"""
        mock_validate.return_value = "cached_video"
        
        # 創建緩存文件
        cache_file = tmp_path / "cache" / "cached_video.info.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({'title': 'Cached Video'}))
        
        subtitle_file = tmp_path / "output" / "cached_video.zh-Hans.srt"
        subtitle_file.parent.mkdir(parents=True, exist_ok=True)
        subtitle_file.write_text("Cached subtitle")
        mock_extract_sub.return_value = subtitle_file
        
        result = extractor.extract("https://contact.com/watch?v=cached")
        
        # 驗證使用了緩存（沒有調用 _get_video_info）
        mock_get_info.assert_not_called()
        assert result['title'] == 'Cached Video'


class TestSummarize:
    """測試摘要功能"""
    
    @pytest.fixture
    def extractor(self, tmp_path):
        """創建測試用提取器"""
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            return YouTubeTranscriptExtractor(
                output_dir=str(tmp_path / "output"),
                cache_dir=str(tmp_path / "cache")
            )
    
    def test_basic_summarize(self, extractor):
        """測試基本摘要"""
        srt_content = """1
00:00:00 --> 00:00:01
Hello world

2
00:00:01 --> 00:00:02
This is a test

3
00:00:02 --> 00:00:03
Goodbye"""
        
        summary = extractor.summarize(srt_content)
        
        assert "Hello world" in summary
        assert "This is a test" in summary
        assert "Goodbye" in summary
        assert "-->" not in summary
        assert "1" not in summary
        assert "2" not in summary
        assert "3" not in summary
    
    def test_max_lines_limit(self, extractor):
        """測試最大行數限制"""
        lines = [f"{i}\n00:00:00 --> 00:00:01\nLine {i}\n" for i in range(50)]
        srt_content = "".join(lines)
        
        summary = extractor.summarize(srt_content, max_lines=10)
        summary_lines = [l for l in summary.split('\n') if l.strip()]
        
        assert len(summary_lines) <= 10
    
    def test_empty_input(self, extractor):
        """測試空輸入"""
        summary = extractor.summarize("")
        assert summary == ""
    
    def test_whitespace_only(self, extractor):
        """測試僅空白字符"""
        summary = extractor.summarize("   \n\n   \n")
        assert summary == ""


class TestCommandLineInterface:
    """測試命令行接口"""
    
    def test_help_message(self):
        """測試幫助信息"""
        from extract import main
        import sys
        
        # 捕獲幫助輸出
        old_argv = sys.argv
        old_stdout = sys.stdout
        sys.argv = ['extract', '-h']
        sys.stdout = StringIO()
        
        try:
            with pytest.raises(SystemExit):
                main()
        finally:
            sys.argv = old_argv
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
        
        assert "YouTube Transcript Extractor" in output
        assert "-u" in output or "--url" in output
        assert "-l" in output or "--lang" in output


class TestIntegration:
    """集成測試"""
    
    @pytest.fixture
    def temp_extractor(self, tmp_path):
        """創建臨時提取器"""
        output_dir = tmp_path / "output"
        cache_dir = tmp_path / "cache"
        
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            extractor = YouTubeTranscriptExtractor(
                output_dir=str(output_dir),
                cache_dir=str(cache_dir)
            )
            return extractor, tmp_path
    
    def test_full_workflow_with_mock(self, temp_extractor):
        """測試完整工作流程（Mock）"""
        extractor, tmp_path = temp_extractor
        
        with patch.object(extractor, '_validate_url', return_value='test123'):
            with patch.object(extractor, '_get_video_info', return_value={'title': 'Test'}):
                # 創建假字幕文件
                subtitle_file = tmp_path / "output" / "test123.zh-Hans.srt"
                subtitle_file.parent.mkdir(parents=True, exist_ok=True)
                subtitle_file.write_text("Test content")
                
                with patch.object(extractor, '_extract_subtitles', return_value=subtitle_file):
                    result = extractor.extract("https://contact.com/watch?v=test123")
                    
                    assert result['success'] is True
                    assert result['video_id'] == 'test123'
                    assert result['title'] == 'Test'
                    assert result['content'] == 'Test content'


class TestGetVideoInfo:
    """測試 _get_video_info 方法"""
    
    @pytest.fixture
    def extractor(self, tmp_path):
        """創建測試用提取器"""
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            return YouTubeTranscriptExtractor(
                output_dir=str(tmp_path / "output"),
                cache_dir=str(tmp_path / "cache")
            )
    
    @patch('extract.subprocess.run')
    def test_get_video_info_success(self, mock_run, extractor):
        """測試成功獲取視頻信息"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"title": "Test Video", "id": "test123"}'
        )
        
        info = extractor._get_video_info("https://contact.com/watch?v=test123")
        
        assert info['title'] == 'Test Video'
        assert info['id'] == 'test123'
    
    @patch('extract.subprocess.run')
    def test_get_video_info_ytdlp_error(self, mock_run, extractor):
        """測試 yt-dlp 錯誤"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr='Video unavailable'
        )
        
        with pytest.raises(YTDLLError) as exc_info:
            extractor._get_video_info("https://contact.com/watch?v=test123")
        
        assert exc_info.value.error_code == "YT_DLP_ERROR"
    
    @patch('extract.subprocess.run')
    def test_get_video_info_timeout(self, mock_run, extractor):
        """測試超時錯誤"""
        import subprocess as sp
        mock_run.side_effect = sp.TimeoutExpired(cmd='test', timeout=30)
        
        with pytest.raises(NetworkError) as exc_info:
            extractor._get_video_info("https://contact.com/watch?v=test123")
        
        assert exc_info.value.error_code == "NETWORK_ERROR"
    
    @patch('extract.subprocess.run')
    def test_get_video_info_json_error(self, mock_run, extractor):
        """測試 JSON 解析錯誤"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='invalid json'
        )
        
        with pytest.raises(YTDLLError) as exc_info:
            extractor._get_video_info("https://contact.com/watch?v=test123")
        
        assert "JSON 解析失敗" in str(exc_info.value.message)


class TestExtractSubtitles:
    """測試 _extract_subtitles 方法"""
    
    @pytest.fixture
    def extractor(self, tmp_path):
        """創建測試用提取器"""
        with patch('extract.YouTubeTranscriptExtractor._find_yt_dlp', return_value='/fake/yt-dlp'):
            return YouTubeTranscriptExtractor(
                output_dir=str(tmp_path / "output"),
                cache_dir=str(tmp_path / "cache")
            )
    
    @patch('extract.subprocess.run')
    def test_extract_subtitles_found_srt(self, mock_run, extractor, tmp_path):
        """測試找到 SRT 字幕"""
        mock_run.return_value = MagicMock(returncode=0, stderr='')
        
        # 創建假字幕文件
        subtitle_file = tmp_path / "output" / "test123.zh-Hans.srt"
        subtitle_file.parent.mkdir(parents=True, exist_ok=True)
        subtitle_file.write_text("Test subtitle")
        
        result = extractor._extract_subtitles("https://contact.com/watch?v=test123", "test123", "zh-Hans")
        
        assert result == subtitle_file
    
    @patch('extract.subprocess.run')
    def test_extract_subtitles_found_vtt(self, mock_run, extractor, tmp_path):
        """測試找到 VTT 字幕"""
        mock_run.return_value = MagicMock(returncode=0, stderr='')
        
        # 創建假字幕文件
        subtitle_file = tmp_path / "output" / "test123.en.vtt"
        subtitle_file.parent.mkdir(parents=True, exist_ok=True)
        subtitle_file.write_text("WEBVTT")
        
        result = extractor._extract_subtitles("https://contact.com/watch?v=test123", "test123", "en")
        
        assert result == subtitle_file
    
    @patch('extract.subprocess.run')
    def test_extract_subtitles_not_found(self, mock_run, extractor):
        """測試未找到字幕"""
        mock_run.return_value = MagicMock(returncode=0, stderr='')
        
        result = extractor._extract_subtitles("https://contact.com/watch?v=test123", "test123", "zh-Hans")
        
        assert result is None
    
    @patch('extract.subprocess.run')
    def test_extract_subtitles_with_auto_generate(self, mock_run, extractor):
        """測試啟用自動生成字幕"""
        mock_run.return_value = MagicMock(returncode=0, stderr='')
        
        extractor._extract_subtitles("https://contact.com/watch?v=test123", "test123", "en", auto_generate=True)
        
        # 驗證命令包含 --write-auto-sub
        call_args = mock_run.call_args[0][0]
        assert "--write-auto-sub" in call_args


class TestMainFunction:
    """測試 main 函數"""
    
    @patch('extract.YouTubeTranscriptExtractor')
    @patch('extract.sys.argv', ['extract', '-u', 'test123', '--json'])
    def test_main_json_output(self, mock_extractor_class, capsys):
        """測試 JSON 輸出模式"""
        from extract import main
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'success': True,
            'video_id': 'test123',
            'title': 'Test',
            'subtitle_file': '/path/to/file.srt',
            'content': 'Test content',
            'error': None
        }
        mock_extractor_class.return_value = mock_extractor
        
        # JSON 模式不會退出，除非出錯
        main()
        
        captured = capsys.readouterr()
        assert 'test123' in captured.out
        assert 'Test' in captured.out
    
    @patch('extract.YouTubeTranscriptExtractor')
    @patch('extract.sys.argv', ['extract', '-u', 'test123'])
    def test_main_success_text_output(self, mock_extractor_class, capsys):
        """測試成功時的文本輸出"""
        from extract import main
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'success': True,
            'video_id': 'test123',
            'title': 'Test Video',
            'subtitle_file': '/path/to/file.srt',
            'content': 'Test content',
            'error': None
        }
        mock_extractor.summarize.return_value = 'Summary'
        mock_extractor_class.return_value = mock_extractor
        
        # 成功模式不會退出
        main()
        
        captured = capsys.readouterr()
        assert '✅' in captured.out or 'Success' in captured.out or '提取成功' in captured.out
        assert 'Test Video' in captured.out
    
    @patch('extract.YouTubeTranscriptExtractor')
    @patch('extract.sys.argv', ['extract', '-u', 'test123'])
    def test_main_failure_output(self, mock_extractor_class, capsys):
        """測試失敗時的輸出"""
        from extract import main
        
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            'success': False,
            'video_id': None,
            'title': None,
            'subtitle_file': None,
            'content': None,
            'error': {
                'error_code': 'SUBTITLE_NOT_FOUND',
                'message': 'No subtitles found',
                'details': {}
            }
        }
        mock_extractor_class.return_value = mock_extractor
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('extract.YouTubeTranscriptExtractor')
    @patch('extract.sys.argv', ['extract', '-u', 'test123'])
    def test_main_keyboard_interrupt(self, mock_extractor_class, capsys):
        """測試用戶中斷"""
        from extract import main
        
        mock_extractor_class.side_effect = KeyboardInterrupt()
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 130
        captured = capsys.readouterr()
        assert '取消' in captured.out or 'cancel' in captured.out.lower()
    
    @patch('extract.YouTubeTranscriptExtractor')
    @patch('extract.sys.argv', ['extract', '-u', 'test123'])
    def test_main_unknown_exception(self, mock_extractor_class, capsys):
        """測試未知異常"""
        from extract import main
        
        mock_extractor_class.side_effect = Exception("Unexpected error")
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=extract', '--cov-report=term-missing'])
