<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted, onUnmounted } from 'vue'
import { Plus, Trash2, Check, ChevronDown } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import GsMonthPicker from '@/components/ui/GsMonthPicker.vue'

const auth   = useAuthStore()
const saving = ref<string | null>(null)
const saved  = ref<string | null>(null)

// ── Personal info ─────────────────────────────────────────────────
const personal = reactive({
  name:         '',
  phone:        '',
  gender:       '',
  job_status:   'available_now',
  birth_year:   null as number | null,
  birth_month:  null as number | null,
  desired_city: '',
  wechat:       '',
})

// ── Bio ───────────────────────────────────────────────────────────
const bio = ref('')

// ── Desired position ──────────────────────────────────────────────
const desired = reactive({
  positions:  [] as string[],
  salary_min: null as number | null,
  salary_max: null as number | null,
  city:       '',
  available:  '',
})
const posInput = ref('')
function addPos() {
  const p = posInput.value.trim()
  if (p && !desired.positions.includes(p)) desired.positions.push(p)
  posInput.value = ''
}
function removePos(i: number) { desired.positions.splice(i, 1) }

// ── Work experience ───────────────────────────────────────────────
interface WorkExp { company: string; position: string; start_date: string; end_date: string; description: string }
const works = ref<WorkExp[]>([])
function addWork() { works.value.push({ company: '', position: '', start_date: '', end_date: '', description: '' }) }
function removeWork(i: number) { works.value.splice(i, 1) }

// ── Project experience ────────────────────────────────────────────
interface ProjExp { project_name: string; project_link: string; start_date: string; end_date: string; tech_stack: string[]; description: string; results: string }
const projects   = ref<ProjExp[]>([])
const techInputs = ref<string[]>([])
function addProject() {
  projects.value.push({ project_name: '', project_link: '', start_date: '', end_date: '', tech_stack: [], description: '', results: '' })
  techInputs.value.push('')
}
function removeProject(i: number) { projects.value.splice(i, 1); techInputs.value.splice(i, 1) }
function addTech(i: number) {
  const t = techInputs.value[i]?.trim()
  if (t && !projects.value[i].tech_stack.includes(t)) projects.value[i].tech_stack.push(t)
  techInputs.value[i] = ''
}
function removeTech(pi: number, ti: number) { projects.value[pi].tech_stack.splice(ti, 1) }

// ── Education ─────────────────────────────────────────────────────
const education = ref('')

// ── Skills ────────────────────────────────────────────────────────
const skills     = ref<string[]>([])
const skillInput = ref('')
function addSkill() {
  const s = skillInput.value.trim()
  if (s && !skills.value.includes(s)) skills.value.push(s)
  skillInput.value = ''
}
function removeSkill(i: number) { skills.value.splice(i, 1) }

// ── Init ──────────────────────────────────────────────────────────
function initForm(u: any) {
  if (!u) return
  personal.name         = u.name         ?? ''
  personal.phone        = u.phone        ?? ''
  personal.gender       = u.gender       ?? ''
  personal.job_status   = u.job_status   ?? 'available_now'
  personal.birth_year   = u.birth_year   ?? null
  personal.birth_month  = u.birth_month  ?? null
  personal.desired_city = u.desired_city ?? ''
  personal.wechat       = u.wechat       ?? ''

  bio.value       = u.bio       ?? ''
  education.value = u.education ?? ''
  skills.value    = [...(u.skills ?? [])]

  const dp = u.desired_position
  desired.positions  = Array.isArray(dp) ? [...dp] : (dp ? [dp] : [])
  desired.salary_min = u.desired_salary_min ?? null
  desired.salary_max = u.desired_salary_max ?? null
  desired.city       = u.desired_city       ?? ''
  desired.available  = u.available_date     ?? ''

  works.value    = (u.work_experience    ?? []).map((e: any) => ({ ...e }))
  projects.value = (u.project_experience ?? []).map((p: any) => ({ ...p, tech_stack: [...(p.tech_stack ?? [])] }))
  techInputs.value = projects.value.map(() => '')
}

watch(() => auth.user, initForm, { immediate: true })

// ── Save section ──────────────────────────────────────────────────
async function saveSection(section: string) {
  saving.value = section
  saved.value  = null
  let payload: Record<string, any> = {}

  if (section === 'personal') payload = {
    name: personal.name, phone: personal.phone, gender: personal.gender,
    job_status: personal.job_status, birth_year: personal.birth_year,
    birth_month: personal.birth_month, desired_city: personal.desired_city,
    wechat: personal.wechat,
  }
  if (section === 'bio')       payload = { bio: bio.value }
  if (section === 'desired')   payload = {
    desired_position:   desired.positions,
    desired_salary_min: desired.salary_min,
    desired_salary_max: desired.salary_max,
    desired_city:       desired.city,
    available_date:     desired.available || null,
  }
  if (section === 'work')      payload = { work_experience: works.value }
  if (section === 'project')   payload = { project_experience: projects.value }
  if (section === 'education') payload = { education: education.value }
  if (section === 'skills')    payload = { skills: skills.value }

  try {
    const res = await api.patch('/auth/me', payload)
    auth.user = res.data
    saved.value = section
    setTimeout(() => { if (saved.value === section) saved.value = null }, 2200)
  } finally {
    saving.value = null
  }
}

// ── Form helpers ──────────────────────────────────────────────────
const jobStatusOptions = [
  { value: 'available_now',  label: '随时到岗' },
  { value: 'available_soon', label: '一个月内' },
  { value: 'not_looking',    label: '暂不考虑' },
]
const genderOptions = [
  { value: 'male',   label: '男' },
  { value: 'female', label: '女' },
  { value: '',       label: '不透露' },
]
const birthYearOpts = computed(() => {
  const arr: number[] = []
  for (let y = new Date().getFullYear() - 18; y >= 1970; y--) arr.push(y)
  return arr
})
const birthMonthOpts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

// ── Sidebar nav ───────────────────────────────────────────────────
const sections = [
  { id: 'personal',  label: '个人信息' },
  { id: 'bio',       label: '个人优势' },
  { id: 'desired',   label: '期望职位' },
  { id: 'work',      label: '工作经历' },
  { id: 'project',   label: '项目经历' },
  { id: 'education', label: '教育经历' },
  { id: 'skills',    label: '专业技能' },
]

function scrollTo(id: string) {
  document.getElementById(`rs-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// ── Scroll spy ────────────────────────────────────────────────────
const activeSection = ref('personal')
let observer: IntersectionObserver | null = null

onMounted(() => {
  observer = new IntersectionObserver(
    entries => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          activeSection.value = entry.target.id.replace('rs-', '')
          break
        }
      }
    },
    { rootMargin: '-10% 0px -60% 0px', threshold: 0 },
  )
  sections.forEach(s => {
    const el = document.getElementById(`rs-${s.id}`)
    if (el) observer!.observe(el)
  })
})

onUnmounted(() => { observer?.disconnect() })
</script>

<template>
  <div class="resume-layout">
    <!-- Left sidebar nav -->
    <aside class="resume-sidebar">
      <nav class="resume-nav">
        <button
          v-for="s in sections"
          :key="s.id"
          class="resume-nav__item"
          :class="{ 'resume-nav__item--active': activeSection === s.id }"
          @click="scrollTo(s.id)"
        >{{ s.label }}</button>
      </nav>
    </aside>

    <!-- Right content -->
    <div class="resume-content">

      <!-- ── 个人信息 ────────────────────────────────── -->
      <section :id="`rs-personal`" class="rs-card">
        <div class="rs-card__head">
          <h2 class="rs-card__title">个人信息</h2>
          <button class="btn btn--primary btn--sm" :disabled="saving === 'personal'" @click="saveSection('personal')">
            <Check v-if="saved === 'personal'" :size="14" style="margin-right:4px" />
            {{ saving === 'personal' ? '保存中…' : saved === 'personal' ? '已保存 ✓' : '保存' }}
          </button>
        </div>
        <div class="rs-grid">
          <div class="field">
            <label class="field__label">姓名</label>
            <input v-model="personal.name" class="input" placeholder="你的真实姓名" />
          </div>
          <div class="field">
            <label class="field__label">手机号</label>
            <input v-model="personal.phone" class="input" type="tel" placeholder="138..." />
          </div>
          <div class="field">
            <label class="field__label">所在城市</label>
            <input v-model="personal.desired_city" class="input" placeholder="例：北京" />
          </div>
          <div class="field">
            <label class="field__label">微信号（选填）</label>
            <input v-model="personal.wechat" class="input" placeholder="WeChat ID" />
          </div>
          <div class="field">
            <label class="field__label">求职状态</label>
            <div class="select-wrap">
              <select v-model="personal.job_status" class="input">
                <option v-for="o in jobStatusOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
              </select>
              <ChevronDown :size="14" class="select-icon" />
            </div>
          </div>
          <div class="field">
            <label class="field__label">性别</label>
            <div class="radio-row">
              <label v-for="g in genderOptions" :key="g.value" class="radio-label">
                <input type="radio" v-model="personal.gender" :value="g.value" class="radio-input" />
                <span>{{ g.label }}</span>
              </label>
            </div>
          </div>
          <div class="field field--full">
            <label class="field__label">出生日期</label>
            <div class="birth-date-row">
              <div class="select-wrap">
                <select v-model.number="personal.birth_year" class="input">
                  <option value="" disabled>选择年份</option>
                  <option v-for="y in birthYearOpts" :key="y" :value="y">{{ y }} 年</option>
                </select>
                <ChevronDown :size="14" class="select-icon" />
              </div>
              <div class="select-wrap">
                <select v-model.number="personal.birth_month" class="input">
                  <option value="" disabled>选择月份</option>
                  <option v-for="m in birthMonthOpts" :key="m" :value="m">{{ m }} 月</option>
                </select>
                <ChevronDown :size="14" class="select-icon" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── 个人优势 ────────────────────────────────── -->
      <section id="rs-bio" class="rs-card">
        <div class="rs-card__head">
          <h2 class="rs-card__title">个人优势</h2>
          <button class="btn btn--primary btn--sm" :disabled="saving === 'bio'" @click="saveSection('bio')">
            <Check v-if="saved === 'bio'" :size="14" style="margin-right:4px" />
            {{ saving === 'bio' ? '保存中…' : saved === 'bio' ? '已保存 ✓' : '保存' }}
          </button>
        </div>
        <div class="field">
          <textarea v-model="bio" class="input textarea textarea--tall" placeholder="描述你的核心优势、个人亮点，让招聘方快速了解你…"></textarea>
        </div>
      </section>

      <!-- ── 期望职位 ────────────────────────────────── -->
      <section id="rs-desired" class="rs-card">
        <div class="rs-card__head">
          <h2 class="rs-card__title">期望职位</h2>
          <button class="btn btn--primary btn--sm" :disabled="saving === 'desired'" @click="saveSection('desired')">
            <Check v-if="saved === 'desired'" :size="14" style="margin-right:4px" />
            {{ saving === 'desired' ? '保存中…' : saved === 'desired' ? '已保存 ✓' : '保存' }}
          </button>
        </div>
        <div class="rs-grid">
          <div class="field field--full">
            <label class="field__label">期望职位</label>
            <div class="skill-tags">
              <span v-for="(p, i) in desired.positions" :key="p" class="tag tag--green skill-tag">
                {{ p }}<button type="button" class="skill-tag__remove" @click="removePos(i)">×</button>
              </span>
            </div>
            <div class="skill-input-row">
              <input v-model="posInput" class="input" placeholder="输入职位名称，按 Enter 添加" @keydown.enter.prevent="addPos" />
              <button type="button" class="btn btn--outline btn--sm" @click="addPos">添加</button>
            </div>
          </div>
          <div class="field">
            <label class="field__label">期望薪资（元/月）</label>
            <div class="salary-range">
              <input v-model.number="desired.salary_min" class="input" type="number" min="0" placeholder="最低" />
              <span class="salary-sep">—</span>
              <input v-model.number="desired.salary_max" class="input" type="number" min="0" placeholder="最高" />
            </div>
          </div>
          <div class="field">
            <label class="field__label">期望城市</label>
            <input v-model="desired.city" class="input" placeholder="例：北京、上海" />
          </div>
          <div class="field">
            <label class="field__label">到岗时间</label>
            <GsMonthPicker v-model="desired.available" placeholder="选择到岗月份" :clearable="true" />
          </div>
        </div>
      </section>

      <!-- ── 工作经历 ────────────────────────────────── -->
      <section id="rs-work" class="rs-card">
        <div class="rs-card__head">
          <h2 class="rs-card__title">工作经历</h2>
          <button class="btn btn--primary btn--sm" :disabled="saving === 'work'" @click="saveSection('work')">
            <Check v-if="saved === 'work'" :size="14" style="margin-right:4px" />
            {{ saving === 'work' ? '保存中…' : saved === 'work' ? '已保存 ✓' : '保存' }}
          </button>
        </div>
        <div v-if="works.length === 0" class="exp-empty-inline">暂无工作经历</div>
        <div v-for="(w, i) in works" :key="i" class="exp-entry">
          <div class="exp-entry__header">
            <span class="exp-entry__num">经历 {{ i + 1 }}</span>
            <button type="button" class="btn btn--ghost btn--sm exp-remove" @click="removeWork(i)">
              <Trash2 :size="13" /> 删除
            </button>
          </div>
          <div class="rs-grid">
            <div class="field">
              <label class="field__label">公司名称</label>
              <input v-model="w.company" class="input" placeholder="公司名称" />
            </div>
            <div class="field">
              <label class="field__label">职位名称</label>
              <input v-model="w.position" class="input" placeholder="岗位" />
            </div>
            <div class="field">
              <label class="field__label">开始时间</label>
              <GsMonthPicker v-model="w.start_date" placeholder="开始年月" />
            </div>
            <div class="field">
              <label class="field__label">结束时间（在职留空）</label>
              <GsMonthPicker v-model="w.end_date" placeholder="结束年月" :clearable="true" />
            </div>
            <div class="field field--full">
              <label class="field__label">工作描述</label>
              <textarea v-model="w.description" class="input textarea" placeholder="描述主要职责与成果…"></textarea>
            </div>
          </div>
        </div>
        <button type="button" class="btn btn--outline btn--sm rs-add-btn" @click="addWork">
          <Plus :size="14" style="margin-right:4px" />添加工作经历
        </button>
      </section>

      <!-- ── 项目经历 ────────────────────────────────── -->
      <section id="rs-project" class="rs-card">
        <div class="rs-card__head">
          <h2 class="rs-card__title">项目经历</h2>
          <button class="btn btn--primary btn--sm" :disabled="saving === 'project'" @click="saveSection('project')">
            <Check v-if="saved === 'project'" :size="14" style="margin-right:4px" />
            {{ saving === 'project' ? '保存中…' : saved === 'project' ? '已保存 ✓' : '保存' }}
          </button>
        </div>
        <div v-if="projects.length === 0" class="exp-empty-inline">暂无项目经历</div>
        <div v-for="(p, i) in projects" :key="i" class="exp-entry">
          <div class="exp-entry__header">
            <span class="exp-entry__num">项目 {{ i + 1 }}</span>
            <button type="button" class="btn btn--ghost btn--sm exp-remove" @click="removeProject(i)">
              <Trash2 :size="13" /> 删除
            </button>
          </div>
          <div class="rs-grid">
            <div class="field">
              <label class="field__label">项目名称</label>
              <input v-model="p.project_name" class="input" placeholder="项目名称" />
            </div>
            <div class="field">
              <label class="field__label">项目链接（选填）</label>
              <input v-model="p.project_link" class="input" placeholder="https://..." />
            </div>
            <div class="field">
              <label class="field__label">开始时间</label>
              <GsMonthPicker v-model="p.start_date" placeholder="开始年月" />
            </div>
            <div class="field">
              <label class="field__label">结束时间（进行中留空）</label>
              <GsMonthPicker v-model="p.end_date" placeholder="结束年月" :clearable="true" />
            </div>
            <div class="field field--full">
              <label class="field__label">技术栈</label>
              <div class="skill-tags">
                <span v-for="(t, ti) in p.tech_stack" :key="t" class="tag tag--green skill-tag">
                  {{ t }}<button type="button" class="skill-tag__remove" @click="removeTech(i, ti)">×</button>
                </span>
              </div>
              <div class="skill-input-row">
                <input v-model="techInputs[i]" class="input" placeholder="Vue3、Python… 按 Enter 添加" @keydown.enter.prevent="addTech(i)" />
                <button type="button" class="btn btn--outline btn--sm" @click="addTech(i)">添加</button>
              </div>
            </div>
            <div class="field field--full">
              <label class="field__label">项目描述</label>
              <textarea v-model="p.description" class="input textarea" placeholder="项目背景与你的职责…"></textarea>
            </div>
            <div class="field field--full">
              <label class="field__label">项目成果</label>
              <textarea v-model="p.results" class="input textarea" style="height:72px" placeholder="量化成果，如：用户增长 30%…"></textarea>
            </div>
          </div>
        </div>
        <button type="button" class="btn btn--outline btn--sm rs-add-btn" @click="addProject">
          <Plus :size="14" style="margin-right:4px" />添加项目经历
        </button>
      </section>

      <!-- ── 教育经历 ────────────────────────────────── -->
      <section id="rs-education" class="rs-card">
        <div class="rs-card__head">
          <h2 class="rs-card__title">教育经历</h2>
          <button class="btn btn--primary btn--sm" :disabled="saving === 'education'" @click="saveSection('education')">
            <Check v-if="saved === 'education'" :size="14" style="margin-right:4px" />
            {{ saving === 'education' ? '保存中…' : saved === 'education' ? '已保存 ✓' : '保存' }}
          </button>
        </div>
        <div class="field">
          <textarea v-model="education" class="input textarea" placeholder="例：XX大学 计算机科学与技术 本科 2021—2025"></textarea>
        </div>
      </section>

      <!-- ── 专业技能 ────────────────────────────────── -->
      <section id="rs-skills" class="rs-card">
        <div class="rs-card__head">
          <h2 class="rs-card__title">专业技能</h2>
          <button class="btn btn--primary btn--sm" :disabled="saving === 'skills'" @click="saveSection('skills')">
            <Check v-if="saved === 'skills'" :size="14" style="margin-right:4px" />
            {{ saving === 'skills' ? '保存中…' : saved === 'skills' ? '已保存 ✓' : '保存' }}
          </button>
        </div>
        <div class="skill-tags">
          <span v-for="(s, i) in skills" :key="s" class="tag tag--green skill-tag">
            {{ s }}<button type="button" class="skill-tag__remove" @click="removeSkill(i)">×</button>
          </span>
        </div>
        <div class="skill-input-row" style="margin-top:var(--space-3)">
          <input v-model="skillInput" class="input" placeholder="输入技能名称，按 Enter 添加" @keydown.enter.prevent="addSkill" />
          <button type="button" class="btn btn--outline btn--sm" @click="addSkill">添加</button>
        </div>
      </section>

    </div><!-- /resume-content -->
  </div><!-- /resume-layout -->
</template>

<style scoped>
/* ── Layout ── */
.resume-layout {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: var(--space-8);
  align-items: start;
}

/* ── Sidebar ── */
.resume-sidebar {
  position: sticky;
  top: 80px;
}
.resume-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  padding: var(--space-3);
}
.resume-nav__item {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--gs-text-2);
  text-align: left;
  background: none;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--duration-fast), color var(--duration-fast);
}
.resume-nav__item:hover {
  background: var(--gs-primary-tint);
  color: var(--gs-primary);
}
.resume-nav__item--active {
  background: var(--gs-primary-tint);
  color: var(--gs-primary);
  font-weight: 600;
}

/* ── Content ── */
.resume-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* ── Section card ── */
.rs-card {
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  padding: var(--space-7);
}
.rs-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--gs-border);
}
.rs-card__title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--gs-text);
  letter-spacing: -0.01em;
}

/* ── Grid ── */
.rs-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-5);
}
.field--full { grid-column: 1 / -1; }

/* ── Birth date ── */
.birth-date-row {
  display: flex;
  gap: var(--space-3);
}
.birth-date-row .select-wrap { flex: 1; }

/* ── Fields ── */
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.textarea { height: 100px; resize: vertical; padding-block: var(--space-3); }
.textarea--tall { height: 140px; }

/* ── Select ── */
.select-wrap { position: relative; }
.select-wrap select { appearance: none; padding-right: 32px; cursor: pointer; }
.select-icon {
  position: absolute; right: var(--space-3); top: 50%;
  transform: translateY(-50%); pointer-events: none; color: var(--gs-text-3);
}

/* ── Radio ── */
.radio-row { display: flex; gap: var(--space-5); align-items: center; height: 42px; }
.radio-label { display: flex; align-items: center; gap: var(--space-2); cursor: pointer; font-size: var(--text-sm); color: var(--gs-text-2); }
.radio-input { accent-color: var(--gs-primary); width: 15px; height: 15px; cursor: pointer; }

/* ── Salary ── */
.salary-range { display: flex; align-items: center; gap: var(--space-2); }
.salary-range .input { flex: 1; }
.salary-sep { color: var(--gs-text-3); font-weight: 500; flex-shrink: 0; }

/* ── Skill tags ── */
.skill-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); min-height: 28px; margin-bottom: var(--space-2); }
.skill-tag { gap: var(--space-1); }
.skill-tag__remove { background: none; border: none; color: inherit; cursor: pointer; font-size: 1rem; line-height: 1; padding: 0 2px; }
.skill-input-row { display: flex; gap: var(--space-2); }
.skill-input-row .input { flex: 1; height: 36px; }

/* ── Exp entries ── */
.exp-empty-inline {
  font-size: var(--text-sm); color: var(--gs-text-3);
  padding: var(--space-4) 0;
  margin-bottom: var(--space-4);
}
.exp-entry {
  display: flex; flex-direction: column; gap: var(--space-4);
  padding: var(--space-5);
  background: var(--gs-bg);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}
.exp-entry__header { display: flex; align-items: center; justify-content: space-between; }
.exp-entry__num { font-size: var(--text-sm); font-weight: 600; color: var(--gs-text-2); }
.exp-remove { display: flex; align-items: center; gap: 4px; color: oklch(55% 0.18 25); }
.exp-remove:hover { background: oklch(97% 0.01 25); }

.rs-add-btn { width: 100%; justify-content: center; }

/* ── Responsive ── */
@media (max-width: 900px) {
  .resume-layout { grid-template-columns: 1fr; }
  .resume-sidebar { position: static; }
  .resume-nav { flex-direction: row; flex-wrap: wrap; gap: var(--space-1); }
  .resume-nav__item { padding: var(--space-2) var(--space-3); font-size: var(--text-xs); }
}
@media (max-width: 640px) {
  .rs-grid { grid-template-columns: 1fr; }
}
</style>
