# 🚀 CreditSphere 后端部署到 Railway 指南

**目标**: 将 FastAPI 后端 + PostgreSQL + Redis 部署到 Railway  
**预计时间**: 60 分钟  
**日期**: 2025-11-06

---

## 📋 前置准备

### 必需账号和工具
- ✅ Railway 账号: https://railway.app/
- ✅ GitHub 账号（推荐通过 GitHub 登录）
- ✅ OpenAI API Key（用于 AI 分类功能）
- ✅ 本地 Git 仓库已推送到 GitHub

### 检查清单
```bash
# 1. 确认项目已推送到 GitHub
git remote -v
git status

# 2. 确认 Dockerfile 存在
ls backend/Dockerfile

# 3. 确认必要文件存在
ls railway.toml
ls backend/requirements.txt
```

---

## 🎯 部署步骤

### Step 1: 创建 Railway 项目并添加数据库

#### 1.1 创建新项目
1. 访问 https://railway.app/dashboard
2. 点击 **"New Project"**
3. 选择 **"Empty Project"**
4. 项目命名: `creditsphere` 或 `financial-advisor`

#### 1.2 添加 PostgreSQL 数据库
1. 在项目中点击 **"+ New"**
2. 选择 **"Database"** → **"Add PostgreSQL"**
3. 等待数据库创建完成（约 30 秒）
4. 数据库会自动生成以下变量：
   - `DATABASE_URL` (内部连接)
   - `DATABASE_PUBLIC_URL` (外部连接)
   - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

📝 **记录**:
```
PostgreSQL Database Name: [自动生成]
Internal DATABASE_URL: [复制保存]
```

#### 1.3 添加 Redis
1. 点击 **"+ New"**
2. 选择 **"Database"** → **"Add Redis"**
3. 等待 Redis 创建完成（约 20 秒）
4. Redis 会自动生成：
   - `REDIS_URL` (内部连接)
   - `REDIS_PUBLIC_URL` (外部连接)

📝 **记录**:
```
Redis Instance Name: [自动生成]
Internal REDIS_URL: [复制保存]
```

---

### Step 2: 部署 FastAPI 后端应用

#### 2.1 连接 GitHub 仓库
1. 在项目中点击 **"+ New"**
2. 选择 **"GitHub Repo"**
3. 授权 Railway 访问你的 GitHub（如果首次使用）
4. 选择仓库: `你的用户名/financial-advisor`
5. Railway 会自动检测 `railway.toml` 和 `Dockerfile`

#### 2.2 配置构建设置
1. 点击部署的服务 → **"Settings"**
2. **Root Directory**: 保持为根目录 `/`
3. **Dockerfile Path**: 确认为 `backend/Dockerfile`
4. **Build Command**: 留空（使用 Dockerfile）
5. **Start Command**: 
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```

#### 2.3 配置环境变量
点击 **"Variables"** 标签，添加以下变量：

**基础配置**:
```bash
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC
PORT=8000
```

**安全密钥** (生成随机字符串):
```bash
# 生成 SECRET_KEY (在本地运行)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成 ENCRYPTION_KEY (在本地运行)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

添加到 Railway:
```bash
SECRET_KEY=[粘贴生成的值]
ENCRYPTION_KEY=[粘贴生成的值]
JWT_ALG=HS256
JWT_ACCESS_TTL_MIN=15
JWT_REFRESH_TTL_DAYS=14
```

**数据库连接** (使用 Railway 变量引用):
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

**API 密钥**:
```bash
OPENAI_API_KEY=sk-你的OpenAI密钥
OPENAI_MODEL=gpt-4o-mini
```

**CORS 配置** (部署后更新):
```bash
BACKEND_CORS_ORIGINS=https://你的前端域名.vercel.app
# 或临时允许所有（仅测试用）
# BACKEND_CORS_ORIGINS=*
```

**文件存储**:
```bash
FILE_STORAGE_DIR=/app/data/uploads
MAX_FILE_SIZE_MB=25
```

**速率限制**:
```bash
RATE_LIMIT_FREE=60/minute
RATE_LIMIT_OPTIMIZER=240/minute
RATE_LIMIT_AUTOPILOT=600/minute
```

**AI 配额**:
```bash
AI_QUOTA_FREE=100
AI_QUOTA_OPTIMIZER=1000
AI_QUOTA_AUTOPILOT=3000
```

**Stripe** (可选，暂时留空):
```bash
STRIPE_SECRET_KEY=
STRIPE_PUBLIC_KEY=
STRIPE_WEBHOOK_SECRET=
```

---

### Step 3: 部署并获取 URL

#### 3.1 触发部署
1. 环境变量配置完成后，点击 **"Deploy"** 或等待自动部署
2. 查看 **"Deployments"** 标签，观察构建日志
3. 构建时间约 3-5 分钟

#### 3.2 配置公开访问
1. 部署成功后，点击 **"Settings"** → **"Networking"**
2. 点击 **"Generate Domain"**
3. Railway 会生成一个公开域名，格式如:
   ```
   https://creditsphere-backend-production.up.railway.app
   ```

📝 **记录后端 URL**:
```
Backend API URL: [复制保存]
```

#### 3.3 验证部署
在浏览器访问以下端点：

✅ **健康检查**:
```
https://你的域名.up.railway.app/health
```
期望响应:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

✅ **API 文档** (确认可访问):
```
https://你的域名.up.railway.app/docs
```

---

### Step 4: 数据库初始化

#### 4.1 运行数据库迁移

**方法 A: 通过 Railway CLI** (推荐)
```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 链接到项目
railway link

# 连接到后端服务
railway run --service=backend bash

# 在容器内运行迁移
alembic upgrade head

# 退出
exit
```

**方法 B: 通过一次性 Deployment Command**
1. 在 Railway 项目中，点击后端服务
2. **Settings** → **Deploy** → **Custom Start Command**
3. 临时修改为:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
4. 点击 **"Redeploy"**
5. 部署成功后，改回原命令

#### 4.2 初始化信用卡数据

**方法 A: 通过 Railway CLI**
```bash
railway run --service=backend bash

# 初始化 11 张基础卡片
python scripts/seed_credit_cards.py

# 初始化 31 张扩展卡片
python scripts/seed_credit_cards_extended.py

exit
```

**方法 B: 添加初始化脚本到 Dockerfile**
在 `backend/Dockerfile` 的 CMD 前添加：
```dockerfile
# Copy scripts
COPY scripts ./scripts
COPY alembic.ini .
COPY alembic ./alembic

# Run migrations and seed on startup (optional)
# CMD ["sh", "-c", "alembic upgrade head && python scripts/seed_credit_cards_extended.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2"]
```

---

### Step 5: 验证完整部署

#### 5.1 测试 API 端点

**注册新用户**:
```bash
curl -X POST https://你的域名.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'
```

期望响应:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "tier": "analyst"
  }
}
```

**获取信用卡推荐**:
```bash
# 保存 access_token
TOKEN="你的access_token"

curl -X GET "https://你的域名.up.railway.app/recommendations/cards?months=6" \
  -H "Authorization: Bearer $TOKEN"
```

**检查数据库数据**:
```bash
curl -X GET https://你的域名.up.railway.app/credit-cards \
  -H "Authorization: Bearer $TOKEN"
```

应该返回 31 张信用卡数据。

#### 5.2 测试 CORS

从前端域名发起请求，确认 CORS 正常工作：
```javascript
// 在浏览器控制台测试
fetch('https://你的域名.up.railway.app/health')
  .then(res => res.json())
  .then(console.log)
```

如果出现 CORS 错误，检查 `BACKEND_CORS_ORIGINS` 环境变量。

---

## 📊 部署检查清单

### 基础设施
- [ ] PostgreSQL 数据库创建成功
- [ ] Redis 实例创建成功
- [ ] 后端服务部署成功
- [ ] 公开域名生成并可访问

### 环境变量
- [ ] APP_ENV=production
- [ ] SECRET_KEY (已生成)
- [ ] ENCRYPTION_KEY (已生成)
- [ ] DATABASE_URL (已引用)
- [ ] REDIS_URL (已引用)
- [ ] OPENAI_API_KEY (已设置)
- [ ] BACKEND_CORS_ORIGINS (已配置)

### 数据库
- [ ] 迁移已运行 (`alembic upgrade head`)
- [ ] 信用卡数据已初始化（31张）
- [ ] 数据库连接正常

### API 测试
- [ ] `/health` 返回 200
- [ ] `/docs` 可访问
- [ ] 用户注册成功
- [ ] 用户登录成功
- [ ] Token 认证正常
- [ ] 信用卡推荐 API 正常

---

## 🔧 故障排查

### 问题 1: 构建失败
**症状**: Dockerfile 构建错误

**解决方案**:
1. 检查 `railway.toml` 中的 `dockerfilePath`
2. 确认 `backend/requirements.txt` 存在
3. 查看构建日志中的具体错误

### 问题 2: 数据库连接失败
**症状**: `/health` 返回 database: disconnected

**解决方案**:
1. 确认 `DATABASE_URL` 格式正确
2. 检查是否使用了 `${{Postgres.DATABASE_URL}}`
3. 在 Railway Dashboard 检查 PostgreSQL 服务状态

### 问题 3: 迁移失败
**症状**: `alembic upgrade head` 报错

**解决方案**:
```bash
# 检查当前迁移状态
railway run --service=backend alembic current

# 重置并重新迁移（谨慎！）
railway run --service=backend alembic downgrade base
railway run --service=backend alembic upgrade head
```

### 问题 4: CORS 错误
**症状**: 前端无法访问后端 API

**解决方案**:
1. 更新 `BACKEND_CORS_ORIGINS` 包含前端域名
2. 临时设置为 `*` 测试
3. 确认前端使用 HTTPS

### 问题 5: 文件上传失败
**症状**: 上传接口返回错误

**解决方案**:
1. Railway 提供临时文件系统，重启会清空
2. 考虑使用 S3/Cloudinary 等外部存储
3. 或使用 Railway Volumes（需要付费计划）

---

## 💰 成本估算

### Railway 免费计划
- ✅ $5/月 免费额度
- ✅ PostgreSQL Starter: ~$5/月
- ✅ Redis Starter: ~$5/月  
- ✅ Web Service: 按使用量计费

**总计**: 约 $10-15/月（超出免费额度后）

### 优化建议
1. 使用 Railway 免费额度（$5）
2. 考虑 Hobby Plan ($5/月) + 免费数据库
3. 生产环境建议 Pro Plan ($20/月)

---

## 📝 后续步骤

### 立即完成
1. [ ] 复制后端 URL 到前端 `.env` 文件
2. [ ] 更新 CORS 允许的前端域名
3. [ ] 测试完整的注册→登录→API 调用流程

### Phase 2 准备
1. [ ] 配置 Stripe Webhook URL
2. [ ] 设置自定义域名（可选）
3. [ ] 配置 Sentry 错误监控
4. [ ] 设置 S3/Cloudinary 文件存储

---

## 🎉 完成确认

部署成功后，你应该有：

1. ✅ **后端 API URL**: `https://xxxx.up.railway.app`
2. ✅ **数据库**: PostgreSQL + Redis 运行中
3. ✅ **健康检查**: `/health` 返回正常
4. ✅ **数据初始化**: 31 张信用卡数据
5. ✅ **API 文档**: `/docs` 可访问
6. ✅ **CORS 配置**: 允许前端访问

---

## 📄 交付清单

请在完成后提供以下信息：

```
✅ Railway 项目名称: _________________
✅ 后端 API URL: https://_________________
✅ PostgreSQL 状态: [ ] 运行中
✅ Redis 状态: [ ] 运行中
✅ 健康检查截图: [ ] 已截图
✅ API 文档访问: [ ] 可访问
✅ 数据库迁移: [ ] 已完成
✅ 信用卡数据: [ ] 31张已初始化
```

---

**预计完成时间**: 60 分钟  
**难度**: 中等  
**优先级**: 高

祝部署顺利！🚀
