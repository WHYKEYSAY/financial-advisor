# ⚡ Railway 部署 - 快速开始（5步搞定）

**目标**: 60分钟内完成后端部署  
**难度**: ⭐⭐⭐ 中等

---

## 🎯 5步部署流程

### 步骤 1️⃣: 生成密钥（2分钟）

```bash
# 在项目根目录运行
python generate_production_secrets.py
```

复制输出的所有环境变量，保存到记事本（后面要用）。

---

### 步骤 2️⃣: Railway 创建项目（10分钟）

1. 访问 https://railway.app/ 并登录
2. 点击 **"New Project"** → **"Empty Project"**
3. 在项目中添加：
   - **PostgreSQL**: 点击 "+ New" → "Database" → "Add PostgreSQL"
   - **Redis**: 点击 "+ New" → "Database" → "Add Redis"
   - **GitHub 仓库**: 点击 "+ New" → "GitHub Repo" → 选择 `financial-advisor`

---

### 步骤 3️⃣: 配置环境变量（15分钟）

1. 点击后端服务（GitHub 仓库部署的服务）
2. 点击 **"Variables"** 标签
3. 粘贴步骤 1 生成的所有变量
4. **重要**：修改以下两个变量：
   ```bash
   OPENAI_API_KEY=你的真实OpenAI密钥
   BACKEND_CORS_ORIGINS=*  # 临时允许所有（测试用）
   ```

**最少必需的 15 个变量**:
```
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC
SECRET_KEY=[已生成]
ENCRYPTION_KEY=[已生成]
JWT_ALG=HS256
JWT_ACCESS_TTL_MIN=15
JWT_REFRESH_TTL_DAYS=14
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
OPENAI_API_KEY=[你的密钥]
OPENAI_MODEL=gpt-4o-mini
BACKEND_CORS_ORIGINS=*
FILE_STORAGE_DIR=/app/data/uploads
MAX_FILE_SIZE_MB=25
```

---

### 步骤 4️⃣: 生成公开域名（3分钟）

1. 等待构建完成（约 3-5 分钟）
2. 点击后端服务 → **"Settings"** → **"Networking"**
3. 点击 **"Generate Domain"**
4. 复制域名（类似 `https://xxxx.up.railway.app`）

**验证部署**:
打开浏览器访问: `https://你的域名/health`

期望看到:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

### 步骤 5️⃣: 初始化数据库（30分钟）

#### 选项 A: 使用 Railway CLI ⭐ 推荐

```bash
# 安装 CLI
npm install -g @railway/cli

# 登录（会打开浏览器）
railway login

# 链接项目（选择刚创建的项目）
railway link

# 运行迁移
railway run alembic upgrade head

# 初始化信用卡数据（31张）
railway run python scripts/seed_credit_cards_extended.py
```

#### 选项 B: 修改启动命令（简单但慢）

1. 在 Railway 点击后端服务 → **"Settings"** → **"Deploy"**
2. 找到 **"Custom Start Command"**
3. 临时修改为:
   ```bash
   alembic upgrade head && python scripts/seed_credit_cards_extended.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
4. 点击 **"Redeploy"**（等待 5-8 分钟）
5. 成功后改回:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```

---

## ✅ 验证部署成功

### 1. 测试用户注册

```bash
curl -X POST https://你的域名/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456"}'
```

**成功响应**:
```json
{
  "access_token": "eyJ...",
  "user": {
    "email": "test@example.com",
    "tier": "analyst"
  }
}
```

### 2. 测试信用卡数据

```bash
# 使用上面返回的 access_token
TOKEN="复制上面的access_token"

curl -X GET https://你的域名/recommendations/cards?months=6 \
  -H "Authorization: Bearer $TOKEN"
```

**成功响应**: 返回推荐的信用卡列表

---

## 📋 完成检查清单

```
✅ Railway 项目已创建
✅ PostgreSQL 运行中
✅ Redis 运行中
✅ GitHub 仓库已部署
✅ 环境变量已配置（≥15个）
✅ 公开域名已生成: https://_____________
✅ /health 返回 healthy
✅ /docs 可访问
✅ 数据库迁移已完成
✅ 31张信用卡数据已初始化
✅ 用户注册测试通过
✅ API 认证测试通过
```

---

## 🎉 部署完成！

**后端 API URL**: `https://你的域名.up.railway.app`

### 下一步

1. **保存 API URL**: 添加到前端环境变量
2. **更新 CORS**: 前端部署后更新 `BACKEND_CORS_ORIGINS`
3. **测试完整流程**: 前端 + 后端集成测试

---

## 🆘 遇到问题？

查看详细文档:
- **完整指南**: `RAILWAY_DEPLOY.md`
- **检查清单**: `DEPLOYMENT_CHECKLIST.md`
- **环境变量模板**: `.env.production.template`

---

**总耗时**: ~60 分钟  
**成本**: $0-15/月 (Railway 免费额度 + 付费数据库)  
**下次部署**: 只需 5 分钟（已有配置）

🚀 恭喜！后端部署成功！
