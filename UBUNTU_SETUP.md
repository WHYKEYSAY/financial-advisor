# Ubuntu 22.04 Setup Complete ✅

**Date:** November 1, 2025  
**WSL Version:** WSL2  
**Distribution:** Ubuntu 22.04 LTS

---

## ✅ Installed Packages

### System Tools
- ✅ **Build Essential** - C/C++ compiler and development tools
- ✅ **Git** - Version 2.34.1
- ✅ **Vim/Nano** - Text editors
- ✅ **Curl/Wget** - Download tools

### Programming Languages
- ✅ **Node.js** - Version 20.19.5 (LTS)
- ✅ **npm** - Version 10.8.2
- ✅ **Python 3.11** - Version 3.11.14
- ✅ **Python 3.11 venv** - Virtual environment support
- ✅ **Python 3.11 dev** - Development headers

### Container & Deployment
- ✅ **Docker** - Version 28.2.2
- ✅ **Docker Compose** - Version 1.29.2
- ✅ **Docker Service** - Running and configured

---

## 🚀 Quick Start Commands

### Access Ubuntu
```powershell
# From Windows PowerShell
wsl -d Ubuntu-22.04
```

### Navigate to Project
```bash
# Inside Ubuntu
cd /mnt/c/Users/whyke/financial-advisor
```

### Check Versions
```bash
node --version    # v20.19.5
npm --version     # 10.8.2
python3.11 --version  # Python 3.11.14
docker --version  # Docker version 28.2.2
docker-compose --version  # 1.29.2
```

### Start Docker Service
```bash
sudo service docker start
sudo service docker status
```

---

## 📋 User Configuration

**Username:** keke  
**Groups:** keke, docker  
**Home Directory:** /home/keke

---

## 🔨 Next Steps - Build CreditSphere

### 1. Start Docker Service (if not running)
```bash
sudo service docker start
```

### 2. Navigate to Project
```bash
cd /mnt/c/Users/whyke/financial-advisor
```

### 3. Build Docker Images
```bash
docker compose build
```

### 4. Start All Services
```bash
docker compose up -d
```

### 5. Check Services Status
```bash
docker compose ps
docker compose logs backend
docker compose logs frontend
```

### 6. Access Application
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000 (when ready)

### 7. Setup Alembic (Database Migrations)
```bash
# Inside backend container
docker compose exec backend alembic init alembic

# Edit alembic/env.py to import models
# Then create initial migration
docker compose exec backend alembic revision --autogenerate -m "init schema"

# Apply migration
docker compose exec backend alembic upgrade head
```

---

## 🛠️ Development Workflow

### Working with Backend
```bash
# View logs
docker compose logs -f backend

# Enter backend container
docker compose exec backend bash

# Run Python shell
docker compose exec backend python

# Install new Python package
docker compose exec backend pip install package-name
# Then add to requirements.txt
```

### Working with Frontend (when initialized)
```bash
# View logs
docker compose logs -f frontend

# Enter frontend container
docker compose exec frontend bash

# Install npm package
docker compose exec frontend npm install package-name
```

### Database Access
```bash
# Connect to PostgreSQL
docker compose exec db psql -U app -d fin

# Run SQL query
docker compose exec db psql -U app -d fin -c "SELECT * FROM users;"
```

### Redis Access
```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Check keys
docker compose exec redis redis-cli KEYS '*'
```

---

## 🐛 Troubleshooting

### Docker not starting
```bash
sudo service docker start
sudo service docker status
```

### Permission denied on docker commands
```bash
# You need to logout and login again for docker group to take effect
# Or prefix commands with sudo temporarily
sudo docker ps
```

### Cannot connect to Docker daemon
```bash
# Ensure Docker service is running
sudo service docker status

# Restart Docker
sudo service docker restart
```

### Port already in use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Stop the service using that port or change port in docker-compose.yml
```

---

## 📦 Package Management

### Ubuntu Packages
```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade

# Install new package
sudo apt install package-name
```

### Python Packages (in container)
```bash
# Inside container
pip install package-name

# Or from host
docker compose exec backend pip install package-name
```

### Node Packages (in container)
```bash
# Inside container
npm install package-name

# Or from host
docker compose exec frontend npm install package-name
```

---

## 🔐 Security Notes

**IMPORTANT:** After setup is complete, please change your Ubuntu password:
```bash
passwd
```

---

## ✨ Ubuntu is Ready!

Your development environment is fully configured and ready to build CreditSphere! 🚀

All required tools are installed:
- ✅ Modern Node.js for frontend
- ✅ Python 3.11 for backend
- ✅ Docker for containerization
- ✅ Git for version control

**Next Command to Run:**
```bash
cd /mnt/c/Users/whyke/financial-advisor
docker compose build
docker compose up -d
```
