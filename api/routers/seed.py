"""
一次性数据填充路由 — 创建演示账号及模拟数据。
调用方式：POST /api/seed?token=greenseed-init-2024
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from api.deps import get_supabase_admin

router = APIRouter()

_TOKEN = "greenseed-init-2024"

# ── 演示用户 ──────────────────────────────────────────────────────
_USERS = [
    {
        "email":    "seeker@greenseed.dev",
        "password": "GreenSeed2024!",
        "name":     "张小明",
        "role":     "seeker",
        "bio":      "应届本科毕业生，主修计算机科学，求职方向为前端开发与产品方向，有字节跳动实习经历。",
        "skills":   ["Vue.js", "TypeScript", "Python", "Figma", "数据分析"],
        "education": "北京大学 · 计算机科学与技术 · 2024届",
    },
    {
        "email":    "recruiter@greenseed.dev",
        "password": "GreenSeed2024!",
        "name":     "李建国",
        "role":     "recruiter",
        "bio":      "青禾科技 & 绿芽传媒招聘负责人，专注发掘优质应届生人才，5年校招经验。",
        "skills":   [],
        "education": "",
    },
    {
        "email":    "admin@greenseed.dev",
        "password": "GreenSeed2024!",
        "name":     "王管理",
        "role":     "admin",
        "bio":      "平台管理员。",
        "skills":   [],
        "education": "",
    },
]


def _get_or_create_user(db: Client, u: dict) -> str:
    """创建 auth 用户；若已存在则直接返回其 ID。"""
    try:
        res = db.auth.admin.create_user({
            "email":         u["email"],
            "password":      u["password"],
            "email_confirm": True,          # 跳过邮件验证
        })
        return str(res.user.id)
    except Exception:
        # 用户已存在 — 从列表中查找
        users = db.auth.admin.list_users()
        found = next((x for x in users if x.email == u["email"]), None)
        if found:
            return str(found.id)
        raise


# ── 种子数据 endpoint ────────────────────────────────────────────

@router.post("")
async def seed(
    token: str = Query(..., description="初始化密钥"),
    db:    Annotated[Client, Depends(get_supabase_admin)] = None,
):
    if token != _TOKEN:
        raise HTTPException(403, "无效 token")

    result: dict = {"users": {}, "companies": [], "jobs": [], "applications": []}

    # ── 1. 用户 ──────────────────────────────────────────────────
    uid: dict[str, str] = {}   # role -> user_id
    for u in _USERS:
        user_id = _get_or_create_user(db, u)
        uid[u["role"]] = user_id
        db.table("profiles").upsert({
            "id":        user_id,
            "email":     u["email"],
            "name":      u["name"],
            "role":      u["role"],
            "bio":       u["bio"],
            "skills":    u["skills"],
            "education": u["education"],
        }).execute()
        result["users"][u["role"]] = u["email"]

    recruiter_id = uid["recruiter"]
    seeker_id    = uid["seeker"]

    # ── 2. 公司 ──────────────────────────────────────────────────
    companies_data = [
        {
            "recruiter_id": recruiter_id,
            "name":         "青禾科技有限公司",
            "description":  "青禾科技专注于互联网产品研发，旗下拥有青禾招聘、青禾云等多款产品，是一家高速成长的科技公司。",
            "industry":     "互联网·软件",
            "location":     "北京",
            "website":      "https://greenseed.dev",
            "verified":     True,
        },
        {
            "recruiter_id": recruiter_id,
            "name":         "绿芽传媒集团",
            "description":  "绿芽传媒是一家专注于年轻人内容营销与品牌推广的传媒公司，服务超过 500 家品牌客户。",
            "industry":     "市场·运营",
            "location":     "上海",
            "website":      "https://lvya-media.com",
            "verified":     True,
        },
    ]

    company_ids: list[str] = []
    for c in companies_data:
        existing = (
            db.table("companies")
            .select("id")
            .eq("recruiter_id", recruiter_id)
            .eq("name", c["name"])
            .execute()
        )
        if existing.data:
            cid = existing.data[0]["id"]
        else:
            res = db.table("companies").insert(c).execute()
            cid = res.data[0]["id"]
        company_ids.append(cid)
        result["companies"].append(c["name"])

    c1, c2 = company_ids[0], company_ids[1]

    # ── 3. 职位 ──────────────────────────────────────────────────
    jobs_data = [
        # 青禾科技
        {
            "company_id":   c1,
            "title":        "前端开发工程师",
            "description":  "负责公司核心产品的前端研发工作，参与需求分析、技术方案制定和代码实现。与产品、设计、后端紧密协作，推动产品快速迭代。",
            "requirements": "本科及以上学历，计算机相关专业；熟练掌握 Vue3 / React，了解 TypeScript；有大型项目经验优先。",
            "salary_min":   15000,
            "salary_max":   25000,
            "job_type":     "full",
            "location":     "北京",
            "category":     "互联网·软件",
            "tags":         ["Vue3", "TypeScript", "前端架构"],
            "status":       "open",
        },
        {
            "company_id":   c1,
            "title":        "Python 后端工程师",
            "description":  "参与公司后端服务的设计、开发和维护，负责 API 开发、数据库优化和系统架构改进。",
            "requirements": "熟练掌握 Python，了解 FastAPI / Django；有数据库设计经验；英文读写能力良好。",
            "salary_min":   18000,
            "salary_max":   30000,
            "job_type":     "full",
            "location":     "北京",
            "category":     "互联网·软件",
            "tags":         ["Python", "FastAPI", "PostgreSQL"],
            "status":       "open",
        },
        {
            "company_id":   c1,
            "title":        "产品经理（实习）",
            "description":  "协助产品经理进行需求调研、竞品分析、原型设计和项目跟进，深度参与产品从 0 到 1 的全流程。",
            "requirements": "本科在读，产品/计算机相关专业优先；逻辑思维清晰；熟悉 Figma/Axure；每周可实习 4 天以上。",
            "salary_min":   5000,
            "salary_max":   8000,
            "job_type":     "intern",
            "location":     "北京",
            "category":     "互联网·软件",
            "tags":         ["产品规划", "原型设计", "数据驱动"],
            "status":       "open",
        },
        # 绿芽传媒
        {
            "company_id":   c2,
            "title":        "内容运营专员",
            "description":  "负责公司社交媒体账号运营（微博、微信公众号、小红书等），策划并执行品牌内容，提升用户互动率。",
            "requirements": "本科及以上，文案写作能力强；熟悉主流内容平台；有运营经验优先。",
            "salary_min":   8000,
            "salary_max":   12000,
            "job_type":     "full",
            "location":     "上海",
            "category":     "市场·运营",
            "tags":         ["内容运营", "小红书", "品牌策划"],
            "status":       "open",
        },
        {
            "company_id":   c2,
            "title":        "UI/UX 设计师",
            "description":  "负责公司旗下各品牌视觉设计工作，包括 App 界面、活动海报、品牌物料等，保证视觉一致性。",
            "requirements": "本科及以上，设计相关专业；精通 Figma / Illustrator；有完整项目作品集。",
            "salary_min":   12000,
            "salary_max":   18000,
            "job_type":     "full",
            "location":     "上海",
            "category":     "设计·创意",
            "tags":         ["Figma", "UI设计", "品牌视觉"],
            "status":       "open",
        },
        {
            "company_id":   c2,
            "title":        "品牌营销实习生",
            "description":  "协助市场团队策划品牌推广活动，收集市场数据，撰写营销报告，协调内外部资源推进项目落地。",
            "requirements": "本科在读，市场营销/传媒/广告等相关专业；沟通能力强；每周可实习 3 天以上。",
            "salary_min":   3000,
            "salary_max":   5000,
            "job_type":     "intern",
            "location":     "上海",
            "category":     "市场·运营",
            "tags":         ["市场营销", "活动策划", "品牌推广"],
            "status":       "open",
        },
    ]

    job_ids: list[str] = []
    for j in jobs_data:
        existing = (
            db.table("jobs")
            .select("id")
            .eq("company_id", j["company_id"])
            .eq("title", j["title"])
            .execute()
        )
        if existing.data:
            jid = existing.data[0]["id"]
        else:
            res = db.table("jobs").insert(j).execute()
            jid = res.data[0]["id"]
        job_ids.append(jid)
        result["jobs"].append(j["title"])

    # ── 4. 申请 ──────────────────────────────────────────────────
    applications_data = [
        {
            "job_id":       job_ids[0],   # 前端开发工程师
            "seeker_id":    seeker_id,
            "status":       "reviewing",
            "cover_letter": "您好！我是北大计算机系大四学生张小明，对贵司的前端工程师职位非常感兴趣。我在校期间深入学习了 Vue3 和 TypeScript，并在字节跳动完成了一段实习，独立负责了多个核心功能模块的开发。期待能有机会加入青禾科技！",
        },
        {
            "job_id":       job_ids[2],   # 产品经理实习
            "seeker_id":    seeker_id,
            "status":       "accepted",
            "cover_letter": "您好，我对产品岗位一直怀有热情，在校期间主导了学院小程序的产品设计，从需求调研到上线全程参与。我每周可全职实习，期待加入青禾科技的产品团队！",
        },
        {
            "job_id":       job_ids[3],   # 内容运营专员
            "seeker_id":    seeker_id,
            "status":       "pending",
            "cover_letter": "您好，我对内容运营工作十分感兴趣，平时有个人公众号运营经验，单篇阅读量最高 2 万+。希望有机会在绿芽传媒发挥所长，欢迎进一步沟通！",
        },
    ]

    for a in applications_data:
        existing = (
            db.table("applications")
            .select("id")
            .eq("job_id", a["job_id"])
            .eq("seeker_id", seeker_id)
            .execute()
        )
        if not existing.data:
            db.table("applications").insert(a).execute()
        result["applications"].append(a["job_id"])

    return {
        "message": "初始化完成",
        "accounts": {
            "求职者":  {"email": "seeker@greenseed.dev",    "password": "GreenSeed2024!", "role": "seeker"},
            "招聘方":  {"email": "recruiter@greenseed.dev", "password": "GreenSeed2024!", "role": "recruiter"},
            "管理员":  {"email": "admin@greenseed.dev",     "password": "GreenSeed2024!", "role": "admin"},
        },
        "created": result,
    }
