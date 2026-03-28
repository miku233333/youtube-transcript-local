#!/bin/bash
# 運行測試腳本

set -e

echo "🧪 運行 YouTube Transcript Extractor 測試套件"
echo "=============================================="

# 安裝依賴
echo "📦 安裝測試依賴..."
pip install -r requirements.txt

# 運行測試
echo ""
echo "🚀 運行測試..."
pytest tests/ -v --cov=extract --cov-report=term-missing --cov-report=html:htmlcov

# 顯示覆蓋率報告
echo ""
echo "📊 生成 HTML 覆蓋率報告..."
if [ -d "htmlcov" ]; then
    echo "✅ HTML 報告已生成：htmlcov/index.html"
    echo "   在瀏覽器中打開查看詳細報告"
fi

echo ""
echo "✅ 測試完成！"
