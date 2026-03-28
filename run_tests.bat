@echo off
REM 運行測試腳本 (Windows)

echo 🧪 運行 YouTube Transcript Extractor 測試套件
echo ==============================================

REM 安裝依賴
echo 📦 安裝測試依賴...
pip install -r requirements.txt

REM 運行測試
echo.
echo 🚀 運行測試...
pytest tests/ -v --cov=extract --cov-report=term-missing --cov-report=html:htmlcov

REM 顯示覆蓋率報告
echo.
echo 📊 生成 HTML 覆蓋率報告...
if exist htmlcov (
    echo ✅ HTML 報告已生成：htmlcov\index.html
    echo    在瀏覽器中打開查看詳細報告
)

echo.
echo ✅ 測試完成！
