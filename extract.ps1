# YouTube Transcript Extractor (本地安全版)
# 使用 yt-dlp 提取 YouTube 視頻字幕
# 2026-03-23 qibot

param(
    [string]$url,
    [string]$lang = "en",
    [string]$outputDir = "$env:TEMP\youtube-transcripts"
)

# 創建輸出目錄
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# yt-dlp 路徑（pip 安裝）
$ytDlpPath = "$env:APPDATA\Python\Python314\Scripts\yt-dlp.exe"

if (!(Test-Path $ytDlpPath)) {
    Write-Error "yt-dlp 未找到：$ytDlpPath"
    exit 1
}

# 生成輸出文件名
$videoId = if ($url -match 'v=([a-zA-Z0-9_-]+)') { $matches[1] } else { "unknown" }
$outputTemplate = "$outputDir\$videoId"

Write-Host "🎬 正在提取字幕..."
Write-Host "   URL: $url"
Write-Host "   語言：$lang"
Write-Host "   輸出：$outputTemplate"

# 提取字幕
& $ytDlpPath `
    --write-sub `
    --sub-lang $lang `
    --skip-download `
    --convert-subs srt `
    -o "$outputTemplate" `
    "$url" 2>&1 | ForEach-Object { Write-Host $_ }

# 查找字幕文件
$subFile = Get-ChildItem -Path $outputDir -Filter "$videoId.*.srt" | Select-Object -First 1

if ($subFile) {
    Write-Host "✅ 字幕提取成功！"
    Write-Host "   文件：$($subFile.FullName)"
    
    # 返回字幕內容
    Get-Content $subFile.FullName -Raw
} else {
    Write-Host "⚠️ 未找到字幕，嘗試提取音頻..."
    
    # 提取音頻（用於 Whisper 轉文字）
    & $ytDlpPath `
        --extract-audio `
        --audio-format mp3 `
        -o "$outputTemplate" `
        "$url" 2>&1 | ForEach-Object { Write-Host $_ }
    
    $audioFile = Get-ChildItem -Path $outputDir -Filter "$videoId.mp3" | Select-Object -First 1
    
    if ($audioFile) {
        Write-Host "✅ 音頻提取成功！"
        Write-Host "   文件：$($audioFile.FullName)"
        Write-Host "   下一步：使用 whisper 或 tesseract-ocr 轉文字"
    } else {
        Write-Error "❌ 提取失敗"
        exit 1
    }
}
