<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Check, Plus, Trash2, Upload, FileText, ExternalLink, Camera, Link } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'
import GsMonthPicker from '@/components/ui/GsMonthPicker.vue'

const auth = useAuthStore()
const saving = ref(false)
const saved  = ref(false)
const activeTab = ref<'basic' | 'intention' | 'experience' | 'project' | 'resume'>('basic')

// ── Basic info ────────────────────────────────────────────────────
const basic = reactive({
  name:      '',
  phone:     '',
  bio:       '',
  education: '',
  skills:    [] as string[],
})
const skillInput = ref('')

// ── Avatar ────────────────────────────────────────────────────────
const avatarUploading = ref(false)
const avatarError     = ref('')

async function uploadAvatar(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  avatarError.value   = ''
  avatarUploading.value = true
  try {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post('/auth/me/avatar', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    auth.user = res.data
  } catch (e: any) {
    avatarError.value = e?.response?.data?.detail ?? '上传失败，请重试'
  } finally {
    avatarUploading.value = false
    ;(e.target as HTMLInputElement).value = ''
  }
}

// ── Job intention ─────────────────────────────────────────────────
const intention = reactive({
  desired_positions:  [] as string[],
  desired_salary_min: null as number | null,
  desired_salary_max: null as number | null,
  desired_city:       '',
  available_date:     '',
})
const positionInput = ref('')

function addPosition() {
  const p = positionInput.value.trim()
  if (p && !intention.desired_positions.includes(p)) intention.desired_positions.push(p)
  positionInput.value = ''
}
function removePosition(i: number) { intention.desired_positions.splice(i, 1) }

// ── Work experience ───────────────────────────────────────────────
interface WorkExp {
  company: string
  position: string
  start_date: string
  end_date: string
  description: string
}
const experiences = ref<WorkExp[]>([])

function addExperience() {
  experiences.value.push({ company: '', position: '', start_date: '', end_date: '', description: '' })
}
function removeExperience(i: number) {
  experiences.value.splice(i, 1)
}

// ── Project experience ────────────────────────────────────────────
interface ProjectExp {
  project_name: string
  project_link: string
  start_date: string
  end_date: string
  tech_stack: string[]
  description: string
  results: string
}
const projects = ref<ProjectExp[]>([])
const techInputs = ref<string[]>([])

function addProject() {
  projects.value.push({
    project_name: '', project_link: '',
    start_date: '', end_date: '',
    tech_stack: [], description: '', results: '',
  })
  techInputs.value.push('')
}
function removeProject(i: number) {
  projects.value.splice(i, 1)
  techInputs.value.splice(i, 1)
}
function addTech(i: number) {
  const t = techInputs.value[i]?.trim()
  if (t && !projects.value[i].tech_stack.includes(t)) projects.value[i].tech_stack.push(t)
  techInputs.value[i] = ''
}
function removeTech(pi: number, ti: number) {
  projects.value[pi].tech_stack.splice(ti, 1)
}

// ── Resume ────────────────────────────────────────────────────────
const resumeUrl    = ref('')
const resumeFile   = ref<File | null>(null)
const uploading    = ref(false)
const uploadError  = ref('')

function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) { resumeFile.value = f; uploadError.value = '' }
}

async function uploadResume() {
  if (!resumeFile.value) return
  uploading.value = true
  uploadError.value = ''
  try {
    const form = new FormData()
    form.append('file', resumeFile.value)
    const res = await api.post('/auth/me/resume', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    resumeUrl.value = res.data.resume_url ?? ''
    auth.user = res.data
    resumeFile.value = null
  } catch (e: any) {
    uploadError.value = e?.response?.data?.detail ?? '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

// ── Init ──────────────────────────────────────────────────────────
onMounted(() => {
  const u = auth.user as any
  if (!u) return

  basic.name      = u.name      ?? ''
  basic.phone     = u.phone     ?? ''
  basic.bio       = u.bio       ?? ''
  basic.education = u.education ?? ''
  basic.skills    = [...(u.skills ?? [])]

  const dp = u.desired_position
  intention.desired_positions   = Array.isArray(dp) ? [...dp] : (dp ? [dp] : [])
  intention.desired_salary_min = u.desired_salary_min ?? null
  intention.desired_salary_max = u.desired_salary_max ?? null
  intention.desired_city       = u.desired_city       ?? ''
  intention.available_date     = u.available_date     ?? ''

  experiences.value = (u.work_experience ?? []).map((e: WorkExp) => ({ ...e }))
  projects.value    = (u.project_experience ?? []).map((p: ProjectExp) => ({
    ...p,
    tech_stack: [...(p.tech_stack ?? [])],
  }))
  techInputs.value  = projects.value.map(() => '')
  resumeUrl.value   = u.resume_url ?? ''
})

// ── Save ──────────────────────────────────────────────────────────
const tabPayload = computed(() => {
  if (activeTab.value === 'basic') return { ...basic }
  if (activeTab.value === 'intention') return {
    desired_position:   intention.desired_positions,
    desired_salary_min: intention.desired_salary_min,
    desired_salary_max: intention.desired_salary_max,
    desired_city:       intention.desired_city,
    available_date:     intention.available_date || null,
  }
  if (activeTab.value === 'experience') return { work_experience: experiences.value }
  if (activeTab.value === 'project')    return { project_experience: projects.value }
  return { resume_url: resumeUrl.value }
})

async function save() {
  saving.value = true
  saved.value  = false
  try {
    const res = await api.patch('/auth/me', tabPayload.value)
    auth.user = res.data
    saved.value = true
    setTimeout(() => { saved.value = false }, 2200)
  } finally {
    saving.value = false
  }
}

function addSkill() {
  const s = skillInput.value.trim()
  if (s && !basic.skills.includes(s)) basic.skills.push(s)
  skillInput.value = ''
}
function removeSkill(i: number) { basic.skills.splice(i, 1) }
</script>

<template>
  <div class="page-wrap">
    <div class="container container--narrow">
      <h1 class="page-title fade-up">个人资料</h1>

      <!-- Avatar header -->
      <div class="profile-header fade-up">
        <div class="profile-avatar-wrap">
          <div class="profile-avatar" :class="{ 'profile-avatar--uploading': avatarUploading }">
            <img v-if="auth.user?.avatar_url" :src="auth.user.avatar_url" class="profile-avatar__img" alt="头像" />
            <span v-else>{{ auth.user?.name?.[0]?.toUpperCase() ?? '?' }}</span>
          </div>
          <label class="profile-avatar__camera" :title="avatarUploading ? '上传中…' : '修改头像'">
            <Camera :size="13" />
            <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" style="display:none" @change="uploadAvatar" :disabled="avatarUploading" />
          </label>
        </div>
        <div>
          <p class="profile-name">{{ auth.user?.name }}</p>
          <span class="tag tag--green">{{ auth.user?.role === 'seeker' ? '求职者' : '招聘方' }}</span>
          <p v-if="avatarError" class="avatar-error">{{ avatarError }}</p>
        </div>
      </div>

      <!-- Tab nav -->
      <nav class="tab-nav fade-up" role="tablist">
        <button
          v-for="tab in [
            { key: 'basic',      label: '基本信息' },
            { key: 'intention',  label: '求职意向' },
            { key: 'experience', label: '工作经历' },
            { key: 'project',    label: '项目经历' },
            { key: 'resume',     label: '我的简历' },
          ]"
          :key="tab.key"
          role="tab"
          :aria-selected="activeTab === tab.key"
          class="tab-nav__item"
          :class="{ 'tab-nav__item--active': activeTab === tab.key }"
          @click="activeTab = (tab.key as any)"
        >{{ tab.label }}</button>
      </nav>

      <!-- ── Tab: 基本信息 ─────────────────────────────────────── -->
      <div v-if="activeTab === 'basic'" class="profile-card fade-up">
        <form @submit.prevent="save" class="profile-form">
          <div class="field-row">
            <div class="field">
              <label class="field__label">姓名</label>
              <input v-model="basic.name" class="input" placeholder="你的姓名" />
            </div>
            <div class="field">
              <label class="field__label">手机号</label>
              <input v-model="basic.phone" class="input" placeholder="138..." type="tel" />
            </div>
          </div>

          <div class="field">
            <label class="field__label">教育经历</label>
            <input v-model="basic.education" class="input" placeholder="例：XX大学 计算机科学 2024届" />
          </div>

          <div class="field">
            <label class="field__label">个人简介</label>
            <textarea v-model="basic.bio" class="input textarea" placeholder="简短介绍自己…"></textarea>
          </div>

          <div class="field">
            <label class="field__label">技能标签</label>
            <div class="skill-tags">
              <span v-for="(s, i) in basic.skills" :key="s" class="tag tag--green skill-tag">
                {{ s }}
                <button type="button" class="skill-tag__remove" @click="removeSkill(i)">×</button>
              </span>
            </div>
            <div class="skill-input-row">
              <input v-model="skillInput" class="input" placeholder="输入技能后按 Enter" @keydown.enter.prevent="addSkill" />
              <button type="button" class="btn btn--outline btn--sm" @click="addSkill">添加</button>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn--primary" :disabled="saving">
              <Check v-if="saved" :size="16" style="margin-right:4px" />
              {{ saving ? '保存中…' : saved ? '已保存 ✓' : '保存修改' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ── Tab: 求职意向 ─────────────────────────────────────── -->
      <div v-else-if="activeTab === 'intention'" class="profile-card fade-up">
        <form @submit.prevent="save" class="profile-form">
          <div class="field">
            <label class="field__label">期望职位</label>
            <div class="skill-tags" style="min-height:36px">
              <span v-for="(p, i) in intention.desired_positions" :key="p" class="tag tag--green skill-tag">
                {{ p }}
                <button type="button" class="skill-tag__remove" @click="removePosition(i)">×</button>
              </span>
            </div>
            <div class="skill-input-row">
              <input
                v-model="positionInput"
                class="input"
                placeholder="例：前端开发、产品经理…按 Enter 添加"
                @keydown.enter.prevent="addPosition"
              />
              <button type="button" class="btn btn--outline btn--sm" @click="addPosition">添加</button>
            </div>
          </div>

          <div class="field">
            <label class="field__label">期望薪资（元/月）</label>
            <div class="salary-range">
              <input v-model.number="intention.desired_salary_min" class="input" type="number" min="0" placeholder="最低" />
              <span class="salary-sep">—</span>
              <input v-model.number="intention.desired_salary_max" class="input" type="number" min="0" placeholder="最高" />
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label class="field__label">期望城市</label>
              <input v-model="intention.desired_city" class="input" placeholder="例：北京" />
            </div>
            <div class="field">
              <label class="field__label">到岗时间</label>
              <GsMonthPicker
                v-model="intention.available_date"
                placeholder="选择到岗月份"
                :clearable="true"
              />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn--primary" :disabled="saving">
              <Check v-if="saved" :size="16" style="margin-right:4px" />
              {{ saving ? '保存中…' : saved ? '已保存 ✓' : '保存意向' }}
            </button>
          </div>
        </form>
      </div>

      <!-- ── Tab: 工作经历 ─────────────────────────────────────── -->
      <div v-else-if="activeTab === 'experience'" class="profile-card fade-up">
        <div class="exp-list">
          <div v-if="experiences.length === 0" class="exp-empty">
            <FileText :size="36" color="var(--gs-text-3)" />
            <p>暂无工作经历，点击下方添加</p>
          </div>

          <div v-for="(exp, i) in experiences" :key="i" class="exp-entry">
            <div class="exp-entry__header">
              <span class="exp-entry__num">经历 {{ i + 1 }}</span>
              <button type="button" class="btn btn--ghost btn--sm exp-remove" @click="removeExperience(i)">
                <Trash2 :size="14" /> 删除
              </button>
            </div>
            <div class="field-row">
              <div class="field">
                <label class="field__label">公司名称</label>
                <input v-model="exp.company" class="input" placeholder="公司名称" />
              </div>
              <div class="field">
                <label class="field__label">职位名称</label>
                <input v-model="exp.position" class="input" placeholder="你的岗位" />
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label class="field__label">开始时间</label>
                <GsMonthPicker v-model="exp.start_date" placeholder="开始年月" />
              </div>
              <div class="field">
                <label class="field__label">结束时间（在职留空）</label>
                <GsMonthPicker v-model="exp.end_date" placeholder="结束年月" :clearable="true" />
              </div>
            </div>
            <div class="field">
              <label class="field__label">工作描述</label>
              <textarea v-model="exp.description" class="input textarea" placeholder="描述你的主要职责与成果…"></textarea>
            </div>
          </div>
        </div>

        <div class="exp-footer">
          <button type="button" class="btn btn--outline" @click="addExperience">
            <Plus :size="15" style="margin-right:4px" />添加经历
          </button>
          <button class="btn btn--primary" :disabled="saving" @click="save">
            <Check v-if="saved" :size="16" style="margin-right:4px" />
            {{ saving ? '保存中…' : saved ? '已保存 ✓' : '保存经历' }}
          </button>
        </div>
      </div>

      <!-- ── Tab: 项目经历 ─────────────────────────────────────── -->
      <div v-else-if="activeTab === 'project'" class="profile-card fade-up">
        <div class="exp-list">
          <div v-if="projects.length === 0" class="exp-empty">
            <FileText :size="36" color="var(--gs-text-3)" />
            <p>暂无项目经历，点击下方添加</p>
          </div>

          <div v-for="(proj, i) in projects" :key="i" class="exp-entry">
            <div class="exp-entry__header">
              <span class="exp-entry__num">项目 {{ i + 1 }}</span>
              <button type="button" class="btn btn--ghost btn--sm exp-remove" @click="removeProject(i)">
                <Trash2 :size="14" /> 删除
              </button>
            </div>
            <div class="field-row">
              <div class="field">
                <label class="field__label">项目名称</label>
                <input v-model="proj.project_name" class="input" placeholder="项目名称" />
              </div>
              <div class="field">
                <label class="field__label">项目链接（选填）</label>
                <div class="input-with-icon">
                  <Link :size="14" class="input-icon" />
                  <input v-model="proj.project_link" class="input input--icon" placeholder="https://..." />
                </div>
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label class="field__label">开始时间</label>
                <GsMonthPicker v-model="proj.start_date" placeholder="开始年月" />
              </div>
              <div class="field">
                <label class="field__label">结束时间（进行中留空）</label>
                <GsMonthPicker v-model="proj.end_date" placeholder="结束年月" :clearable="true" />
              </div>
            </div>
            <div class="field">
              <label class="field__label">技术栈</label>
              <div class="skill-tags">
                <span v-for="(t, ti) in proj.tech_stack" :key="t" class="tag tag--green skill-tag">
                  {{ t }}
                  <button type="button" class="skill-tag__remove" @click="removeTech(i, ti)">×</button>
                </span>
              </div>
              <div class="skill-input-row">
                <input
                  v-model="techInputs[i]"
                  class="input"
                  placeholder="输入技术后按 Enter（如 Vue3、Python…）"
                  @keydown.enter.prevent="addTech(i)"
                />
                <button type="button" class="btn btn--outline btn--sm" @click="addTech(i)">添加</button>
              </div>
            </div>
            <div class="field">
              <label class="field__label">项目描述</label>
              <textarea v-model="proj.description" class="input textarea" placeholder="描述项目背景、你的职责与贡献…"></textarea>
            </div>
            <div class="field">
              <label class="field__label">项目成果</label>
              <textarea v-model="proj.results" class="input textarea" style="height:72px" placeholder="量化成果，例：用户增长 30%、性能提升 2x…"></textarea>
            </div>
          </div>
        </div>

        <div class="exp-footer">
          <button type="button" class="btn btn--outline" @click="addProject">
            <Plus :size="15" style="margin-right:4px" />添加项目
          </button>
          <button class="btn btn--primary" :disabled="saving" @click="save">
            <Check v-if="saved" :size="16" style="margin-right:4px" />
            {{ saving ? '保存中…' : saved ? '已保存 ✓' : '保存项目' }}
          </button>
        </div>
      </div>

      <!-- ── Tab: 我的简历 ─────────────────────────────────────── -->
      <div v-else-if="activeTab === 'resume'" class="profile-card fade-up">
        <div v-if="resumeUrl" class="resume-current">
          <FileText :size="20" color="var(--gs-primary)" />
          <span class="resume-current__name">当前简历</span>
          <a :href="resumeUrl" target="_blank" rel="noopener" class="btn btn--ghost btn--sm">
            <ExternalLink :size="13" style="margin-right:3px" />查看
          </a>
        </div>
        <div v-else class="resume-empty">
          <FileText :size="40" color="var(--gs-text-3)" />
          <p>尚未上传简历</p>
        </div>

        <hr class="divider" style="margin-block:var(--space-6)" />

        <div class="field">
          <label class="field__label">上传附件简历</label>
          <p class="field__hint">支持 PDF、DOC、DOCX 格式，建议 5MB 以内</p>
          <label class="upload-zone">
            <Upload :size="22" color="var(--gs-primary)" />
            <span v-if="resumeFile">{{ resumeFile.name }}</span>
            <span v-else>点击选择文件</span>
            <input type="file" accept=".pdf,.doc,.docx" style="display:none" @change="onFileChange" />
          </label>
          <p v-if="uploadError" class="field__error">{{ uploadError }}</p>
          <button
            v-if="resumeFile"
            type="button"
            class="btn btn--primary"
            style="margin-top:var(--space-3)"
            :disabled="uploading"
            @click="uploadResume"
          >
            {{ uploading ? '上传中…' : '确认上传' }}
          </button>
        </div>

        <hr class="divider" style="margin-block:var(--space-6)" />

        <div class="field">
          <label class="field__label">或填写在线简历链接</label>
          <p class="field__hint">可粘贴 Google Drive、OneDrive、超简历等平台的分享链接</p>
          <input v-model="resumeUrl" class="input" placeholder="https://…" />
        </div>

        <div class="form-actions">
          <button class="btn btn--primary" :disabled="saving" @click="save">
            <Check v-if="saved" :size="16" style="margin-right:4px" />
            {{ saving ? '保存中…' : saved ? '已保存 ✓' : '保存链接' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.page-wrap { padding-block: var(--space-10); }

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--gs-text);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-6);
}

/* ── Header ── */
.profile-header {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
  padding: var(--space-5) var(--space-6);
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
}

.profile-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}
.profile-avatar {
  width: 64px; height: 64px;
  border-radius: var(--radius-full);
  background: var(--gs-primary-tint);
  border: 2px solid var(--gs-border);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-size: var(--text-2xl); font-weight: 800;
  color: var(--gs-primary);
  overflow: hidden;
  transition: opacity var(--duration-fast);
}
.profile-avatar--uploading { opacity: 0.6; }
.profile-avatar__img { width: 100%; height: 100%; object-fit: cover; }
.profile-avatar__camera {
  position: absolute;
  bottom: -2px; right: -2px;
  width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  background: var(--gs-primary);
  border: 2px solid var(--gs-surface);
  border-radius: var(--radius-full);
  color: #fff;
  cursor: pointer;
  transition: background var(--duration-fast);
}
.profile-avatar__camera:hover { background: var(--gs-primary-dark, oklch(45% 0.138 144)); }

.profile-name {
  font-size: var(--text-xl); font-weight: 700; color: var(--gs-text);
  margin-bottom: var(--space-2);
}
.avatar-error {
  font-size: var(--text-xs); color: oklch(55% 0.18 25); margin-top: var(--space-1);
}

/* ── Tabs ── */
.tab-nav {
  display: flex;
  gap: 0;
  margin-bottom: var(--space-5);
  border-bottom: 2px solid var(--gs-border);
  overflow-x: auto;
}
.tab-nav__item {
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--gs-text-2);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  white-space: nowrap;
  transition: color var(--duration-fast), border-color var(--duration-fast);
}
.tab-nav__item:hover { color: var(--gs-text); }
.tab-nav__item--active {
  color: var(--gs-primary);
  border-bottom-color: var(--gs-primary);
  font-weight: 600;
}

/* ── Card ── */
.profile-card {
  background: var(--gs-surface);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-sm);
}

/* ── Form ── */
.profile-form { display: flex; flex-direction: column; gap: var(--space-5); }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.field { display: flex; flex-direction: column; gap: var(--space-2); }
.field__label { font-size: var(--text-sm); font-weight: 500; color: var(--gs-text-2); }
.field__hint { font-size: var(--text-xs); color: var(--gs-text-3); margin-top: -4px; }
.field__error { font-size: var(--text-xs); color: oklch(55% 0.18 25); margin-top: var(--space-1); }
.textarea { height: 100px; resize: vertical; padding-block: var(--space-3); }

.salary-range { display: flex; align-items: center; gap: var(--space-3); }
.salary-range .input { flex: 1; }
.salary-sep { color: var(--gs-text-3); font-weight: 500; flex-shrink: 0; }

/* ── Input with icon ── */
.input-with-icon { position: relative; }
.input-icon {
  position: absolute; left: var(--space-3); top: 50%; transform: translateY(-50%);
  color: var(--gs-text-3); pointer-events: none;
}
.input--icon { padding-left: calc(var(--space-3) * 2 + 14px); }

/* ── Skills / Tags ── */
.skill-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-2); min-height: 28px; }
.skill-tag { gap: var(--space-1); }
.skill-tag__remove { background: none; border: none; color: inherit; cursor: pointer; font-size: 1rem; line-height: 1; padding: 0 2px; }
.skill-input-row { display: flex; gap: var(--space-2); }
.skill-input-row .input { flex: 1; height: 36px; }

/* ── Experience entries ── */
.exp-list { display: flex; flex-direction: column; gap: var(--space-6); }
.exp-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--space-3); padding: var(--space-10);
  color: var(--gs-text-3); font-size: var(--text-sm);
}
.exp-entry {
  display: flex; flex-direction: column; gap: var(--space-4);
  padding: var(--space-5);
  background: var(--gs-bg);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
}
.exp-entry__header {
  display: flex; align-items: center; justify-content: space-between;
}
.exp-entry__num { font-size: var(--text-sm); font-weight: 600; color: var(--gs-text-2); }
.exp-remove { display: flex; align-items: center; gap: 4px; color: oklch(55% 0.18 25); }
.exp-remove:hover { background: oklch(97% 0.01 25); }

.exp-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--space-5);
  padding-top: var(--space-5);
  border-top: 1px solid var(--gs-border);
}

/* ── Resume ── */
.resume-current {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  background: var(--gs-primary-tint);
  border: 1px solid var(--gs-border);
  border-radius: var(--radius-lg);
}
.resume-current__name { flex: 1; font-size: var(--text-sm); font-weight: 500; color: var(--gs-text); }
.resume-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--space-3); padding: var(--space-8);
  color: var(--gs-text-3); font-size: var(--text-sm);
}
.upload-zone {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--space-2); padding: var(--space-8);
  border: 2px dashed var(--gs-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  color: var(--gs-text-2);
  font-size: var(--text-sm);
  transition: border-color var(--duration-fast), background var(--duration-fast);
}
.upload-zone:hover {
  border-color: var(--gs-primary);
  background: var(--gs-primary-tint);
}

/* ── Actions ── */
.form-actions { display: flex; justify-content: flex-end; padding-top: var(--space-2); }

@media (max-width: 600px) {
  .field-row { grid-template-columns: 1fr; }
  .tab-nav__item { padding-inline: var(--space-3); font-size: var(--text-xs); }
  .exp-footer { flex-direction: column; gap: var(--space-3); align-items: stretch; }
  .exp-footer .btn { width: 100%; justify-content: center; }
}
</style>
