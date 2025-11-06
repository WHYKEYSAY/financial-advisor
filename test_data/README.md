# CreditSphere 测试数据

本目录包含所有用于测试的文件和脚本。

## 📁 目录结构

```
test_data/
├── statements/          # 测试账单文件
│   ├── MBNA.pdf        # MBNA 信用卡账单
│   ├── RBC.pdf         # RBC 信用卡账单
│   ├── PC.pdf          # PC Financial 账单
│   ├── CIBC.pdf        # CIBC 银行账单
│   └── *.csv           # CSV 格式账单
│
├── test_all_apis.py    # 完整 API 测试脚本
└── README.md           # 本文件
```

## 🧪 测试文件说明

### 账单文件 (statements/)
- **MBNA.pdf**: MBNA World Elite Mastercard 账单，包含 33 笔交易
- **RBC.pdf**: RBC Visa 账单，包含 5 笔交易
- **PC.pdf**: PC Financial Mastercard 账单，包含 7 笔交易
- **CIBC.pdf**: CIBC 银行账户账单，包含转账记录
- **sample_statement.csv**: CSV 格式示例账单

### 测试脚本
- **test_all_apis.py**: 综合 API 测试脚本
  - 测试认证流程（注册/登录/刷新/登出）
  - 测试文件上传和解析
  - 测试交易查询和统计
  - 测试 Quota 管理
  - 自动创建测试用户并清理

## 🚀 运行测试

### 运行完整测试套件
```bash
python test_data/test_all_apis.py
```

### 使用测试账单上传
```bash
# 通过 Swagger UI: http://localhost:8000/docs
# 或使用 curl
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_data/statements/MBNA.pdf"
```

## 📝 测试数据维护

### 添加新的测试账单
1. 将 PDF/CSV 文件放到 `statements/` 目录
2. 使用匿名或脱敏数据
3. 更新本 README 说明文件内容

### 清理测试数据
```bash
# 删除所有上传的文件（Docker 容器内）
docker exec creditsphere-backend rm -rf /data/uploads/*

# 重置数据库（谨慎使用！）
docker exec creditsphere-backend alembic downgrade base
docker exec creditsphere-backend alembic upgrade head
```

## ⚠️ 注意事项

1. **不要提交真实账单**: 所有测试文件应使用脱敏或虚构数据
2. **定期更新**: 测试文件格式应与实际银行账单保持同步
3. **版本控制**: 重要的测试文件应纳入 Git 管理
4. **隔离环境**: 测试应在开发环境进行，避免污染生产数据

## 🔧 故障排查

如果测试失败，检查：
- [ ] Docker 容器是否运行：`docker ps`
- [ ] 后端是否启动：`curl http://localhost:8000/health`
- [ ] 数据库连接是否正常
- [ ] 测试文件路径是否正确
- [ ] API Token 是否有效

---

最后更新：2025-11-06
