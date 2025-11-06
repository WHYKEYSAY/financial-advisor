# ✅ Railway 部署快速检查清单

## 🚀 部署前准备 (10分钟)

### 1. 本地准备
```bash
# 生成生产环境密钥
python generate_production_secrets.py

# 复制输出的环境变量，保存到安全地方
# 推荐使用: 1Password, LastPass, 或本地加密文件

# 确认项目已推送到 GitHub
git status
git push origin main
```

- [ ] 密钥已生成并保存
- [ ] 代码已推送到 GitHub
- [ ] OpenAI API Key 准备就绪

---

## 🏗️ Railway 部署 (30分钟)

### Step 1: 创建项目 (5分钟)
1. 访问 https://railway.app/dashboard
2. 点击 **"New Project"** → **"Empty Project"**
3. 项目命名: `creditsphere` 或 `financial-advisor`

- [ ] Railway 项目已创建

### Step 2: 添加数据库 (5分钟)
1. **PostgreSQL**: 
   - 点击 **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - 等待创建完成（~30秒）
   
2. **Redis**:
   - 点击 **"+ New"** → **"Database"** → **"Add Redis"**
   - 等待创建完成（~20秒）

- [ ] PostgreSQL 数据库运行中
- [ ] Redis 实例运行中

### Step 3: 部署后端应用 (10分钟)
1. 点击 **"+ New"** → **"GitHub Repo"**
2. 选择仓库: `你的用户名/financial-advisor`
3. Railway 自动检测 `railway.toml` 并开始构建

**配置环境变量**:
1. 点击后端服务 → **"Variables"**
2. 粘贴 `generate_production_secrets.py` 生成的所有变量
3. 特别注意替换:
   - `OPENAI_API_KEY=你的真实密钥`
   - `BACKEND_CORS_ORIGINS=https://你的前端域名`

- [ ] GitHub 仓库已连接
- [ ] 环境变量已配置（至少 15 个）
- [ ] 构建成功完成

### Step 4: 生成公开域名 (2分钟)
1. 点击后端服务 → **"Settings"** → **"Networking"**
2. 点击 **"Generate Domain"**
3. 复制生成的域名，格式如:
   ```
   https://creditsphere-production-XXXX.up.railway.app
   ```

- [ ] 公开域名已生成
- [ ] 域名已保存

### Step 5: 验证部署 (5分钟)
访问以下 URL 确认：

1. **健康检查**: `https://你的域名/health`
   ```json
   {"status": "healthy", "database": "connected", "redis": "connected"}
   ```

2. **API 文档**: `https://你的域名/docs`
   - 应该看到 Swagger UI 界面

- [ ] `/health` 返回正常
- [ ] `/docs` 可访问
- [ ] 数据库和 Redis 连接成功

---

## 🗄️ 数据库初始化 (15分钟)

### 方法 A: 使用 Railway CLI (推荐)

```bash
# 1. 安装 CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 链接项目
railway link

# 4. 运行迁移
railway run --service=backend alembic upgrade head

# 5. 初始化信用卡数据
railway run --service=backend python scripts/seed_credit_cards_extended.py
```

- [ ] Railway CLI 已安装
- [ ] 数据库迁移已运行
- [ ] 31张信用卡数据已初始化

### 方法 B: 修改启动命令（临时方案）

1. 点击后端服务 → **"Settings"** → **"Deploy"**
2. **Custom Start Command** 修改为:
   ```bash
   alembic upgrade head && python scripts/seed_credit_cards_extended.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```
3. 点击 **"Redeploy"**
4. 成功后改回原命令:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```

- [ ] 启动命令已临时修改
- [ ] 重新部署成功
- [ ] 启动命令已恢复

---

## 🧪 API 测试 (10分钟)

### 1. 测试用户注册
```bash
curl -X POST https://你的域名/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'
```

期望返回: `access_token`, `refresh_token`, `user`

- [ ] 用户注册成功

### 2. 测试信用卡推荐
```bash
TOKEN="你的access_token"

curl -X GET "https://你的域名/recommendations/cards?months=6" \
  -H "Authorization: Bearer $TOKEN"
```

期望返回: 推荐的信用卡列表（包含 NAV 计算）

- [ ] 信用卡推荐 API 正常

### 3. 验证数据初始化
```bash
curl -X GET https://你的域名/credit-cards \
  -H "Authorization: Bearer $TOKEN"
```

期望返回: 31 张信用卡数据

- [ ] 数据库包含 31 张信用卡

---

## 📝 最终交付清单

```
✅ Railway 项目名称: _________________
✅ 后端 API URL: https://_________________
✅ PostgreSQL 状态: [ ] 运行中
✅ Redis 状态: [ ] 运行中
✅ 环境变量数量: [ ] ≥15 个
✅ /health 状态: [ ] healthy
✅ /docs 访问: [ ] 可访问
✅ 数据库迁移: [ ] 已完成
✅ 信用卡数据: [ ] 31张已初始化
✅ 用户注册测试: [ ] 成功
✅ API 认证测试: [ ] 成功
✅ 推荐引擎测试: [ ] 成功
```

---

## 🎯 后续步骤

1. **更新前端配置**:
   ```bash
   # frontend/.env.production
   NEXT_PUBLIC_BACKEND_URL=https://你的Railway域名
   ```

2. **更新 CORS**:
   - 前端部署完成后，更新 Railway 的 `BACKEND_CORS_ORIGINS` 变量

3. **测试完整流程**:
   - 前端 → 后端 API 调用
   - 用户注册 → 登录 → Dashboard

---

## 🚨 常见问题

### Q: 构建失败
**A**: 检查 `railway.toml` 和 `backend/Dockerfile` 路径

### Q: 数据库连接失败
**A**: 确认使用 `${{Postgres.DATABASE_URL}}` 引用

### Q: CORS 错误
**A**: 确认 `BACKEND_CORS_ORIGINS` 包含前端域名（HTTPS）

### Q: 迁移失败
**A**: 使用 Railway CLI 手动运行 `alembic upgrade head`

---

**预计总时间**: 60 分钟  
**难度**: 中等  
**成功率**: 95%+ (按步骤操作)

🎉 祝部署顺利！
