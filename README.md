# 青禾招聘 GreenSeed

**以青春为籽，启职场新章**

基于 FastAPI + Vue 3 + Supabase 构建的校园招聘系统，作为本科 Python 课程大作业。

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router 4 |
| 后端 | FastAPI（Vercel Serverless） |
| 数据库 | Supabase PostgreSQL + Row Level Security |
| 认证 | Supabase Auth + JWT |
| 图表 | Chart.js（vue-chartjs） |
| 部署 | Vercel |

---

## 功能概览

### 求职者
- 浏览、搜索、筛选职位（关键词 / 城市 / 薪资 / 类型）
- 查看职位详情与公司主页
- 一键投递简历，附求职信
- 追踪投递历史与申请状态

### 招聘方
- 创建公司主页
- 发布 / 编辑 / 关闭职位
- 查看候选人申请，在线更新状态（审核中 → 录用 / 拒绝）

### 管理员
- 用户管理（查看、变更角色、删除）
- 平台数据看板：职位分类分布（饼图）、每日新增申请（折线图）、各公司职位数（柱状图）

---

## 本地运行

**前提条件**：Node.js 18+、Python 3.11+、已配置 `.env`（参考 `.env.example`）

```bash
# 后端
pip install -r requirements.txt
uvicorn api.index:app --reload        # http://localhost:8000

# 前端（另开终端）
cd frontend
npm install
npm run dev                           # http://localhost:5173
```

前端开发服务器已配置代理，`/api/*` 请求自动转发到后端。

## 数据库初始化

在 [Supabase SQL 编辑器](https://supabase.com/dashboard/project/hvjtrjqhsgoordtolwqa/sql/new) 中执行 `database/schema.sql`，完成建表与 RLS 策略配置。

---

## 项目结构

```
GreenSeed/
├── api/                  # FastAPI 后端
│   ├── index.py          # 应用入口（Vercel 导出 app）
│   ├── deps.py           # 依赖注入（认证、Supabase 客户端）
│   ├── models/schemas.py # Pydantic 数据模型
│   └── routers/          # auth / jobs / applications / companies / admin
├── frontend/             # Vue 3 前端
│   └── src/
│       ├── assets/main.css   # OKLCH 设计 Token 系统
│       ├── views/            # 各角色页面
│       ├── stores/auth.ts    # Pinia 认证状态
│       └── router/index.ts   # 路由与权限守卫
├── database/
│   ├── schema.sql        # 建表 + RLS 策略
│   └── apply_schema.py   # 可选：Python 直连执行 schema
├── vercel.json           # Vercel 部署配置
└── .env.example          # 环境变量示例
```

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `SUPABASE_URL` | Supabase 项目 URL |
| `SUPABASE_ANON_KEY` | 匿名公钥 |
| `SUPABASE_SERVICE_KEY` | 服务角色密钥（后端专用） |
| `JWT_SECRET` | JWT 验证密钥（来自 Supabase 项目设置） |
| `FRONTEND_URL` | 前端地址（CORS 白名单） |
