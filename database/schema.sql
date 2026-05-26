-- GreenSeed 青禾招聘 — 数据库建表 SQL
-- 在 Supabase 控制台 SQL Editor 中执行本文件
-- ─────────────────────────────────────────────────────────

-- ── 用户资料表（关联 Supabase auth.users）────────────────
CREATE TABLE IF NOT EXISTS public.profiles (
  id           UUID        REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email        TEXT        NOT NULL UNIQUE,
  name         TEXT        NOT NULL,
  role         TEXT        NOT NULL DEFAULT 'seeker'
                           CHECK (role IN ('seeker', 'recruiter', 'admin')),
  phone        TEXT,
  avatar_url   TEXT,
  skills       TEXT[]      DEFAULT '{}',
  education    TEXT,
  bio          TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 公司信息表 ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.companies (
  id            UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  recruiter_id  UUID        NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  name          TEXT        NOT NULL,
  description   TEXT,
  logo_url      TEXT,
  industry      TEXT,
  location      TEXT,
  verified      BOOLEAN     NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 职位表 ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.jobs (
  id           UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  company_id   UUID        NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
  title        TEXT        NOT NULL,
  description  TEXT        NOT NULL DEFAULT '',
  requirements TEXT        DEFAULT '',
  salary_min   INTEGER,
  salary_max   INTEGER,
  job_type     TEXT        NOT NULL DEFAULT 'full'
               CHECK (job_type IN ('full', 'part', 'intern')),
  location     TEXT,
  category     TEXT,
  tags         TEXT[]      DEFAULT '{}',
  status       TEXT        NOT NULL DEFAULT 'open'
               CHECK (status IN ('open', 'closed')),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 申请表 ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.applications (
  id            UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  job_id        UUID        NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  seeker_id     UUID        NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  status        TEXT        NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'reviewing', 'accepted', 'rejected')),
  cover_letter  TEXT        DEFAULT '',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (job_id, seeker_id)
);

-- ── 自动更新 updated_at 触发器 ────────────────────────────
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER jobs_updated_at
  BEFORE UPDATE ON public.jobs
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

CREATE OR REPLACE TRIGGER applications_updated_at
  BEFORE UPDATE ON public.applications
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ── 启用 Row Level Security ────────────────────────────────
ALTER TABLE public.profiles     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

-- ── RLS 策略：profiles ────────────────────────────────────
CREATE POLICY "profiles_select_all"
  ON public.profiles FOR SELECT USING (true);

CREATE POLICY "profiles_insert_own"
  ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "profiles_update_own"
  ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- ── RLS 策略：companies ───────────────────────────────────
CREATE POLICY "companies_select_all"
  ON public.companies FOR SELECT USING (true);

CREATE POLICY "companies_insert_recruiter"
  ON public.companies FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND role IN ('recruiter', 'admin')
    )
  );

CREATE POLICY "companies_update_own"
  ON public.companies FOR UPDATE USING (recruiter_id = auth.uid());

CREATE POLICY "companies_delete_own"
  ON public.companies FOR DELETE USING (recruiter_id = auth.uid());

-- ── RLS 策略：jobs ────────────────────────────────────────
CREATE POLICY "jobs_select_open_or_own"
  ON public.jobs FOR SELECT USING (
    status = 'open'
    OR EXISTS (
      SELECT 1 FROM public.companies
      WHERE id = jobs.company_id AND recruiter_id = auth.uid()
    )
  );

CREATE POLICY "jobs_insert_own_company"
  ON public.jobs FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.companies
      WHERE id = company_id AND recruiter_id = auth.uid()
    )
  );

CREATE POLICY "jobs_update_own_company"
  ON public.jobs FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.companies
      WHERE id = company_id AND recruiter_id = auth.uid()
    )
  );

CREATE POLICY "jobs_delete_own_company"
  ON public.jobs FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.companies
      WHERE id = company_id AND recruiter_id = auth.uid()
    )
  );

-- ── RLS 策略：applications ────────────────────────────────
CREATE POLICY "applications_select"
  ON public.applications FOR SELECT USING (
    seeker_id = auth.uid()
    OR EXISTS (
      SELECT 1 FROM public.jobs j
      JOIN public.companies c ON j.company_id = c.id
      WHERE j.id = job_id AND c.recruiter_id = auth.uid()
    )
  );

CREATE POLICY "applications_insert_seeker"
  ON public.applications FOR INSERT WITH CHECK (seeker_id = auth.uid());

CREATE POLICY "applications_update"
  ON public.applications FOR UPDATE USING (
    seeker_id = auth.uid()
    OR EXISTS (
      SELECT 1 FROM public.jobs j
      JOIN public.companies c ON j.company_id = c.id
      WHERE j.id = job_id AND c.recruiter_id = auth.uid()
    )
  );

-- ── 服务角色绕过 RLS（后端用 service_key 时自动生效）────────
-- 无需额外配置，service_role 天然绕过 RLS
