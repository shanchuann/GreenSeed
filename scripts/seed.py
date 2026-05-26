"""
青禾招聘 演示数据初始化脚本
用法: python scripts/seed.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

URL  = os.environ["SUPABASE_URL"]
KEY  = os.environ["SUPABASE_SERVICE_KEY"]
db   = create_client(URL, KEY)

# ── 演示账号 ──────────────────────────────────────────────────────

USERS = [
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


def get_or_create_user(u: dict) -> str:
    """创建 Auth 用户，已存在则返回现有 ID。"""
    try:
        res = db.auth.admin.create_user({
            "email":         u["email"],
            "password":      u["password"],
            "email_confirm": True,
        })
        uid = str(res.user.id)
        print(f"  ✓ 创建用户 {u['email']}")
        return uid
    except Exception as e:
        if "already registered" in str(e).lower() or "already been registered" in str(e).lower() or "email" in str(e).lower():
            users = db.auth.admin.list_users()
            found = next((x for x in users if x.email == u["email"]), None)
            if found:
                print(f"  · 已存在 {u['email']}，跳过")
                return str(found.id)
        raise


def main():
    print("\n── Step 1: 创建用户 ─────────────────────────────")
    uid: dict[str, str] = {}
    for u in USERS:
        user_id = get_or_create_user(u)
        uid[u["role"]] = user_id
        db.table("profiles").upsert({
            "id":        user_id,
            "email":     u["email"],
            "name":      u["name"],
            "role":      u["role"],
            "bio":       u["bio"] or None,
            "skills":    u["skills"] or [],
            "education": u["education"] or None,
        }).execute()

    recruiter_id = uid["recruiter"]
    seeker_id    = uid["seeker"]

    print("\n── Step 2: 创建公司 ─────────────────────────────")
    companies_raw = [
        {
            "recruiter_id": recruiter_id,
            "name":         "青禾科技有限公司",
            "description":  "青禾科技专注于互联网产品研发，旗下拥有青禾招聘、青禾云等多款产品，是一家高速成长的科技公司。",
            "industry":     "互联网·软件",
            "location":     "北京",
            "verified":     True,
        },
        {
            "recruiter_id": recruiter_id,
            "name":         "绿芽传媒集团",
            "description":  "绿芽传媒是一家专注于年轻人内容营销与品牌推广的传媒公司，服务超过 500 家品牌客户。",
            "industry":     "市场·运营",
            "location":     "上海",
            "verified":     True,
        },
    ]

    company_ids = []
    for c in companies_raw:
        existing = (
            db.table("companies")
            .select("id")
            .eq("recruiter_id", recruiter_id)
            .eq("name", c["name"])
            .execute()
        )
        if existing.data:
            cid = existing.data[0]["id"]
            print(f"  · 已存在公司「{c['name']}」，跳过")
        else:
            res = db.table("companies").insert(c).execute()
            cid = res.data[0]["id"]
            print(f"  ✓ 创建公司「{c['name']}」")
        company_ids.append(cid)

    c1, c2 = company_ids

    print("\n── Step 3: 创建职位 ─────────────────────────────")
    jobs_raw = [
        {
            "company_id":   c1,
            "title":        "前端开发工程师",
            "description":  "负责公司核心产品的前端研发工作，参与需求分析、技术方案制定和代码实现。与产品、设计、后端紧密协作，推动产品快速迭代。",
            "requirements": "本科及以上学历，计算机相关专业；熟练掌握 Vue3 / React，了解 TypeScript；有大型项目经验优先。",
            "salary_min":   15000,  "salary_max": 25000,
            "job_type":     "full",  "location": "北京",
            "category":     "互联网·软件",
            "tags":         ["Vue3", "TypeScript", "前端架构"],
            "status":       "open",
        },
        {
            "company_id":   c1,
            "title":        "Python 后端工程师",
            "description":  "参与公司后端服务的设计、开发和维护，负责 API 开发、数据库优化和系统架构改进。",
            "requirements": "熟练掌握 Python，了解 FastAPI / Django；有数据库设计经验；英文读写能力良好。",
            "salary_min":   18000,  "salary_max": 30000,
            "job_type":     "full",  "location": "北京",
            "category":     "互联网·软件",
            "tags":         ["Python", "FastAPI", "PostgreSQL"],
            "status":       "open",
        },
        {
            "company_id":   c1,
            "title":        "产品经理（实习）",
            "description":  "协助产品经理进行需求调研、竞品分析、原型设计和项目跟进，深度参与产品从 0 到 1 的全流程。",
            "requirements": "本科在读，产品/计算机相关专业优先；逻辑思维清晰；熟悉 Figma/Axure；每周可实习 4 天以上。",
            "salary_min":   5000,   "salary_max": 8000,
            "job_type":     "intern","location": "北京",
            "category":     "互联网·软件",
            "tags":         ["产品规划", "原型设计", "数据驱动"],
            "status":       "open",
        },
        {
            "company_id":   c2,
            "title":        "内容运营专员",
            "description":  "负责公司社交媒体账号运营（微博、微信公众号、小红书等），策划并执行品牌内容，提升用户互动率。",
            "requirements": "本科及以上，文案写作能力强；熟悉主流内容平台；有运营经验优先。",
            "salary_min":   8000,   "salary_max": 12000,
            "job_type":     "full",  "location": "上海",
            "category":     "市场·运营",
            "tags":         ["内容运营", "小红书", "品牌策划"],
            "status":       "open",
        },
        {
            "company_id":   c2,
            "title":        "UI/UX 设计师",
            "description":  "负责公司旗下各品牌视觉设计工作，包括 App 界面、活动海报、品牌物料等，保证视觉一致性。",
            "requirements": "本科及以上，设计相关专业；精通 Figma / Illustrator；有完整项目作品集。",
            "salary_min":   12000,  "salary_max": 18000,
            "job_type":     "full",  "location": "上海",
            "category":     "设计·创意",
            "tags":         ["Figma", "UI设计", "品牌视觉"],
            "status":       "open",
        },
        {
            "company_id":   c2,
            "title":        "品牌营销实习生",
            "description":  "协助市场团队策划品牌推广活动，收集市场数据，撰写营销报告，协调内外部资源推进项目落地。",
            "requirements": "本科在读，市场营销/传媒/广告等相关专业；沟通能力强；每周可实习 3 天以上。",
            "salary_min":   3000,   "salary_max": 5000,
            "job_type":     "intern","location": "上海",
            "category":     "市场·运营",
            "tags":         ["市场营销", "活动策划", "品牌推广"],
            "status":       "open",
        },
    ]

    job_ids = []
    for j in jobs_raw:
        existing = (
            db.table("jobs")
            .select("id")
            .eq("company_id", j["company_id"])
            .eq("title", j["title"])
            .execute()
        )
        if existing.data:
            jid = existing.data[0]["id"]
            print(f"  · 已存在职位「{j['title']}」，跳过")
        else:
            res = db.table("jobs").insert(j).execute()
            jid = res.data[0]["id"]
            print(f"  ✓ 创建职位「{j['title']}」")
        job_ids.append(jid)

    print("\n── Step 4: 创建申请 ─────────────────────────────")
    apps_raw = [
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
            "cover_letter": "您好，我对内容运营工作十分感兴趣，平时有个人公众号运营经验，单篇阅读量最高 2 万+。希望有机会在绿芽传媒发挥所长！",
        },
    ]

    titles = [jobs_raw[0]["title"], jobs_raw[2]["title"], jobs_raw[3]["title"]]
    for i, a in enumerate(apps_raw):
        existing = (
            db.table("applications")
            .select("id")
            .eq("job_id", a["job_id"])
            .eq("seeker_id", seeker_id)
            .execute()
        )
        if existing.data:
            print(f"  · 已存在申请「{titles[i]}」，跳过")
        else:
            db.table("applications").insert(a).execute()
            print(f"  ✓ 创建申请「{titles[i]}」({a['status']})")

    print("\n" + "─" * 52)
    print("  初始化完成！演示账号：")
    print("─" * 52)
    print(f"  求职者  seeker@greenseed.dev     / GreenSeed2024!")
    print(f"  招聘方  recruiter@greenseed.dev  / GreenSeed2024!")
    print(f"  管理员  admin@greenseed.dev      / GreenSeed2024!")
    print("─" * 52 + "\n")


if __name__ == "__main__":
    main()
