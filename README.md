# YouTube Transcript Local

[![License](https://img.shields.io/badge/license-Non--Commercial-blue)](LICENSE)
[![CI/CD](https://github.com/miku233333/youtube-transcript-local/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/miku233333/youtube-transcript-local/actions)
[![Coverage](https://img.shields.io/badge/coverage-79.75%25-brightgreen)](https://github.com/miku233333/youtube-transcript-local)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macos%20%7C%20linux%20%7C%20windows-lightgrey)](https://github.com/miku233333/youtube-transcript-local)

📺 **本地安全嘅 YouTube 字幕提取工具**

> 無需付費 API、無需網絡請求、支持多語言、批量處理

---

## 🎯 項目特點

- ✅ **完全本地** - 所有處理喺本地完成，保障私隱
- ✅ **無需 API** - 唔使付費，唔使註冊
- ✅ **多語言支持** - 自動檢測並提取字幕
- ✅ **批量處理** - 支持播放列表批量提取
- ✅ **結構化日誌** - 彩色輸出，易於調試
- ✅ **79.75% 測試覆蓋** - 48 個單元測試保證質量
- ✅ **CI/CD 自動化** - GitHub Actions 自動測試同部署

---

## 🚀 快速開始

### 前置要求

- Python 3.11+
- yt-dlp（已包含）

### 安裝

```bash
# 1. 克隆項目
git clone https://github.com/miku233333/youtube-transcript-local.git
cd youtube-transcript-local

# 2. 安裝依賴
pip3 install -r requirements.txt

# 3. 驗證安裝
python3 extract.py --help
```

### 基本使用

```bash
# 提取單一視頻字幕
python3 extract.py https://www.youtube.com/watch?v=VIDEO_ID

# 指定語言（繁體中文）
python3 extract.py https://www.youtube.com/watch?v=VIDEO_ID --lang zh-Hant

# 指定語言（英文）
python3 extract.py https://www.youtube.com/watch?v=VIDEO_ID --lang en

# 批量處理播放列表
python3 extract.py https://www.youtube.com/playlist?list=PLAYLIST_ID

# 輸出到指定目錄
python3 extract.py VIDEO_URL --output ./subtitles
```

---

## 📋 功能詳情

### P0 升級（已完成）✅

| 功能 | 狀態 | 說明 |
|------|------|------|
| **結構化日誌** | ✅ | 彩色輸出 + 文件日誌 + 分級 |
| **錯誤分類** | ✅ | 7 種自定義異常 |
| **單元測試** | ✅ | 48 個測試用例 |
| **CI/CD** | ✅ | GitHub Actions 自動測試 |
| **代碼覆蓋率** | ✅ | 79.75% |

### P1 升級（規劃中）🟡

- [ ] 智能摘要（AI 集成）
- [ ] 配置文件
- [ ] 批量處理增強

### P2 升級（規劃中）⚪

- [ ] Web UI
- [ ] API 服務
- [ ] 瀏覽器擴展

---

## 🔧 技術架構

```
┌─────────────────────────────────────────┐
│         YouTube Transcript Local        │
├─────────────────────────────────────────┤
│  用戶界面 (CLI)                          │
│  - 命令行參數解析                        │
│  - 進度顯示                              │
│  - 彩色輸出                              │
├─────────────────────────────────────────┤
│  核心邏輯 (extract.py)                   │
│  - URL 驗證                              │
│  - 字幕提取                              │
│  - 格式轉換                              │
├─────────────────────────────────────────┤
│  依賴庫                                  │
│  - yt-dlp (視頻/字幕下載)               │
│  - logging (結構化日誌)                 │
│  - pytest (單元測試)                    │
└─────────────────────────────────────────┘
```

---

## 📁 項目結構

```
youtube-transcript-local/
├── extract.py              # 核心提取邏輯
├── tests/
│   └── test_extract.py     # 48 個測試用例
├── .github/
│   └── workflows/
│       └── ci-cd.yml       # CI/CD 配置
├── pyproject.toml          # 項目配置
├── requirements.txt        # Python 依賴
├── README.md               # 本文檔
├── LICENSE                 # 非商業許可證
└── SKILL.md                # OpenClaw 技能配置
```

---

## 🧪 測試

```bash
# 運行所有測試
python3 -m pytest

# 顯示測試覆蓋率
python3 -m pytest --cov=extract --cov-report=html

# 運行特定測試
python3 -m pytest tests/test_extract.py::test_extract_transcript
```

### 測試結果

```
48 passed in 0.09s
代碼覆蓋率：79.75%
```

---

## 🔍 錯誤處理

### 常見錯誤及解決方案

| 錯誤 | 原因 | 解決方案 |
|------|------|---------|
| `URLValidationError` | URL 格式錯誤 | 檢查 YouTube 鏈接是否正確 |
| `NetworkError` | 網絡問題 | 檢查網絡連接 |
| `SubtitleNotFoundError` | 無字幕 | 該視頻可能無字幕 |
| `LanguageNotSupportedError` | 語言不支持 | 使用 `--list-langs` 查看支持語言 |
| `FileWriteError` | 文件權限問題 | 檢查輸出目錄權限 |

### 日誌級別

```bash
# 顯示詳細日誌
python3 extract.py VIDEO_URL --log-level DEBUG

# 僅顯示錯誤
python3 extract.py VIDEO_URL --log-level ERROR
```

---

## 📖 使用示例

### 示例 1: 提取英文視頻字幕

```bash
python3 extract.py https://www.youtube.com/watch?v=dQw4w9WgXcQ --lang en
```

**輸出**:
```
[INFO] 開始提取字幕...
[INFO] 檢測到語言：en
[SUCCESS] 字幕提取成功：subtitles/dQw4w9WgXcQ_en.txt
```

### 示例 2: 批量提取播放列表

```bash
python3 extract.py https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf --output ./my_subs
```

**輸出**:
```
[INFO] 檢測到播放列表：10 個視頻
[INFO] 處理中：1/10
[SUCCESS] 提取成功：my_subs/video1.txt
[INFO] 處理中：2/10
...
[SUCCESS] 批量處理完成：10/10
```

### 示例 3: 指定輸出格式

```bash
python3 extract.py VIDEO_URL --format srt
python3 extract.py VIDEO_URL --format vtt
python3 extract.py VIDEO_URL --format json
```

---

## 🔧 配置選項

### 命令行參數

```
用法：extract.py [-h] [--lang LANG] [--output OUTPUT] [--format FORMAT]
                 [--log-level LEVEL] [--list-langs] [--batch]
                 URL

位置參數:
  URL                  YouTube 視頻或播放列表 URL

選項:
  -h, --help           顯示幫助信息
  --lang LANG          字幕語言（默認：自動檢測）
  --output OUTPUT      輸出目錄（默認：./subtitles）
  --format FORMAT      輸出格式：txt/srt/vtt/json（默認：txt）
  --log-level LEVEL    日誌級別：DEBUG/INFO/WARNING/ERROR（默認：INFO）
  --list-langs         列出支持嘅語言
  --batch              啟用批量處理模式
```

---

## 📊 CI/CD 流程

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest --cov=extract

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install black ruff
      - run: black --check .
      - run: ruff check .

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install bandit
      - run: bandit -r extract.py
```

---

## 📄 開源協議

**非商業許可證** - 允許個人、教育、非營利使用，禁止商業用途。

詳情請閱 [LICENSE](LICENSE)

---

## 🤝 貢獻

歡迎提交 Issue 同 Pull Request！

1. Fork 項目
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 開發者指南

```bash
# 設置開發環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install black ruff pytest

# 運行測試
pytest

# 格式化代碼
black .
ruff check --fix .
```

---

## 📬 聯絡

- **GitHub**: [@miku233333](https://github.com/miku233333)
- **Email**: [通過 GitHub 聯絡](https://github.com/miku233333/youtube-transcript-local/issues)

---

## 🎉 鳴謝

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 強大的視頻下載庫
- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent 生態系統

---

**YouTube Transcript Local v1.0** - 2026-03-28
