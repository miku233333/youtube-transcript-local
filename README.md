# YouTube Transcript Extractor (P0 Upgrade)

[![CI/CD](https://contact.com/miku233333/youtube-transcript-local/actions/workflows/ci-cd.yml/badge.svg)](https://contact.com/miku233333/youtube-transcript-local/actions/workflows/ci-cd.yml)
[![Coverage](https://codecov.io/gh/miku233333/youtube-transcript-local/branch/main/graph/badge.svg)](https://codecov.io/gh/miku233333/youtube-transcript-local)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT--0-green.svg)](LICENSE)

> 🎯 **P0 升級版本**: 增強錯誤處理、結構化日誌、單元測試與 CI/CD

本地安全的 YouTube 字幕提取工具，使用 yt-dlp 從 YouTube 視頻提取字幕，無需上傳到第三方服務，保護隱私。

## ✨ P0 升級特性

### 1. 📝 結構化日誌系統
- ✅ 支持彩色控制台輸出
- ✅ 可選文件日誌記錄
- ✅ 分級日誌（DEBUG/INFO/WARNING/ERROR/CRITICAL）
- ✅ 詳細的調試信息（函數名、行號）

### 2. 🚨 錯誤分類與處理
- ✅ 自定義異常體系（7 種錯誤類型）
  - `URLValidationError`: URL 驗證失敗
  - `NetworkError`: 網絡連接問題
  - `SubtitleNotFoundError`: 字幕未找到
  - `YTDLLError`: yt-dlp 執行錯誤
  - `FileIOError`: 文件讀寫錯誤
  - `CacheError`: 緩存操作錯誤
  - `TranscriptError`: 通用錯誤基類
- ✅ 結構化錯誤信息（JSON 格式）
- ✅ 用戶友好的錯誤提示

### 3. 🧪 單元測試覆蓋
- ✅ 使用 pytest 編寫測試
- ✅ 測試覆蓋率 > 80%
- ✅ 覆蓋所有核心功能：
  - 日誌系統測試
  - 錯誤處理測試
  - URL 驗證測試
  - 提取流程測試
  - 命令行接口測試

### 4. 🚀 CI/CD 自動化
- ✅ GitHub Actions 工作流
- ✅ 多平台測試（Ubuntu/macOS/Windows）
- ✅ 多 Python 版本支持（3.9-3.12）
- ✅ 代碼質量檢查（black, flake8, mypy）
- ✅ 安全掃描（bandit, safety）
- ✅ 自動生成覆蓋率報告
- ✅ 自動發佈到 GitHub Releases

## 📦 安裝

### 快速安裝

```bash
# 克隆倉庫
git clone https://contact.com/miku233333/youtube-transcript-local.git
cd youtube-transcript-local

# 安裝依賴
pip install -r requirements.txt
```

### 開發環境

```bash
# 安裝開發依賴
pip install -r requirements.txt

# 驗證安裝
python extract.py --help
```

## 🚀 使用

### 基本用法

```bash
# 提取字幕（默認中文）
python extract.py -u https://contact.com/watch?v=VIDEO_ID

# 指定語言
python extract.py -u VIDEO_ID -l en

# 輸出到指定目錄
python extract.py -u VIDEO_ID -o ./subtitles

# 啟用詳細日誌
python extract.py -u VIDEO_ID --verbose

# JSON 格式輸出（適合程序調用）
python extract.py -u VIDEO_ID --json
```

### 命令行選項

```
選項:
  -u, --url           YouTube URL 或 VIDEO_ID [必填]
  -l, --lang          語言代碼 (default: zh-Hans)
  -o, --output        輸出目錄
  --auto-generate     允許自動生成字幕
  --no-summarize      跳過摘要
  --verbose, -v       啟用詳細日誌
  --log-file          日誌文件路徑
  --json              以 JSON 格式輸出結果
```

### 示例

```bash
# 提取英文字幕
python extract.py -u https://contact.com/watch?v=dQw4w9WgXcQ -l en

# 提取中文字幕並保存日誌
python extract.py -u dQw4w9WgXcQ -l zh-Hans --log-file ./logs/extract.log

# 程序化調用（JSON 輸出）
python extract.py -u VIDEO_ID --json | jq '.content'
```

## 🧪 測試

### 運行測試

```bash
# Linux/macOS
./run_tests.sh

# Windows
run_tests.bat

# 或直接運行
pytest tests/ -v --cov=extract --cov-report=html
```

### 測試覆蓋率

測試報告將生成在 `htmlcov/` 目錄：

```bash
# 在瀏覽器中打開
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

## 📂 項目結構

```
youtube-transcript-local/
├── extract.py                 # 主程序（P0 升級版）
├── tests/
│   ├── __init__.py
│   └── test_extract.py       # 單元測試
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # CI/CD 配置
├── requirements.txt           # 依賴列表
├── pyproject.toml            # 項目配置（pytest/coverage）
├── run_tests.sh              # 測試腳本（Unix）
├── run_tests.bat             # 測試腳本（Windows）
├── README.md                 # 本文檔
└── LICENSE                   # 許可證
```

## 🔧 開發

### 代碼質量

```bash
# 格式化
black extract.py tests/

# Lint
flake8 extract.py tests/

# 類型檢查
mypy extract.py
```

### 添加新測試

在 `tests/test_extract.py` 中添加測試類：

```python
class TestNewFeature:
    def test_something(self, extractor):
        # 測試代碼
        assert result == expected
```

### CI/CD 配置

GitHub Actions 自動在以下觸發時運行：
- Push 到 main/master/develop 分支
- Pull Request 到 main/master 分支

工作流包括：
1. **Test**: 多平台、多版本測試 + 覆蓋率
2. **Lint**: 代碼質量檢查
3. **Security**: 安全掃描
4. **Build**: 構建分發包
5. **Deploy**: 自動發佈（僅 main 分支）

## 📊 錯誤處理示例

### 成功響應

```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "subtitle_file": "/path/to/transcripts/dQw4w9WgXcQ.zh-Hans.srt",
  "content": "1\n00:00:00 --> 00:00:05\nWe're no strangers to love...",
  "error": null
}
```

### 錯誤響應

```json
{
  "success": false,
  "video_id": "dQw4w9WgXcQ",
  "title": null,
  "subtitle_file": null,
  "content": null,
  "error": {
    "error_code": "SUBTITLE_NOT_FOUND",
    "message": "No subtitles found for video dQw4w9WgXcQ (lang: zh-Hans)",
    "details": {
      "video_id": "dQw4w9WgXcQ",
      "lang": "zh-Hans",
      "auto_generate": true
    },
    "timestamp": "2026-03-28T19:56:00.000000"
  }
}
```

### 用戶友好提示

```
📝 未找到字幕，該視頻可能沒有可用字幕

技術細節：字幕文件不存在
建議：嘗試其他語言，或使用音頻提取 + Whisper 識別

詳細信息:
  - video_id: dQw4w9WgXcQ
  - lang: zh-Hans
```

## 🛡️ 安全

- ✅ 本地運行，無數據上傳
- ✅ 依賴安全掃描（bandit, safety）
- ✅ 無硬編碼密鑰
- ✅ 輸入驗證（URL、文件路徑）
- ✅ 超時控制（防止無限等待）

## 📝 日誌示例

```
2026-03-28 19:56:00 | INFO | YouTube Transcript Extractor v2.0.0 (P0 Upgrade)
2026-03-28 19:56:00 | DEBUG | 初始化輸出目錄：/path/to/transcripts
2026-03-28 19:56:00 | DEBUG | 初始化緩存目錄：/path/to/.cache
2026-03-28 19:56:00 | INFO | 目錄初始化成功
2026-03-28 19:56:00 | DEBUG | 找到 yt-dlp: /usr/local/bin/yt-dlp
2026-03-28 19:56:00 | INFO | 開始提取：https://contact.com/watch?v=VIDEO_ID
2026-03-28 19:56:00 | DEBUG | 驗證成功，video_id: VIDEO_ID
2026-03-28 19:56:01 | INFO | 正在獲取視頻信息...
2026-03-28 19:56:02 | INFO | 獲取成功：Video Title
2026-03-28 19:56:02 | INFO | 正在提取字幕 (lang: zh-Hans, auto: True)...
2026-03-28 19:56:05 | INFO | 找到字幕文件：/path/to/transcripts/VIDEO_ID.zh-Hans.srt
2026-03-28 19:56:05 | INFO | 提取成功：/path/to/transcripts/VIDEO_ID.zh-Hans.srt
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 貢獻流程

1. Fork 本倉庫
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

### 開發要求

- ✅ 測試覆蓋率 > 80%
- ✅ 通過所有 CI 檢查
- ✅ 代碼符合 black/flake8 規範
- ✅ 添加必要的文檔

## 📄 許可證

MIT-0 License - 詳見 [LICENSE](LICENSE) 文件

## 👤 作者

- **qibot**
- GitHub: [@miku233333](https://contact.com/miku233333)

## 🙏 致謝

- [yt-dlp](https://contact.com/yt-dlp/yt-dlp) - 強大的視頻下載工具
- [pytest](https://docs.pytest.org/) - 優秀的測試框架
- [GitHub Actions](https://contact.com/features/actions) - CI/CD 自動化

---

**P0 Upgrade Version**: 2.0.0  
**Last Updated**: 2026-03-28
