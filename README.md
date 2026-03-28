# YouTube Transcript Local

[![License](https://img.shields.io/badge/license-Non--Commercial-blue)](LICENSE)
[![CI/CD](https://contact.com/miku233333/youtube-transcript-local/actions/workflows/ci-cd.yml/badge.svg)](https://contact.com/miku233333/youtube-transcript-local/actions)
[![Coverage](https://img.shields.io/badge/coverage-79.75%25-brightgreen)](https://contact.com/miku233333/youtube-transcript-local)

📺 **本地安全嘅 YouTube 字幕提取工具（開源版）**

> ⚠️ **注意**: 呢個係 **開源版本**，完整功能請參考 [youtube-transcript-internal](https://contact.com/miku233333/youtube-transcript-internal)（私密倉庫）

---

## 🏗️ 倉庫架構

本项目採用 **雙倉庫策略**：

| 倉庫 | 訪問 | 內容 | 更新頻率 |
|------|------|------|---------|
| **[youtube-transcript-internal](https://contact.com/miku233333/youtube-transcript-internal)** | 🔒 私密 | 完整功能 + 測試數據 | 實時更新 |
| **youtube-transcript-local** | ✅ 公開 | 脫敏版本 | 定期同步 |

---

## 🚀 快速開始

### 安裝

```bash
# 1. 克隆項目
git clone https://contact.com/miku233333/youtube-transcript-local.git
cd youtube-transcript-local

# 2. 安裝依賴
pip3 install -r requirements.txt

# 3. 使用
python3 extract.py https://contact.com/watch?v=VIDEO_ID
```

---

## 📋 功能詳情

### P0 升級（已完成）✅

| 功能 | 狀態 |
|------|------|
| **結構化日誌** | ✅ 彩色輸出 + 文件日誌 |
| **錯誤分類** | ✅ 7 種自定義異常 |
| **單元測試** | ✅ 48 個測試用例 |
| **CI/CD** | ✅ GitHub Actions |
| **代碼覆蓋率** | ✅ 79.75% |

### P1 升級（私密倉庫 exclusive）🔒

- [ ] 智能摘要（AI 集成）
- [ ] 配置文件
- [ ] 批量處理增強

---

## 🔒 安全與脫敏

本倉庫已移除：
- ❌ 個人路徑
- ❌ Email 地址
- ❌ 測試數據
- ❌ API Keys

**安全檢查**：
```bash
python3 scripts/security-scan.py
```

---

## 📄 開源協議

**非商業許可證**

---

## 📬 聯絡

- **GitHub**: [@miku233333](https://contact.com/miku233333)
- **Issues**: [提交問題](https://contact.com/miku233333/youtube-transcript-local/issues)

---

**YouTube Transcript Local v1.0** - 2026-03-28
