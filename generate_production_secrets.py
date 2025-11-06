#!/usr/bin/env python3
"""
生成 Railway 部署所需的生产环境密钥
运行: python generate_production_secrets.py
"""

import secrets
from cryptography.fernet import Fernet

def generate_secrets():
    """生成所有必需的安全密钥"""
    
    print("=" * 60)
    print("🔐 Railway 部署 - 生产环境密钥生成器")
    print("=" * 60)
    print()
    
    # 生成 SECRET_KEY (JWT signing)
    secret_key = secrets.token_urlsafe(32)
    print("SECRET_KEY (JWT 签名密钥):")
    print(f"  {secret_key}")
    print()
    
    # 生成 ENCRYPTION_KEY (Fernet encryption)
    encryption_key = Fernet.generate_key().decode()
    print("ENCRYPTION_KEY (数据加密密钥):")
    print(f"  {encryption_key}")
    print()
    
    print("=" * 60)
    print("📋 Railway 环境变量配置 (复制到 Railway Dashboard)")
    print("=" * 60)
    print()
    print("# 安全配置")
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print("JWT_ALG=HS256")
    print("JWT_ACCESS_TTL_MIN=15")
    print("JWT_REFRESH_TTL_DAYS=14")
    print()
    
    print("# 应用配置")
    print("APP_ENV=production")
    print("LOG_LEVEL=INFO")
    print("TZ=UTC")
    print()
    
    print("# 数据库连接 (使用 Railway 变量引用)")
    print("DATABASE_URL=${{Postgres.DATABASE_URL}}")
    print("REDIS_URL=${{Redis.REDIS_URL}}")
    print()
    
    print("# API 密钥 (需要替换)")
    print("OPENAI_API_KEY=sk-你的OpenAI密钥")
    print("OPENAI_MODEL=gpt-4o-mini")
    print()
    
    print("# CORS 配置 (需要替换)")
    print("BACKEND_CORS_ORIGINS=https://你的前端域名.vercel.app")
    print()
    
    print("# 文件存储")
    print("FILE_STORAGE_DIR=/app/data/uploads")
    print("MAX_FILE_SIZE_MB=25")
    print()
    
    print("# 速率限制")
    print("RATE_LIMIT_FREE=60/minute")
    print("RATE_LIMIT_OPTIMIZER=240/minute")
    print("RATE_LIMIT_AUTOPILOT=600/minute")
    print()
    
    print("# AI 配额")
    print("AI_QUOTA_FREE=100")
    print("AI_QUOTA_OPTIMIZER=1000")
    print("AI_QUOTA_AUTOPILOT=3000")
    print()
    
    print("=" * 60)
    print("⚠️  重要提示:")
    print("=" * 60)
    print("1. 保存这些密钥到安全的地方（密码管理器）")
    print("2. 不要将密钥提交到 Git 仓库")
    print("3. 不要在公开场合分享这些密钥")
    print("4. 定期轮换生产环境密钥")
    print()
    print("✅ 密钥生成完成！")
    print()

if __name__ == "__main__":
    generate_secrets()
