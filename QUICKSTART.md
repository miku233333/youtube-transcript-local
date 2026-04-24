# 快速開始指南

## 🚀 5 分鐘快速上手

### 1. 安裝依賴

```bash
# 進入項目目錄
cd youtube-transcript-local-upgrade

# 創建虛擬環境（推薦）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 基本使用

```bash
# 提取字幕（默認中文）
python extract.py -u https://www.youtube.com/watch?v=VIDEO_ID

# 示例（Rick Astley - Never Gonna Give You Up）
python extract.py -u https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 3. 常用命令

```bash
# 指定語言（英文）
python extract.py -u VIDEO_ID -l en

# 輸出到指定目錄
python extract.py -u VIDEO_ID -o ./my_subtitles

# 啟用詳細日誌
python extract.py -u VIDEO_ID --verbose

# 保存日誌到文件
python extract.py -u VIDEO_ID --log-file ./logs/extract.log

# JSON 格式輸出（適合程序調用）
python extract.py -u VIDEO_ID --json

# 跳過摘要
python extract.py -u VIDEO_ID --no-summarize
```

### 4. 運行測試

```bash
# 快速測試
./run_tests.sh  # macOS/Linux
# 或
run_tests.bat  # Windows

# 或手動運行
source venv/bin/activate
pytest tests/ -v

# 查看覆蓋率
pytest tests/ --cov=extract --cov-report=html
open htmlcov/index.html  # 在瀏覽器中查看
```

### 5. 查看幫助

```bash
python extract.py --help
```

## 📝 輸出示例

### 成功輸出

```
2026-03-28 20:00:00 | INFO | YouTube Transcript Extractor v2.0.0 (P0 Upgrade)
2026-03-28 20:00:01 | INFO | 開始提取：https://www.youtube.com/watch?v=dQw4w9WgXcQ
2026-03-28 20:00:02 | INFO | 獲取成功：Rick Astley - Never Gonna Give You Up
2026-03-28 20:00:05 | INFO | 提取成功：/path/to/transcripts/dQw4w9WgXcQ.zh-Hans.srt

✅ 提取成功!
  標題：Rick Astley - Never Gonna Give You Up
  文件：/path/to/transcripts/dQw4w9WgXcQ.zh-Hans.srt

📝 摘要:
--------------------------------------------------
We're no strangers to love
You know the rules and so do I
A full commitment's what I'm thinking of
...
--------------------------------------------------
```

### 錯誤輸出

```
📝 未找到字幕，該視頻可能沒有可用字幕

技術細節：字幕文件不存在
建議：嘗試其他語言，或使用音頻提取 + Whisper 識別

詳細信息:
  - video_id: dQw4w9WgXcQ
  - lang: zh-Hans
```

## 🔧 常見問題

### Q1: 提示 "yt-dlp 未找到"

**解決方法**:
```bash
# 手動安裝 yt-dlp
pip install yt-dlp

# 或使用 Homebrew (macOS)
brew install yt-dlp

# 或使用 apt (Linux)
sudo apt install yt-dlp
```

### Q2: 提示 "無效的 YouTube 連結"

**解決方法**:
- 確保連結格式正確：`https://www.youtube.com/watch?v=VIDEO_ID`
- 或直接使用 VIDEO_ID：`python extract.py -u dQw4w9WgXcQ`

### Q3: 提示 "未找到字幕"

**解決方法**:
1. 嘗試其他語言：`python extract.py -u VIDEO_ID -l en`
2. 啟用自動生成：`python extract.py -u VIDEO_ID --auto-generate`
3. 該視頻可能真的沒有字幕，需要音頻提取 + Whisper 識別

### Q4: 網絡連接超時

**解決方法**:
- 檢查網絡連接
- 使用代理：`export https_proxy=http://proxy:port`
- 稍後重試

## 📚 進階使用

### 程序化調用

```python
from extract import YouTubeTranscriptExtractor, setup_logging

# 設置日誌
logger = setup_logging(verbose=True)

# 創建提取器
extractor = YouTubeTranscriptExtractor(
    output_dir='./subtitles',
    logger=logger
)

# 提取字幕
result = extractor.extract(
    url='https://www.youtube.com/watch?v=VIDEO_ID',
    lang='zh-Hans',
    auto_generate=True
)

if result['success']:
    print(f"標題：{result['title']}")
    print(f"文件：{result['subtitle_file']}")
    print(f"內容：{result['content'][:100]}...")
else:
    print(f"失敗：{result['error']['message']}")
```

### 批量處理

```python
video_ids = ['video1', 'video2', 'video3']

for video_id in video_ids:
    result = extractor.extract(f'https://www.youtube.com/watch?v={video_id}')
    if result['success']:
        print(f"✅ {video_id}: {result['title']}")
    else:
        print(f"❌ {video_id}: {result['error']['message']}")
```

## 🎯 P0 升級特性

本次升級包含：

- ✅ **結構化日誌**：支持彩色輸出和文件日誌
- ✅ **錯誤分類**：7 種錯誤類型，精確定位問題
- ✅ **用戶友好提示**：清晰的錯誤信息和解決建議
- ✅ **單元測試**：48 個測試用例，覆蓋率 80%
- ✅ **CI/CD**：GitHub Actions 自動化測試和部署

詳細文檔請查看：
- [README.md](README.md) - 完整使用說明
- [P0_UPGRADE.md](P0_UPGRADE.md) - 升級詳情

## 🆘 獲取幫助

- 查看文檔：`README.md`
- 提交 Issue：https://github.com/miku233333/youtube-transcript-local/issues
- 查看日誌：`--log-file` 選項保存詳細日誌

---

**版本**: 2.0.0 (P0 Upgrade)  
**更新日期**: 2026-03-28
