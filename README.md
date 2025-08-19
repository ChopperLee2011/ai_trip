# 智能旅游推荐系统 MVP

基于用户选择的旅游目的地和时间，结合小红书账号分析，提供个性化旅游推荐的系统。

## 技术栈

### 前端
- Next.js 14
- React
- Tailwind CSS
- TypeScript

### 后端
- Python 3.9+
- CrewAI (多智能体框架)
- FastAPI
- DeepSeek LLM

## 功能特性

- 🌍 基于目的地和时间的旅游推荐
- 📱 小红书账号偏好分析（可选）
- 🤖 多智能体协作生成个性化推荐
- 💡 智能行程规划
- 📊 推荐结果可视化

## 快速开始

### 环境准备

1. 克隆项目
```bash
git clone <repository-url>
cd trip
```

2. 设置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，添加 DeepSeek API Key
```

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000 查看应用

## API 接口

### POST /api/recommend
生成旅游推荐

**请求体:**
```json
{
  "destination": "日本东京",
  "travel_dates": {
    "start": "2024-03-01",
    "end": "2024-03-07"
  },
  "xiaohongshu_account": "optional_username",
  "preferences": {
    "budget": "medium",
    "travel_style": "cultural"
  }
}
```

**响应:**
```json
{
  "recommendations": {
    "itinerary": [...],
    "restaurants": [...],
    "attractions": [...],
    "accommodations": [...]
  },
  "analysis": "基于您的偏好分析..."
}
```

## 项目结构

```
trip/
├── frontend/          # Next.js 前端应用
├── backend/           # Python 后端服务
├── .env.example       # 环境变量模板
└── README.md         # 项目说明
```

## 使用说明

### 1. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，添加您的 DeepSeek API Key
```

### 2. 一键启动（推荐）
```bash
./start.sh
```

### 3. 手动启动

**后端启动:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**前端启动:**
```bash
cd frontend
npm install
npm run dev
```

### 4. 测试系统
```bash
python3 test_api.py
```

## 系统架构

### CrewAI 多智能体架构
- **目的地专家**: 分析目的地特色、景点、美食等信息
- **偏好分析师**: 基于小红书账号分析用户旅行偏好
- **行程规划师**: 制定详细的日程安排和路线规划
- **协调员**: 整合所有信息，生成最终推荐

### 技术特色
- 🤖 多智能体协作，专业分工
- 🧠 DeepSeek大模型驱动
- 📱 响应式Web界面
- 🔄 实时API交互
- 📊 结构化推荐结果

## 开发计划

- [x] 项目初始化和架构设计
- [x] 后端 CrewAI agents 实现
- [x] DeepSeek LLM 集成
- [x] 前端界面开发
- [x] API 接口实现
- [x] 基础功能测试
- [ ] 小红书真实数据集成
- [ ] 推荐算法优化
- [ ] 用户反馈系统
- [ ] 部署和监控
