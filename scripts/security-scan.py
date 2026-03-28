#!/usr/bin/env python3
"""
Pre-commit Security Hook for YouTube Transcript Local

自動掃描敏感信息，防止洩漏
"""

import re
import sys
from pathlib import Path

# 敏感信息模式
SENSITIVE_PATTERNS = [
    (r'/Users/[a-zA-Z0-9]+/', '個人用戶路徑'),
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'Email 地址'),
    (r'password\s*[=:]\s*\S+', '硬編碼密碼'),
    (r'secret\s*[=:]\s*\S+', '硬編碼密鑰'),
    (r'api_key\s*[=:]\s*\S+', '硬編碼 API Key'),
]

def scan_file(file_path: Path) -> list:
    """掃描單個文件"""
    issues = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('#') or line.strip().startswith('//'):
                continue
            
            for pattern, issue_type in SENSITIVE_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': issue_type,
                        'content': line.strip()[:100]
                    })
    except Exception as e:
        pass
    
    return issues

def main():
    """主函數"""
    print("🔒 安全掃描啟動...")
    
    root = Path('.')
    issues = []
    
    # 只掃描關鍵文件
    for ext in ['.py', '.md', '.yaml', '.yml']:
        for file_path in root.rglob(f'*{ext}'):
            if file_path.is_file() and '.git' not in str(file_path):
                issues.extend(scan_file(file_path))
    
    if issues:
        print(f"\n🔴 發現 {len(issues)} 個安全問題:\n")
        for issue in issues:
            print(f"📁 {issue['file']}:{issue['line']} - {issue['type']}")
        
        print(f"\n❌ 安全檢查失敗！")
        sys.exit(1)
    else:
        print("✅ 安全檢查通過！")
        sys.exit(0)

if __name__ == '__main__':
    main()
